from typing_extensions import TypedDict


class QAPairGenerationFeedback(TypedDict):
    after_n_questions: int
    feedback: str
