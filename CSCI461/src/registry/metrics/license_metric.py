"""
License metric: evaluates license permissiveness and clarity.
"""
from __future__ import annotations

from typing import Any, Dict

from .base import BaseMetric


class LicenseMetric(BaseMetric):
    """
    License metric based on license type.
    
    Scoring:
    - Permissive licenses (MIT, Apache, BSD, LGPL): 1.0
    - License mentioned in README: 0.5
    - Other licenses: 0.2
    - No license: 0.0
    """
    
    def compute(self, ctx: Dict[str, Any]) -> float:
        """
        Compute license score.
        
        Args:
            ctx: Context containing 'license' and 'hf_readme' keys
            
        Returns:
            Score from 0.0 to 1.0
        """
        lic = ctx.get("license", "").lower() if ctx.get("license") else ""
        
        if not lic:
            # Try README as fallback
            readme = ctx.get("hf_readme", "").lower()
            if "license" in readme:
                return 0.5
            return 0.0
        
        # Check for permissive licenses
        permissive_licenses = ["lgpl", "mit", "apache", "bsd"]
        if any(pl in lic for pl in permissive_licenses):
            return 1.0
        
        return 0.2

