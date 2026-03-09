"""
Local test: confirm retriever uses bundled path phase4_retrieval/data/rag_chunks.json
Run from repo root: python test_bundled_path.py
"""
import sys
from pathlib import Path

# Project root on path
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# Optional: simulate Streamlit cwd (run from subdir)
# import os; os.chdir(_root / "phase6_chatbot")

from phase4_retrieval.retriever import _find_chunks_path, retrieve_from_json

def main():
    path = _find_chunks_path()
    bundled = Path(__file__).resolve().parent / "phase4_retrieval" / "data" / "rag_chunks.json"

    print("1. _find_chunks_path() returned:", path)
    print("   Bundled path (expected):", bundled)
    assert path is not None, "Chunks path should not be None"
    assert path.exists(), f"Chunks file should exist: {path}"
    assert path.resolve() == bundled.resolve(), (
        f"Should use bundled path; got {path.resolve()}"
    )
    print("   OK — using bundled path\n")

    print("2. retrieve_from_json('equity fund') ...")
    chunks, scores = retrieve_from_json("equity fund", top_k=2)
    assert len(chunks) > 0, "Should return at least one chunk"
    assert len(scores) == len(chunks), "Scores length should match chunks"
    print(f"   Got {len(chunks)} chunk(s), scores: {[round(s, 4) for s in scores]}")
    print("   OK — retrieval works\n")

    print("All checks passed. Bundled path is used and retrieval works.")

if __name__ == "__main__":
    main()
