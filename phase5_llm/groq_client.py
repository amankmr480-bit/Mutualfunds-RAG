"""
Phase 5: GROQ API client — chat completion (no streaming by default).
"""
import logging
from typing import Any

from phase5_llm.config import (
    DEFAULT_MODEL,
    FALLBACK_MODELS,
    GROQ_API_KEY,
    MAX_TOKENS,
    TEMPERATURE,
)
from phase5_llm.prompts import build_messages

logger = logging.getLogger(__name__)


def generate_answer(
    context: str,
    user_query: str,
    model: str | None = None,
    max_tokens: int = MAX_TOKENS,
    temperature: float = TEMPERATURE,
) -> str:
    """
    Call GROQ chat completion with context + question. Returns answer text.
    Tries DEFAULT_MODEL first, then FALLBACK_MODELS on failure.
    """
    api_key = (GROQ_API_KEY or "").strip()
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Add it to the .env file in the project root (copy .env.example to .env)."
        )
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("Install groq: pip install groq")
    client = Groq(api_key=api_key)
    messages = build_messages(context, user_query)
    models_to_try = [model or DEFAULT_MODEL] + [m for m in FALLBACK_MODELS if m != (model or DEFAULT_MODEL)]
    last_error = None
    for m in models_to_try:
        try:
            response = client.chat.completions.create(
                messages=messages,
                model=m,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            if not response.choices:
                raise ValueError("GROQ returned no choices")
            text = (response.choices[0].message.content or "").strip()
            if text:
                return text
        except Exception as e:
            last_error = e
            logger.warning("GROQ model %s failed: %s", m, e)
            continue
    if last_error:
        raise last_error
    raise ValueError("GROQ returned an empty response")


def generate_answer_streaming(
    context: str,
    user_query: str,
    model: str | None = None,
    max_tokens: int = MAX_TOKENS,
    temperature: float = TEMPERATURE,
):
    """
    Stream GROQ completion chunks (generator of text deltas).
    For use in Streamlit streaming UI.
    """
    if not GROQ_API_KEY:
        raise ValueError("Set GROQ_API_KEY in the environment.")
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("Install groq: pip install groq")
    client = Groq(api_key=GROQ_API_KEY)
    messages = build_messages(context, user_query)
    stream = client.chat.completions.create(
        messages=messages,
        model=model or DEFAULT_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            yield delta
