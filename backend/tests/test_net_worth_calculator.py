"""Tests for basic financial-position calculations."""

import math
import sys

import pytest

from app.core.net_worth_calculator import (
    calculate_debt_to_income_ratio,
    calculate_monthly_surplus,
    calculate_net_worth,
    calculate_savings_rate,
)


@pytest.mark.parametrize(
    ("assets", "liabilities", "expected"),
    [(500_000, 125_000, 375_000.0), (50_000, 80_000, -30_000.0), (0, 0, 0.0)],
)
def test_calculate_net_worth(
    assets: float,
    liabilities: float,
    expected: float,
) -> None:
    assert calculate_net_worth(assets, liabilities) == expected


@pytest.mark.parametrize(
    ("income", "expenses", "expected"),
    [(100_000, 65_000, 35_000.0), (40_000, 50_000, -10_000.0), (0, 0, 0.0)],
)
def test_calculate_monthly_surplus(
    income: float,
    expenses: float,
    expected: float,
) -> None:
    assert calculate_monthly_surplus(income, expenses) == expected


def test_calculate_debt_to_income_ratio_returns_decimal_ratio() -> None:
    assert calculate_debt_to_income_ratio(150_000, 50_000) == pytest.approx(3.0)


def test_calculate_debt_to_income_ratio_handles_two_zero_values() -> None:
    assert calculate_debt_to_income_ratio(0, 0) == 0.0


def test_calculate_debt_to_income_ratio_rejects_positive_debt_with_zero_income() -> None:
    with pytest.raises(ValueError, match="monthly_income"):
        calculate_debt_to_income_ratio(10_000, 0)


@pytest.mark.parametrize(
    ("surplus", "income", "expected"),
    [(20_000, 100_000, 0.2), (0, 100_000, 0.0), (-5_000, 50_000, -0.1)],
)
def test_calculate_savings_rate(
    surplus: float,
    income: float,
    expected: float,
) -> None:
    assert calculate_savings_rate(surplus, income) == pytest.approx(expected)


def test_calculate_savings_rate_handles_two_zero_values() -> None:
    assert calculate_savings_rate(0, 0) == 0.0


def test_calculate_savings_rate_rejects_nonzero_surplus_with_zero_income() -> None:
    with pytest.raises(ValueError, match="monthly_income"):
        calculate_savings_rate(1, 0)


@pytest.mark.parametrize(
    ("function", "arguments"),
    [
        (calculate_net_worth, (-1, 0)),
        (calculate_net_worth, (0, -1)),
        (calculate_monthly_surplus, (-1, 0)),
        (calculate_monthly_surplus, (0, -1)),
        (calculate_debt_to_income_ratio, (-1, 1)),
        (calculate_savings_rate, (0, -1)),
    ],
)
def test_disallowed_negative_inputs_raise_value_error(function, arguments) -> None:
    with pytest.raises(ValueError):
        function(*arguments)


@pytest.mark.parametrize("invalid", [True, "100", None])
def test_non_numeric_values_raise_type_error(invalid: object) -> None:
    with pytest.raises(TypeError):
        calculate_net_worth(invalid, 0)  # type: ignore[arg-type]


@pytest.mark.parametrize("invalid", [math.nan, math.inf, -math.inf])
def test_non_finite_values_raise_value_error(invalid: float) -> None:
    with pytest.raises(ValueError):
        calculate_monthly_surplus(invalid, 0)


def test_unrepresentable_ratios_are_rejected() -> None:
    smallest_positive_float = float.fromhex("0x0.0000000000001p-1022")
    with pytest.raises(ValueError, match="unrepresentable"):
        calculate_debt_to_income_ratio(sys.float_info.max, smallest_positive_float)
    with pytest.raises(ValueError, match="unrepresentable"):
        calculate_savings_rate(sys.float_info.max, smallest_positive_float)


def test_integer_too_large_for_float_is_rejected_cleanly() -> None:
    with pytest.raises(ValueError, match="supported numeric range"):
        calculate_net_worth(10**10_000, 0)
