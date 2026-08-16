"""Tests for deterministic three-plan generation."""

from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from app.core.goal_calculator import (
    calculate_future_value,
    calculate_required_monthly_investment,
)
from app.core.plan_generator import generate_plans


@pytest.fixture
def historical_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "asset_category": ["Equity", "Debt", "Gold", "Real_Estate", "Cash"],
            "avg_annual_return": [12.0, 7.0, 9.0, 8.0, 5.5],
            "volatility": [18.0, 4.0, 12.0, 8.0, 1.0],
        }
    )


@pytest.fixture
def customer_profile() -> dict[str, float]:
    return {"monthly_income": 100_000, "monthly_expenses": 60_000}


@pytest.fixture
def goal() -> dict[str, float]:
    return {
        "target_amount": 5_000_000,
        "current_amount": 200_000,
        "time_horizon_years": 5,
    }


def _round_half_up(value: float) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


def test_generate_plans_returns_three_plans_in_stable_order(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    plans = generate_plans(customer_profile, "Moderate", goal, historical_data)
    assert [plan["plan_name"] for plan in plans] == [
        "Conservative",
        "Balanced",
        "Growth",
    ]


def test_every_plan_has_exactly_the_required_keys(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    required_keys = {
        "plan_name",
        "allocation",
        "blended_expected_return",
        "projected_corpus",
        "gap_vs_target",
        "required_monthly_investment",
        "risk_level",
    }
    plans = generate_plans(customer_profile, "Conservative", goal, historical_data)
    assert all(set(plan) == required_keys for plan in plans)


def test_allocations_and_risk_levels_match_the_contract(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    plans = generate_plans(customer_profile, "Aggressive", goal, historical_data)
    assert plans[0]["allocation"] == {
        "Equity": 20,
        "Debt": 50,
        "Gold": 15,
        "Real_Estate": 10,
        "Cash": 5,
    }
    assert plans[1]["allocation"] == {
        "Equity": 50,
        "Debt": 25,
        "Gold": 15,
        "Real_Estate": 10,
        "Cash": 0,
    }
    assert plans[2]["allocation"] == {
        "Equity": 70,
        "Debt": 10,
        "Gold": 10,
        "Real_Estate": 10,
        "Cash": 0,
    }
    assert [sum(plan["allocation"].values()) for plan in plans] == [100, 100, 100]
    assert [plan["risk_level"] for plan in plans] == [
        "Conservative",
        "Moderate",
        "Aggressive",
    ]


def test_blended_returns_are_weighted_averages(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    plans = generate_plans(customer_profile, "Moderate", goal, historical_data)
    assert [plan["blended_expected_return"] for plan in plans] == [8.33, 9.9, 10.8]


def test_projection_uses_goal_balance_and_monthly_surplus(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    plan = generate_plans(customer_profile, "Moderate", goal, historical_data)[0]
    expected = calculate_future_value(200_000, 40_000, 8.325, 5)
    assert plan["projected_corpus"] == _round_half_up(expected)


def test_each_plan_uses_its_own_return_for_required_investment(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    plans = generate_plans(customer_profile, "Moderate", goal, historical_data)
    unrounded_returns = [8.325, 9.9, 10.8]
    expected = [
        _round_half_up(
            calculate_required_monthly_investment(5_000_000, 200_000, rate, 5)
        )
        for rate in unrounded_returns
    ]
    assert [plan["required_monthly_investment"] for plan in plans] == expected


def test_gap_is_negative_for_shortfall_and_positive_for_surplus(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    shortfall_goal = {**goal, "target_amount": 50_000_000}
    surplus_goal = {**goal, "target_amount": 100_000}
    shortfall_plans = generate_plans(
        customer_profile, "Moderate", shortfall_goal, historical_data
    )
    surplus_plans = generate_plans(
        customer_profile, "Moderate", surplus_goal, historical_data
    )
    assert all(plan["gap_vs_target"] < 0 for plan in shortfall_plans)
    assert all(plan["gap_vs_target"] > 0 for plan in surplus_plans)


def test_already_achieved_goal_requires_no_monthly_investment(
    customer_profile: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    achieved_goal = {
        "target_amount": 100_000,
        "current_amount": 100_000,
        "time_horizon_years": 1,
    }
    plans = generate_plans(
        customer_profile, "Conservative", achieved_goal, historical_data
    )
    assert all(plan["required_monthly_investment"] == 0.0 for plan in plans)


def test_zero_income_uses_zero_monthly_contribution(
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    profile = {"monthly_income": 0, "monthly_expenses": 0}
    plans = generate_plans(profile, "Conservative", goal, historical_data)
    expected = calculate_future_value(200_000, 0, 8.325, 5)
    assert plans[0]["projected_corpus"] == _round_half_up(expected)


def test_monthly_deficit_is_not_treated_as_a_withdrawal(
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    profile = {"monthly_income": 20_000, "monthly_expenses": 30_000}
    plans = generate_plans(profile, "Conservative", goal, historical_data)
    expected = calculate_future_value(200_000, 0, 8.325, 5)
    assert plans[0]["projected_corpus"] == _round_half_up(expected)


@pytest.mark.parametrize("horizon", [0, -1])
def test_nonpositive_goal_horizon_is_rejected(
    horizon: float,
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    invalid_goal = {**goal, "time_horizon_years": horizon}
    with pytest.raises(ValueError, match="years"):
        generate_plans(
            customer_profile, "Moderate", invalid_goal, historical_data
        )


@pytest.mark.parametrize(
    ("mapping_name", "missing_field"),
    [
        ("customer_profile", "monthly_income"),
        ("customer_profile", "monthly_expenses"),
        ("goal", "target_amount"),
        ("goal", "current_amount"),
        ("goal", "time_horizon_years"),
    ],
)
def test_missing_required_mapping_fields_are_rejected(
    mapping_name: str,
    missing_field: str,
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    profile_input = dict(customer_profile)
    goal_input = dict(goal)
    target = profile_input if mapping_name == "customer_profile" else goal_input
    target.pop(missing_field)
    with pytest.raises(ValueError, match=missing_field):
        generate_plans(profile_input, "Moderate", goal_input, historical_data)


@pytest.mark.parametrize("invalid", ["Balanced", "moderate", "", 2, None])
def test_invalid_customer_risk_category_is_rejected(
    invalid: object,
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    expected_error = TypeError if not isinstance(invalid, str) else ValueError
    with pytest.raises(expected_error):
        generate_plans(
            customer_profile,
            invalid,  # type: ignore[arg-type]
            goal,
            historical_data,
        )


def test_historical_data_must_be_a_dataframe(
    customer_profile: dict[str, float],
    goal: dict[str, float],
) -> None:
    with pytest.raises(TypeError, match="DataFrame"):
        generate_plans(customer_profile, "Moderate", goal, [])  # type: ignore[arg-type]


def test_missing_dataframe_column_is_rejected(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    invalid_data = historical_data.drop(columns="volatility")
    with pytest.raises(ValueError, match="volatility"):
        generate_plans(customer_profile, "Moderate", goal, invalid_data)


def test_duplicate_dataframe_column_is_rejected(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    invalid_data = pd.concat(
        [historical_data, historical_data[["volatility"]]],
        axis=1,
    )
    with pytest.raises(ValueError, match="duplicate columns.*volatility"):
        generate_plans(customer_profile, "Moderate", goal, invalid_data)


def test_missing_asset_category_is_rejected(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    invalid_data = historical_data[historical_data["asset_category"] != "Cash"]
    with pytest.raises(ValueError, match="missing asset categories.*Cash"):
        generate_plans(customer_profile, "Moderate", goal, invalid_data)


def test_duplicate_asset_category_is_rejected(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    invalid_data = pd.concat([historical_data, historical_data.iloc[[0]]])
    with pytest.raises(ValueError, match="duplicate.*Equity"):
        generate_plans(customer_profile, "Moderate", goal, invalid_data)


def test_unexpected_asset_category_is_rejected(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    extra_row = pd.DataFrame(
        [{"asset_category": "Crypto", "avg_annual_return": 20, "volatility": 50}]
    )
    invalid_data = pd.concat([historical_data, extra_row], ignore_index=True)
    with pytest.raises(ValueError, match="unexpected.*Crypto"):
        generate_plans(customer_profile, "Moderate", goal, invalid_data)


@pytest.mark.parametrize(
    ("column", "invalid", "error"),
    [
        ("avg_annual_return", "twelve", TypeError),
        ("avg_annual_return", float("nan"), ValueError),
        ("avg_annual_return", float("inf"), ValueError),
        ("avg_annual_return", -100, ValueError),
        ("volatility", "high", TypeError),
        ("volatility", float("nan"), ValueError),
        ("volatility", -1, ValueError),
    ],
)
def test_invalid_historical_numbers_are_rejected(
    column: str,
    invalid: object,
    error: type[Exception],
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    invalid_data = historical_data.copy()
    if isinstance(invalid, str):
        invalid_data[column] = invalid_data[column].astype(object)
    invalid_data.loc[0, column] = invalid
    with pytest.raises(error):
        generate_plans(customer_profile, "Moderate", goal, invalid_data)


def test_inputs_are_not_mutated(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    original_profile = deepcopy(customer_profile)
    original_goal = deepcopy(goal)
    original_data = historical_data.copy(deep=True)
    generate_plans(customer_profile, "Moderate", goal, historical_data)
    assert customer_profile == original_profile
    assert goal == original_goal
    assert_frame_equal(historical_data, original_data)


def test_returned_allocations_do_not_share_mutable_state(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    plans = generate_plans(customer_profile, "Moderate", goal, historical_data)
    plans[0]["allocation"]["Equity"] = 99
    fresh_plans = generate_plans(customer_profile, "Moderate", goal, historical_data)
    assert plans[1]["allocation"]["Equity"] == 50
    assert fresh_plans[0]["allocation"]["Equity"] == 20


def test_identical_inputs_produce_identical_outputs(
    customer_profile: dict[str, float],
    goal: dict[str, float],
    historical_data: pd.DataFrame,
) -> None:
    first = generate_plans(customer_profile, "Moderate", goal, historical_data)
    second = generate_plans(customer_profile, "Moderate", goal, historical_data)
    assert first == second
