from sqlalchemy import UUID, Column, Integer, String

from src.config import config

from ._base import Base


class QASession(Base):
    __tablename__ = config["table_names_prefix"] + "qa_sessions"
    __table_args__ = {"schema": "public"}

    user_id = Column(String, default="")
    session_id = Column(String, primary_key=True)
    latest_hash = Column(String, default="")
    cv = Column(String, default="")
    job_description = Column(String, default="")
    qa_pairs = Column(String, default="[]")
    feedbacks = Column(String, default="[]")
