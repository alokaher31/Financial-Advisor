"""Tests for deterministic goal calculations."""

import math
import sys

import pytest

from app.core.goal_calculator import (
    calculate_future_value,
    calculate_goal_gap,
    calculate_required_monthly_investment,
)


def _ordinary_annuity_future_value(
    present_value: float,
    monthly_contribution: float,
    annual_rate_pct: float,
    years: float,
) -> float:
    """Independent reference formula used only by the tests."""

    monthly_rate = annual_rate_pct / 100 / 12
    months = int(years * 12)
    return present_value * (1 + monthly_rate) ** months + monthly_contribution * (
        ((1 + monthly_rate) ** months - 1) / monthly_rate
    )


def test_calculate_future_value_with_positive_return() -> None:
    expected = _ordinary_annuity_future_value(100_000, 10_000, 12, 5)
    actual = calculate_future_value(100_000, 10_000, 12, 5)
    assert actual == pytest.approx(expected)


def test_calculate_future_value_with_zero_return() -> None:
    assert calculate_future_value(100_000, 10_000, 0, 2) == 340_000.0


def test_near_zero_return_is_numerically_stable() -> None:
    annual_rate = 1e-15
    projected = calculate_future_value(0, 1_000, annual_rate, 1)
    required = calculate_required_monthly_investment(
        12_000,
        0,
        annual_rate,
        1,
    )
    assert projected == pytest.approx(12_000, rel=1e-14)
    assert required == pytest.approx(1_000, rel=1e-14)


def test_calculate_future_value_supports_zero_principal_or_contribution() -> None:
    contributions_only = calculate_future_value(0, 5_000, 8, 3)
    principal_only = calculate_future_value(50_000, 0, 8, 3)
    assert contributions_only > 180_000
    assert principal_only > 50_000


def test_required_monthly_investment_reaches_target() -> None:
    required = calculate_required_monthly_investment(1_000_000, 100_000, 10, 5)
    projected = calculate_future_value(100_000, required, 10, 5)
    assert projected == pytest.approx(1_000_000)


def test_required_monthly_investment_with_zero_return() -> None:
    required = calculate_required_monthly_investment(340_000, 100_000, 0, 2)
    assert required == pytest.approx(10_000)


def test_required_monthly_investment_is_zero_if_current_amount_grows_to_target() -> None:
    assert calculate_required_monthly_investment(100_000, 100_000, 8, 1) == 0.0


def test_already_funded_goal_requires_zero_even_with_negative_return() -> None:
    assert calculate_required_monthly_investment(100_000, 120_000, -50, 10) == 0.0


def test_already_funded_goal_still_rejects_invalid_horizon() -> None:
    with pytest.raises(ValueError, match="years"):
        calculate_required_monthly_investment(100_000, 120_000, 5, 0)


@pytest.mark.parametrize(
    ("projected", "target", "expected"),
    [(80_000, 100_000, -20_000.0), (100_000, 100_000, 0.0), (120_000, 100_000, 20_000.0)],
)
def test_calculate_goal_gap(
    projected: float,
    target: float,
    expected: float,
) -> None:
    assert calculate_goal_gap(projected, target) == expected


@pytest.mark.parametrize("years", [0, -1])
def test_nonpositive_horizon_is_rejected(years: float) -> None:
    with pytest.raises(ValueError, match="years"):
        calculate_future_value(100, 10, 5, years)


def test_whole_month_fractional_horizon_is_supported() -> None:
    assert calculate_future_value(0, 1_000, 0, 0.5) == 6_000.0


def test_fractional_month_horizon_is_rejected() -> None:
    with pytest.raises(ValueError, match="whole number of months"):
        calculate_future_value(0, 1_000, 0, 0.1)


def test_rate_at_or_below_negative_one_hundred_percent_is_rejected() -> None:
    with pytest.raises(ValueError, match="greater than -100"):
        calculate_future_value(100, 10, -100, 1)


@pytest.mark.parametrize(
    ("function", "arguments"),
    [
        (calculate_future_value, (-1, 0, 5, 1)),
        (calculate_future_value, (0, -1, 5, 1)),
        (calculate_required_monthly_investment, (-1, 0, 5, 1)),
        (calculate_required_monthly_investment, (1, -1, 5, 1)),
        (calculate_goal_gap, (-1, 1)),
        (calculate_goal_gap, (1, -1)),
    ],
)
def test_negative_amounts_are_rejected(function, arguments) -> None:
    with pytest.raises(ValueError):
        function(*arguments)


@pytest.mark.parametrize("invalid", [True, "5", None])
def test_wrong_types_are_rejected(invalid: object) -> None:
    with pytest.raises(TypeError):
        calculate_future_value(100, 10, invalid, 1)  # type: ignore[arg-type]


@pytest.mark.parametrize("invalid", [math.nan, math.inf, -math.inf])
def test_non_finite_values_are_rejected(invalid: float) -> None:
    with pytest.raises(ValueError):
        calculate_required_monthly_investment(100, 0, invalid, 1)


def test_horizon_that_overflows_month_conversion_is_rejected() -> None:
    with pytest.raises(ValueError, match="too large"):
        calculate_future_value(100, 10, 5, sys.float_info.max)


def test_integer_too_large_for_float_is_rejected_cleanly() -> None:
    with pytest.raises(ValueError, match="supported numeric range"):
        calculate_future_value(10**10_000, 10, 5, 1)
