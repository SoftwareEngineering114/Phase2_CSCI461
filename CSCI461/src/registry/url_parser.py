"""
URL parsing and category detection for models, datasets, and code repositories.
"""
from __future__ import annotations

from .models import ParsedURL


def parse_url(url: str) -> ParsedURL:
    """
    Parse a URL and determine its category (MODEL, DATASET, CODE, or UNKNOWN).
    
    Args:
        url: The URL string to parse
        
    Returns:
        ParsedURL object containing category and extracted name
    """
    s = url.strip()
    
    if "huggingface.co" in s:
        if "/datasets/" in s:
            name = s.split("/datasets/", 1)[1].split("/", 1)[0]
            return ParsedURL(s, "DATASET", name)
        else:
            # Heuristic: take owner/repo
            tail = s.split("huggingface.co/", 1)[1]
            parts = [p for p in tail.split("/") if p]
            name = "/".join(parts[:2]) if len(parts) >= 2 else (parts[0] if parts else s)
            return ParsedURL(s, "MODEL", name)
    
    if "github.com" in s:
        tail = s.split("github.com/", 1)[1]
        parts = [p for p in tail.split("/") if p]
        name = "/".join(parts[:2]) if len(parts) >= 2 else (parts[0] if parts else s)
        return ParsedURL(s, "CODE", name)
    
    return ParsedURL(s, "UNKNOWN", s)

