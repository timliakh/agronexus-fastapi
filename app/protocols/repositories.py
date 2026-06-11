from typing import Protocol

from sqlalchemy.orm import Session

from app.db_models import FeedbackRecord, OrderRecord, ProductRecord
from app.models import Category, ProductBase, ProductCreate, ProductUpdate


class ProductRepository(Protocol):
    def count(self, db: Session) -> int: ...

    def get_by_id(self, db: Session, product_id: int) -> ProductRecord | None: ...

    def get_by_slug(self, db: Session, slug: str) -> ProductRecord | None: ...

    def list_records(
        self,
        db: Session,
        category: Category | None = None,
        manufacturer: str | None = None,
        limit: int | None = 20,
    ) -> list[ProductRecord]: ...

    def list_manufacturers(self, db: Session) -> list[str]: ...

    def list_all(self, db: Session) -> list[ProductRecord]: ...

    def create(self, db: Session, product_data: ProductBase) -> ProductRecord: ...

    def update(
        self,
        db: Session,
        product_id: int,
        product_data: ProductUpdate,
    ) -> ProductRecord | None: ...

    def set_image_url(
        self,
        db: Session,
        product_id: int,
        image_url: str | None,
    ) -> ProductRecord | None: ...

    def delete(self, db: Session, product_id: int) -> bool: ...


class OrderRepository(Protocol):
    def get_by_id(self, db: Session, order_id: int) -> OrderRecord | None: ...

    def list_all(self, db: Session) -> list[OrderRecord]: ...

    def create(
        self,
        db: Session,
        customer_name: str,
        email: str,
        items: list[dict],
        total_price: float,
    ) -> OrderRecord: ...

    def total_revenue(self, db: Session) -> float: ...


class FeedbackRepository(Protocol):
    def count(self, db: Session) -> int: ...

    def list_all(self, db: Session) -> list[FeedbackRecord]: ...

    def create(
        self,
        db: Session,
        name: str,
        message: str,
        email: str,
        phone: str | None,
        is_premium: bool,
    ) -> FeedbackRecord: ...

    def delete(self, db: Session, feedback_id: int) -> bool: ...
