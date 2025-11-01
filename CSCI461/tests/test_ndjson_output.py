"""
Tests for NDJSON output formatting.
"""
from __future__ import annotations

import json

from registry.models import ModelScore
from registry.ndjson_output import modelscore_to_ndjson_line


def test_modelscore_to_ndjson_line_valid_json() -> None:
    """Test that ModelScore converts to valid JSON."""
    model_score = ModelScore(
        name="bert-base-uncased",
        category="MODEL",
        ramp_up_time=0.5,
        ramp_up_time_latency=100,
        bus_factor=0.6,
        bus_factor_latency=200,
        performance_claims=1.0,
        performance_claims_latency=50,
        license=1.0,
        license_latency=30,
        size_score={"raspberry_pi": 0.1, "jetson_nano": 0.2, "desktop_pc": 1.0, "aws_server": 1.0},
        size_score_latency=150,
        dataset_and_code_score=0.5,
        dataset_and_code_score_latency=80,
        dataset_quality=0.7,
        dataset_quality_latency=120,
        code_quality=0.8,
        code_quality_latency=90,
        net_score=0.75,
        net_score_latency=10,
    )
    
    # Convert to NDJSON
    ndjson_line = modelscore_to_ndjson_line(model_score)
    
    # Should be valid JSON
    parsed = json.loads(ndjson_line)
    assert isinstance(parsed, dict)


def test_modelscore_to_ndjson_line_has_required_keys() -> None:
    """Test that output has all required keys from spec Table 1."""
    model_score = ModelScore(
        name="bert-base-uncased",
        category="MODEL",
        ramp_up_time=0.5,
        ramp_up_time_latency=100,
        bus_factor=0.6,
        bus_factor_latency=200,
        performance_claims=1.0,
        performance_claims_latency=50,
        license=1.0,
        license_latency=30,
        size_score={"raspberry_pi": 0.1, "jetson_nano": 0.2, "desktop_pc": 1.0, "aws_server": 1.0},
        size_score_latency=150,
        dataset_and_code_score=0.5,
        dataset_and_code_score_latency=80,
        dataset_quality=0.7,
        dataset_quality_latency=120,
        code_quality=0.8,
        code_quality_latency=90,
        net_score=0.75,
        net_score_latency=10,
    )
    
    ndjson_line = modelscore_to_ndjson_line(model_score)
    parsed = json.loads(ndjson_line)
    
    # Required keys from spec Table 1
    required_keys = [
        "name",
        "category",
        "net_score",
        "net_score_latency",
        "ramp_up_time",
        "ramp_up_time_latency",
        "bus_factor",
        "bus_factor_latency",
        "performance_claims",
        "performance_claims_latency",
        "license",
        "license_latency",
        "size_score",
        "size_score_latency",
        "dataset_and_code_score",
        "dataset_and_code_score_latency",
        "dataset_quality",
        "dataset_quality_latency",
        "code_quality",
        "code_quality_latency",
    ]
    
    for key in required_keys:
        assert key in parsed, f"Missing required key: {key}"


def test_modelscore_to_ndjson_line_values_in_range() -> None:
    """Test that all metric values are in [0,1] and latencies are ints."""
    model_score = ModelScore(
        name="bert-base-uncased",
        category="MODEL",
        ramp_up_time=0.5,
        ramp_up_time_latency=100,
        bus_factor=0.6,
        bus_factor_latency=200,
        performance_claims=1.0,
        performance_claims_latency=50,
        license=1.0,
        license_latency=30,
        size_score={"raspberry_pi": 0.1, "jetson_nano": 0.2, "desktop_pc": 1.0, "aws_server": 1.0},
        size_score_latency=150,
        dataset_and_code_score=0.5,
        dataset_and_code_score_latency=80,
        dataset_quality=0.7,
        dataset_quality_latency=120,
        code_quality=0.8,
        code_quality_latency=90,
        net_score=0.75,
        net_score_latency=10,
    )
    
    ndjson_line = modelscore_to_ndjson_line(model_score)
    parsed = json.loads(ndjson_line)
    
    # Check metric values are in [0, 1]
    metric_keys = [
        "ramp_up_time",
        "bus_factor",
        "performance_claims",
        "license",
        "dataset_and_code_score",
        "dataset_quality",
        "code_quality",
        "net_score",
    ]
    
    for key in metric_keys:
        value = parsed[key]
        assert isinstance(value, (int, float)), f"{key} should be numeric"
        assert 0.0 <= value <= 1.0, f"{key} = {value} is not in [0, 1]"
    
    # Check size_score values
    size_score = parsed["size_score"]
    assert isinstance(size_score, dict)
    for device, score in size_score.items():
        assert 0.0 <= score <= 1.0, f"size_score[{device}] = {score} not in [0, 1]"
    
    # Check latencies are ints
    latency_keys = [
        "ramp_up_time_latency",
        "bus_factor_latency",
        "performance_claims_latency",
        "license_latency",
        "size_score_latency",
        "dataset_and_code_score_latency",
        "dataset_quality_latency",
        "code_quality_latency",
        "net_score_latency",
    ]
    
    for key in latency_keys:
        value = parsed[key]
        assert isinstance(value, int), f"{key} should be int, got {type(value)}"
        assert value >= 0, f"{key} = {value} should be non-negative"


def test_modelscore_to_ndjson_line_compact_format() -> None:
    """Test that output is compact (no extra spaces)."""
    model_score = ModelScore(
        name="test-model",
        category="MODEL",
        ramp_up_time=0.5,
        ramp_up_time_latency=100,
        bus_factor=0.6,
        bus_factor_latency=200,
        performance_claims=1.0,
        performance_claims_latency=50,
        license=1.0,
        license_latency=30,
        size_score={"raspberry_pi": 0.1, "jetson_nano": 0.2, "desktop_pc": 1.0, "aws_server": 1.0},
        size_score_latency=150,
        dataset_and_code_score=0.5,
        dataset_and_code_score_latency=80,
        dataset_quality=0.7,
        dataset_quality_latency=120,
        code_quality=0.8,
        code_quality_latency=90,
        net_score=0.75,
        net_score_latency=10,
    )
    
    ndjson_line = modelscore_to_ndjson_line(model_score)
    
    # Should not have spaces after colons or commas (compact format)
    assert ": " not in ndjson_line, "Output should be compact (no spaces after colons)"
    assert ", " not in ndjson_line, "Output should be compact (no spaces after commas)"
    
    # Should not have trailing newline
    assert not ndjson_line.endswith("\n"), "Output should not have trailing newline"


def test_modelscore_to_ndjson_line_category_is_model() -> None:
    """Test that category is correctly set to MODEL."""
    model_score = ModelScore(
        name="test-model",
        category="MODEL",
        ramp_up_time=0.5,
        ramp_up_time_latency=100,
        bus_factor=0.6,
        bus_factor_latency=200,
        performance_claims=1.0,
        performance_claims_latency=50,
        license=1.0,
        license_latency=30,
        size_score={"raspberry_pi": 0.1, "jetson_nano": 0.2, "desktop_pc": 1.0, "aws_server": 1.0},
        size_score_latency=150,
        dataset_and_code_score=0.5,
        dataset_and_code_score_latency=80,
        dataset_quality=0.7,
        dataset_quality_latency=120,
        code_quality=0.8,
        code_quality_latency=90,
        net_score=0.75,
        net_score_latency=10,
    )
    
    ndjson_line = modelscore_to_ndjson_line(model_score)
    parsed = json.loads(ndjson_line)
    
    assert parsed["category"] == "MODEL"
