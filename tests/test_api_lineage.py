from __future__ import annotations

import pytest
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


def test_lineage_uses_real_ingested_base_model_id_when_present(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Ingest two models A and B. Patch HF card data so B references A as base_model by name.
    Lineage for B should include an edge A.id -> B.id with relationship "base_model".
    """

    class _FakeInfo:
        def __init__(self, repo_id: str) -> None:
            self._repo_id = repo_id

        def to_dict(self) -> dict:
            # base_model must match the ingested artifact name exactly.
            if self._repo_id == "org/model-b":
                return {"cardData": {"base_model": "org/model-a"}}
            return {"cardData": {}}

    def _fake_model_info(repo_id: str) -> _FakeInfo:
        return _FakeInfo(repo_id)

    monkeypatch.setattr("huggingface_hub.model_info", _fake_model_info)

    client = TestClient(app)
    tok = client.put(
        "/authenticate",
        json={"user": {"name": "x", "is_admin": True}, "secret": {"password": "y"}},
    ).json()

    a = client.post(
        "/artifact/model",
        json={"url": "https://huggingface.co/org/model-a"},
        headers={"X-Authorization": tok},
    ).json()
    b = client.post(
        "/artifact/model",
        json={"url": "https://huggingface.co/org/model-b"},
        headers={"X-Authorization": tok},
    ).json()

    aid = a["metadata"]["id"]
    bid = b["metadata"]["id"]

    lin = client.get(f"/artifact/model/{bid}/lineage", headers={"X-Authorization": tok}).json()

    # Nodes should include both real ids.
    node_ids = {n.get("artifact_id") for n in lin.get("nodes", [])}
    assert aid in node_ids
    assert bid in node_ids

    # And include the base_model edge A -> B.
    edges = lin.get("edges", [])
    assert {"from_node_artifact_id": aid, "to_node_artifact_id": bid, "relationship": "base_model"} in edges


