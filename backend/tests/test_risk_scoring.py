"""Tests for the deterministic risk questionnaire and score boundaries."""

from dataclasses import FrozenInstanceError

import pytest

from app.core.risk_scoring import (
    RISK_QUESTIONNAIRE,
    calculate_risk_score,
    classify_risk,
)


def _answers_at_weight(weight: int) -> dict[str, str]:
    return {
        question.id: next(
            option.id for option in question.options if option.weight == weight
        )
        for question in RISK_QUESTIONNAIRE
    }


def test_questionnaire_covers_exactly_seven_required_topics() -> None:
    assert tuple(question.id for question in RISK_QUESTIONNAIRE) == (
        "investment_experience",
        "market_drop_reaction",
        "income_stability",
        "investment_time_horizon",
        "primary_goal",
        "volatility_comfort",
        "investment_knowledge",
    )


def test_each_question_has_exactly_one_option_for_every_weight() -> None:
    for question in RISK_QUESTIONNAIRE:
        assert sorted(option.weight for option in question.options) == [0, 1, 2, 3, 4]
        assert len({option.id for option in question.options}) == 5


def test_questionnaire_records_are_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        RISK_QUESTIONNAIRE[0].text = "Changed"  # type: ignore[misc]


def test_all_lowest_risk_answers_score_zero() -> None:
    assert calculate_risk_score(_answers_at_weight(0)) == 0


def test_all_highest_risk_answers_score_one_hundred() -> None:
    assert calculate_risk_score(_answers_at_weight(4)) == 100


def test_mixed_answers_are_scaled_to_integer_score() -> None:
    answers = _answers_at_weight(2)
    answers["investment_experience"] = "none"
    answers["market_drop_reaction"] = "buy_more"
    score = calculate_risk_score(answers)
    assert score == 50
    assert isinstance(score, int)


def test_answer_dictionary_order_does_not_change_score() -> None:
    answers = _answers_at_weight(3)
    reversed_answers = dict(reversed(tuple(answers.items())))
    assert calculate_risk_score(answers) == calculate_risk_score(reversed_answers)


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0, "Conservative"),
        (33, "Conservative"),
        (34, "Moderate"),
        (66, "Moderate"),
        (67, "Aggressive"),
        (100, "Aggressive"),
    ],
)
def test_classify_risk_exact_boundaries(score: int, expected: str) -> None:
    assert classify_risk(score) == expected


def test_missing_question_is_rejected() -> None:
    answers = _answers_at_weight(2)
    answers.pop("primary_goal")
    with pytest.raises(ValueError, match="missing.*primary_goal"):
        calculate_risk_score(answers)


def test_unexpected_question_is_rejected() -> None:
    answers = _answers_at_weight(2)
    answers["favorite_colour"] = "blue"
    with pytest.raises(ValueError, match="unexpected.*favorite_colour"):
        calculate_risk_score(answers)


def test_unknown_answer_id_is_rejected() -> None:
    answers = _answers_at_weight(2)
    answers["primary_goal"] = "not_an_option"
    with pytest.raises(ValueError, match="unknown answer ID.*primary_goal"):
        calculate_risk_score(answers)


@pytest.mark.parametrize("invalid", [None, [], "answers"])
def test_answers_must_be_a_mapping(invalid: object) -> None:
    with pytest.raises(TypeError, match="answers must be a mapping"):
        calculate_risk_score(invalid)  # type: ignore[arg-type]


def test_answer_ids_must_be_strings() -> None:
    answers: dict[str, object] = _answers_at_weight(2)
    answers["primary_goal"] = 2
    with pytest.raises(TypeError, match="primary_goal"):
        calculate_risk_score(answers)  # type: ignore[arg-type]


@pytest.mark.parametrize("invalid", [-1, 101])
def test_classify_risk_rejects_out_of_range_scores(invalid: int) -> None:
    with pytest.raises(ValueError, match="between 0 and 100"):
        classify_risk(invalid)


@pytest.mark.parametrize("invalid", [True, 50.0, "50", None])
def test_classify_risk_requires_an_integer(invalid: object) -> None:
    with pytest.raises(TypeError, match="integer"):
        classify_risk(invalid)  # type: ignore[arg-type]
