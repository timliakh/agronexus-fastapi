from sqlalchemy.orm import Session

from app.db_models import ProductRecord
from app.models import Category, ProductBase, ProductCreate, ProductUpdate


class SqlAlchemyProductRepository:
    def count(self, db: Session) -> int:
        return db.query(ProductRecord).count()

    def get_by_id(self, db: Session, product_id: int) -> ProductRecord | None:
        return db.get(ProductRecord, product_id)

    def get_by_slug(self, db: Session, slug: str) -> ProductRecord | None:
        return db.query(ProductRecord).filter(ProductRecord.slug == slug).first()

    def list_records(
        self,
        db: Session,
        category: Category | None = None,
        manufacturer: str | None = None,
        limit: int | None = 20,
    ) -> list[ProductRecord]:
        query = db.query(ProductRecord)
        if category is not None:
            query = query.filter(ProductRecord.category == category.value)
        if manufacturer is not None:
            query = query.filter(ProductRecord.manufacturer == manufacturer)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def list_manufacturers(self, db: Session) -> list[str]:
        rows = (
            db.query(ProductRecord.manufacturer)
            .distinct()
            .order_by(ProductRecord.manufacturer)
            .all()
        )
        return [row[0] for row in rows]

    def list_all(self, db: Session) -> list[ProductRecord]:
        return db.query(ProductRecord).order_by(ProductRecord.id).all()

    def create(self, db: Session, product_data: ProductBase) -> ProductRecord:
        record = ProductRecord(
            slug=product_data.slug,
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            category=product_data.category.value,
            manufacturer=product_data.manufacturer,
            configurations=product_data.configurations,
            in_stock=product_data.in_stock,
            image_url=product_data.image_url,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def update(
        self,
        db: Session,
        product_id: int,
        product_data: ProductUpdate,
    ) -> ProductRecord | None:
        record = db.get(ProductRecord, product_id)
        if record is None:
            return None

        updates = product_data.model_dump(exclude_unset=True)
        if "category" in updates and updates["category"] is not None:
            updates["category"] = updates["category"].value

        for field, value in updates.items():
            setattr(record, field, value)

        db.commit()
        db.refresh(record)
        return record

    def set_image_url(
        self,
        db: Session,
        product_id: int,
        image_url: str | None,
    ) -> ProductRecord | None:
        record = db.get(ProductRecord, product_id)
        if record is None:
            return None
        record.image_url = image_url
        db.commit()
        db.refresh(record)
        return record

    def delete(self, db: Session, product_id: int) -> bool:
        record = db.get(ProductRecord, product_id)
        if record is None:
            return False
        db.delete(record)
        db.commit()
        return True
