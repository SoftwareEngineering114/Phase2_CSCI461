"""
Performance claims metric: measures presence of benchmarks and evaluations.
"""
from __future__ import annotations

import re
import time
from typing import Any, Dict, Tuple


class PerformanceClaimsMetric:
    """
    Performance claims metric based on README content.
    
    Evaluates:
    - Presence of benchmarks
    - Accuracy metrics
    - Evaluation results
    """
    
    name: str = "performance_claims"
    
    def compute(self, repo_info: Dict[str, Any]) -> Tuple[float, int]:
        """
        Compute performance claims score.
        
        Args:
            repo_info: Context containing 'hf_readme' key
            
        Returns:
            Tuple of (score, latency_ms).
            Uses a conservative tiered approach to avoid over-crediting vague claims:
            - 1.0: benchmark keyword AND metric keyword AND numeric evidence
            - 0.5: benchmark keyword AND metric keyword (but no numbers)
            - 0.25: metric keyword only (weak evidence)
            - 0.0: no evidence
        """
        t0 = time.perf_counter()
        
        try:
            readme = (repo_info.get("hf_readme", "") or "")
            text = readme.lower()

            benchmark_keyword = any(k in text for k in ("benchmark", "benchmarks", "leaderboard", "sota"))
            metric_keyword = any(
                k in text
                for k in (
                    "accuracy",
                    "f1",
                    "bleu",
                    "rouge",
                    "perplexity",
                    "mmlu",
                    "hellaswag",
                    "truthfulqa",
                    "precision",
                    "recall",
                    "auc",
                )
            )

            # Numeric evidence: percentages or decimals commonly used for metrics.
            has_numbers = bool(re.search(r"(\b\d{1,3}(\.\d+)?\s*%|\b0\.\d+\b|\b\d+\.\d+\b)", text))

            if benchmark_keyword and metric_keyword and has_numbers:
                score = 1.0
            elif benchmark_keyword and metric_keyword:
                score = 0.5
            elif metric_keyword:
                score = 0.25
            else:
                score = 0.0
            
        except Exception:
            score = 0.0
        
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        
        return score, latency_ms
