# Phase 4: Retrieval Layer

Implements the retrieval layer for the RAG chatbot: **query preprocessing → embedding → vector search (with optional filters) → top-K chunks → context assembly** for the LLM.

Per [RAG_ARCHITECTURE_MUTUAL_FUNDS.md](../RAG_ARCHITECTURE_MUTUAL_FUNDS.md).

## Query flow

```
User Query → Preprocess (normalize, expand 1Y/5Y/NAV etc.) → Embed (Phase 3 model) → Chroma similarity search → Top-K chunks → Assemble context string
```

## Features

- **Query preprocessing:** Normalize whitespace; expand abbreviations (1Y → 1 year return, NAV → net asset value, AUM, expense ratio, etc.).
- **Embedding:** Same sentence-transformers model as Phase 3 (`embed_query`).
- **Search:** Chroma similarity search; configurable `top_k` (default 7).
- **Filtering:** Optional `where` filter by `category` and `risk`; optional post-filter by fund name substring.
- **Context assembly:** Concatenate top-K chunk texts into one string with `max_context_chars` (default 6000) so context + query + system prompt fit in GROQ’s window.

## Input

- **Phase 3** Chroma DB at `phase3_vectorstore/chroma_db/` (default). Run Phase 3 first so the collection exists.

## Output

- **Retrieved context:** Ranked list of chunks `[{ "text", "metadata" }, ...]` and a single **context** string to pass to the LLM (Phase 5).

## Dependencies

Phase 4 uses Phase 3 (Chroma + sentence-transformers). Install Phase 3 deps:

```bash
pip install -r phase3_vectorstore/requirements.txt
```

## Usage

### From code

```python
from phase4_retrieval import retrieve_context

result = retrieve_context("What is the 5Y return of ICICI Prudential Value Fund?")
print(result["context"])   # string for LLM
print(result["chunks"])    # list of { text, metadata }
print(result["distances"]) # similarity distances
```

With filters:

```python
result = retrieve_context(
    "Equity funds with high returns",
    top_k=5,
    category="Equity",
    risk="Very High",
)
```

### CLI

From project root:

```bash
# Default: 7 chunks, print context
python -m phase4_retrieval.run "What is the NAV of ICICI Value Fund?"

# Custom top-k and max context length
python -m phase4_retrieval.run "Best equity funds" --top-k 5 --max-context-chars 4000

# Filter by category/risk
python -m phase4_retrieval.run "High return funds" --category Equity --risk "Very High"

# Output as JSON
python -m phase4_retrieval.run "Value fund returns" --json
```

## Tests

```bash
python -m pytest phase4_retrieval/tests/test_phase4.py -v
```

Preprocess and context-assembly tests run without Phase 3. Retrieval tests are skipped if Chroma or sentence-transformers are unavailable or the Chroma DB is missing.

## Folder structure

```
phase4_retrieval/
├── __init__.py
├── config.py       # TOP_K, MAX_CONTEXT_CHARS, Chroma path, abbreviations
├── preprocess.py   # preprocess_query()
├── retriever.py    # retrieve() — embed, Chroma query, optional filters
├── context.py      # assemble_context()
├── pipeline.py     # retrieve_context()
├── run.py          # CLI
├── requirements.txt
├── README.md
└── tests/
    ├── __init__.py
    └── test_phase4.py
```

## Phase 5

Phase 5 (GROQ LLM) should call `retrieve_context(query)` to get `context`, then build the user message as:  
`Context: {context}\n\nQuestion: {user_query}` and call GROQ with the system prompt from the architecture.
