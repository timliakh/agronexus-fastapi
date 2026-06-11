from sqlalchemy.orm import Session

from app.db_models import FeedbackRecord


class SqlAlchemyFeedbackRepository:
    def count(self, db: Session) -> int:
        return db.query(FeedbackRecord).count()

    def list_all(self, db: Session) -> list[FeedbackRecord]:
        return db.query(FeedbackRecord).order_by(FeedbackRecord.id.desc()).all()

    def create(
        self,
        db: Session,
        name: str,
        message: str,
        email: str,
        phone: str | None,
        is_premium: bool,
    ) -> FeedbackRecord:
        record = FeedbackRecord(
            name=name,
            message=message,
            email=email,
            phone=phone,
            is_premium=is_premium,
        )
        db.add(record)
        db.commit()
        return record

    def delete(self, db: Session, feedback_id: int) -> bool:
        record = db.get(FeedbackRecord, feedback_id)
        if record is None:
            return False
        db.delete(record)
        db.commit()
        return True
