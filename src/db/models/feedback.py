from sqlalchemy import UUID, Column, Integer, String

from src.config import config

from ._base import Base


class Feedback(Base):
    __tablename__ = config["table_names_prefix"] + "feedbacks"

    feedback_id = Column(String, primary_key=True)
    user_id = Column(String)

    type = Column(String)
    content = Column(String)
