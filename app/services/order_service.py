from sqlalchemy.orm import Session

from app.exceptions import OrderValidationError
from app.mappers import to_order, to_product
from app.models import Order, OrderCreate
from app.protocols.repositories import OrderRepository, ProductRepository


class OrderService:
    def __init__(
        self,
        product_repo: ProductRepository,
        order_repo: OrderRepository,
    ) -> None:
        self._products = product_repo
        self._orders = order_repo

    def create_order(self, db: Session, order_data: OrderCreate) -> Order:
        total_price = 0.0

        for item in order_data.items:
            record = self._products.get_by_id(db, item.product_id)
            if record is None:
                raise OrderValidationError(
                    f"Товар с id={item.product_id} не найден"
                )
            product = to_product(record)
            if not product.in_stock:
                raise OrderValidationError(
                    f"Техника «{product.name}» временно недоступна"
                )
            if item.configuration not in product.configurations:
                raise OrderValidationError(
                    f"Комплектация {item.configuration} недоступна для «{product.name}»"
                )
            total_price += product.price * item.quantity

        record = self._orders.create(
            db,
            customer_name=order_data.customer_name,
            email=str(order_data.email),
            items=[item.model_dump() for item in order_data.items],
            total_price=total_price,
        )
        return to_order(record)

    def get_order(self, db: Session, order_id: int) -> Order | None:
        record = self._orders.get_by_id(db, order_id)
        if record is None:
            return None
        return to_order(record)

    def exists(self, db: Session, order_id: int) -> bool:
        return self._orders.get_by_id(db, order_id) is not None
