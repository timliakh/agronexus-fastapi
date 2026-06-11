import pytest


@pytest.mark.smoke
@pytest.mark.regression
def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_product_page_by_slug(client):
    response = client.get("/catalog/agribot-x1")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_product_page_redirects_numeric_id(client):
    response = client.get("/catalog/1", follow_redirects=False)
    assert response.status_code == 301
    assert response.headers["location"] == "/catalog/agribot-x1"


def test_order_page_serves_spa(client):
    response = client.get("/order/9999")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_about_page_serves_spa(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
