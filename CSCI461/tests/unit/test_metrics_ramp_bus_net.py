import math
from cli import metrics


def test_ramp_up_time_examples_and_length():
    ctx = {"hf_readme": "This is an example quickstart README with many words " * 20}
    val, ms = metrics.ramp_up_time(ctx)
    assert 0.0 <= val <= 1.0


def test_bus_factor_single_contributor():
    ctx = {"git_contributors": 1}
    val, ms = metrics.bus_factor(ctx)
    assert val == 0.1


def test_bus_factor_multiple_contributors():
    ctx = {"git_contributors": 5}
    val, ms = metrics.bus_factor(ctx)
    assert math.isclose(val, 1.0, rel_tol=1e-6)


def test_compute_net_score_simple_weights():
    # provide deterministic metrics dict
    m = {
        "size_score": {"desktop_pc": 1.0},
        "license": 1.0,
        "ramp_up_time": 1.0,
        "bus_factor": 1.0,
        "dataset_and_code_score": 1.0,
        "dataset_quality": 1.0,
        "code_quality": 1.0,
        "performance_claims": 1.0,
    }
    val, ms = metrics.compute_net_score(m)
    assert 0.0 <= val <= 1.0
