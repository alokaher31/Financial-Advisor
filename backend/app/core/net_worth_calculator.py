"""Deterministic calculations for a customer's basic financial position.

Rates returned by this module are decimal ratios. For example, ``0.25``
represents 25 percent. Presentation layers are responsible for percentage
formatting.
"""

from __future__ import annotations

import math
from numbers import Real


def _finite_float(value: Real, *, name: str) -> float:
    """Return *value* as a finite float or raise a descriptive exception."""

    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")

    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} is outside the supported numeric range") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _nonnegative_float(value: Real, *, name: str) -> float:
    """Return *value* as a finite, nonnegative float."""

    result = _finite_float(value, name=name)
    if result < 0:
        raise ValueError(f"{name} must be greater than or equal to zero")
    return result


def calculate_net_worth(total_assets: Real, total_liabilities: Real) -> float:
    """Calculate assets minus liabilities.

    Args:
        total_assets: Total monetary value of assets. Must be nonnegative.
        total_liabilities: Total outstanding liabilities. Must be nonnegative.

    Returns:
        Net worth as a float. The result may be negative.
    """

    assets = _nonnegative_float(total_assets, name="total_assets")
    liabilities = _nonnegative_float(total_liabilities, name="total_liabilities")
    return assets - liabilities


def calculate_monthly_surplus(monthly_income: Real, monthly_expenses: Real) -> float:
    """Calculate monthly income minus monthly expenses.

    A negative result represents a monthly deficit and is intentionally not
    clamped to zero.
    """

    income = _nonnegative_float(monthly_income, name="monthly_income")
    expenses = _nonnegative_float(monthly_expenses, name="monthly_expenses")
    return income - expenses


def calculate_debt_to_income_ratio(
    total_liabilities: Real,
    monthly_income: Real,
) -> float:
    """Calculate total liabilities divided by annual gross income.

    Monthly debt-payment data is not collected by the application, so a
    conventional lending DTI cannot be calculated. Using annual income keeps
    the available debt-burden proxy dimensionally meaningful; the previous
    implementation divided total debt by a single month's income and inflated
    every result by a factor of twelve.

    Returns:
        A decimal ratio. If both values are zero, returns ``0.0``.

    Raises:
        ValueError: If income is zero while liabilities are positive.
    """

    liabilities = _nonnegative_float(total_liabilities, name="total_liabilities")
    income = _nonnegative_float(monthly_income, name="monthly_income")

    if income == 0:
        if liabilities == 0:
            return 0.0
        raise ValueError(
            "monthly_income must be greater than zero when total_liabilities "
            "is positive"
        )
    ratio = liabilities / (income * 12)
    if not math.isfinite(ratio):
        raise ValueError("inputs produce an unrepresentable debt-to-income ratio")
    return ratio


def calculate_savings_rate(monthly_surplus: Real, monthly_income: Real) -> float:
    """Calculate monthly surplus divided by monthly income.

    The surplus may be negative, in which case the returned decimal savings
    rate is also negative. If income and surplus are both zero, returns 0.0.
    """

    surplus = _finite_float(monthly_surplus, name="monthly_surplus")
    income = _nonnegative_float(monthly_income, name="monthly_income")

    if income == 0:
        if surplus == 0:
            return 0.0
        raise ValueError(
            "monthly_income must be greater than zero when monthly_surplus "
            "is nonzero"
        )
    rate = surplus / income
    if not math.isfinite(rate):
        raise ValueError("inputs produce an unrepresentable savings rate")
    return rate
