import re

from app.exceptions import FeedbackValidationError

FORBIDDEN_WORD_PATTERNS = (
    re.compile(r"редиск\w*", re.IGNORECASE),
    re.compile(r"бяк\w*", re.IGNORECASE),
    re.compile(r"козявк\w*", re.IGNORECASE),
)
PHONE_PATTERN = re.compile(r"^\d{7,15}$")


def validate_phone(phone: str | None) -> None:
    if phone is None:
        return
    if not PHONE_PATTERN.match(phone):
        raise FeedbackValidationError(
            "Номер телефона должен содержать только цифры и быть длиной от 7 до 15 символов"
        )


def validate_feedback_message(message: str) -> None:
    for pattern in FORBIDDEN_WORD_PATTERNS:
        if pattern.search(message):
            raise FeedbackValidationError("Использование недопустимых слов")
