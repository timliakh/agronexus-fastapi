from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.db_models import ProductRecord
from app.i18n import get_product_translation, get_ui
from app.mappers import localize_product, to_product
from app.models import BrandOption, Category, Product, ProductBase, ProductCreate, ProductUpdate
from app.protocols.repositories import ProductRepository
from app.protocols.storage import ImageStorage
from app.search import score_product
from app.slugify import unique_slug


class ProductService:
    def __init__(
        self,
        product_repo: ProductRepository,
        image_storage: ImageStorage,
    ) -> None:
        self._products = product_repo
        self._images = image_storage

    def count(self, db: Session) -> int:
        return self._products.count(db)

    def get_product(
        self,
        db: Session,
        product_id: int,
        lang: str | None = None,
    ) -> Product | None:
        record = self._products.get_by_id(db, product_id)
        if record is None:
            return None
        return localize_product(to_product(record), lang)

    def get_product_by_slug(
        self,
        db: Session,
        slug: str,
        lang: str | None = None,
    ) -> Product | None:
        record = self._products.get_by_slug(db, slug)
        if record is None:
            return None
        return localize_product(to_product(record), lang)

    def get_product_by_identifier(
        self,
        db: Session,
        identifier: str,
        lang: str | None = None,
    ) -> Product | None:
        if identifier.isdigit():
            return self.get_product(db, int(identifier), lang=lang)
        return self.get_product_by_slug(db, identifier, lang=lang)

    def list_products(
        self,
        db: Session,
        category: Category | None = None,
        brand: str | None = None,
        q: str | None = None,
        limit: int = 20,
        lang: str | None = None,
    ) -> list[Product]:
        if q and q.strip():
            return self.search_products(
                db,
                q=q.strip(),
                category=category,
                brand=brand,
                limit=limit,
                lang=lang,
            )
        manufacturer = self._resolve_brand(db, brand) if brand else None
        if brand and manufacturer is None:
            return []
        records = self._products.list_records(
            db,
            category=category,
            manufacturer=manufacturer,
            limit=limit,
        )
        return [localize_product(to_product(record), lang) for record in records]

    def search_products(
        self,
        db: Session,
        q: str,
        category: Category | None = None,
        brand: str | None = None,
        limit: int = 20,
        lang: str | None = None,
    ) -> list[Product]:
        manufacturer = self._resolve_brand(db, brand) if brand else None
        if brand and manufacturer is None:
            return []

        records = self._products.list_records(
            db,
            category=category,
            manufacturer=manufacturer,
            limit=None,
        )
        ui = get_ui(lang)
        category_labels = ui.get("categories", {})

        scored: list[tuple[int, ProductRecord]] = []
        for record in records:
            points = score_product(
                record,
                q,
                translation=get_product_translation(record.id, lang),
                category_label=category_labels.get(record.category),
            )
            if points > 0:
                scored.append((points, record))

        scored.sort(key=lambda item: (-item[0], item[1].name.lower()))
        top = [record for _, record in scored[:limit]]
        return [localize_product(to_product(record), lang) for record in top]

    def list_brands(self, db: Session) -> list[BrandOption]:
        return [
            BrandOption(name=name, slug=self._brand_slug(name))
            for name in self._products.list_manufacturers(db)
        ]

    def _brand_slug(self, name: str) -> str:
        from app.slugify import slugify

        return slugify(name)

    def _resolve_brand(self, db: Session, brand_slug: str) -> str | None:
        for name in self._products.list_manufacturers(db):
            if self._brand_slug(name) == brand_slug:
                return name
        return None

    def list_all_products(self, db: Session) -> list[Product]:
        records = self._products.list_all(db)
        return [to_product(record) for record in records]

    def add_product(self, db: Session, product_data: ProductCreate) -> Product:
        slug = unique_slug(db, product_data.slug or product_data.name)
        payload = ProductBase(**product_data.model_dump(exclude={"slug"}), slug=slug)
        record = self._products.create(db, payload)
        return to_product(record)

    def update_product(
        self,
        db: Session,
        product_id: int,
        product_data: ProductUpdate,
    ) -> Product | None:
        updates = product_data.model_dump(exclude_unset=True)
        if updates.get("slug"):
            updates["slug"] = unique_slug(
                db, updates["slug"], exclude_id=product_id
            )
        record = self._products.update(db, product_id, ProductUpdate(**updates))
        if record is None:
            return None
        return to_product(record)

    def delete_product(self, db: Session, product_id: int) -> bool:
        record = self._products.get_by_id(db, product_id)
        if record is None:
            return False
        image_url = record.image_url
        if not self._products.delete(db, product_id):
            return False
        self._images.remove_by_url(image_url)
        return True

    async def upload_image(
        self,
        db: Session,
        product_id: int,
        file: UploadFile,
    ) -> Product | None:
        record = self._products.get_by_id(db, product_id)
        if record is None:
            return None

        self._images.remove_by_url(record.image_url)
        content = await file.read()
        image_url = self._images.save(product_id, file.filename or "", content)
        updated = self._products.set_image_url(db, product_id, image_url)
        if updated is None:
            return None
        return to_product(updated)

    def exists(self, db: Session, product_id: int) -> bool:
        return self._products.get_by_id(db, product_id) is not None

    def exists_by_slug(self, db: Session, slug: str) -> bool:
        return self._products.get_by_slug(db, slug) is not None