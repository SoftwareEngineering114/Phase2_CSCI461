from __future__ import annotations
from cli.url_types import parse_url
from cli.metrics import compute_all_metrics, compute_net_score

def test_parse_model():
    p = parse_url("https://huggingface.co/google/gemma-3-270m/tree/main")
    assert p.category == "MODEL"
    assert "google" in p.name

def test_metrics_bounds():
    ctx = {"url": "x", "name": "y"}
    m = compute_all_metrics(ctx)
    assert 0.0 <= m["ramp_up_time"] <= 1.0
    net, ms = compute_net_score(m)
    assert 0.0 <= net <= 1.0
    assert isinstance(ms, int)

