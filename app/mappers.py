from app.db_models import FeedbackRecord, OrderRecord, ProductRecord
from app.i18n import get_product_translation
from app.models import AdminFeedback, Category, Order, OrderItem, Product


def to_product(record: ProductRecord) -> Product:
    return Product(
        id=record.id,
        slug=record.slug,
        name=record.name,
        description=record.description,
        price=record.price,
        category=Category(record.category),
        manufacturer=record.manufacturer,
        configurations=record.configurations,
        in_stock=record.in_stock,
        image_url=record.image_url,
    )


def to_order(record: OrderRecord) -> Order:
    return Order(
        id=record.id,
        customer_name=record.customer_name,
        email=record.email,
        items=[OrderItem(**item) for item in record.items],
        total_price=record.total_price,
    )


def to_feedback(record: FeedbackRecord) -> AdminFeedback:
    return AdminFeedback(
        id=record.id,
        name=record.name,
        message=record.message,
        email=record.email,
        phone=record.phone,
        is_premium=record.is_premium,
    )


def localize_product(product: Product, lang: str | None) -> Product:
    translation = get_product_translation(product.id, lang)
    if translation is None:
        return product
    return product.model_copy(
        update={
            "name": translation.get("name", product.name),
            "description": translation.get("description", product.description),
        }
    )
