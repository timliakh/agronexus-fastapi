from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db_models import OrderRecord


class SqlAlchemyOrderRepository:
    def get_by_id(self, db: Session, order_id: int) -> OrderRecord | None:
        return db.get(OrderRecord, order_id)

    def list_all(self, db: Session) -> list[OrderRecord]:
        return db.query(OrderRecord).order_by(OrderRecord.id.desc()).all()

    def create(
        self,
        db: Session,
        customer_name: str,
        email: str,
        items: list[dict],
        total_price: float,
    ) -> OrderRecord:
        record = OrderRecord(
            customer_name=customer_name,
            email=email,
            items=items,
            total_price=total_price,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def total_revenue(self, db: Session) -> float:
        total = db.query(func.coalesce(func.sum(OrderRecord.total_price), 0.0)).scalar()
        return float(total)
