from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app


def test_authenticate_returns_bearer_token_string() -> None:
    client = TestClient(app)
    resp = client.put(
        "/authenticate",
        json={"user": {"name": "anyone", "is_admin": True}, "secret": {"password": "anything"}},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), str)
    assert "bearer " in resp.json().lower()


def test_authenticate_missing_fields_returns_400() -> None:
    client = TestClient(app)
    resp = client.put("/authenticate", json={"user": {"name": "x", "is_admin": True}})
    assert resp.status_code == 400


