from cli import metrics


def test_size_score_none_weights():
    ctx = {}
    val, ms = metrics.size_score(ctx)
    assert isinstance(val, dict)
    assert "desktop_pc" in val


def test_code_quality_various_flags():
    ctx = {"has_tests": True, "has_ci": True, "lint_ok": True}
    val, ms = metrics.code_quality(ctx)
    assert 0.0 <= val <= 1.0


def test_dataset_quality_zero_downloads():
    ctx = {"dataset_downloads": 0}
    val, ms = metrics.dataset_quality(ctx)
    assert 0.0 <= val <= 1.0
