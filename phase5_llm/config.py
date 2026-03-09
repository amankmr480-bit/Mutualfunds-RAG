"""
Configuration for Phase 5: LLM Integration (GROQ).
Loads .env from project root so GROQ_API_KEY can be set in .env file.
"""
import os
from pathlib import Path

# Load .env from project root (parent of phase5_llm)
try:
    from dotenv import load_dotenv
    _root = Path(__file__).resolve().parent.parent
    load_dotenv(_root / ".env")
except ImportError:
    pass  # dotenv optional; use env vars only

# GROQ API key (from .env or GROQ_API_KEY environment variable); strip quotes/newlines
_raw = os.environ.get("GROQ_API_KEY", "").strip().strip('"').strip("'")
GROQ_API_KEY = _raw

# Model: try in order (GROQ may deprecate models)
DEFAULT_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODELS = ["llama-3.1-8b-instant", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"]

# Generation config
MAX_TOKENS = 1024
TEMPERATURE = 0.2  # Factual answers

# System prompt (mutual fund assistant; no personal questions; no personal data)
SYSTEM_PROMPT = """You are a mutual fund assistant for ICICI Prudential Mutual Funds. Your role is to answer questions ONLY about ICICI Prudential mutual fund schemes using the provided context.

Rules:
- Answer ONLY from the provided context. If the answer is not in the context, say exactly: "Don't have relevant information."
- Cite fund names and metrics (NAV, returns, expense ratio, AUM, etc.) when relevant.
- Do NOT answer personal questions (e.g. about the user's identity, income, investments, contact details, or any personal data). If asked a personal question, reply: "I can only answer questions about ICICI Prudential mutual funds. I don't handle personal questions or store any personal data."
- Do NOT store or request any personal data.
- Keep answers clear and concise. """

# Refusal message for personal queries (shown before calling LLM)
PERSONAL_QUERY_REFUSAL = "I can only answer questions about ICICI Prudential mutual funds. I don't handle personal questions or store any personal data."

