# Phase 5: LLM Integration (GROQ)

Calls GROQ with context from Phase 4 to generate answers. Includes guardrails: **do not answer personal questions** and **do not store personal data**.

## Setup

1. Get an API key from [Groq Console](https://console.groq.com).
2. Set `GROQ_API_KEY` in the environment.
3. `pip install groq`

## Usage

```python
from phase5_llm import answer_query

result = answer_query("What is the 5Y return of ICICI Prudential Value Fund?")
# result["answer"], result["sources"], result["refused_personal"]
```

## Guardrails

- **Personal queries** (e.g. "my name", "store my email", "my income") are detected and refused with a standard message. They are not sent to the LLM and no personal data is stored.
- **No personal data** is logged or stored in this phase.

## Config

- `config.py`: `SYSTEM_PROMPT`, `PERSONAL_QUERY_REFUSAL`, `DEFAULT_MODEL`, `MAX_TOKENS`, `TEMPERATURE`.
