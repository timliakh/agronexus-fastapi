import pytest


@pytest.mark.smoke
@pytest.mark.regression
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.regression
def test_languages(client):
    response = client.get("/languages")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"languages", "labels", "default", "locale_tags"}
    assert "ru" in data["languages"]
    assert "en" in data["languages"]
    assert data["labels"]["ru"] == "Русский"
    assert data["default"] == "ru"
    assert data["locale_tags"]["en"] == "en-US"


@pytest.mark.regression
def test_store_info(client):
    response = client.get("/store?lang=ru")
    assert response.status_code == 200
    data = response.json()
    assert data["products_count"] == 6
    assert data["lang"] == "ru"
    assert data["name"]


@pytest.mark.regression
def test_i18n_translations(client):
    response = client.get("/i18n/en")
    assert response.status_code == 200
    ui = response.json()
    assert "store_name" in ui
    assert "categories" in ui
