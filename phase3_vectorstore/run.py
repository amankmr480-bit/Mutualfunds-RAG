"""
CLI entry point for Phase 3: Embedding & Vector Store.
Usage:
  python -m phase3_vectorstore.run
  python -m phase3_vectorstore.run --chunks phase2_processing/output/rag_chunks.json --persist-dir ./chroma_db --no-replace
"""
import argparse
import logging
import sys
from pathlib import Path

from phase3_vectorstore.config import DEFAULT_CHUNKS_PATH, DEFAULT_PERSIST_DIR
from phase3_vectorstore.pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 3: Embed chunks and build vector store (Chroma)")
    parser.add_argument("--chunks", type=str, default=str(DEFAULT_CHUNKS_PATH), help="Path to Phase 2 rag_chunks.json")
    parser.add_argument("--persist-dir", type=str, default=None, help="Chroma persist directory")
    parser.add_argument("--no-replace", action="store_true", help="Do not replace existing collection (append instead)")
    parser.add_argument("--batch-size", type=int, default=32, help="Embedding batch size")
    args = parser.parse_args()
    persist_dir = Path(args.persist_dir) if args.persist_dir else DEFAULT_PERSIST_DIR
    try:
        result = run_pipeline(
            chunks_path=args.chunks,
            persist_dir=persist_dir,
            replace_collection=not args.no_replace,
            embed_batch_size=args.batch_size,
        )
        print("Phase 3 complete.")
        print("Chunk count:", result["chunk_count"])
        print("Persist dir:", result["persist_dir"])
        print("Collection:", result["collection_name"])
        return 0
    except Exception as e:
        logging.exception("Phase 3 failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
