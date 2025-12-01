from types import SimpleNamespace
from unittest.mock import patch

from cli import metrics


def make_ctx_with_readme(readme_text: str):
    return {"hf_readme": readme_text, "weights_total_bytes": 1024 * 1024 * 10}


def test_ramp_up_and_net_score_without_hf(monkeypatch):
    # Provide a simple README and no HF calls
    ctx = make_ctx_with_readme("# Example\nThis repo contains an example model.\n")

    # Call ramp_up_time directly
    ramp_score, ramp_ms = metrics.ramp_up_time(ctx)
    assert 0.0 <= ramp_score <= 1.0

    # Build a minimal metrics dict and compute net score
    metric_values = {
        "ramp_up_time": ramp_score,
        "bus_factor": 0.5,
        "performance_claims": 0.0,
        "size_score": {"desktop_pc": 0.5},
        "dataset_quality": 0.5,
        "code_quality": 0.5,
    }

    net, ms = metrics.compute_net_score(metric_values)
    assert isinstance(net, float)
    assert net >= 0.0
