from __future__ import annotations
import os
from typing import Optional, Dict, Any, List
from .config import AI_ENABLED, GEMINI_API_KEY, MAX_AI_TOKENS

try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None


class LLMClient:
    def __init__(self, enabled: bool = AI_ENABLED, api_key: Optional[str] = GEMINI_API_KEY):
        self.enabled = enabled and bool(api_key) and genai is not None
        self.api_key = api_key if self.enabled else None
        if self.enabled:
            genai.configure(api_key=self.api_key)
            # Choose a sensible default model name; allow override via env
            self.model_name = os.getenv("ROVO_DEV_GEMINI_MODEL", "gemini-1.5-flash")
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None

    def available(self) -> bool:
        return self.enabled

    def suggest_mapping(self, lens_name: str, patterns: List[Dict[str, Any]], variations: List[Dict[str, Any]]) -> Dict[int, int]:
        """
        Ask the LLM to propose a mapping from variation_number -> pattern_number.
        Returns a dict; empty if not available or on error.
        """
        if not self.available():
            return {}
        try:
            prompt = self._build_prompt(lens_name, patterns, variations)
            resp = self.model.generate_content(prompt)
            text = resp.text or ""
            mapping = self._parse_mapping(text)
            return mapping
        except Exception:
            return {}

    def _build_prompt(self, lens_name: str, patterns, variations) -> str:
        def clean(s: str) -> str:
            return (s or "").replace("\n", " ").strip()
        lines = [
            f"You are helping map variations to their best matching patterns for a lens named: {lens_name}.",
            "Patterns:",
        ]
        for p in patterns:
            lines.append(f"- Pattern {p.get('pattern_number')}: {clean(p.get('title'))}")
        lines.append("Variations:")
        for v in variations:
            lines.append(f"- Variation {v.get('variation_number')}: {clean(v.get('title'))}")
        lines.append("Return ONLY a JSON object mapping variation_number to pattern_number, e.g. {\"1\":1,\"2\":1,...}")
        return "\n".join(lines)

    def _parse_mapping(self, text: str) -> Dict[int, int]:
        import json
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1:
                return {}
            obj = json.loads(text[start:end+1])
            out = {}
            for k, v in obj.items():
                try:
                    out[int(k)] = int(v)
                except Exception:
                    continue
            return out
        except Exception:
            return {}
