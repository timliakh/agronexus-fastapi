import pytest

from tests.factories import TINY_PNG, make_product_payload


@pytest.mark.admin
@pytest.mark.regression
def test_admin_login_success(client):
    response = client.post("/admin/api/login", json={"password": "test-admin-pass"})
    assert response.status_code == 200
    assert "token" in response.json()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_login_invalid_password(client):
    response = client.post("/admin/api/login", json={"password": "wrong"})
    assert response.status_code == 401


@pytest.mark.admin
@pytest.mark.regression
def test_admin_stats_requires_auth(client):
    response = client.get("/admin/api/stats")
    assert response.status_code == 422


@pytest.mark.admin
@pytest.mark.regression
def test_admin_stats(client, admin_headers):
    response = client.get("/admin/api/stats", headers=admin_headers)
    assert response.status_code == 200
    stats = response.json()
    assert stats["products_count"] == 6
    assert stats["orders_count"] == 0


@pytest.mark.admin
@pytest.mark.regression
def test_admin_product_crud(client, admin_headers):
    create_response = client.post(
        "/admin/api/products",
        headers=admin_headers,
        json=make_product_payload(),
    )
    assert create_response.status_code == 201
    product = create_response.json()
    product_id = product["id"]
    assert product["slug"] == "test-drone-sprayer"

    update_response = client.put(
        f"/admin/api/products/{product_id}",
        headers=admin_headers,
        json={"price": 1600.0},
    )
    assert update_response.status_code == 200
    assert update_response.json()["price"] == 1600.0

    delete_response = client.delete(
        f"/admin/api/products/{product_id}",
        headers=admin_headers,
    )
    assert delete_response.status_code == 204

    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404


@pytest.mark.admin
@pytest.mark.regression
def test_admin_upload_product_image(client, admin_headers):
    create_response = client.post(
        "/admin/api/products",
        headers=admin_headers,
        json=make_product_payload(name="Image Upload Drone"),
    )
    product_id = create_response.json()["id"]

    upload_response = client.post(
        f"/admin/api/products/{product_id}/image",
        headers=admin_headers,
        files={"file": ("product.png", TINY_PNG, "image/png")},
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["image_url"] == f"/uploads/products/{product_id}.png"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_upload_invalid_image_format(client, admin_headers):
    create_response = client.post(
        "/admin/api/products",
        headers=admin_headers,
        json=make_product_payload(name="Invalid Image Drone"),
    )
    product_id = create_response.json()["id"]

    response = client.post(
        f"/admin/api/products/{product_id}/image",
        headers=admin_headers,
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400
    assert "Allowed formats" in response.json()["detail"]


@pytest.mark.admin
@pytest.mark.regression
def test_admin_feedbacks_list_and_delete(client, admin_headers):
    from tests.factories import make_feedback_payload

    submit_response = client.post("/feedback", json=make_feedback_payload())
    assert submit_response.status_code == 200

    list_response = client.get("/admin/api/feedbacks", headers=admin_headers)
    assert list_response.status_code == 200
    feedbacks = list_response.json()
    assert len(feedbacks) == 1
    feedback_id = feedbacks[0]["id"]

    delete_response = client.delete(
        f"/admin/api/feedbacks/{feedback_id}",
        headers=admin_headers,
    )
    assert delete_response.status_code == 204

    empty_response = client.get("/admin/api/feedbacks", headers=admin_headers)
    assert empty_response.json() == []
