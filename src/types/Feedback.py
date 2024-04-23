from typing_extensions import Literal, TypedDict, Union


class FeedbackQuestionThumnsUp(TypedDict):
    type: Literal["question_thumbs_up"]
    user_id: str


class FeedbackQuestionThumnsDown(TypedDict):
    type: Literal["question_thumbs_down"]
    user_id: str
    content: str


class BottomFeedback(TypedDict):
    type: Literal["bottom_feedback"]
    user_id: str
    content: str


Feedback = Union[FeedbackQuestionThumnsUp, FeedbackQuestionThumnsDown, BottomFeedback]
