import json

from typing_extensions import List

from src.db.engine_session import SessionLocal
from src.db.models.user import User as UserModel
from src.types.UserFlag import Flag


def add_flag(user_id: str, flag: Flag):
    with SessionLocal() as session:
        row = session.query(UserModel).filter(UserModel.user_id == user_id).first()
        if row:
            flags = json.loads(row.flags)  # type: ignore
            new_flags = flags + [flag]
            row.flags = json.dumps(new_flags)  # type: ignore
            session.commit()
            return

        # create if doesn't exist
        row = UserModel(user_id=user_id, flags=[flag])
        session.add(row)
        session.commit()


def add_tokens(user_id: str, num_tokens: int):
    with SessionLocal() as session:
        row = session.query(UserModel).filter(UserModel.user_id == user_id).first()
        if row:
            row.tokens = row.tokens + num_tokens  # type: ignore
            session.commit()
            return

        # create if doesn't exist
        row = UserModel(user_id=user_id, tokens=num_tokens)
        session.add(row)
        session.commit()


def get_flags(user_id: str) -> List[Flag]:
    with SessionLocal() as session:
        row = session.query(UserModel).filter(UserModel.user_id == user_id).first()
        if row:
            return json.loads(row.flags)  # type: ignore

        # default if doesn't exist
        return []


def get_tokens(user_id: str) -> int:
    with SessionLocal() as session:
        row = session.query(UserModel).filter(UserModel.user_id == user_id).first()
        if row:
            return row.tokens  # type: ignore

        # default if doesn't exist
        return 5000
