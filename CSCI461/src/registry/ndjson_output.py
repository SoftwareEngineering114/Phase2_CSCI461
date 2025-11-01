"""
NDJSON output formatting for model scores.
"""
from __future__ import annotations

import json
from typing import Any, Dict


def format_ndjson_line(data: Dict[str, Any]) -> str:
    """
    Format a dictionary as a compact NDJSON line.
    
    Args:
        data: Dictionary to serialize
        
    Returns:
        Compact JSON string with no spaces
    """
    return json.dumps(data, separators=(",", ":"))

