"""Tests for deterministic chatbot what-if intent parsing."""

import pytest

from app.genai.chatbot import detect_whatif_intent


@pytest.mark.parametrize(
    ("message", "expected", "is_delta"),
    [
        ("What if I invest ₹10,000 per month?", 10_000, False),
        ("What if I increase my investment by 5k?", 5_000, True),
        ("What if I save 2 lakh more?", 200_000, True),
        ("What if my target corpus is 1 crore?", 10_000_000, False),
        ("If I increase my risk and invest 1000?", 1_000, False),
    ],
)
def test_whatif_amounts_and_units(message, expected, is_delta):
    intent = detect_whatif_intent(message)
    assert intent is not None
    assert intent["value"] == expected
    assert intent["is_delta"] is is_delta


def test_unrelated_letter_k_does_not_multiply_amount():
    intent = detect_whatif_intent("What if I increase risk and invest 74?")
    assert intent["value"] == 74


def test_regular_question_is_not_a_whatif():
    assert detect_whatif_intent("Explain this plan") is None
