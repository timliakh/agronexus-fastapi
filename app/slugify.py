import re
import unicodedata

from sqlalchemy.orm import Session

from app.db_models import ProductRecord


def slugify(text: str, max_length: int = 80) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    slug = slug[:max_length].rstrip("-")
    return slug or "product"


def unique_slug(
    db: Session,
    base: str,
    *,
    exclude_id: int | None = None,
) -> str:
    candidate = slugify(base)
    if not _slug_taken(db, candidate, exclude_id):
        return candidate

    suffix = 2
    while True:
        candidate = f"{slugify(base, max_length=72)}-{suffix}"
        if not _slug_taken(db, candidate, exclude_id):
            return candidate
        suffix += 1


def _slug_taken(db: Session, slug: str, exclude_id: int | None) -> bool:
    record = db.query(ProductRecord).filter(ProductRecord.slug == slug).first()
    if record is None:
        return False
    return exclude_id is None or record.id != exclude_id
