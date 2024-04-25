import asyncio
import json
import os
import uuid
from collections import deque
from time import sleep

from openai import OpenAI
from typing_extensions import Deque, List, cast

from src.services.usage_tracker import UsageTracker
from src.types.QAPair import QAPair, QAPairWithId
from src.types.QAPairGenerationFeedback import QAPairGenerationFeedback

os.environ["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]


def generate_qas_bulk_no_history(
    cv: str,
    job_description: str,
    prev_qa_pairs: List[QAPair],
    feedbacks: List[QAPairGenerationFeedback],
    usage_tacker: UsageTracker,
) -> List[QAPair]:
    # prompt that will result in generated json object
    prompt_messages = [
        {
            "role": "system",
            "content": f'''
Your goal is to produce high-quality meritocratic question-answer pairs. Those should be interview questions. Some of those should be addressing CV and job description (in combination). You should create 3 qa pairs.
You will be provided with the following:
- applicant's CV (CV)
- job description (JOB_DESCRIPTION)

""" CV
{cv}
"""

""" JOB_DESCRIPTION
{job_description}
"""
'''
            + """
IMPORTANT: You should reply according to the schema:
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "result": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "question": {
            "type": "string"
          },
          "answer": {
            "type": "string"
          }
        },
        "required": ["question", "answer"]
      }
    }
  },
  "required": ["result"]
}
""",
        }
    ]

    client = OpenAI()
    completion = client.chat.completions.create(
        # model="gpt-4-turbo-preview",
        model="gpt-3.5-turbo",
        messages=prompt_messages,  # type: ignore
        response_format={"type": "json_object"},
    )

    usage_tacker.add_usage(completion.usage.completion_tokens)  # type: ignore

    json_str = str(completion.choices[0].message.content)

    return json.loads(json_str)["result"]


async def generate_qas_(
    cv: str,
    job_description: str,
    prev_qa_pairs: List[QAPair],
    feedbacks: List[QAPairGenerationFeedback],
    usage_tacker: UsageTracker,
) -> List[QAPair]:
    # replace with generate q and generate a
    #   generate q based on prev qs and feedbacks
    #   generate a once q is generated
    PAIRS_TO_GENERATE = 3

    # i am ready to generate a once q is generated
    # but, I am ready to generate next question only once prev is generated. so, each generated question triggers two tasks
    # i can have two workers or functions
    #   one runs if prev question generated and there are more qs to generate
    #   2 runs if prev question generated and generates a
    generated_pairs: List[QAPairWithId] = []
    finished_event = asyncio.Event()
    await generate_qas_recursive(
        cv,
        job_description,
        prev_qa_pairs,
        feedbacks,
        PAIRS_TO_GENERATE,
        generated_pairs,
        finished_event,
    )

    # while not finished_event.is_set():
    #     sleep(0.1)

    return cast(List[QAPair], generated_pairs)


async def generate_qas_recursive(
    cv: str,
    job_description: str,
    prev_qa_pairs: List[QAPair],
    feedbacks: List[QAPairGenerationFeedback],
    num_to_generate: int,
    pairs_out: List[QAPairWithId],
    finished_event: asyncio.Event,
):
    # generate question
    # send to the loop
    #   answer generation
    #   next question generation
    pair_id = await generate_question(
        cv, job_description, prev_qa_pairs, feedbacks, pairs_out
    )

    loop = asyncio.get_event_loop()

    started_tasks = []

    # generate answer
    started_tasks.append(loop.create_task(generate_answer(pair_id, pairs_out)))

    # generate next question
    if num_to_generate > 1:
        started_tasks.append(
            loop.create_task(
                generate_qas_recursive(
                    cv,
                    job_description,
                    prev_qa_pairs,
                    feedbacks,
                    num_to_generate - 1,
                    pairs_out,
                    finished_event,
                )
            )
        )

    # wait for started tasks to complete
    await asyncio.gather(*started_tasks)

    # if first_call:
    #     # spin until there are no more tasks in the loop - to make sure that asyncio.run won't clean up the loop etc just because the initial task finished
    #     while [
    #         task for task in asyncio.all_tasks() if task is not asyncio.current_task()
    #     ]:
    #         await asyncio.sleep(0.1)


async def generate_question_(
    cv: str,
    job_description: str,
    prev_pairs: List[QAPair],
    feedbacks: List[QAPairGenerationFeedback],
) -> str:
    # construct prompt
    # generate question
    prompt_messages = [
        {
            "role": "system",
            "content": f'''
Your goal is to generate one high-quality interview question.
You will be provided with the following:
- applicant's CV (CV)
- job description (JOB_DESCRIPTION)

""" CV
{cv}
"""

""" JOB_DESCRIPTION
{job_description}
"""
'''
            + """
IMPORTANT: You should reply with JSON that adheres to the following schema:
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string",
      "description": "Place for you to do chain-of-thought. Do some reasoning before you generate question."
    },
    "question": {
      "type": "string",
      "description": "The Question. This is what all of this is for."
    }
    },
    "reflexion": {
      "type": "string",
      "description": "Your reflexion. How well did you do? Place for you to reflect. Next you will need to mark yourself on scale from 1 to 5. 1 being - you done awfull, and 5 - you've done great. This mark is important because I will use it to decide whether I need to check question that you generated and whether I can show to client. Whether it's good enough and won't damage my brand. So, you can also think of this as another chain-of-thought/reasoning opportunity for you to be able to give yourself appropriate mark."
    }
    },
    "mark": {
      "type": "integer",
      "description": "Finally, grade yourself (Question that you generated) on scale from 1 to 5. 1 being - you done awfull, and 5 - you've done great."
    }
  },
  "required": ["reasoning", "question", "reflexion", "mark"]
}

IMPORTANT: Questions json objects that are part of the context might be missing some fields. More specifically - they will be set to null. This is for the purpose of saving context space. You obviously must respond with strict adherence to provided JSON schema.
""",
        }
    ]
    for idx, prev_pair in enumerate(prev_pairs):
        # add prev_pair
        prompt_messages.append(
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "reasoning": None,
                        "question": prev_pair["question"],
                        "reflexion": None,
                        "mark": None,
                    }
                ),
            }
        )

        # add feedback message if appropriate
        current_question_num = idx + 1
        feedback_to_add = [
            feedback
            for feedback in feedbacks
            if feedback["after_n_questions"] == current_question_num
        ]
        if feedback_to_add:
            prompt_messages.append(
                {
                    "role": "system",
                    "content": f'''
User just shared feedback on the recent questions (FEEDBACK). Try to incorporate it when generating next questions.
""" FEEDBACK
{feedback_to_add[0]}
"""
''',
                }
            )

    client = OpenAI()
    completion = client.chat.completions.create(
        # model="gpt-4-turbo-preview",
        model="gpt-3.5-turbo",
        messages=prompt_messages,  # type: ignore
        response_format={"type": "json_object"},
    )

    # usage_tacker.add_usage(completion.usage.completion_tokens)  # type: ignore

    json_str = str(completion.choices[0].message.content)

    generated = json.loads(json_str)

    return generated.get(
        "question",
        f"ops doops (couldn't find expected top-level 'question' field):\n{json.dumps(generated)}",
    )
    # return "question_123"


async def generate_question(
    cv: str,
    job_description: str,
    prev_pairs: List[QAPair],
    feedbacks: List[QAPairGenerationFeedback],
    pairs_out: List[QAPairWithId],
) -> str:
    await asyncio.sleep(1)
    pair_id = str(uuid.uuid4())
    question = await generate_question_(cv, job_description, prev_pairs, feedbacks)
    pairs_out.append({"id": pair_id, "answer": "", "question": question})

    # print(f"q generated, pairs: {pairs}")

    return pair_id


async def generate_answer(
    pair_id: str,
    pairs: List[QAPairWithId],
):
    await asyncio.sleep(1)
    pair_of_interest = [pair for pair in pairs if pair["id"] == pair_id][0]
    question = pair_of_interest["question"]
    answer = f"a to {question}"
    pair_of_interest["answer"] = answer

    # print(f"a generated, pairs: {pairs}")
