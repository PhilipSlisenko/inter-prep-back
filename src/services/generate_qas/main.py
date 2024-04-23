from typing_extensions import List, Literal, TypedDict

from src.db.repositories.user import add_tokens, get_tokens
from src.services.generate_qas.generate_qas import generate_qas_
from src.services.usage_tracker import UsageTracker
from src.types.QAPair import QAPair
from src.types.QAPairGenerationFeedback import QAPairGenerationFeedback


class QenerateQAsOutput(TypedDict):
    status: Literal["success", "prompt_to_top_up"]
    qa_pairs: List[QAPair]


async def generate_qas(
    user_id: str,
    cv: str,
    job_description: str,
    prev_qa_pairs: List[QAPair],
    feedbacks: List[QAPairGenerationFeedback],
) -> QenerateQAsOutput:
    # check if can generate
    # available_tokens = get_tokens(user_id)
    available_tokens = 5000
    if available_tokens <= 0:
        # handle/send plan upgrade prompt or sth
        return {"status": "prompt_to_top_up", "qa_pairs": []}

    usage_tracker = UsageTracker()
    qas = await generate_qas_(
        cv, job_description, prev_qa_pairs, feedbacks, usage_tracker
    )
    # replace with generate q and generate a
    #   generate q based on prev qs and feedbacks
    #   generate a once q is generated

    # update/deduct tokens
    # add_tokens(user_id, usage_tracker.usage * -1)

    return {"status": "success", "qa_pairs": qas}
