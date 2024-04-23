from uuid import uuid4

from src.db.engine_session import SessionLocal
from src.db.models.feedback import Feedback as FeedbackModel
from src.types.Feedback import Feedback


def log_feedback(feedback: Feedback):
    with SessionLocal() as session:
        row = FeedbackModel(
            feedback_id=str(uuid4()),
            user_id=feedback["user_id"],
            type=feedback["type"],
            content=feedback.get("content", ""),
        )
        session.add(row)
        session.commit()
