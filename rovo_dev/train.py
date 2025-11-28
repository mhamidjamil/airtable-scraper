from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime
from .extractor import RovoExtractor
from .trainer import train_adapter


def parse_args():
    ap = argparse.ArgumentParser(description="Train a projection adapter on top of SentenceTransformer using pseudo labels")
    ap.add_argument("--folder", "-f", required=True, help="Folder to process (absolute or relative)")
    ap.add_argument("--model", default="multi-qa-mpnet-base-dot-v1", help="Base SentenceTransformer model")
    ap.add_argument("--epochs", type=int, default=3, help="Training epochs")
    ap.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    ap.add_argument("--batch-size", type=int, default=32, help="Batch size")
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

    extractor = RovoExtractor()

    for proj in projects:
        print(f"Training adapter for project: {proj}")
        step2 = proj / "STEP 2"
        if not step2.exists():
            step2 = proj / "Step 2"
        target = step2 if step2.exists() else proj

        documents = []
        for f in target.glob("*.docx"):
            if f.name.startswith("~$"):
                continue
            parsed = extractor.parse_document(f)
            if not parsed:
                continue
            # in training we keep patterns and variations doc-level
            documents.append({
                "lens": parsed["lens"],
                "file_path": parsed["file_path"],
                "summary": parsed["summary"],
                "patterns": parsed["patterns"],
                "variations": parsed["variations"],
            })

        if not documents:
            print(f"No documents found for training in {proj.name}")
            continue

        out_dir = Path(__file__).resolve().parent / "trained_models" / proj.name.lower()
        train_adapter(args.model, documents, out_dir, epochs=args.epochs, lr=args.lr, batch_size=args.batch_size)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
