from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime
from .config import DEFAULT_OUTPUT_DIR, AI_ENABLED
from .extractor import RovoExtractor
from .linker import RovoLinker
from .knowledge import KnowledgeBase
from .llm_client import LLMClient
from .semantic_mapper import SemanticMapper


def parse_args():
    ap = argparse.ArgumentParser(description="Rovo Dev robust extractor")
    ap.add_argument("--folder", "-f", required=True, help="Folder to process (absolute or relative)")
    ap.add_argument("--use-ai", action="store_true", help="Enable AI fallback (requires GEMINI_API_KEY)")
    ap.add_argument("--semantic-model", default="multi-qa-mpnet-base-dot-v1", help="SentenceTransformer model name")
    ap.add_argument("--semantic-threshold", type=float, default=0.35, help="Minimum cosine similarity to accept a mapping")
    ap.add_argument("--no-index-map", action="store_true", help="Disable index-based 1-to-1 mapping")
    ap.add_argument("--adapter", type=str, default=None, help="Path to trained adapter .pt (optional)")
    return ap.parse_args()


def find_project_folders(start_path: Path) -> list[Path]:
    def is_project(p: Path) -> bool:
        return (p / "STEP 2").exists() or (p / "Step 2").exists() or any(f.suffix.lower()==".docx" and not f.name.startswith("~$") for f in p.glob("*.docx"))

    if is_project(start_path):
        return [start_path]
    out = []
    for child in start_path.iterdir():
        if child.is_dir() and is_project(child):
            out.append(child)
    return out


def main():
    args = parse_args()
    start = Path(args.folder)
    projects = find_project_folders(start)
    if not projects:
        print(f"No projects found at {start}")
        return 1

    kb = KnowledgeBase()
    llm = LLMClient(enabled=args.use_ai or AI_ENABLED)

    extractor = RovoExtractor()
    semantic = SemanticMapper(logger=None, model_name=args.semantic_model, threshold=args.semantic_threshold, adapter_path=args.adapter)
    linker = RovoLinker(kb=kb, llm=llm, semantic=semantic, allow_index=not args.no_index_map)

    for proj in projects:
        print(f"Processing project: {proj}")
        # choose STEP 2 if present
        step2 = proj / "STEP 2"
        if not step2.exists():
            step2 = proj / "Step 2"
        target = step2 if step2.exists() else proj

        documents = []
        doc_stats = []
        for f in target.glob("*.docx"):
            if f.name.startswith("~$"):
                continue
            parsed = extractor.parse_document(f)
            if not parsed:
                continue
            lens_name = parsed["lens"]
            patterns = parsed["patterns"]
            variations = parsed["variations"]
            linked = linker.link(lens_name, patterns, variations)
            documents.append({
                "lens": lens_name,
                "file_path": parsed["file_path"],
                "summary": parsed["summary"],
                "patterns": linked,
                "sources": []
            })
            # stats
            total_vars = len(variations)
            sem_count = sum(1 for p in linked for v in p.get("variations", []) if v.get("_mapped_semantic"))
            fuzzy_count = sum(1 for p in linked for v in p.get("variations", []) if v.get("_mapped_score") is not None and not v.get("_mapped_semantic"))
            kb_llm_count = 0  # not explicitly flagged; infer later if needed
            fallback_count = 0
            # infer fallback by low scores and no semantic/fuzzy flags; approximate: none of the flags present
            for p in linked:
                for v in p.get("variations", []):
                    if not v.get("_mapped_semantic") and v.get("_mapped_score") is None:
                        fallback_count += 1
            doc_stats.append({
                "file": str(f),
                "lens": lens_name,
                "patterns": len(patterns),
                "variations": total_vars,
                "mapped_semantic": sem_count,
                "mapped_fuzzy": fuzzy_count,
                "mapped_fallback": fallback_count
            })

        if not documents:
            print(f"No documents extracted for {proj.name}")
            continue

        payload = {
            "base_folder": proj.name,
            "timestamp": datetime.now().isoformat(),
            "metas": [],
            "documents": documents,
        }
        out_file = DEFAULT_OUTPUT_DIR / f"rovo_dev_{proj.name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"Saved: {out_file}")

        # write run summaries
        from pathlib import Path as _P
        rs_dir = _P(__file__).resolve().parent / "run_summaries"
        rs_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        md_path = rs_dir / f"summary_{proj.name.lower()}_{ts}.md"
        json_path = rs_dir / f"summary_{proj.name.lower()}_{ts}.json"
        # markdown summary
        lines = [f"# Run Summary for {proj.name}", f"Timestamp: {ts}", "", "## Documents"]
        for s in doc_stats:
            lines.append(f"- {s['file']} (Lens: {s['lens']}) -> Patterns: {s['patterns']}, Variations: {s['variations']}, Semantically Mapped: {s['mapped_semantic']}, Fuzzy Mapped: {s['mapped_fuzzy']}, Fallback: {s['mapped_fallback']}")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"project": proj.name, "timestamp": ts, "documents": doc_stats}, f, indent=2)
        print(f"Run summary saved: {md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
