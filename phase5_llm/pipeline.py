"""
Phase 5 pipeline: guardrails → retrieve context (Phase 4) → GROQ → answer.
Does not store or log personal data.
"""
import logging
from typing import Any

from phase4_retrieval.pipeline import retrieve_context
from phase5_llm.groq_client import generate_answer
from phase5_llm.guardrails import get_refusal_message, is_personal_query

logger = logging.getLogger(__name__)


def answer_query(
    user_query: str,
    top_k: int = 7,
    use_retrieval: bool = True,
    **retrieve_kwargs: Any,
) -> dict[str, Any]:
    """
    Full RAG answer: reject personal questions; else retrieve context and call GROQ.
    Returns { "answer": str, "sources": list (chunk metadata), "from_cache": bool (caller can set), "refused_personal": bool }.
    No personal data is stored or logged.
    """
    if not (user_query or "").strip():
        return {
            "answer": "Please ask a question about ICICI Prudential mutual funds.",
            "sources": [],
            "from_cache": False,
            "refused_personal": False,
            "no_data_found": False,
        }
    if is_personal_query(user_query):
        logger.info("Personal query refused (no data stored)")
        return {
            "answer": get_refusal_message(),
            "sources": [],
            "from_cache": False,
            "refused_personal": True,
            "no_data_found": False,
        }
    if not use_retrieval:
        return {
            "answer": "Retrieval is disabled. Enable it to get answers from fund data.",
            "sources": [],
            "from_cache": False,
            "refused_personal": False,
            "no_data_found": False,
        }
    try:
        ret = retrieve_context(user_query, top_k=top_k, **retrieve_kwargs)
    except Exception as e:
        logger.warning("Retrieval failed, trying JSON fallback: %s", e)
        try:
            from phase4_retrieval.context import assemble_context
            from phase4_retrieval.retriever import retrieve_from_json

            chunks, _ = retrieve_from_json(user_query, top_k=top_k)
            context = assemble_context(chunks)
            ret = {"chunks": chunks, "context": context, "distances": []}
        except Exception as e2:
            logger.exception("JSON fallback also failed: %s", e2)
            err_msg = str(e2).strip()[:200]
            return {
                "answer": "Sorry, I couldn't search the fund data. Please try again."
                + (f" (Error: {err_msg})" if err_msg else ""),
                "sources": [],
                "from_cache": False,
                "refused_personal": False,
                "no_data_found": True,
            }
    context = ret.get("context") or ""
    chunks = ret.get("chunks") or []
    if not context.strip():
        return {
            "answer": "Don't have relevant information. For more funds detail visit https://www.icicipruamc.com/home",
            "sources": [],
            "from_cache": False,
            "refused_personal": False,
            "no_data_found": True,
        }
    try:
        answer = generate_answer(context=context, user_query=user_query)
    except ValueError as e:
        msg = str(e)
        if "GROQ_API_KEY" in msg:
            return {
                "answer": "GROQ API key is missing or invalid. Please add GROQ_API_KEY to the .env file in the project root (see .env.example).",
                "sources": [],
                "from_cache": False,
                "refused_personal": False,
                "no_data_found": False,
            }
        logger.exception("GROQ failed: %s", e)
        return {"answer": msg[:500], "sources": [], "from_cache": False, "refused_personal": False, "no_data_found": False}
    except Exception as e:
        logger.exception("GROQ failed: %s", e)
        err = str(e).strip()[:200]
        return {
            "answer": f"Could not generate an answer. ({err}). Check GROQ_API_KEY in .env and try again.",
            "sources": [],
            "from_cache": False,
            "refused_personal": False,
            "no_data_found": False,
        }
    sources = [c.get("metadata") for c in chunks if c.get("metadata")]
    # Detect when LLM says it doesn't have the information; replace with standardized message
    no_data_phrases = ("don't have that information", "don't have relevant information", "not in the current data", "does not mention", "provided context does not")
    no_data_found = any(phrase.lower() in answer.lower() for phrase in no_data_phrases)
    if no_data_found:
        answer = "Don't have relevant information. For more funds detail visit https://www.icicipruamc.com/home"
    return {
        "answer": answer,
        "sources": sources,
        "from_cache": False,
        "refused_personal": False,
        "no_data_found": no_data_found,
    }
