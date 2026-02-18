"""
Vantablack Core v5 - Detection Scanner
======================================

Static analysis tool to score phishlets against known signatures.
"""

import re
import logging
from typing import List, Dict

class DetectionScanner:
    def __init__(self):
        self.logger = logging.getLogger("vantablack.mutation.scanner")
        # Signatures to look for (Regex)
        self.signatures = {
            "eval_usage": r"eval\(",
            "base64_decode": r"atob\(",
            "document_write": r"document\.write\(",
            "phishing_keyword": r"(password|login|credential)",
            "external_loader": r"script\.src\s*=",
            "iframe_usage": r"<iframe"
        }

    def scan_content(self, content: str) -> Dict[str, float]:
        """
        Analyze content and return a detection score (0.0 - 1.0).
        Higher score = Higher risk of detection.
        """
        score = 0.0
        matches = []

        for name, regex in self.signatures.items():
            if re.search(regex, content, re.IGNORECASE):
                score += 0.2
                matches.append(name)

        # Cap score at 1.0
        score = min(score, 1.0)
        
        return {
            "score": score,
            "matches": matches,
            "status": "RISKY" if score > 0.5 else "SAFE"
        }
