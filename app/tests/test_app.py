import json

import pytest

from calculator import create_app


@pytest.fixture(name="client")
def client_fixture():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_root_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"RetroCalc" in response.data


def test_calculate_addition(client):
    payload = {"left": 5, "right": 7, "operator": "+"}
    response = client.post(
        "/api/calculate", data=json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["result"] == pytest.approx(12.0)


def test_calculate_invalid_operator(client):
    payload = {"left": 1, "right": 1, "operator": "invalid"}
    response = client.post(
        "/api/calculate", data=json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
