from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import torch
import torch.nn as nn
import torch.optim as optim
from .extractor import RovoExtractor
from .semantic_mapper import SentenceTransformer, util, torch as torch_mod


class ProjectionAdapter(nn.Module):
    def __init__(self, dim: int):
        super().__init__()
        self.proj = nn.Linear(dim, dim, bias=False)
        # initialize close to identity
        with torch.no_grad():
            self.proj.weight.copy_(torch.eye(dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.proj(x)


def build_pairs(model, documents: List[Dict[str, Any]]):
    # Build training pairs using baseline semantic mapping as pseudo labels
    pattern_texts = []
    pattern_meta = []  # (doc_idx, pattern_number)
    variation_texts = []
    variation_targets = []  # index into pattern_texts

    # Flatten patterns across docs but keep mapping indices
    offset = 0
    pat_indices_by_doc_and_num = {}
    for di, doc in enumerate(documents):
        pats = doc.get("patterns", [])
        this_map = {}
        for p in pats:
            text = f"Pattern {p.get('pattern_number')}: {p.get('title','')}\n{p.get('overview','')}\n{p.get('choice','')}\n{p.get('source','')}".strip()
            pattern_texts.append(text)
            idx = offset
            this_map[p.get('pattern_number')] = idx
            pattern_meta.append((di, p.get('pattern_number')))
            offset += 1
        pat_indices_by_doc_and_num[di] = this_map

    # Encode patterns once
    device = "cuda" if torch_mod is not None and torch_mod.cuda.is_available() else "cpu"
    with torch.no_grad():
        p_emb = model.encode(pattern_texts, convert_to_tensor=True, normalize_embeddings=True)
    # Detach/clone to avoid inference-mode autograd issues
    p_emb = p_emb.detach().clone()

    # Build baseline mapping via similarity (pseudo labels)
    for di, doc in enumerate(documents):
        vars = []
        for p in doc.get("patterns", []):
            # variations for training come from doc-level variations aggregated; fallback to pattern-embedded variations
            vars.extend(p.get("variations", []))
        # If extractor stored doc-level variations separately, include them too
        if doc.get("variations"):
            vars.extend(doc.get("variations", []))
        # remove duplicates
        seen = set()
        uniq_vars = []
        for v in vars:
            key = (v.get("variation_number"), v.get("title"))
            if key in seen:
                continue
            seen.add(key)
            uniq_vars.append(v)
        for v in uniq_vars:
            v_text = f"Variation {v.get('variation_number')}: {v.get('title','')}\n{v.get('content','')}".strip()
            variation_texts.append(v_text)
            # baseline best pattern within the same doc
            # compute sim of this variation against patterns of this doc only
            pat_idx_map = pat_indices_by_doc_and_num[di]
            this_pat_indices = list(pat_idx_map.values())
            with torch.no_grad():
                v_emb = model.encode([v_text], convert_to_tensor=True, normalize_embeddings=True)
            sims = util.cos_sim(v_emb, p_emb[this_pat_indices])  # [1, P_doc]
            best_local = int(torch.argmax(sims[0]).item())
            global_idx = this_pat_indices[best_local]
            variation_targets.append(global_idx)

    with torch.no_grad():
        v_emb_all = model.encode(variation_texts, convert_to_tensor=True, normalize_embeddings=True)
    # Detach/clone to avoid inference-mode autograd issues
    v_emb_all = v_emb_all.detach().clone()
    return p_emb, v_emb_all, variation_targets, pattern_meta


def train_adapter(model_name: str, documents: List[Dict[str, Any]], out_dir: Path, epochs: int = 3, lr: float = 1e-4, batch_size: int = 32):
    if SentenceTransformer is None:
        raise RuntimeError("sentence-transformers not installed.")
    model = SentenceTransformer(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    p_emb, v_emb, v_targets, pattern_meta = build_pairs(model, documents)
    dim = p_emb.shape[1]

    adapter = ProjectionAdapter(dim).to(device)
    opt = optim.Adam(adapter.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()

    # Build mapping from global pattern index -> local class index per variation batch
    # For simplicity, we'll classify over all patterns globally (approximation). For better results, we could batch per doc.
    global_targets = torch.tensor(v_targets, dtype=torch.long, device=device)

    # Train
    n = v_emb.shape[0]
    steps_per_epoch = max(1, (n + batch_size - 1) // batch_size)
    v_emb = v_emb.to(device)
    p_emb = p_emb.to(device)

    for epoch in range(epochs):
        perm = torch.randperm(n)
        total_loss = 0.0
        for i in range(steps_per_epoch):
            batch_idx = perm[i*batch_size:(i+1)*batch_size]
            if batch_idx.numel() == 0:
                continue
            v_batch = v_emb[batch_idx]
            t_batch = global_targets[batch_idx]
            # Project
            v_proj = adapter(v_batch)
            p_proj = adapter(p_emb)
            # Similarity as logits
            logits = torch.matmul(v_proj, p_proj.t())  # [B, P]
            loss = loss_fn(logits, t_batch)
            opt.zero_grad()
            loss.backward()
            opt.step()
            total_loss += loss.item()
        avg_loss = total_loss / steps_per_epoch
        print(f"Epoch {epoch+1}/{epochs} - loss: {avg_loss:.4f}")

    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({
        "state_dict": adapter.state_dict(),
        "dim": dim,
        "base_model": model_name
    }, out_dir / "adapter.pt")
    with open(out_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump({
            "epochs": epochs,
            "lr": lr,
            "batch_size": batch_size,
            "base_model": model_name
        }, f, indent=2)
    print(f"Adapter saved to: {out_dir}")
