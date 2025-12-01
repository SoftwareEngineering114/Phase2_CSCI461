from cli import metrics


def test_license_score_empty_and_readme():
    ctx = {"license": None, "hf_readme": "This project includes a LICENSE file."}
    val, ms = metrics.license_score(ctx)
    assert 0.0 <= val <= 1.0


def test_dataset_and_code_score_none_both():
    ctx = {}
    val, ms = metrics.dataset_and_code_score(ctx)
    assert val == 0.0


def test_performance_claims_detection():
    ctx = {"hf_readme": "This model achieves 95% accuracy on the test set."}
    val, ms = metrics.performance_claims(ctx)
    assert val == 1.0


def test_code_quality_lint_warn():
    ctx = {"has_tests": False, "has_ci": False, "lint_warn": True}
    val, ms = metrics.code_quality(ctx)
    assert 0.0 <= val <= 1.0
