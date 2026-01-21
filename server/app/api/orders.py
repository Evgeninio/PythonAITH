from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.models import Order
from app.metrics import ORDERS_CREATED_TOTAL
from app.services.publisher import publish_order_created
from app.settings import settings

router = APIRouter()


class Item(BaseModel):
    sku: str = Field(min_length=1)
    qty: int = Field(ge=1)


class CreateOrderIn(BaseModel):
    customer_id: int = Field(ge=1)
    items: list[Item] = Field(min_length=1)
    total: float = Field(gt=0)


class OrderOut(BaseModel):
    id: int
    customer_id: int
    status: str
    items: list[Item]
    total: float
    error: str | None = None


def _order_to_out(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        customer_id=order.customer_id,
        status=order.status,
        items=[Item(**i) for i in order.items],
        total=float(order.total),
        error=order.error,
    )


@router.post("/orders", response_model=OrderOut, status_code=201)
async def create_order(payload: CreateOrderIn, request: Request):
    db: Session = request.state.db

    order = Order(
        customer_id=payload.customer_id,
        items=[i.model_dump() for i in payload.items],
        total=payload.total,
        status="NEW",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    ORDERS_CREATED_TOTAL.inc()

    try:
        publisher = getattr(request.app.state, "publisher", None)
        if publisher is None:
            await publish_order_created(
                rmq_url=settings.rmq_url,
                exchange_name=settings.rmq_exchange,
                routing_key=settings.rmq_routing_key_created,
                order_id=order.id,
            )
        else:
            await publisher(order.id)
    except Exception as e:
        order.status = "PUBLISH_FAILED"
        order.error = f"publish_error: {type(e).__name__}"
        db.add(order)
        db.commit()
        db.refresh(order)
        raise HTTPException(status_code=503, detail="Failed to publish event") from e

    return _order_to_out(order)


@router.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, request: Request):
    db: Session = request.state.db
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _order_to_out(order)
