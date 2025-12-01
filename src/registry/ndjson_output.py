"""
NDJSON output formatting for model scores.
"""
from __future__ import annotations

import json

from .models import ModelScore


def modelscore_to_ndjson_line(score: ModelScore) -> str:
    """
    Convert a ModelScore to a compact NDJSON line.
    
    Args:
        score: ModelScore object to serialize
        
    Returns:
        Compact JSON string (no extra formatting, no trailing newline)
        
    Note:
        Output is exactly one JSON object per line (NDJSON format).
        All floats are standard Python floats (0.0-1.0).
        All ints are plain ints.
    """
    # Get the ordered dictionary from ModelScore
    data = score.to_ndjson_dict()
    
    # Convert to compact JSON (no spaces, no newlines)
    return json.dumps(data, separators=(",", ":"))


def format_ndjson_line(data: dict) -> str:
    """
    Format a dictionary as a compact NDJSON line.
    
    Args:
        data: Dictionary to serialize
        
    Returns:
        Compact JSON string with no spaces
        
    Note:
        Deprecated: Use modelscore_to_ndjson_line() for ModelScore objects.
    """
    return json.dumps(data, separators=(",", ":"))
