"""
Bus factor metric: measures project resilience based on contributor diversity.
"""
from __future__ import annotations

from typing import Any, Dict

from .base import BaseMetric


class BusFactorMetric(BaseMetric):
    """
    Bus factor metric based on number of contributors.
    
    Evaluates project resilience:
    - 1 contributor: 0.1
    - 5+ contributors: 1.0
    - Linear scaling between
    """
    
    def compute(self, ctx: Dict[str, Any]) -> float:
        """
        Compute bus factor score.
        
        Args:
            ctx: Context containing 'git_contributors' key
            
        Returns:
            Score from 0.1 to 1.0
        """
        contributors = ctx.get("git_contributors", 1)
        
        if contributors <= 1:
            return 0.1
        
        return min(1.0, contributors / 5.0)

