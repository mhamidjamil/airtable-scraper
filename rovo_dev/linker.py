from __future__ import annotations
from typing import List, Dict, Any
from .text_utils import normalize_key, fuzzy_ratio


class RovoLinker:
    def __init__(self, logger=None, kb=None, llm=None, semantic=None, allow_index: bool = True):
        self.logger = logger
        self.kb = kb
        self.llm = llm
        self.semantic = semantic
        self.allow_index = allow_index

    def log(self, msg, level="info"):
        if self.logger:
            getattr(self.logger, level if hasattr(self.logger, level) else "info")(msg)
        else:
            print(f"[{level.upper()}] {msg}")

    def link(self, lens_name: str, patterns: List[Dict[str, Any]], variations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not patterns:
            return []
        # Build map
        p_map = {p["pattern_number"]: p for p in patterns}
        for p in patterns:
            p.setdefault("variations", [])

        # 1) If counts align and numbers are 1..N, map by index
        if self.allow_index and variations and all(v.get("variation_number") for v in variations):
            v_nums = [v["variation_number"] for v in variations]
            p_nums = [p["pattern_number"] for p in patterns]
            if len(v_nums) == len(p_nums) and min(v_nums) == 1 and min(p_nums) == 1:
                self.log("Using index-based 1-to-1 mapping due to aligned counts")
                for v in variations:
                    target = p_map.get(v["variation_number"]) or patterns[0]
                    target["variations"].append(v)
                return patterns

        # 2) Semantic mapping (GPU if available)
        if self.semantic and self.semantic.available():
            sem_map = self.semantic.best_mapping(patterns, variations)
        else:
            sem_map = {}
        p_by_num = {p["pattern_number"]: p for p in patterns}
        for v in variations:
            t_num = sem_map.get(v.get("variation_number"))
            if t_num and p_by_num.get(t_num):
                p_by_num[t_num].setdefault("variations", []).append(v)
                v["_mapped_semantic"] = True
            else:
                v["_unresolved"] = True

        unresolved = [v for v in variations if v.get("_unresolved")]
        if unresolved:
            self.log(f"Unresolved after semantic mapping: {len(unresolved)}; trying fuzzy match")

        # 3) Heuristic keyword match of titles
        for v in unresolved:
            best = None
            best_score = 0.0
            for p in patterns:
                s = fuzzy_ratio(v.get("title", ""), p.get("title", ""))
                if s > best_score:
                    best = p
                    best_score = s
            if best is None or best_score < 0.55:
                # remains unresolved
                v["_unresolved"] = True
            else:
                best.setdefault("variations", []).append(v)
                v["_mapped_score"] = best_score
                v.pop("_unresolved", None)

        unresolved = [v for v in variations if v.get("_unresolved")]
        if unresolved:
            self.log(f"Unresolved variations: {len(unresolved)}; trying KB/LLM")

        unresolved = [v for v in variations if v.get("_unresolved")]
        if unresolved:
            self.log(f"Unresolved variations: {len(unresolved)}; trying KB/LLM")

        # 3) Apply KB mappings if present
        if self.kb:
            kb_map = self.kb.get_mapping(lens_name)
            if kb_map:
                for v in list(unresolved):
                    target_num = kb_map.get(v["variation_number"])  # type: ignore
                    if target_num:
                        target = p_map.get(target_num)
                        if target:
                            target.setdefault("variations", []).append(v)
                            v.pop("_unresolved", None)
                            self.log(f"KB mapped Variation {v['variation_number']} -> Pattern {target_num}")
                unresolved = [v for v in variations if v.get("_unresolved")]

        # 4) Optional LLM mapping
        if unresolved and self.llm and self.llm.available():
            mapping = self.llm.suggest_mapping(lens_name, patterns, variations)
            if mapping:
                for v in list(unresolved):
                    target_num = mapping.get(v["variation_number"])  # type: ignore
                    if target_num:
                        target = p_map.get(target_num)
                        if target:
                            target.setdefault("variations", []).append(v)
                            v.pop("_unresolved", None)
                            self.log(f"LLM mapped Variation {v['variation_number']} -> Pattern {target_num}")
                # persist
                if self.kb:
                    self.kb.add_mapping(lens_name, mapping)
                unresolved = [v for v in variations if v.get("_unresolved")]

        # 5) Fallback: attach all remaining to Pattern 1
        if unresolved:
            self.log(f"Fallback: attaching {len(unresolved)} unresolved variations to Pattern 1")
            for v in unresolved:
                patterns[0].setdefault("variations", []).append(v)
                v.pop("_unresolved", None)
        return patterns
