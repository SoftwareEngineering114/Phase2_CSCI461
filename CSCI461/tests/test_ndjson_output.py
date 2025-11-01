"""
Tests for NDJSON output formatting.
"""
from __future__ import annotations

import json

from registry.ndjson_output import format_ndjson_line


def test_format_ndjson_line_basic() -> None:
    """Test basic NDJSON formatting."""
    data = {"name": "test", "score": 0.5}
    result = format_ndjson_line(data)
    
    # Should be valid JSON
    parsed = json.loads(result)
    assert parsed == data
    
    # Should be compact (no spaces)
    assert " " not in result


def test_format_ndjson_line_complex() -> None:
    """Test NDJSON formatting with nested structures."""
    data = {
        "name": "model",
        "scores": {"a": 1.0, "b": 0.5},
        "latencies": [10, 20, 30],
    }
    result = format_ndjson_line(data)
    
    parsed = json.loads(result)
    assert parsed == data


def test_format_ndjson_line_no_trailing_newline() -> None:
    """Test that output doesn't include trailing newline."""
    data = {"test": "value"}
    result = format_ndjson_line(data)
    
    assert not result.endswith("\n")

