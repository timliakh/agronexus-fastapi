from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_order_service
from app.i18n import translate
from app.logger import logger
from app.models import Order, OrderCreate
from app.services.order_service import OrderService

router = APIRouter(tags=["orders"])


@router.post("/orders", response_model=Order, status_code=201)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    order = order_service.create_order(db, order_data)
    logger.info("Created order #%s for %s", order.id, order.customer_name)
    return order


@router.get("/orders/{order_id}", response_model=Order)
def get_order(
    order_id: int,
    lang: str = Query(default="ru"),
    db: Session = Depends(get_db),
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    order = order_service.get_order(db, order_id)
    if order is None:
        raise HTTPException(
            status_code=404,
            detail=translate("order_not_found", lang),
        )
    return order
