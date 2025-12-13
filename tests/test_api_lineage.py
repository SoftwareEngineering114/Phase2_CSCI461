from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app


def test_lineage_root_node_uses_requested_id() -> None:
    client = TestClient(app)

    # Authenticate (always succeeds)
    tok = client.put(
        "/authenticate",
        json={"user": {"name": "x", "is_admin": True}, "secret": {"password": "y"}},
    ).json()

    # Ingest a model
    m = client.post(
        "/artifact/model",
        json={"url": "https://huggingface.co/google-bert/bert-base-uncased"},
        headers={"X-Authorization": tok},
    ).json()
    mid = m["metadata"]["id"]

    # Lineage for this model must include a root node with artifact_id == mid
    lin = client.get(f"/artifact/model/{mid}/lineage", headers={"X-Authorization": tok}).json()
    root_nodes = [n for n in lin.get("nodes", []) if n.get("artifact_id") == mid]
    assert len(root_nodes) == 1


