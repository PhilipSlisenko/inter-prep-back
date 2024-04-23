import json

from typing_extensions import List

from src.db.engine_session import SessionLocal
from src.db.models.qa_session import QASession as QASessionModel
from src.types.QAPair import QAPair
from src.types.QAPairGenerationFeedback import QAPairGenerationFeedback


def register_qa_session(user_id: str, session_id: str):
    with SessionLocal() as session:
        row = (
            session.query(QASessionModel)
            .filter(QASessionModel.session_id == session_id)
            .first()
        )
        if row:
            row.user_id = user_id  # type: ignore
            session.commit()
            return

        # create if doesn't exist
        row = QASessionModel(user_id=user_id, session_id=session_id)
        session.add(row)
        session.commit()


def get_latest_hash(user_id: str) -> str:
    with SessionLocal() as session:
        row = (
            session.query(QASessionModel)
            .filter(QASessionModel.user_id == user_id)
            .first()
        )

    if row:
        return row.latest_hash  # type: ignore

    return ""


def get_qa_pairs(session_id: str) -> List[QAPair]:
    with SessionLocal() as session:
        row = (
            session.query(QASessionModel)
            .filter(QASessionModel.session_id == session_id)
            .first()
        )

    if row:
        return json.loads(row.qa_pairs)  # type: ignore

    # create if doesn't exist
    blank_qa_pairs: List[QAPair] = []
    return blank_qa_pairs


def update_qa_pairs(session_id: str, new_qa_pairs: List[QAPair], hash: str = ""):
    with SessionLocal() as session:
        row = (
            session.query(QASessionModel)
            .filter(QASessionModel.session_id == session_id)
            .first()
        )
        if row:
            row.qa_pairs = json.dumps(new_qa_pairs)  # type: ignore
            session.commit()
            return

        # create if doesn't exist
        row = QASessionModel(
            session_id=session_id, latest_hash=hash, qa_pairs=json.dumps(new_qa_pairs)
        )
        session.add(row)
        session.commit()


def get_session_ids(user_id: str) -> List[str]:
    with SessionLocal() as session:
        rows = (
            session.query(QASessionModel)
            .filter(QASessionModel.user_id == user_id)
            .all()
        )

        if not rows:
            return []

        session_ids: List[str] = [row.session_id for row in rows]  # type: ignore
        return session_ids


def get_cv(session_id: str):
    with SessionLocal() as session:
        row = (
            session.query(QASessionModel)
            .filter(QASessionModel.session_id == session_id)
            .first()
        )

    if row:
        return row.cv  # type: ignore

    return ""


def update_cv(session_id: str, new_cv: str):
    with SessionLocal() as session:
        row = (
            session.query(QASessionModel)
            .filter(QASessionModel.session_id == session_id)
            .first()
        )
        if row:
            row.cv = new_cv  # type: ignore
            session.commit()
            return

        # create if doesn't exist
        row = QASessionModel(session_id=session_id, cv=new_cv)
        session.add(row)
        session.commit()


def get_job_description(session_id: str):
    with SessionLocal() as session:
        row = (
            session.query(QASessionModel)
            .filter(QASessionModel.session_id == session_id)
            .first()
        )

    if row:
        return row.job_description  # type: ignore

    return ""


def update_job_description(session_id: str, new_job_description: str):
    with SessionLocal() as session:
        row = (
            session.query(QASessionModel)
            .filter(QASessionModel.session_id == session_id)
            .first()
        )
        if row:
            row.job_description = new_job_description  # type: ignore
            session.commit()
            return

        # create if doesn't exist
        row = QASessionModel(session_id=session_id, job_description=new_job_description)
        session.add(row)
        session.commit()


def log_generate_more_feedback(session_id: str, feedback: QAPairGenerationFeedback):
    with SessionLocal() as session:
        row = (
            session.query(QASessionModel)
            .filter(QASessionModel.session_id == session_id)
            .first()
        )
        if row:
            existing_feedbacks: List[QAPairGenerationFeedback] = json.loads(row.feedbacks)  # type: ignore
            new_feedbacks = existing_feedbacks + [feedback]
            row.feedbacks = json.dumps(new_feedbacks)  # type: ignore
            session.commit()
            return

        # create if doesn't exist
        row = QASessionModel(session_id=session_id, feedbacks=json.dumps([feedback]))
        session.add(row)
        session.commit()


def get_generate_more_feedbacks(session_id: str) -> List[QAPairGenerationFeedback]:
    with SessionLocal() as session:
        row = (
            session.query(QASessionModel)
            .filter(QASessionModel.session_id == session_id)
            .first()
        )

        if row:
            return json.loads(row.feedbacks)  # type: ignore

        return []
