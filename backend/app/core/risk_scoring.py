"""Deterministic risk questionnaire, scoring, and classification.

Callers submit a mapping of stable question IDs to stable answer IDs. Numeric
weights are resolved only inside this module so clients cannot accidentally
couple themselves to scoring internals.
"""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class AnswerOption:
    """A selectable questionnaire answer and its deterministic weight."""

    id: str
    label: str
    weight: int


@dataclass(frozen=True, slots=True)
class RiskQuestion:
    """A risk-assessment question with five ordered answer options."""

    id: str
    text: str
    options: tuple[AnswerOption, ...]


RISK_QUESTIONNAIRE: tuple[RiskQuestion, ...] = (
    RiskQuestion(
        id="investment_experience",
        text="How much investment experience do you have?",
        options=(
            AnswerOption("none", "None", 0),
            AnswerOption("basic", "Very limited experience", 1),
            AnswerOption("some", "Some experience", 2),
            AnswerOption("experienced", "Several years of experience", 3),
            AnswerOption("extensive", "Extensive experience", 4),
        ),
    ),
    RiskQuestion(
        id="market_drop_reaction",
        text="What would you most likely do if your portfolio fell by 20%?",
        options=(
            AnswerOption("sell_all", "Sell all investments", 0),
            AnswerOption("sell_some", "Sell part of the portfolio", 1),
            AnswerOption("hold", "Hold and make no changes", 2),
            AnswerOption("wait_then_buy", "Wait, then consider buying", 3),
            AnswerOption("buy_more", "Invest more at lower prices", 4),
        ),
    ),
    RiskQuestion(
        id="income_stability",
        text="How stable is your regular income?",
        options=(
            AnswerOption("highly_unstable", "Highly unstable", 0),
            AnswerOption("variable", "Variable", 1),
            AnswerOption("mostly_stable", "Mostly stable", 2),
            AnswerOption("stable", "Stable", 3),
            AnswerOption("very_stable", "Very stable", 4),
        ),
    ),
    RiskQuestion(
        id="investment_time_horizon",
        text="How long can you keep this money invested?",
        options=(
            AnswerOption("under_1_year", "Less than 1 year", 0),
            AnswerOption("1_to_3_years", "1 to 3 years", 1),
            AnswerOption("3_to_5_years", "3 to 5 years", 2),
            AnswerOption("5_to_10_years", "5 to 10 years", 3),
            AnswerOption("over_10_years", "More than 10 years", 4),
        ),
    ),
    RiskQuestion(
        id="primary_goal",
        text="What is your primary objective for this investment?",
        options=(
            AnswerOption("capital_preservation", "Preserve capital", 0),
            AnswerOption("income", "Generate regular income", 1),
            AnswerOption("balanced", "Balance income and growth", 2),
            AnswerOption("long_term_growth", "Pursue long-term growth", 3),
            AnswerOption("aggressive_growth", "Pursue aggressive growth", 4),
        ),
    ),
    RiskQuestion(
        id="volatility_comfort",
        text="How comfortable are you with changes in investment value?",
        options=(
            AnswerOption("none", "Not comfortable", 0),
            AnswerOption("low", "Comfortable with small changes", 1),
            AnswerOption("moderate", "Comfortable with moderate changes", 2),
            AnswerOption("high", "Comfortable with large changes", 3),
            AnswerOption("very_high", "Comfortable with very large changes", 4),
        ),
    ),
    RiskQuestion(
        id="investment_knowledge",
        text="How would you describe your investment knowledge?",
        options=(
            AnswerOption("none", "No knowledge", 0),
            AnswerOption("basic", "Basic knowledge", 1),
            AnswerOption("intermediate", "Intermediate knowledge", 2),
            AnswerOption("strong", "Strong knowledge", 3),
            AnswerOption("advanced", "Advanced knowledge", 4),
        ),
    ),
    RiskQuestion(
        id="emergency_fund_coverage",
        text=(
            "How many months of essential expenses could your emergency savings "
            "cover without selling investments?"
        ),
        options=(
            AnswerOption("under_1_month", "Less than 1 month", 0),
            AnswerOption("1_to_3_months", "1 to under 3 months", 1),
            AnswerOption("3_to_6_months", "3 to under 6 months", 2),
            AnswerOption("6_to_12_months", "6 to 12 months", 3),
            AnswerOption("over_12_months", "More than 12 months", 4),
        ),
    ),
    RiskQuestion(
        id="debt_payment_pressure",
        text="How do your current debt payments affect your monthly finances?",
        options=(
            AnswerOption(
                "severe",
                "Payments make essential expenses difficult to meet",
                0,
            ),
            AnswerOption(
                "high",
                "Payments significantly limit saving and flexibility",
                1,
            ),
            AnswerOption(
                "manageable",
                "Payments are manageable with limited flexibility",
                2,
            ),
            AnswerOption(
                "low",
                "Payments are comfortably manageable",
                3,
            ),
            AnswerOption(
                "none_or_minimal",
                "I have no debt payments or only minimal payments",
                4,
            ),
        ),
    ),
    RiskQuestion(
        id="loss_capacity",
        text=(
            "If this investment lost 20% and took several years to recover, "
            "how would that affect your essential expenses and financial goals?"
        ),
        options=(
            AnswerOption(
                "major_disruption",
                "It would prevent me from meeting essential commitments",
                0,
            ),
            AnswerOption(
                "significant_adjustments",
                "It would require significant financial adjustments",
                1,
            ),
            AnswerOption(
                "some_adjustments",
                "It would require some non-essential adjustments",
                2,
            ),
            AnswerOption(
                "minor_impact",
                "It would have only a minor effect on my plans",
                3,
            ),
            AnswerOption(
                "no_material_impact",
                "It would not materially affect essential expenses or goals",
                4,
            ),
        ),
    ),
)


_ANSWER_WEIGHTS: Mapping[str, Mapping[str, int]] = MappingProxyType(
    {
        question.id: MappingProxyType(
            {option.id: option.weight for option in question.options}
        )
        for question in RISK_QUESTIONNAIRE
    }
)
_MAX_RAW_SCORE = len(RISK_QUESTIONNAIRE) * 4


def calculate_risk_score(answers: Mapping[str, str]) -> int:
    """Scale all questionnaire answers to an integer score from 0 to 100.

    Args:
        answers: Mapping of every question ID to one valid answer ID.

    Raises:
        TypeError: If *answers*, a question ID, or an answer ID has the wrong
            type.
        ValueError: If questions are missing or unexpected, or an answer ID is
            not valid for its question.
    """

    if not isinstance(answers, Mapping):
        raise TypeError("answers must be a mapping of question IDs to answer IDs")

    for question_id, answer_id in answers.items():
        if not isinstance(question_id, str):
            raise TypeError("every question ID must be a string")
        if not isinstance(answer_id, str):
            raise TypeError(f"answer for {question_id!r} must be a string ID")

    expected_ids = set(_ANSWER_WEIGHTS)
    received_ids = set(answers)
    missing_ids = expected_ids - received_ids
    unexpected_ids = received_ids - expected_ids

    if missing_ids:
        raise ValueError(
            "answers are missing required questions: " + ", ".join(sorted(missing_ids))
        )
    if unexpected_ids:
        raise ValueError(
            "answers contain unexpected questions: "
            + ", ".join(sorted(unexpected_ids))
        )

    raw_score = 0
    for question in RISK_QUESTIONNAIRE:
        answer_id = answers[question.id]
        try:
            raw_score += _ANSWER_WEIGHTS[question.id][answer_id]
        except KeyError as exc:
            raise ValueError(
                f"unknown answer ID {answer_id!r} for question {question.id!r}"
            ) from exc

    return round(raw_score / _MAX_RAW_SCORE * 100)


def classify_risk(risk_score: int) -> str:
    """Classify an integer score using the required inclusive thresholds."""

    if isinstance(risk_score, bool) or not isinstance(risk_score, Integral):
        raise TypeError("risk_score must be an integer")

    score = int(risk_score)
    if not 0 <= score <= 100:
        raise ValueError("risk_score must be between 0 and 100 inclusive")
    if score <= 33:
        return "Conservative"
    if score <= 66:
        return "Moderate"
    return "Aggressive"
