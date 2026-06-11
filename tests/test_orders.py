import pytest

from tests.factories import make_order_payload


@pytest.mark.smoke
@pytest.mark.regression
def test_create_and_get_order(client):
    create_response = client.post("/orders", json=make_order_payload())
    assert create_response.status_code == 201
    order = create_response.json()
    assert order["id"] >= 1
    assert order["customer_name"] == "Иван Тестов"
    assert order["total_price"] == 12500.0

    get_response = client.get(f"/orders/{order['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == order["id"]


@pytest.mark.regression
def test_create_order_unknown_product(client):
    response = client.post(
        "/orders",
        json=make_order_payload(
            items=[{"product_id": 999, "configuration": "Level 4", "quantity": 1}]
        ),
    )
    assert response.status_code == 400
    assert "не найден" in response.json()["detail"]


@pytest.mark.regression
def test_create_order_invalid_configuration(client):
    response = client.post(
        "/orders",
        json=make_order_payload(
            items=[{"product_id": 1, "configuration": "Unknown", "quantity": 1}]
        ),
    )
    assert response.status_code == 400
    assert "Комплектация" in response.json()["detail"]


@pytest.mark.regression
def test_create_order_out_of_stock(client, admin_headers):
    create_response = client.post(
        "/admin/api/products",
        headers=admin_headers,
        json={
            "name": "Offline Harvest Unit",
            "description": "Autonomous harvester temporarily unavailable for orders.",
            "price": 9900.0,
            "category": "harvesters",
            "manufacturer": "TestAgri",
            "configurations": ["Standard"],
            "in_stock": False,
        },
    )
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]

    response = client.post(
        "/orders",
        json=make_order_payload(
            items=[
                {
                    "product_id": product_id,
                    "configuration": "Standard",
                    "quantity": 1,
                }
            ]
        ),
    )
    assert response.status_code == 400
    assert "недоступна" in response.json()["detail"]


@pytest.mark.regression
def test_get_order_not_found(client):
    response = client.get("/orders/9999")
    assert response.status_code == 404
