"""
CLI for Phase 4: run retrieval and print context.
Usage:
  python -m phase4_retrieval.run "What is the 5Y return of ICICI Value Fund?"
  python -m phase4_retrieval.run "Equity funds with high risk" --top-k 5
"""
import argparse
import json
import logging
import sys
from pathlib import Path

from phase4_retrieval.config import DEFAULT_PERSIST_DIR
from phase4_retrieval.pipeline import retrieve_context

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4: Retrieve chunks and assemble context")
    parser.add_argument("query", type=str, nargs="?", default="", help="User question")
    parser.add_argument("--top-k", type=int, default=7, help="Number of chunks to retrieve")
    parser.add_argument("--max-context-chars", type=int, default=None, help="Max context length")
    parser.add_argument("--category", type=str, default=None, help="Filter by category (e.g. Equity)")
    parser.add_argument("--risk", type=str, default=None, help="Filter by risk (e.g. Very High)")
    parser.add_argument("--fund-name", type=str, default=None, help="Filter by fund name substring")
    parser.add_argument("--persist-dir", type=str, default=None, help="Chroma DB path")
    parser.add_argument("--json", action="store_true", help="Output full result as JSON")
    args = parser.parse_args()

    if not args.query.strip():
        parser.error("Provide a query (e.g. phase4_retrieval.run 'What is the NAV of Value Fund?')")
        return 1

    persist_dir = Path(args.persist_dir) if args.persist_dir else DEFAULT_PERSIST_DIR
    try:
        result = retrieve_context(
            args.query,
            top_k=args.top_k,
            max_context_chars=args.max_context_chars,
            category=args.category,
            risk=args.risk,
            fund_name_contains=args.fund_name,
            persist_dir=persist_dir,
        )
        if args.json:
            out = {
                "context": result["context"],
                "num_chunks": len(result["chunks"]),
                "chunks": [{"text": c.get("text", ""), "metadata": c.get("metadata", {})} for c in result["chunks"]],
                "distances": result.get("distances", []),
            }
            print(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            print("--- Retrieved context (for LLM) ---")
            print(result["context"])
            print("\n--- Chunks: %s ---" % len(result["chunks"]))
            for i, c in enumerate(result["chunks"], 1):
                print("[%s] %s" % (i, (c.get("text") or "")[:150] + "..." if len(c.get("text") or "") > 150 else (c.get("text") or "")))
        return 0
    except Exception as e:
        logging.exception("Retrieval failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
