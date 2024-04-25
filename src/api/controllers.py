# /generate_questions
import hashlib
import json

import httpx
from fastapi import APIRouter, Body, Depends, Query
from typing_extensions import Annotated, List, Optional

from src.api.utils.auth import auth
from src.db.repositories.feedback import log_feedback
from src.db.repositories.qa_session import (
    get_cv,
    get_generate_more_feedbacks,
    get_job_description,
    get_latest_hash,
    get_qa_pairs,
    get_session_ids,
    log_generate_more_feedback,
    register_qa_session,
    update_cv,
    update_job_description,
    update_qa_pairs,
)
from src.services.generate_qas.main import QenerateQAsOutput, generate_qas
from src.services.handle_log_in import handle_log_in as handle_log_in_
from src.types.Feedback import Feedback

router = APIRouter()


@router.post("/register_session")
async def register_session(
    user_id: Annotated[str, Depends(auth)],
    session_id: Annotated[str, Body()],
):
    register_qa_session(user_id, session_id)


@router.post("/log_cv_and_job_description")
async def log_cv_and_job_description(
    user_sub: Annotated[str, Depends(auth)],
    session_id: Annotated[str, Body()],
    cv: Annotated[str, Body()],
    job_description: Annotated[str, Body()],
):
    update_cv(session_id, cv)
    update_job_description(session_id, job_description)


@router.get("/get_cv_and_job_description")
async def get_cv_and_job_description(
    user_sub: Annotated[str, Depends(auth)], session_id: str
):
    cv = get_cv(session_id)
    job_description = get_job_description(session_id)
    return {"cv": cv, "job_description": job_description}


@router.get("/generate_qa_batch")
async def generate_qa_batch(
    user_id: str,
    session_id: str,
    cv: str,
    job_description: str,
    user_sub: Annotated[str, Depends(auth)],
    last_question_n: int = 0,
    feedback: str = "",
) -> QenerateQAsOutput:
    # /generate with optional feedback param
    #   register feedback if provided
    #   fetch feedbacks
    #   fetch prev questions
    #   do the other stuff - construct object, construct prompt
    if feedback and last_question_n:
        log_generate_more_feedback(
            session_id, {"after_n_questions": last_question_n, "feedback": feedback}
        )

    feedbacks = get_generate_more_feedbacks(session_id)

    qa_pairs = get_qa_pairs(session_id)

    """
    1. based on cv and job_description generate qa pairs

    3. update db with new pairs and hash
        - have standard db shit
    4. return pairs and hash
    """
    qas_generation_out = await generate_qas(
        user_id, cv, job_description, qa_pairs, feedbacks
    )

    if qas_generation_out["status"] == "prompt_to_top_up":
        return qas_generation_out

    # db
    #   incorporate new questions into qa pairs
    qa_pairs_ = qa_pairs + qas_generation_out["qa_pairs"]
    update_qa_pairs(session_id, qa_pairs_)

    # return
    return qas_generation_out


@router.get("/get_qas")
async def get_qas(user_sub: Annotated[str, Depends(auth)], session_id: str):
    qa_pairs = get_qa_pairs(session_id)
    return {"qa_pairs": qa_pairs}


@router.get("/get_qa_session_ids")
async def get_qa_session_ids(user_sub: Annotated[str, Depends(auth)]):
    # returns list of session ids that are associated with given user_id
    # when I have auth - user_id is sub and is retrieved from auth details
    session_ids = get_session_ids(user_id=user_sub)
    return {"session_ids": session_ids}


@router.post("/handle_log_in")
async def handle_log_in(user_sub: Annotated[str, Depends(auth)]):
    handle_log_in_(user_id=user_sub)


@router.post("/feedback")
async def feedback(user_id: Annotated[str, Depends(auth)], feedback: Feedback):
    log_feedback(feedback)
