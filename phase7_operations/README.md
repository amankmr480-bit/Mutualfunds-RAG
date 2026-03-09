# Phase 7: Operations & Maintenance

## Data refresh (weekly or manual)

Run the full pipeline to update fund data and re-index:

```bash
# From project root
python -m phase7_operations.refresh_pipeline
```

This runs:

1. **Phase 1** — Scrape Groww AMC page → `scraper/output/icici_prudential_funds.json`
2. **Phase 2** — Clean & chunk → `phase2_processing/output/rag_chunks.json`
3. **Phase 3** — Embed & index → `phase3_vectorstore/chroma_db/`
4. **Cache invalidation** — Clear Phase 6 FAQ cache

## Scheduling (weekly)

- **Windows:** Task Scheduler — run `python -m phase7_operations.refresh_pipeline` weekly.
- **Linux/Mac:** Cron — e.g. `0 2 * * 0 cd /path/to/project && python -m phase7_operations.refresh_pipeline`

## Monitoring

- `phase7_operations/logs/last_refresh.txt` — timestamp of last run
- `phase7_operations/logs/status.json` — success, last_step, error (if any)

Use `check_pipeline_ready()` from code to verify Phase 1–3 outputs exist before starting the chatbot.
