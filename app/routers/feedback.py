from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_feedback_service
from app.models import Feedback
from app.services.feedback_service import FeedbackService

router = APIRouter(tags=["feedback"])


@router.post("/feedback")
def submit_feedback(
    feedback: Feedback,
    is_premium: bool = False,
    lang: str = Query(default="ru"),
    db: Session = Depends(get_db),
    feedback_service: FeedbackService = Depends(get_feedback_service),
) -> dict[str, str]:
    return feedback_service.submit_feedback(
        db, feedback, is_premium=is_premium, lang=lang
    )
