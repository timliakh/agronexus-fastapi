from sqlalchemy.orm import Session

from app.i18n import translate
from app.models import Feedback
from app.protocols.repositories import FeedbackRepository
from app.validators import validate_feedback_message, validate_phone


class FeedbackService:
    def __init__(self, feedback_repo: FeedbackRepository) -> None:
        self._feedbacks = feedback_repo

    def submit_feedback(
        self,
        db: Session,
        feedback: Feedback,
        is_premium: bool = False,
        lang: str | None = None,
    ) -> dict[str, str]:
        validate_feedback_message(feedback.message)
        validate_phone(feedback.contact.phone)

        self._feedbacks.create(
            db,
            name=feedback.name,
            message=feedback.message,
            email=str(feedback.contact.email),
            phone=feedback.contact.phone,
            is_premium=is_premium,
        )

        message = translate("feedback_thanks", lang, name=feedback.name)
        if is_premium:
            message += translate("feedback_premium", lang)
        return {"message": message}
