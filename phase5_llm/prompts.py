"""
Phase 5: Prompt building — system prompt and user message with context.
"""
from phase5_llm.config import SYSTEM_PROMPT


def build_messages(context: str, user_query: str) -> list[dict[str, str]]:
    """
    Build messages for GROQ chat completion.
    No personal data in prompts; only context (fund data) and the user's question.
    """
    user_content = f"Context:\n{context}\n\nQuestion: {user_query}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
