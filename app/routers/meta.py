from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_product_service
from app.i18n import get_language_config, get_ui, normalize_lang
from app.services.product_service import ProductService

router = APIRouter(tags=["meta"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/languages")
def get_languages() -> dict:
    return get_language_config()


@router.get("/i18n/{lang}")
def get_translations(lang: str) -> dict:
    return get_ui(lang)


@router.get("/store")
def store_info(
    lang: str = Query(default="ru"),
    db: Session = Depends(get_db),
    product_service: ProductService = Depends(get_product_service),
) -> dict[str, str | int]:
    code = normalize_lang(lang)
    ui = get_ui(code)
    return {
        "name": ui["store_name"],
        "tagline": ui["store_tagline_short"],
        "products_count": product_service.count(db),
        "lang": code,
    }
