from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.config import config
from app.database import get_db
from app.dependencies import get_product_service
from app.services.product_service import ProductService

router = APIRouter(tags=["pages"])

SPA_INDEX = config.paths.static_dir / "dist" / "index.html"


def _spa() -> FileResponse:
    if not SPA_INDEX.is_file():
        raise HTTPException(
            status_code=503,
            detail="Frontend not built. Run: cd frontend && npm install && npm run build",
        )
    return FileResponse(SPA_INDEX, media_type="text/html")


@router.get("/")
def read_root():
    return _spa()


@router.get("/catalog/{identifier}")
def read_product_page(
    identifier: str,
    request: Request,
    db: Session = Depends(get_db),
    product_service: ProductService = Depends(get_product_service),
):
    if identifier.isdigit():
        product = product_service.get_product(db, int(identifier))
        if product is None:
            raise HTTPException(status_code=404, detail="Товар не найден")
        target = f"/catalog/{product.slug}"
        if request.url.query:
            target = f"{target}?{request.url.query}"
        return RedirectResponse(url=target, status_code=301)
    return _spa()


@router.get("/{full_path:path}")
def spa_fallback(full_path: str):
    return _spa()
