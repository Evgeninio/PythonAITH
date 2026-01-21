from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def mark_processing(db: Session, order_id: int) -> None:
    db.execute(
        text("UPDATE orders SET status='PROCESSING', updated_at=NOW() WHERE id=:id"),
        {"id": order_id},
    )


def mark_processed(db: Session, order_id: int) -> None:
    db.execute(
        text("UPDATE orders SET status='PROCESSED', updated_at=NOW() WHERE id=:id"),
        {"id": order_id},
    )


def mark_failed(db: Session, order_id: int, error: str) -> None:
    db.execute(
        text("UPDATE orders SET status='FAILED', error=:err, updated_at=NOW() WHERE id=:id"),
        {"id": order_id, "err": error[:500]},
    )


def process_order(db: Session, order_id: int) -> None:
    mark_processing(db, order_id)
    mark_processed(db, order_id)
