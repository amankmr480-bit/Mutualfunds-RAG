"""
Tests for Phase 5: guardrails (personal query detection), prompts.
"""
import pytest

from phase5_llm.guardrails import is_personal_query, get_refusal_message
from phase5_llm.prompts import build_messages


def test_is_personal_query_detects_my_name():
    assert is_personal_query("What is my name?") is True


def test_is_personal_query_detects_store_my():
    assert is_personal_query("Store my email for later") is True


def test_is_personal_query_detects_income():
    assert is_personal_query("How much do I earn?") is True


def test_is_personal_query_allows_fund_questions():
    assert is_personal_query("What is the NAV of ICICI Value Fund?") is False
    assert is_personal_query("List equity funds with high returns") is False


def test_get_refusal_message_non_empty():
    msg = get_refusal_message()
    assert isinstance(msg, str)
    assert "personal" in msg.lower() or "only" in msg.lower()


def test_build_messages_has_system_and_user():
    msgs = build_messages("Context here", "What is NAV?")
    assert len(msgs) >= 2
    assert msgs[0]["role"] == "system"
    assert msgs[1]["role"] == "user"
    assert "Context here" in msgs[1]["content"]
    assert "What is NAV?" in msgs[1]["content"]
