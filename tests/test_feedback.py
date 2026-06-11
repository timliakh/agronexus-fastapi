import pytest

from tests.factories import make_feedback_payload


@pytest.mark.regression
def test_submit_feedback(client):
    response = client.post("/feedback", json=make_feedback_payload())
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.regression
def test_submit_feedback_forbidden_word(client):
    response = client.post(
        "/feedback",
        json=make_feedback_payload(message="Вы редиска и некультурный продавец техники"),
    )
    assert response.status_code == 400
    assert "недопустимых слов" in response.json()["detail"]


@pytest.mark.regression
def test_submit_feedback_invalid_phone(client):
    response = client.post(
        "/feedback",
        json=make_feedback_payload(contact={"email": "maria@example.com", "phone": "abc"}),
    )
    assert response.status_code == 400


@pytest.mark.regression
def test_submit_feedback_premium_flag(client, admin_headers):
    response = client.post(
        "/feedback?is_premium=true",
        json=make_feedback_payload(message="Premium support request for fleet rollout."),
    )
    assert response.status_code == 200

    list_response = client.get("/admin/api/feedbacks", headers=admin_headers)
    assert list_response.status_code == 200
    feedbacks = list_response.json()
    assert len(feedbacks) == 1
    assert feedbacks[0]["is_premium"] is True
    assert "Premium support" in feedbacks[0]["message"]
