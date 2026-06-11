"""Test data builders for API integration tests."""

TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
    b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05"
    b"\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


def make_order_payload(**overrides):
    payload = {
        "customer_name": "Иван Тестов",
        "email": "ivan@example.com",
        "items": [
            {
                "product_id": 1,
                "configuration": "Level 4",
                "quantity": 1,
            }
        ],
    }
    payload.update(overrides)
    return payload


def make_feedback_payload(**overrides):
    payload = {
        "name": "Мария",
        "message": "Отличный магазин автономной техники!",
        "contact": {"email": "maria@example.com", "phone": "79001234567"},
    }
    payload.update(overrides)
    return payload


def make_product_payload(**overrides):
    payload = {
        "name": "Test Drone Sprayer",
        "description": "Compact autonomous sprayer for demo fields and testing.",
        "price": 1500.0,
        "category": "sprayers",
        "manufacturer": "TestAgri",
        "configurations": ["Demo"],
        "in_stock": True,
    }
    payload.update(overrides)
    return payload
