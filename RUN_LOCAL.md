# Run the RAG Chatbot Locally

End-to-end steps to run and test the ICICI Prudential Mutual Fund chatbot on your machine.

## 1. Create `.env` with your GROQ API key

```bash
# Windows (PowerShell)
copy .env.example .env

# Linux / Mac
cp .env.example .env
```

Open `.env` and replace `paste_your_groq_api_key_here` with your key from [Groq Console](https://console.groq.com):

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
```

Do not commit `.env`; it is in `.gitignore` and for local use only.

## 2. Install dependencies

From the project root (`Mutual Funds-RAG`):

```bash
pip install -r requirements.txt
```

First time only: install Playwright browser for the scraper:

```bash
playwright install chromium
```

## 3. Refresh data (first time or weekly)

This runs Phase 1 (scrape) → Phase 2 (clean & chunk) → Phase 3 (embed & index) → clears the chat cache:

```bash
python run_local.py --refresh
```

Or run the refresh pipeline only:

```bash
python -m phase7_operations.refresh_pipeline
```

## 4. Start the chat UI

```bash
python run_local.py
```

The Streamlit app opens at **http://localhost:8501**. You can ask questions about ICICI Prudential funds (NAV, returns, expense ratio, etc.).

## 5. Optional: check pipeline status

```bash
python run_local.py --check
```

Shows whether Phase 1–3 outputs exist and the last refresh time.

## Quick test (no refresh)

If you already ran `--refresh` once:

```bash
python run_local.py
```

Then in the browser try:

- "What is the NAV of ICICI Prudential Value Fund?"
- "List equity funds with high 5Y returns"
- "What is the minimum investment for Large Cap fund?"

## Phase overview

| Phase | What it does |
|-------|----------------|
| 1 | Scrapes Groww AMC page → JSON |
| 2 | Cleans data, builds RAG chunks → CSV + rag_chunks.json |
| 3 | Embeds chunks, builds Chroma index |
| 4 | Retrieves relevant chunks for each query |
| 5 | GROQ LLM turns context + query into an answer |
| 6 | Streamlit UI + FAQ cache |
| 7 | Refresh pipeline (1→2→3) + cache clear; run weekly or manually |

All phases are integrated when you run `run_local.py` (refresh optional, then Streamlit).
