from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ParsedURL:
    raw: str
    category: str  # MODEL | DATASET | CODE | UNKNOWN
    name: str

def parse_url(u: str) -> ParsedURL:
    s = u.strip()
    if "huggingface.co" in s:
        if "/datasets/" in s:
            name = s.split("/datasets/", 1)[1].split("/", 1)[0]
            return ParsedURL(s, "DATASET", name)
        else:
            # heuristic: take owner/repo
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

