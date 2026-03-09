# Phase-wise Architecture: RAG Chatbot for Mutual Fund Queries

## Overview

A Retrieval-Augmented Generation (RAG) chatbot that answers mutual fund queries using scraped data from Groww (ICICI Prudential Mutual Fund) and GROQ LLM for response generation. Users interact via a **web-based UI**. The **scraper runs weekly** to refresh fund data.

**Data Source:** https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds  
**LLM:** GROQ  
**Scraper schedule:** Weekly  
**Interface:** Web-based chat UI

---

## Phase 1: Data Acquisition & Scraping

### 1.1 Scraper Design

| Component | Description |
|-----------|-------------|
| **Target URL** | Groww ICICI Prudential Mutual Fund AMC page |
| **Method** | Web scraper (e.g., BeautifulSoup, Playwright/Selenium for JS-rendered content if needed) |
| **Rate limiting** | Respect robots.txt; add delays between requests to avoid blocking |
| **Error handling** | Retry logic, fallback for partial failures, logging failed pages |

### 1.2 Data Fields to Capture

| Field | Source (e.g., table column / section) | Notes |
|-------|--------------------------------------|--------|
| **Fund Name** | List/table – Fund Name column | Include plan type (Direct Growth, etc.) if present |
| **Category** | Category column | Equity, Hybrid, Debt, etc. |
| **Risk** | Risk column | Very High, Moderate, Low, etc. |
| **NAV** | NAV column | Current NAV value |
| **Expense Ratio** | Expense Ratio column | Percentage |
| **1Y Returns** | 1Y Returns column | Percentage |
| **5Y Returns** | 5Y Returns column | Percentage |
| **10Y Returns** | 10Y Returns column | Percentage (handle "--" / N/A) |
| **Exit Load** | Exit Load column | Text description |
| **Min Investment Amount** | From “Let's have a closer look” fund-wise sections | Lump sum minimum (₹) |
| **AUM** | Fund Size column / fund detail sections | In Cr (₹) |

### 1.3 Schedule

| Item | Description |
|------|-------------|
| **Frequency** | **Weekly** (scheduled run) |
| **Trigger** | Cron/scheduler (e.g., every Sunday 02:00) or workflow orchestrator (e.g., Apache Airflow, Prefect) |
| **Rationale** | NAV and returns change periodically; weekly refresh balances data freshness with scraper load and Groww politeness |

### 1.4 Output of Phase 1

- **Raw scraped payload:** JSON/CSV per fund or single JSON array of all funds.
- **Metadata:** Scrape timestamp, source URL, schema version for reproducibility.

---

## Phase 2: Data Processing & Enrichment

### 2.1 Cleaning & Normalization

| Step | Action |
|------|--------|
| **Missing values** | Standardize "--", "N/A", empty cells (e.g., null or "Not available") |
| **Numbers** | Parse NAV, returns, expense ratio, AUM; handle comma/thousand separators and "Cr" suffix |
| **Text** | Normalize category and risk labels; trim whitespace |
| **Exit load** | Keep as text or parse into structured fields (e.g., percentage, holding period) if needed for retrieval |

### 2.2 Enrichment for RAG

- **Synthetic Q&A pairs (optional):** Generate likely user questions per fund (e.g., "What is the 5Y return of ICICI Prudential Value Fund?") for better retrieval.
- **Unified text chunks:** Create readable paragraphs per fund combining: Fund Name, Category, Risk, NAV, Expense Ratio, 1Y/5Y/10Y returns, Exit Load, Min Investment, AUM so that both keyword and semantic search work well.

### 2.3 Chunking Strategy

| Strategy | Use case |
|----------|----------|
| **One chunk per fund** | Small number of funds; each chunk = one fund’s full summary |
| **Fixed-size with overlap** | If you add long-form content (e.g., AMC description) later |
| **Hybrid** | Fund table row as primary chunk + optional chunks for “Key information” / “How to invest” sections |

### 2.4 Output of Phase 2

- **Structured dataset:** Clean table (CSV/Parquet/DB) with schema aligned to captured fields.
- **RAG-ready documents:** List of chunks (e.g., list of dicts with `text`, `metadata` such as fund_name, category, risk).

---

## Phase 3: Embedding & Vector Store

### 3.1 Embedding Model

| Decision | Options |
|----------|---------|
| **Model** | Open-source sentence embeddings (e.g., sentence-transformers, GROQ-compatible or same ecosystem) or API-based (OpenAI, Cohere, etc.) |
| **Input** | Each RAG chunk (fund summary text + key metadata concatenated or in separate fields) |
| **Output** | Vector per chunk stored in vector DB |

### 3.2 Vector Database

| Component | Description |
|-----------|-------------|
| **Choice** | Chroma, FAISS, Pinecone, Weaviate, Qdrant, or pgvector (if already using Postgres) |
| **Index** | Dense vector index; optional metadata filters (e.g., category, risk) for filtered retrieval |
| **Metadata stored** | fund_name, category, risk, nav, returns, min_investment, aum, source_url, scrape_date |

### 3.3 Indexing Pipeline

1. Load processed chunks from Phase 2.
2. Generate embeddings in batches (with rate limits if using API).
3. Upsert vectors + metadata into vector store.
4. Persist index and version it (e.g., linked to scrape date).

### 3.4 Output of Phase 3

- **Vector store:** Populated index queryable by vector similarity and (if supported) metadata filters.

---

## Phase 4: Retrieval Layer

### 4.1 Query Flow

```
User Query → Query preprocessing → Embedding → Vector search (+ optional filter) → Top-K chunks
```

### 4.2 Retrieval Design

| Aspect | Design |
|--------|--------|
| **Query preprocessing** | Normalize text, expand abbreviations (e.g., "1Y" → "1 year return"), spell-check if needed |
| **Embedding** | Same model as indexing; embed the user question |
| **Search** | Similarity search (cosine / dot product); return top-K (e.g., K=5–10) chunks |
| **Filtering** | Optional: filter by category, risk, or fund name from query/NER before vector search |
| **Reranking (optional)** | Cross-encoder or LLM-based reranker to improve relevance of top-K |

### 4.3 Context Assembly

- Concatenate top-K chunk texts (and key metadata) into a single “context” string.
- Enforce max context length so that context + user query + system prompt fit within GROQ’s context window.

### 4.4 Output of Phase 4

- **Retrieved context:** Ranked list of chunks and the assembled context string for the LLM.

---

## Phase 5: LLM Integration (GROQ)

### 5.1 GROQ Setup

| Item | Description |
|------|-------------|
| **API** | GROQ API for inference (low latency) |
| **Model** | Use a GROQ-available model (e.g., Llama, Mixtral) suitable for Q&A |
| **Config** | Set max_tokens, temperature (e.g., 0.2–0.5 for factual answers), stop sequences if needed |

### 5.2 Prompt Design

| Part | Content |
|------|--------|
| **System prompt** | Role: “You are a mutual fund assistant. Answer only from the provided context. If the answer is not in the context, say so. Cite fund names and metrics when relevant.” |
| **User message** | “Context: {retrieved_context}\n\nQuestion: {user_query}” (or structured with context in a separate block) |
| **Output** | Plain text answer; optionally enforce JSON for structured replies (e.g., comparison table) |

### 5.3 Response Generation Flow

1. Receive user query.
2. Get retrieved context from Phase 4.
3. Build messages (system + user with context + question).
4. Call GROQ API; parse response.
5. Optional: post-process (format numbers, add disclaimers, citations).

### 5.4 Output of Phase 5

- **Final answer:** Text (or structured) response to the user.

---

## Phase 6: Web-Based Chat UI & Orchestration

### 6.1 Interface: Web-Based UI

| Component | Description |
|-----------|-------------|
| **Primary interface** | **Web-based UI** for all user queries (no CLI as primary) |
| **Front-end** | Single-page app (e.g., React, Next.js, Vue) or rapid UI (Streamlit, Gradio) with chat layout |
| **Back-end** | REST API (FastAPI/Flask): POST `/query` or `/chat` with JSON body; returns answer + optional sources/citations |
| **Streaming** | If GROQ supports streaming, stream tokens to the web client for responsive, typing-style UX |
| **Features** | Input box, send button, message history in session, clear conversation, optional “Data as on &lt;date&gt;” banner |

### 6.2 Orchestration (RAG Pipeline)

```
User Input (Web UI) → Retrieval (Phase 4) → Context + Query → GROQ (Phase 5) → Response → User
```

- **State:** Optional conversation history (e.g., last N turns in session) for follow-up questions in the same browser session.
- **Sources:** Each answer shows a single source URL link (Groww ICICI Prudential MF page).

### 6.3 Observability & Safety

- **Logging:** Log queries, retrieved doc IDs, token usage, latency.
- **Guardrails:** Validate that answers are grounded in context.
- **Feedback:** Single source URL link shown per answer for citations.

### 6.5 Output of Phase 6

- **Web-based RAG chatbot:** Users interact via browser; full RAG path runs for each query; single source URL shown per answer.

---

## Phase 7: Operations & Maintenance

### 7.1 Data Refresh (Weekly)

| Task | Frequency | Action |
|------|-----------|--------|
| **Re-scrape** | **Weekly** (e.g., fixed day/time) | Re-run Phase 1; capture latest NAV, returns, AUM, new funds |
| **Re-process** | After each scrape | Phase 2: clean, chunk |
| **Re-index** | After new dataset | Phase 3: re-embed and upsert (or replace) vector store |

Scraper runs on a **weekly schedule**; the rest of the pipeline (process → index) runs in sequence after each successful scrape.

### 7.2 Monitoring

- Scraper success rate and parsing errors.
- Retrieval relevance (e.g., manual sample or user feedback).
- GROQ latency, error rate, and cost.
- Drift in query distribution to adjust prompts or chunking.

---

## High-Level Architecture Diagram (Conceptual)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RAG CHATBOT FOR MUTUAL FUNDS                       │
└─────────────────────────────────────────────────────────────────────────────┘

  PHASE 1                PHASE 2                 PHASE 3              PHASE 4
  ┌──────────┐          ┌──────────┐           ┌──────────┐         ┌──────────┐
  │  GROWW   │  scrape  │  Clean &  │  chunks  │ Embedding │ vectors │  Vector  │
  │  (URL)   │ ───────► │  Chunk    │ ───────► │  Model   │ ──────► │  Store   │
  └──────────┘          └──────────┘           └──────────┘         └────┬─────┘
       │                     │                       ▲                    │
       │                     │                       │                    │
       ▼                     ▼                       │                    │
  Raw HTML/JSON         RAG documents           (same model)              │
  (Fund table +         (per fund /              for query                │
   fund details)         enriched text)                │                    │
                                                      │                    │
  PHASE 6 (Web UI)            PHASE 5                  │                    │
  ┌──────────────┐            ┌──────────┐              │                    │
  │  Web UI      │  question  │  GROQ    │   context    │                    │
  │  (Browser)   │ ─────────► │  LLM     │ ◄────────────┴────────────────────┘
  └──────┬───────┘            └────┬─────┘   (retrieved chunks)
         │                         │
         └─────────────────────────┘
                     │
                     ▼
              answer + source URL → User

  SCRAPER: runs WEEKLY → Phase 1 → Phase 2 → Phase 3
```

---

## Summary: Deliverables by Phase

| Phase | Deliverable |
|-------|-------------|
| **1** | Scraper; raw data (Fund Name, Category, Risk, NAV, Expense Ratio, 1Y/5Y/10Y returns, Exit Load, Min Investment, AUM) |
| **2** | Clean, normalized dataset; RAG-ready chunks with metadata |
| **3** | Vector store populated with embeddings and metadata |
| **4** | Retrieval API: query → top-K chunks + assembled context |
| **5** | GROQ integration: context + query → generated answer |
| **6** | Web-based chat UI; REST API; single source URL per answer |
| **7** | Weekly scraper schedule; re-process & re-index; monitoring |

This document is implementation-agnostic and can be implemented in Python (e.g., LangChain, LlamaIndex, or custom pipelines) or another stack of your choice.
