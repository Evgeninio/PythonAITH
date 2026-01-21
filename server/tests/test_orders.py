import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import create_app
from app.db.models import Base


@pytest.fixture()
def client():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    app = create_app()

    app.state.SessionLocal = SessionLocal

    published = {"order_ids": []}

    async def fake_publisher(order_id: int):
        published["order_ids"].append(order_id)

    app.state.publisher = fake_publisher
    app.state.published = published

    with TestClient(app) as c:
        yield c


def test_health_ok(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_order_publishes_event(client: TestClient):
    payload = {"customer_id": 1, "items": [{"sku": "abc", "qty": 2}], "total": 10.5}
    r = client.post("/orders", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] >= 1
    assert data["status"] == "NEW"
    assert data["customer_id"] == 1
    assert data["items"] == [{"sku": "abc", "qty": 2}]
    assert float(data["total"]) == 10.5

    assert data["id"] in client.app.state.published["order_ids"]


def test_get_order_not_found(client: TestClient):
    r = client.get("/orders/99999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Order not found"


def test_get_order_existing(client: TestClient):
    payload = {"customer_id": 7, "items": [{"sku": "milk", "qty": 1}], "total": 3.0}
    created = client.post("/orders", json=payload).json()

    r = client.get(f"/orders/{created['id']}")
    assert r.status_code == 200
    got = r.json()
    assert got["id"] == created["id"]
    assert got["customer_id"] == 7
    assert got["status"] == "NEW"
