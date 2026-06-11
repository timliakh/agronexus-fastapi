from sqlalchemy.orm import Session

from app.mappers import to_feedback, to_order
from app.models import AdminFeedback, AdminStats, Order
from app.protocols.repositories import (
    FeedbackRepository,
    OrderRepository,
    ProductRepository,
)


class AdminService:
    def __init__(
        self,
        product_repo: ProductRepository,
        order_repo: OrderRepository,
        feedback_repo: FeedbackRepository,
    ) -> None:
        self._products = product_repo
        self._orders = order_repo
        self._feedbacks = feedback_repo

    def get_stats(self, db: Session) -> AdminStats:
        return AdminStats(
            products_count=self._products.count(db),
            orders_count=len(self._orders.list_all(db)),
            feedbacks_count=self._feedbacks.count(db),
            total_revenue=self._orders.total_revenue(db),
        )

    def list_orders(self, db: Session) -> list[Order]:
        records = self._orders.list_all(db)
        return [to_order(record) for record in records]

    def list_feedbacks(self, db: Session) -> list[AdminFeedback]:
        records = self._feedbacks.list_all(db)
        return [to_feedback(record) for record in records]

    def delete_feedback(self, db: Session, feedback_id: int) -> bool:
        return self._feedbacks.delete(db, feedback_id)
