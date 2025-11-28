from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any
from .config import KB_PATH


class KnowledgeBase:
    def __init__(self, path: Path = KB_PATH):
        self.path = path
        self.data: Dict[str, Any] = {
            "label_synonyms": {
                # maps variants to canonical labels used by extractor
                "pattern": ["pattern", "patterns", "task", "part"],
                "variation": ["variation", "variations", "var", "alt", "option"],
            },
            "heading_aliases": {},
            "known_titles": {
                # normalized_title -> canonical_title
            },
            "mappings": {
                # lens_name -> {variation_number -> pattern_number}
            }
        }
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                    self._deep_merge(self.data, stored)
            except Exception:
                pass

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _deep_merge(self, base: Dict[str, Any], other: Dict[str, Any]):
        for k, v in other.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                self._deep_merge(base[k], v)
            else:
                base[k] = v

    def add_mapping(self, lens_name: str, mapping: Dict[int, int]):
        self.data.setdefault("mappings", {}).setdefault(lens_name, {}).update(mapping)
        self.save()

    def get_mapping(self, lens_name: str) -> Dict[int, int]:
        return self.data.get("mappings", {}).get(lens_name, {})
