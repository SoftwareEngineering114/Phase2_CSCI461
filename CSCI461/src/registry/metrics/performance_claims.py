"""
Performance claims metric: measures presence of benchmarks and evaluations.
"""
from __future__ import annotations

from typing import Any, Dict

from .base import BaseMetric


class PerformanceClaimsMetric(BaseMetric):
    """
    Performance claims metric based on README content.
    
    Evaluates:
    - Presence of benchmarks
    - Accuracy metrics
    - Evaluation results
    """
    
    def compute(self, ctx: Dict[str, Any]) -> float:
        """
        Compute performance claims score.
        
        Args:
            ctx: Context containing 'hf_readme' key
            
        Returns:
            1.0 if benchmarks/accuracy/eval mentioned, 0.0 otherwise
        """
        readme = ctx.get("hf_readme", "")
        readme_lower = readme.lower()
        
        has_claims = (
            "benchmark" in readme_lower
            or "accuracy" in readme_lower
            or "eval" in readme_lower
        )
        
        return 1.0 if has_claims else 0.0

