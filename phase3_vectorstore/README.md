# Phase 3: Embedding & Vector Store

Loads **Phase 2** RAG chunks, generates embeddings with **sentence-transformers**, and stores them in **Chroma** with metadata for similarity search and filtering.

Per [RAG_ARCHITECTURE_MUTUAL_FUNDS.md](../RAG_ARCHITECTURE_MUTUAL_FUNDS.md).

## Steps

1. **Load** processed chunks from Phase 2 (`rag_chunks.json`).
2. **Embed** each chunk text with a local embedding model (default: `all-MiniLM-L6-v2`, 384 dims).
3. **Upsert** into Chroma: vectors + documents + metadata (fund_name, category, risk, nav, aum, etc.).
4. **Persist** the vector store to disk for Phase 4 retrieval.

## Input

- Phase 2 output: `phase2_processing/output/rag_chunks.json` (default).

## Output

- **Chroma DB** under `phase3_vectorstore/chroma_db/` (default). Queryable by vector similarity and metadata filters (e.g. category, risk).

## Setup

```bash
pip install -r phase3_vectorstore/requirements.txt
```

First run will download the embedding model (~80MB).

## Run

From project root:

```bash
# Default: read phase2_processing/output/rag_chunks.json, write to phase3_vectorstore/chroma_db/
python -m phase3_vectorstore.run

# Custom paths
python -m phase3_vectorstore.run --chunks phase2_processing/output/rag_chunks.json --persist-dir ./my_chroma_db

# Append to existing collection (do not replace)
python -m phase3_vectorstore.run --no-replace
```

## Tests

```bash
python -m pytest phase3_vectorstore/tests/test_phase3.py -v
```

- Embedding and full-pipeline tests are **skipped** if `sentence-transformers` is not installed.
- Full pipeline test is also skipped if Phase 2 `rag_chunks.json` is missing.
- With deps installed, all 7 tests run (including embed and Chroma pipeline).

## Folder structure

```
phase3_vectorstore/
├── __init__.py
├── config.py         # Chunks path, persist dir, model name, metadata keys
├── embeddings.py     # sentence-transformers: embed_texts, embed_query
├── store.py          # Chroma: get client, create collection, add chunks
├── pipeline.py       # load_chunks, run_pipeline
├── run.py            # CLI
├── requirements.txt
├── README.md
├── chroma_db/        # Created on first run (Chroma persistence)
└── tests/
    ├── __init__.py
    └── test_phase3.py
```

## Phase 4

Use `embed_query()` and `load_collection()` from this package for retrieval: embed the user query, then `collection.query(embedding, n_results=k)`.
