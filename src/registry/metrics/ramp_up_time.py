# """
# Ramp-up time metric: measures documentation quality and ease of getting started.
# """
# from __future__ import annotations

# import time
# from typing import Any, Dict, Tuple


# class RampUpTimeMetric:
#     """
#     Ramp-up time metric based on README quality.
    
#     Evaluates:
#     - Presence of examples or quickstart guides
#     - Length and completeness of documentation
#     """
    
#     name: str = "ramp_up_time"
    
#     def compute(self, repo_info: Dict[str, Any]) -> Tuple[float, int]:
#         """
#         Compute ramp-up time score.
        
#         Args:
#             repo_info: Context containing 'hf_readme' key
            
#         Returns:
#             Tuple of (score, latency_ms) where score is 0.0 to 1.0
#         """
#         t0 = time.perf_counter()
        
#         try:
#             readme = repo_info.get("hf_readme", "")
            
#             # Check for examples or quickstart
#             examples = 1.0 if ("example" in readme.lower() or "quickstart" in readme.lower()) else 0.0
            
#             # Score based on documentation length (300 words = 1.0)
#             length_score = min(1.0, len(readme.split()) / 300.0)
            
#             score = 0.5 * length_score + 0.5 * examples
            
#             # Clamp to [0, 1]
#             score = max(0.0, min(1.0, score))
            
#         except Exception:
#             score = 0.0
        
#         t1 = time.perf_counter()
#         latency_ms = int(round((t1 - t0) * 1000))
        
#         return score, latency_ms


"""
Ramp-up time metric: measures documentation quality and ease of getting started.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Tuple


class RampUpTimeMetric:
    """
    Ramp-up time metric based on README quality.
    
    Evaluates:
    - Presence of examples or quickstart guides
    - Length and completeness of documentation
    """
    
    name: str = "ramp_up_time"
    
    def compute(self, repo_info: Dict[str, Any]) -> Tuple[float, int]:
        """
        Compute ramp-up time score.
        
        Args:
            repo_info: Context containing 'hf_readme' key
            
        Returns:
            Tuple of (score, latency_ms) where score is 0.0 to 1.0
        """
        t0 = time.perf_counter()
        
        try:
            readme = repo_info.get("hf_readme", "")
            readme_lower = readme.lower()
            
            # Base score starts at 0
            score = 0.0
            
            # Documentation length score (up to 0.5 points)
            # More lenient thresholds - 150 words gets full 0.5
            word_count = len(readme.split())
            if word_count >= 150:
                length_score = 0.5
            elif word_count >= 100:
                length_score = 0.4
            elif word_count >= 50:
                length_score = 0.3
            elif word_count > 0:
                length_score = 0.1
            else:
                length_score = 0.0
            
            score += length_score
            
            # Examples/quickstart presence (up to 0.35 points)
            has_examples = any([
                "example" in readme_lower,
                "quickstart" in readme_lower,
                "getting started" in readme_lower,
                "usage" in readme_lower
            ])
            if has_examples:
                score += 0.35
            
            # Code snippets presence (up to 0.15 points)
            # Check for common code indicators
            has_code = any([
                "```" in readme,  # Markdown code blocks
                "import" in readme_lower,
                "from " in readme_lower,
                "def " in readme_lower,
                "class " in readme_lower
            ])
            if has_code:
                score += 0.15
            
            # Clamp to [0, 1]
            score = max(0.0, min(1.0, score))
            
        except Exception:
            score = 0.0
        
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        
        return score, latency_ms
