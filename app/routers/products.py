from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_product_service
from app.i18n import translate
from app.logger import logger
from app.models import BrandOption, Category, Product
from app.services.product_service import ProductService

router = APIRouter(tags=["products"])


@router.get("/products", response_model=list[Product])
def get_products(
    category: Category | None = None,
    brand: str | None = None,
    q: str | None = Query(default=None, min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    lang: str = Query(default="ru"),
    db: Session = Depends(get_db),
    product_service: ProductService = Depends(get_product_service),
) -> list[Product]:
    logger.info("Fetching products list")
    return product_service.list_products(
        db,
        category=category,
        brand=brand,
        q=q,
        limit=limit,
        lang=lang,
    )


@router.get("/products/brands", response_model=list[BrandOption])
def list_brands(
    db: Session = Depends(get_db),
    product_service: ProductService = Depends(get_product_service),
) -> list[BrandOption]:
    return product_service.list_brands(db)


@router.get("/products/suggest", response_model=list[Product])
def suggest_products(
    q: str = Query(..., min_length=2, max_length=100),
    category: Category | None = None,
    brand: str | None = None,
    limit: int = Query(default=5, ge=1, le=10),
    lang: str = Query(default="ru"),
    db: Session = Depends(get_db),
    product_service: ProductService = Depends(get_product_service),
) -> list[Product]:
    return product_service.search_products(
        db,
        q=q.strip(),
        category=category,
        brand=brand,
        limit=limit,
        lang=lang,
    )


@router.get("/products/{identifier}", response_model=Product)
def get_product(
    identifier: str,
    lang: str = Query(default="ru"),
    db: Session = Depends(get_db),
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    product = product_service.get_product_by_identifier(db, identifier, lang=lang)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail=translate("product_not_found", lang),
        )
    return product
