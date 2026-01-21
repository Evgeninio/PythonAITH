from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker

from app.settings import settings as app_settings
from app.db.models import Order


def _get_last_order_id() -> int:
    engine = create_engine(app_settings.db_dsn, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with SessionLocal() as db:
        row = db.execute(select(Order.id).order_by(desc(Order.id))).first()
        assert row is not None
        return int(row[0])


def test_create_order_publish_failed_marks_order(client: TestClient):
    async def failing_publisher(order_id: int):
        raise RuntimeError("rmq down")

    client.app.state.publisher = failing_publisher

    payload = {"customer_id": 1, "items": [{"sku": "abc", "qty": 1}], "total": 1.0}
    r = client.post("/orders", json=payload)

    assert r.status_code == 503
    assert r.json()["detail"] == "Failed to publish event"

    order_id = _get_last_order_id()
    r2 = client.get(f"/orders/{order_id}")

    assert r2.status_code == 200
    data = r2.json()
    assert data["status"] == "PUBLISH_FAILED"
    assert data["error"].startswith("publish_error:")
