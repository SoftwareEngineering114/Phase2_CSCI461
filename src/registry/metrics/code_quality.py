"""
Code quality metric: evaluates code quality based on tests, CI, and linting.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Tuple


class CodeQualityMetric:
    """
    Code quality metric based on engineering practices.
    
    Evaluates:
    - Presence of tests (40% weight)
    - Presence of CI/CD (30% weight)
    - Linting status (30% weight)
    """
    
    name: str = "code_quality"
    
    def compute(self, repo_info: Dict[str, Any]) -> Tuple[float, int]:
        """
        Compute code quality score.
        
        Args:
            repo_info: Context containing 'has_tests', 'has_ci', 'lint_ok', 'lint_warn' keys
            
        Returns:
            Tuple of (score, latency_ms) where score is 0.0 to 1.0
        """
        t0 = time.perf_counter()
        
        try:
            has_tests = repo_info.get("has_tests", False)
            has_ci = repo_info.get("has_ci", False)
            
            # Lint score: 1.0 if passes, 0.5 if warnings, 0.0 if fails
            lint_score = 1.0 if repo_info.get("lint_ok", False) else (
                0.5 if repo_info.get("lint_warn", False) else 0.0
            )
            
            # Weighted combination
            score = 0.4 * float(has_tests) + 0.3 * float(has_ci) + 0.3 * lint_score
            
            # Clamp to [0, 1]
            score = max(0.0, min(1.0, score))
            
        except Exception:
            score = 0.0
        
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        
        return score, latency_ms
