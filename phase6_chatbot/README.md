# Phase 6: Chat UI & Orchestration

Streamlit web UI for the ICICI Prudential Mutual Fund RAG chatbot, with query-answer cache and guardrails.

## Privacy

- **No personal questions answered.** Queries that ask for personal data, identity, or to store information are refused.
- **No personal data stored.** The cache stores only normalized question text and answer text. No user IDs, emails, or PII.

## Features

- **Streamlit UI:** Chat layout, message history in session, clear chat.
- **Cache:** Repeated or similar questions served from cache (faster).
- **Flow:** Personal check → cache lookup → on miss: Phase 4 retrieval + Phase 5 GROQ → cache set → response.

## Prerequisites

1. **Phase 3** Chroma DB populated (`python -m phase3_vectorstore.run`).
2. **GROQ API key:** Set `GROQ_API_KEY` in the environment.
3. Install deps: `pip install groq streamlit` and Phase 3 deps (sentence-transformers, chromadb).

## Run the app

From project root:

```bash
# Set your GROQ API key (get from https://console.groq.com)
set GROQ_API_KEY=your_key_here    # Windows
export GROQ_API_KEY=your_key_here # Linux/Mac

# Launch Streamlit (default: http://localhost:8501)
streamlit run phase6_chatbot/app.py
```

Or from the `phase6_chatbot` folder:

```bash
streamlit run app.py
```

## Folder structure

```
phase6_chatbot/
├── __init__.py
├── config.py       # Cache TTL, normalize_query_for_cache
├── cache.py        # QueryAnswerCache (no PII)
├── orchestrator.py # chat_turn: personal → cache → RAG
├── app.py          # Streamlit UI
├── requirements.txt
└── README.md
```
