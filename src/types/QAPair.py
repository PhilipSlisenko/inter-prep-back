from typing_extensions import TypedDict


class QAPair(TypedDict):
    question: str
    answer: str


class QAPairWithId(QAPair):
    id: str
