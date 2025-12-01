"""
Data models and types for scores and resource requirements.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, Literal

# Resource category type
ResourceCategory = Literal["MODEL", "DATASET", "CODE"]


@dataclass
class ParsedURL:
    """Parsed URL with category detection."""
    raw: str
    category: ResourceCategory | Literal["UNKNOWN"]
    name: str


@dataclass
class ModelScore:
    """
    Complete scoring result for a model.
    
    Contains all metric scores, latencies, and net score.
    Provides to_ndjson_dict() for exact output format matching spec Table 1.
    """
    name: str
    category: ResourceCategory
    
    # Individual metric scores (0.0 - 1.0)
    ramp_up_time: float
    bus_factor: float
    performance_claims: float
    license: float
    dataset_and_code_score: float
    dataset_quality: float
    code_quality: float
    
    # Size score is special - dict with hardware targets
    size_score: Dict[str, float]
    
    # Latencies in milliseconds
    ramp_up_time_latency: int
    bus_factor_latency: int
    performance_claims_latency: int
    license_latency: int
    size_score_latency: int
    dataset_and_code_score_latency: int
    dataset_quality_latency: int
    code_quality_latency: int
    
    # Net score and its latency
    net_score: float
    net_score_latency: int
    
    def to_ndjson_dict(self) -> OrderedDict[str, Any]:
        """
        Convert to OrderedDict with exact field names and order from spec Table 1.
        
        Returns:
            OrderedDict with fields in correct order for NDJSON output
        """
        return OrderedDict([
            ("name", self.name),
            ("category", self.category),
            ("net_score", round(self.net_score, 3)),
            ("net_score_latency", self.net_score_latency),
            ("ramp_up_time", round(self.ramp_up_time, 3)),
            ("ramp_up_time_latency", self.ramp_up_time_latency),
            ("bus_factor", round(self.bus_factor, 3)),
            ("bus_factor_latency", self.bus_factor_latency),
            ("performance_claims", round(self.performance_claims, 3)),
            ("performance_claims_latency", self.performance_claims_latency),
            ("license", round(self.license, 3)),
            ("license_latency", self.license_latency),
            ("size_score", self.size_score),
            ("size_score_latency", self.size_score_latency),
            ("dataset_and_code_score", round(self.dataset_and_code_score, 3)),
            ("dataset_and_code_score_latency", self.dataset_and_code_score_latency),
            ("dataset_quality", round(self.dataset_quality, 3)),
            ("dataset_quality_latency", self.dataset_quality_latency),
            ("code_quality", round(self.code_quality, 3)),
            ("code_quality_latency", self.code_quality_latency),
        ])
