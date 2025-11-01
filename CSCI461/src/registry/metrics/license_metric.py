"""
License metric: evaluates license permissiveness and clarity.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Tuple


class LicenseMetric:
    """
    License metric based on license type.
    
    Scoring:
    - Permissive licenses (MIT, Apache, BSD, LGPL): 1.0
    - License mentioned in README: 0.5
    - Other licenses: 0.2
    - No license: 0.0
    """
    
    name: str = "license"
    
    def compute(self, repo_info: Dict[str, Any]) -> Tuple[float, int]:
        """
        Compute license score.
        
        Args:
            repo_info: Context containing 'license' and 'hf_readme' keys
            
        Returns:
            Tuple of (score, latency_ms) where score is 0.0 to 1.0
        """
        t0 = time.perf_counter()
        
        try:
            lic = repo_info.get("license", "").lower() if repo_info.get("license") else ""
            
            if not lic:
                # Try README as fallback
                readme = repo_info.get("hf_readme", "").lower()
                if "license" in readme:
                    score = 0.5
                else:
                    score = 0.0
            else:
                # Check for permissive licenses
                permissive_licenses = ["lgpl", "mit", "apache", "bsd"]
                if any(pl in lic for pl in permissive_licenses):
                    score = 1.0
                else:
                    score = 0.2
            
            # Clamp to [0, 1]
            score = max(0.0, min(1.0, score))
            
        except Exception:
            score = 0.0
        
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        
        return score, latency_ms
