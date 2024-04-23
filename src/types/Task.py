from typing_extensions import Literal, TypedDict


class GenerateQuestionTask(TypedDict):
    type: Literal["generate_question"]

class GenerateAnswerTask(TypedDict):
    type: Literal["generate_question"]


Task = Union[]

async def generate_question_recursive():
    # generate question
    # send to the loop
    #   answer generation
    #   next question generation
    pass

async def generate_question():
    pass

async def generate_answer():
    pass