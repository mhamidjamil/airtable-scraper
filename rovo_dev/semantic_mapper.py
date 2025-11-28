from __future__ import annotations
from typing import List, Dict, Any, Optional
import math

try:
    import torch
    from sentence_transformers import SentenceTransformer, util
except Exception:  # pragma: no cover
    torch = None
    SentenceTransformer = None
    util = None


class SemanticMapper:
    def __init__(self, model_name: str = "multi-qa-mpnet-base-dot-v1", device: Optional[str] = None, logger=None, threshold: float = 0.35, adapter_path: Optional[str] = None):
        self.logger = logger
        self.available_flag = False
        self.device = device or ("cuda" if torch is not None and torch.cuda.is_available() else "cpu")
        self.threshold = threshold
        self.adapter = None
        try:
            if SentenceTransformer is not None:
                self.model = SentenceTransformer(model_name, device=self.device)
                self.available_flag = True
            else:
                self.model = None
        except Exception as e:
            self.model = None
            self._log(f"Semantic model init failed: {e}", "warning")
        # load adapter if provided
        if adapter_path and torch is not None:
            try:
                ckpt = torch.load(adapter_path, map_location=self.device)
                dim = ckpt.get("dim")
                from .trainer import ProjectionAdapter
                self.adapter = ProjectionAdapter(dim)
                self.adapter.load_state_dict(ckpt["state_dict"])
                self.adapter.to(self.device)
                self.adapter.eval()
                self._log(f"Loaded adapter: {adapter_path}")
            except Exception as e:
                self._log(f"Failed to load adapter: {e}", "warning")

    def available(self) -> bool:
        return bool(self.available_flag and self.model is not None)

    def _log(self, msg, level="info"):
        if self.logger:
            getattr(self.logger, level if hasattr(self.logger, level) else "info")(msg)
        else:
            print(f"[{level.upper()}] {msg}")

    def best_mapping(self, patterns: List[Dict[str, Any]], variations: List[Dict[str, Any]]) -> Dict[int, int]:
        """
        Returns a mapping of variation_number -> pattern_number based on semantic similarity
        using titles + content bodies for richer context.
        """
        if not self.available() or not patterns or not variations:
            return {}
        try:
            p_texts = [self._pat_text(p) for p in patterns]
            v_texts = [self._var_text(v) for v in variations]
            p_emb = self.model.encode(p_texts, convert_to_tensor=True, normalize_embeddings=True)
            v_emb = self.model.encode(v_texts, convert_to_tensor=True, normalize_embeddings=True)
            # apply adapter if present
            if self.adapter is not None:
                p_emb = self.adapter(p_emb)
                v_emb = self.adapter(v_emb)
            sim = util.cos_sim(v_emb, p_emb)  # [V, P]
            mapping: Dict[int, int] = {}
            for vi, v in enumerate(variations):
                scores = sim[vi].tolist()
                best_pi = max(range(len(patterns)), key=lambda i: scores[i])
                best_score = scores[best_pi]
                target_num = patterns[best_pi]["pattern_number"]
                # threshold is configurable via constructor
                if best_score < self.threshold:
                    continue
                mapping[v["variation_number"]] = target_num
                v["_semantic_score"] = float(best_score)
            return mapping
        except Exception as e:
            self._log(f"Semantic mapping failed: {e}", "warning")
            return {}

    def _pat_text(self, p: Dict[str, Any]) -> str:
        return f"Pattern {p.get('pattern_number')}: {p.get('title','')}\n{p.get('overview','')}\n{p.get('choice','')}\n{p.get('source','')}".strip()

    def _var_text(self, v: Dict[str, Any]) -> str:
        return f"Variation {v.get('variation_number')}: {v.get('title','')}\n{v.get('content','')}".strip()
