"""
Ramp-up time metric: measures documentation quality and ease of getting started.
"""
from __future__ import annotations

from typing import Any, Dict

from .base import BaseMetric


class RampUpTimeMetric(BaseMetric):
    """
    Ramp-up time metric based on README quality.
    
    Evaluates:
    - Presence of examples or quickstart guides
    - Length and completeness of documentation
    """
    
    def compute(self, ctx: Dict[str, Any]) -> float:
        """
        Compute ramp-up time score.
        
        Args:
            ctx: Context containing 'hf_readme' key
            
        Returns:
            Score from 0.0 to 1.0
        """
        readme = ctx.get("hf_readme", "")
        
        # Check for examples or quickstart
        examples = 1.0 if ("example" in readme.lower() or "quickstart" in readme.lower()) else 0.0
        
        # Score based on documentation length (300 words = 1.0)
        length_score = min(1.0, len(readme.split()) / 300.0)
        
        return 0.5 * length_score + 0.5 * examples

