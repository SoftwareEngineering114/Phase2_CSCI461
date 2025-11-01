"""
Code quality metric: evaluates code quality based on tests, CI, and linting.
"""
from __future__ import annotations

from typing import Any, Dict

from .base import BaseMetric


class CodeQualityMetric(BaseMetric):
    """
    Code quality metric based on engineering practices.
    
    Evaluates:
    - Presence of tests (40% weight)
    - Presence of CI/CD (30% weight)
    - Linting status (30% weight)
    """
    
    def compute(self, ctx: Dict[str, Any]) -> float:
        """
        Compute code quality score.
        
        Args:
            ctx: Context containing 'has_tests', 'has_ci', 'lint_ok', 'lint_warn' keys
            
        Returns:
            Score from 0.0 to 1.0
        """
        has_tests = ctx.get("has_tests", False)
        has_ci = ctx.get("has_ci", False)
        
        # Lint score: 1.0 if passes, 0.5 if warnings, 0.0 if fails
        lint_score = 1.0 if ctx.get("lint_ok", False) else (0.5 if ctx.get("lint_warn", False) else 0.0)
        
        # Weighted combination
        score = 0.4 * float(has_tests) + 0.3 * float(has_ci) + 0.3 * lint_score
        return min(1.0, score)

