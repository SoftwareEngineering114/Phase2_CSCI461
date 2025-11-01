"""
Data models and types for scores and resource requirements.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ParsedURL:
    """Parsed URL with category detection."""
    raw: str
    category: str  # MODEL | DATASET | CODE | UNKNOWN
    name: str


@dataclass
class ResourceScore:
    """Resource compatibility scores for different hardware targets."""
    raspberry_pi: float
    jetson_nano: float
    desktop_pc: float
    aws_server: float

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary format."""
        return {
            "raspberry_pi": self.raspberry_pi,
            "jetson_nano": self.jetson_nano,
            "desktop_pc": self.desktop_pc,
            "aws_server": self.aws_server,
        }


@dataclass
class MetricResult:
    """Result of a single metric computation."""
    value: float | ResourceScore
    latency_ms: int


@dataclass
class ModelScores:
    """Complete scoring result for a model."""
    name: str
    category: str
    net_score: float
    net_score_latency: int
    ramp_up_time: float
    ramp_up_time_latency: int
    bus_factor: float
    bus_factor_latency: int
    performance_claims: float
    performance_claims_latency: int
    license: float
    license_latency: int
    size_score: ResourceScore
    size_score_latency: int
    dataset_and_code_score: float
    dataset_and_code_score_latency: int
    dataset_quality: float
    dataset_quality_latency: int
    code_quality: float
    code_quality_latency: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization."""
        return {
            "name": self.name,
            "category": self.category,
            "net_score": round(self.net_score, 3),
            "net_score_latency": self.net_score_latency,
            "ramp_up_time": round(self.ramp_up_time, 3),
            "ramp_up_time_latency": self.ramp_up_time_latency,
            "bus_factor": round(self.bus_factor, 3),
            "bus_factor_latency": self.bus_factor_latency,
            "performance_claims": round(self.performance_claims, 3),
            "performance_claims_latency": self.performance_claims_latency,
            "license": round(self.license, 3),
            "license_latency": self.license_latency,
            "size_score": self.size_score.to_dict(),
            "size_score_latency": self.size_score_latency,
            "dataset_and_code_score": round(self.dataset_and_code_score, 3),
            "dataset_and_code_score_latency": self.dataset_and_code_score_latency,
            "dataset_quality": round(self.dataset_quality, 3),
            "dataset_quality_latency": self.dataset_quality_latency,
            "code_quality": round(self.code_quality, 3),
            "code_quality_latency": self.code_quality_latency,
        }

