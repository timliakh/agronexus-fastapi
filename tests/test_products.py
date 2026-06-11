import pytest


@pytest.mark.smoke
@pytest.mark.regression
def test_list_products(client):
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 6
    assert products[0]["slug"] == "agribot-x1"


def test_get_product_by_slug(client):
    response = client.get("/products/agribot-x1")
    assert response.status_code == 200
    product = response.json()
    assert product["slug"] == "agribot-x1"
    assert product["manufacturer"] == "NeuroField Robotics"


def test_get_product_by_id(client):
    response = client.get("/products/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_product_not_found(client):
    response = client.get("/products/unknown-slug")
    assert response.status_code == 404


def test_filter_by_category(client):
    response = client.get("/products", params={"category": "tractors"})
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["category"] == "tractors"


def test_filter_by_brand(client):
    response = client.get("/products", params={"brand": "neurofield-robotics"})
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["slug"] == "agribot-x1"


def test_search_products(client):
    response = client.get("/products", params={"q": "LiDAR"})
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 1
    assert any(p["slug"] == "agribot-x1" for p in products)


def test_suggest_products(client):
    response = client.get("/products/suggest", params={"q": "harvest"})
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 1
    assert products[0]["slug"] == "harvestai-9000"


def test_list_brands(client):
    response = client.get("/products/brands")
    assert response.status_code == 200
    brands = response.json()
    assert len(brands) == 6
    slugs = {brand["slug"] for brand in brands}
    assert "neurofield-robotics" in slugs


@pytest.mark.regression
@pytest.mark.parametrize(
    ("lang", "expected_name"),
    [
        ("ru", "AgriBot X1 — автономный трактор"),
        ("en", "AgriBot X1 — Autonomous Tractor"),
        ("de", "AgriBot X1 — Autonomer Traktor"),
    ],
)
def test_product_localization(client, lang, expected_name):
    response = client.get("/products/agribot-x1", params={"lang": lang})
    assert response.status_code == 200
    assert response.json()["name"] == expected_name


@pytest.mark.regression
def test_product_not_found_localized(client):
    response = client.get("/products/unknown-slug", params={"lang": "en"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."
