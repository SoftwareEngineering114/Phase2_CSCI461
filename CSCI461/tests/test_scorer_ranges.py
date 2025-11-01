"""
Tests for metric scoring ranges and edge cases.
"""
from __future__ import annotations

from typing import Any, Dict

import pytest

from registry.models import ModelScore
from registry.scorer import score_model


def test_score_model_returns_modelscore(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that score_model returns a ModelScore object."""
    # Monkeypatch fetch_repo_info to return minimal fake data
    def fake_fetch_repo_info(url: str) -> Dict[str, Any]:
        return {
            "url": url,
            "hf_readme": "Example README with quickstart guide.",
            "license": "MIT",
            "git_contributors": 3,
            "weights_total_bytes": 500 * 1024 * 1024,
            "has_tests": True,
            "has_ci": True,
            "lint_ok": True,
            "dataset_link": "",
            "example_code_present": False,
            "dataset_downloads": 100,
        }
    
    # Monkeypatch each metric's compute method
    def fake_ramp_up_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[float, int]:
        return 0.8, 50
    
    def fake_bus_factor_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[float, int]:
        return 0.6, 100
    
    def fake_performance_claims_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[float, int]:
        return 1.0, 20
    
    def fake_license_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[float, int]:
        return 1.0, 30
    
    def fake_size_score_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[Dict[str, float], int]:
        return {"raspberry_pi": 0.2, "jetson_nano": 0.5, "desktop_pc": 1.0, "aws_server": 1.0}, 80
    
    def fake_dataset_code_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[float, int]:
        return 0.5, 40
    
    def fake_dataset_quality_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[float, int]:
        return 0.7, 60
    
    def fake_code_quality_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[float, int]:
        return 0.9, 90
    
    # Apply monkeypatches
    monkeypatch.setattr("registry.scorer.fetch_repo_info", fake_fetch_repo_info)
    monkeypatch.setattr("registry.metrics.ramp_up_time.RampUpTimeMetric.compute", fake_ramp_up_compute)
    monkeypatch.setattr("registry.metrics.bus_factor.BusFactorMetric.compute", fake_bus_factor_compute)
    monkeypatch.setattr("registry.metrics.performance_claims.PerformanceClaimsMetric.compute", fake_performance_claims_compute)
    monkeypatch.setattr("registry.metrics.license_metric.LicenseMetric.compute", fake_license_compute)
    monkeypatch.setattr("registry.metrics.size_score.SizeScoreMetric.compute", fake_size_score_compute)
    monkeypatch.setattr("registry.metrics.dataset_and_code_score.DatasetAndCodeScoreMetric.compute", fake_dataset_code_compute)
    monkeypatch.setattr("registry.metrics.dataset_quality.DatasetQualityMetric.compute", fake_dataset_quality_compute)
    monkeypatch.setattr("registry.metrics.code_quality.CodeQualityMetric.compute", fake_code_quality_compute)
    
    # Call score_model with spec example URL
    result = score_model("https://huggingface.co/google/gemma-3-270m/tree/main", {})
    
    # Assert it's a ModelScore
    assert isinstance(result, ModelScore)


def test_score_model_category_is_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that score_model sets category to MODEL."""
    # Monkeypatch with minimal fake data
    def fake_fetch_repo_info(url: str) -> Dict[str, Any]:
        return {"url": url, "hf_readme": "", "license": "", "git_contributors": 1}
    
    def fake_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[float, int]:
        return 0.5, 10
    
    def fake_size_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[Dict[str, float], int]:
        return {"raspberry_pi": 0.5, "jetson_nano": 0.5, "desktop_pc": 0.5, "aws_server": 0.5}, 10
    
    monkeypatch.setattr("registry.scorer.fetch_repo_info", fake_fetch_repo_info)
    monkeypatch.setattr("registry.metrics.ramp_up_time.RampUpTimeMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.bus_factor.BusFactorMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.performance_claims.PerformanceClaimsMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.license_metric.LicenseMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.size_score.SizeScoreMetric.compute", fake_size_compute)
    monkeypatch.setattr("registry.metrics.dataset_and_code_score.DatasetAndCodeScoreMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.dataset_quality.DatasetQualityMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.code_quality.CodeQualityMetric.compute", fake_compute)
    
    result = score_model("https://huggingface.co/google/gemma-3-270m/tree/main", {})
    
    assert result.category == "MODEL"


def test_score_model_all_metrics_in_range(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that all metric scores are between 0 and 1."""
    def fake_fetch_repo_info(url: str) -> Dict[str, Any]:
        return {"url": url, "hf_readme": "", "license": "", "git_contributors": 1}
    
    def fake_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[float, int]:
        return 0.75, 50
    
    def fake_size_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[Dict[str, float], int]:
        return {"raspberry_pi": 0.3, "jetson_nano": 0.6, "desktop_pc": 0.9, "aws_server": 1.0}, 80
    
    monkeypatch.setattr("registry.scorer.fetch_repo_info", fake_fetch_repo_info)
    monkeypatch.setattr("registry.metrics.ramp_up_time.RampUpTimeMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.bus_factor.BusFactorMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.performance_claims.PerformanceClaimsMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.license_metric.LicenseMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.size_score.SizeScoreMetric.compute", fake_size_compute)
    monkeypatch.setattr("registry.metrics.dataset_and_code_score.DatasetAndCodeScoreMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.dataset_quality.DatasetQualityMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.code_quality.CodeQualityMetric.compute", fake_compute)
    
    result = score_model("https://huggingface.co/google/gemma-3-270m/tree/main", {})
    
    # Check all metric scores are in [0, 1]
    assert 0.0 <= result.ramp_up_time <= 1.0
    assert 0.0 <= result.bus_factor <= 1.0
    assert 0.0 <= result.performance_claims <= 1.0
    assert 0.0 <= result.license <= 1.0
    assert 0.0 <= result.dataset_and_code_score <= 1.0
    assert 0.0 <= result.dataset_quality <= 1.0
    assert 0.0 <= result.code_quality <= 1.0
    
    # Check size_score values
    for device, score in result.size_score.items():
        assert 0.0 <= score <= 1.0, f"size_score[{device}] = {score} not in [0, 1]"


def test_score_model_net_score_in_range(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that net_score is between 0 and 1."""
    def fake_fetch_repo_info(url: str) -> Dict[str, Any]:
        return {"url": url, "hf_readme": "", "license": "", "git_contributors": 1}
    
    def fake_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[float, int]:
        return 0.5, 25
    
    def fake_size_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[Dict[str, float], int]:
        return {"raspberry_pi": 0.5, "jetson_nano": 0.5, "desktop_pc": 0.5, "aws_server": 0.5}, 30
    
    monkeypatch.setattr("registry.scorer.fetch_repo_info", fake_fetch_repo_info)
    monkeypatch.setattr("registry.metrics.ramp_up_time.RampUpTimeMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.bus_factor.BusFactorMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.performance_claims.PerformanceClaimsMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.license_metric.LicenseMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.size_score.SizeScoreMetric.compute", fake_size_compute)
    monkeypatch.setattr("registry.metrics.dataset_and_code_score.DatasetAndCodeScoreMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.dataset_quality.DatasetQualityMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.code_quality.CodeQualityMetric.compute", fake_compute)
    
    result = score_model("https://huggingface.co/google/gemma-3-270m/tree/main", {})
    
    assert 0.0 <= result.net_score <= 1.0


def test_score_model_latencies_are_positive_ints(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that all latencies are positive integers."""
    def fake_fetch_repo_info(url: str) -> Dict[str, Any]:
        return {"url": url, "hf_readme": "", "license": "", "git_contributors": 1}
    
    def fake_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[float, int]:
        return 0.5, 42
    
    def fake_size_compute(self: Any, repo_info: Dict[str, Any]) -> tuple[Dict[str, float], int]:
        return {"raspberry_pi": 0.5, "jetson_nano": 0.5, "desktop_pc": 0.5, "aws_server": 0.5}, 77
    
    monkeypatch.setattr("registry.scorer.fetch_repo_info", fake_fetch_repo_info)
    monkeypatch.setattr("registry.metrics.ramp_up_time.RampUpTimeMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.bus_factor.BusFactorMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.performance_claims.PerformanceClaimsMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.license_metric.LicenseMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.size_score.SizeScoreMetric.compute", fake_size_compute)
    monkeypatch.setattr("registry.metrics.dataset_and_code_score.DatasetAndCodeScoreMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.dataset_quality.DatasetQualityMetric.compute", fake_compute)
    monkeypatch.setattr("registry.metrics.code_quality.CodeQualityMetric.compute", fake_compute)
    
    result = score_model("https://huggingface.co/google/gemma-3-270m/tree/main", {})
    
    # Check all latencies are positive ints
    assert isinstance(result.ramp_up_time_latency, int)
    assert result.ramp_up_time_latency >= 0
    
    assert isinstance(result.bus_factor_latency, int)
    assert result.bus_factor_latency >= 0
    
    assert isinstance(result.performance_claims_latency, int)
    assert result.performance_claims_latency >= 0
    
    assert isinstance(result.license_latency, int)
    assert result.license_latency >= 0
    
    assert isinstance(result.size_score_latency, int)
    assert result.size_score_latency >= 0
    
    assert isinstance(result.dataset_and_code_score_latency, int)
    assert result.dataset_and_code_score_latency >= 0
    
    assert isinstance(result.dataset_quality_latency, int)
    assert result.dataset_quality_latency >= 0
    
    assert isinstance(result.code_quality_latency, int)
    assert result.code_quality_latency >= 0
    
    assert isinstance(result.net_score_latency, int)
    assert result.net_score_latency >= 0
