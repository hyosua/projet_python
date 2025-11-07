import json
import re
from difflib import SequenceMatcher
from typing import Any

class BaselineGrader:
    """
    Correction sans LLM :
      - similarité avec la réponse attendue (0..40 points)
      - bonus +10 par point obligatoire trouvé
      - malus -10 par point interdit détecté
    """
    def __init__(self, required_points: list[Any], forbidden_points: list[Any], expected: str):
        self.req = required_points or []
        self.forb = forbidden_points or []
        self.expected = expected or ""

    def _check_point(self, spec, text: str) -> bool:
        if isinstance(spec, str):
            return spec.lower() in text.lower()
        if isinstance(spec, dict) and spec.get("type") == "regex":
            return re.search(spec.get("value", ""), text, flags=re.I) is not None
        return False

    def grade(self, answer: str) -> tuple[float, str]:
        text = answer or ""
        # 1) similarité
        sim = SequenceMatcher(None, text.lower(), self.expected.lower()).ratio()
        base = round(sim * 40, 2)  # max 40
        # 2) requis
        found, missing = [], []
        for p in self.req:
            (found if self._check_point(p, text) else missing).append(p)
        req_score = 10 * len(found)
        # 3) interdits
        violated = [p for p in self.forb if self._check_point(p, text)]
        pen = 10 * len(violated)

        score = max(0, min(100, base + req_score - pen))
        feedback = {
            "similarity_score": base,
            "required_found": found,
            "required_missing": missing,
            "forbidden_detected": violated,
            "final": score,
        }
        return score, json.dumps(feedback, ensure_ascii=False, indent=2)
