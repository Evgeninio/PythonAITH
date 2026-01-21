from fastapi.testclient import TestClient


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
    assert got["items"] == [{"sku": "milk", "qty": 1}]
    assert float(got["total"]) == 3.0
