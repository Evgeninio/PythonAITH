import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "payload",
    [
        {"customer_id": 0, "items": [{"sku": "a", "qty": 1}], "total": 1.0},
        {"customer_id": 1, "items": [], "total": 1.0},
        {"customer_id": 1, "items": [{"sku": "", "qty": 1}], "total": 1.0},
        {"customer_id": 1, "items": [{"sku": "a", "qty": 0}], "total": 1.0},
        {"customer_id": 1, "items": [{"sku": "a", "qty": 1}], "total": 0}, 
    ],
)
def test_create_order_validation_422(client: TestClient, payload):
    r = client.post("/orders", json=payload)
    assert r.status_code == 422
