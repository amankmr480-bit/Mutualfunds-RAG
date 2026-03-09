"""
Tests for Phase 6: orchestrator flow (no PII).
"""
import pytest

from phase6_chatbot.orchestrator import chat_turn


def test_chat_turn_refuses_personal():
    result = chat_turn("What is my name?")
    assert result.get("refused_personal") is True
    assert "personal" in (result.get("answer") or "").lower() or "only" in (result.get("answer") or "").lower()
