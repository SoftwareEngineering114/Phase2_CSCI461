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
    """Test that bus_factor returns values in [0, 1]."""
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
    """Test that dataset_quality returns values in [0, 1]."""
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
        result = metric.compute(minimal_context)
        # Returns tuple of (score, latency)
        assert isinstance(result, tuple)
        assert len(result) == 2
        score, latency = result
        assert score is not None
        assert isinstance(latency, int)


def test_metric_name_attributes() -> None:
    """Test that all metrics have correct name attributes matching NDJSON keys."""
    expected_names = {
        RampUpTimeMetric: "ramp_up_time",
        BusFactorMetric: "bus_factor",
        PerformanceClaimsMetric: "performance_claims",
        LicenseMetric: "license",
        SizeScoreMetric: "size_score",
        DatasetAndCodeScoreMetric: "dataset_and_code_score",
        DatasetQualityMetric: "dataset_quality",
        CodeQualityMetric: "code_quality",
    }
    
    for metric_class, expected_name in expected_names.items():
        metric = metric_class()
        assert metric.name == expected_name

