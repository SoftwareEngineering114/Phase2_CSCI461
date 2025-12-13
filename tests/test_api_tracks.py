from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app


def test_tracks_returns_exact_spec_json() -> None:
    client = TestClient(app)
    resp = client.get("/tracks")
    assert resp.status_code == 200
    assert resp.json() == {
        "plannedTracks": [
            "Performance track",
            "Access control track",
            "Access Control Track",
        ]
    }


