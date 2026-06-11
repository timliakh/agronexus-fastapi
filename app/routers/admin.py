from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.admin_auth import create_admin_token, require_admin, verify_admin_password
from app.database import get_db
from app.dependencies import get_admin_service, get_product_service
from app.models import (
    AdminFeedback,
    AdminLogin,
    AdminStats,
    Order,
    Product,
    ProductCreate,
    ProductUpdate,
)
from app.services.admin_service import AdminService
from app.services.product_service import ProductService

router = APIRouter(prefix="/admin/api", tags=["admin"])


@router.post("/login")
def admin_login(credentials: AdminLogin) -> dict[str, str]:
    if not verify_admin_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    return {"token": create_admin_token()}


@router.get("/stats", response_model=AdminStats)
def admin_stats(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
    admin_service: AdminService = Depends(get_admin_service),
) -> AdminStats:
    return admin_service.get_stats(db)


@router.get("/products", response_model=list[Product])
def admin_list_products(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
    product_service: ProductService = Depends(get_product_service),
) -> list[Product]:
    return product_service.list_all_products(db)


@router.post("/products", response_model=Product, status_code=201)
def admin_create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    return product_service.add_product(db, product_data)


@router.put("/products/{product_id}", response_model=Product)
def admin_update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    product = product_service.update_product(db, product_id, product_data)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/products/{product_id}", status_code=204)
def admin_delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
    product_service: ProductService = Depends(get_product_service),
) -> None:
    if not product_service.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")


@router.post("/products/{product_id}/image", response_model=Product)
async def admin_upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    product = await product_service.upload_image(db, product_id, file)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/orders", response_model=list[Order])
def admin_list_orders(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
    admin_service: AdminService = Depends(get_admin_service),
) -> list[Order]:
    return admin_service.list_orders(db)


@router.get("/feedbacks", response_model=list[AdminFeedback])
def admin_list_feedbacks(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
    admin_service: AdminService = Depends(get_admin_service),
) -> list[AdminFeedback]:
    return admin_service.list_feedbacks(db)


@router.delete("/feedbacks/{feedback_id}", status_code=204)
def admin_delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
    admin_service: AdminService = Depends(get_admin_service),
) -> None:
    if not admin_service.delete_feedback(db, feedback_id):
        raise HTTPException(status_code=404, detail="Feedback not found")
