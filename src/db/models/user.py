from sqlalchemy import UUID, Column, Integer, String

from src.config import config

from ._base import Base


class User(Base):
    __tablename__ = config["table_names_prefix"] + "users"

    user_id = Column(String, primary_key=True)  # auth0_sub
    tokens = Column(Integer, default=0)
    flags = Column(String, default="[]")
