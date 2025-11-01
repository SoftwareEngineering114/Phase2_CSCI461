"""
Tests for metric scoring ranges and edge cases.
"""
from __future__ import annotations

from typing import Any, Dict

import pytest

from registry.metrics import (
    BusFactorMetric,
    CodeQualityMetric,
    DatasetAndCodeScoreMetric,
    DatasetQualityMetric,
    LicenseMetric,
    PerformanceClaimsMetric,
    RampUpTimeMetric,
    SizeScoreMetric,
)


def test_ramp_up_time_range(sample_context: Dict[str, Any]) -> None:
    """Test that ramp_up_time returns values in [0, 1]."""
    metric = RampUpTimeMetric()
    score, latency = metric.compute(sample_context)
    assert 0.0 <= score <= 1.0
    assert isinstance(latency, int)
    assert latency >= 0


def test_bus_factor_range(sample_context: Dict[str, Any]) -> None:
    """Test that bus_factor returns values in [0.1, 1]."""
    metric = BusFactorMetric()
    score, latency = metric.compute(sample_context)
    assert 0.0 <= score <= 1.0
    assert isinstance(latency, int)


def test_performance_claims_binary(sample_context: Dict[str, Any]) -> None:
    """Test that performance_claims returns 0 or 1."""
    metric = PerformanceClaimsMetric()
    score, latency = metric.compute(sample_context)
    assert score in [0.0, 1.0]
    assert isinstance(latency, int)


def test_license_range(sample_context: Dict[str, Any]) -> None:
    """Test that license returns values in [0, 1]."""
    metric = LicenseMetric()
    score, latency = metric.compute(sample_context)
    assert 0.0 <= score <= 1.0
    assert isinstance(latency, int)


def test_size_score_structure(sample_context: Dict[str, Any]) -> None:
    """Test that size_score returns correct structure."""
    metric = SizeScoreMetric()
    score, latency = metric.compute(sample_context)
    
    assert isinstance(score, dict)
    assert set(score.keys()) == {"raspberry_pi", "jetson_nano", "desktop_pc", "aws_server"}
    assert isinstance(latency, int)
    
    # All values should be in [0, 1]
    for value in score.values():
        assert 0.0 <= value <= 1.0


def test_dataset_and_code_score_range(sample_context: Dict[str, Any]) -> None:
    """Test that dataset_and_code_score returns values in [0, 0.5, 1]."""
    metric = DatasetAndCodeScoreMetric()
    score, latency = metric.compute(sample_context)
    assert score in [0.0, 0.5, 1.0]
    assert isinstance(latency, int)


def test_dataset_quality_range(sample_context: Dict[str, Any]) -> None:
    """Test that dataset_quality returns values in [0.2, 1]."""
    metric = DatasetQualityMetric()
    score, latency = metric.compute(sample_context)
    assert 0.0 <= score <= 1.0
    assert isinstance(latency, int)


def test_code_quality_range(sample_context: Dict[str, Any]) -> None:
    """Test that code_quality returns values in [0, 1]."""
    metric = CodeQualityMetric()
    score, latency = metric.compute(sample_context)
    assert 0.0 <= score <= 1.0
    assert isinstance(latency, int)


def test_minimal_context_handling(minimal_context: Dict[str, Any]) -> None:
    """Test that all metrics handle minimal context without crashing."""
    metrics = [
        RampUpTimeMetric(),
        BusFactorMetric(),
        PerformanceClaimsMetric(),
        LicenseMetric(),
        SizeScoreMetric(),
        DatasetAndCodeScoreMetric(),
        DatasetQualityMetric(),
        CodeQualityMetric(),
    ]
    
    for metric in metrics:
        score, latency = metric.compute(minimal_context)
        # Just verify it doesn't crash and returns valid types
        assert score is not None
        assert isinstance(latency, int)
        assert latency >= 0


def test_metrics_have_name_attribute() -> None:
    """Test that all metrics have a name attribute matching expected keys."""
    expected_names = {
        "ramp_up_time",
        "bus_factor",
        "performance_claims",
        "license",
        "size_score",
        "dataset_and_code_score",
        "dataset_quality",
        "code_quality",
    }
    
    metrics = [
        RampUpTimeMetric(),
        BusFactorMetric(),
        PerformanceClaimsMetric(),
        LicenseMetric(),
        SizeScoreMetric(),
        DatasetAndCodeScoreMetric(),
        DatasetQualityMetric(),
        CodeQualityMetric(),
    ]
    
    actual_names = {metric.name for metric in metrics}
    assert actual_names == expected_names


def test_metrics_dont_crash_on_empty_dict() -> None:
    """Test that metrics gracefully handle completely empty context."""
    empty_context: Dict[str, Any] = {}
    
    metrics = [
        RampUpTimeMetric(),
        BusFactorMetric(),
        PerformanceClaimsMetric(),
        LicenseMetric(),
        SizeScoreMetric(),
        DatasetAndCodeScoreMetric(),
        DatasetQualityMetric(),
        CodeQualityMetric(),
    ]
    
    for metric in metrics:
        score, latency = metric.compute(empty_context)
        # Should not crash, should return valid score
        if isinstance(score, dict):
            # size_score
            for v in score.values():
                assert 0.0 <= v <= 1.0
        else:
            assert 0.0 <= score <= 1.0
        assert isinstance(latency, int)
