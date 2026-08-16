"""Pure functions for goal projection and contribution calculations.

Annual return rates are expressed in percentage points: ``12.0`` means a
12 percent nominal annual return. Growth is compounded monthly and recurring
contributions are assumed to occur at the end of each month.
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


def _monthly_terms(annual_return_rate: Real, years: Real) -> tuple[float, int]:
    """Validate a rate and horizon and return monthly rate and whole months."""

    annual_rate = _finite_float(annual_return_rate, name="annual_return_rate")
    horizon_years = _finite_float(years, name="years")

    if annual_rate <= -100:
        raise ValueError("annual_return_rate must be greater than -100 percent")
    if horizon_years <= 0:
        raise ValueError("years must be greater than zero")

    raw_months = horizon_years * 12
    if not math.isfinite(raw_months):
        raise ValueError("years is too large to convert to monthly periods")
    months = round(raw_months)
    if not math.isclose(raw_months, months, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("years must represent a whole number of months")

    return annual_rate / 100 / 12, months


def _growth_factors(monthly_rate: float, months: int) -> tuple[float, float]:
    """Return lump-sum and ordinary-annuity growth factors."""

    if monthly_rate == 0:
        return 1.0, float(months)

    try:
        growth_exponent = months * math.log1p(monthly_rate)
        lump_sum_factor = math.exp(growth_exponent)
        annuity_factor = math.expm1(growth_exponent) / monthly_rate
    except (OverflowError, ValueError) as exc:
        raise ValueError("rate and horizon produce an unrepresentable result") from exc

    if not math.isfinite(lump_sum_factor) or not math.isfinite(annuity_factor):
        raise ValueError("rate and horizon produce an unrepresentable result")
    return lump_sum_factor, annuity_factor


def calculate_future_value(
    present_value: Real,
    monthly_contribution: Real,
    annual_return_rate: Real,
    years: Real,
) -> float:
    """Project a balance with monthly compounding and end-month deposits.

    Args:
        present_value: Amount invested at the start of the horizon.
        monthly_contribution: Amount deposited at the end of every month.
        annual_return_rate: Nominal annual return in percentage points.
        years: Positive horizon representing a whole number of months.

    Returns:
        The unrounded projected future value.
    """

    principal = _nonnegative_float(present_value, name="present_value")
    contribution = _nonnegative_float(
        monthly_contribution,
        name="monthly_contribution",
    )
    monthly_rate, months = _monthly_terms(annual_return_rate, years)
    lump_sum_factor, annuity_factor = _growth_factors(monthly_rate, months)

    future_value = principal * lump_sum_factor + contribution * annuity_factor
    if not math.isfinite(future_value):
        raise ValueError("inputs produce an unrepresentable future value")
    return future_value


def calculate_required_monthly_investment(
    target_amount: Real,
    current_amount: Real,
    annual_return_rate: Real,
    years: Real,
) -> float:
    """Solve for the end-of-month deposit required to reach a target.

    Returns zero when the current amount, grown without further deposits,
    already reaches the target. The returned value is not rounded.
    """

    target = _nonnegative_float(target_amount, name="target_amount")
    current = _nonnegative_float(current_amount, name="current_amount")
    monthly_rate, months = _monthly_terms(annual_return_rate, years)

    # The goal can be funded immediately, so no future deposit is required.
    # Horizon validation intentionally happens first so an invalid request does
    # not become valid merely because its current balance is high enough.
    if current >= target:
        return 0.0

    lump_sum_factor, annuity_factor = _growth_factors(monthly_rate, months)

    future_current_amount = current * lump_sum_factor
    if not math.isfinite(future_current_amount):
        raise ValueError("inputs produce an unrepresentable future current amount")
    remaining_target = target - future_current_amount
    if remaining_target <= 0:
        return 0.0

    required_contribution = remaining_target / annuity_factor
    if not math.isfinite(required_contribution):
        raise ValueError("inputs produce an unrepresentable monthly investment")
    return max(required_contribution, 0.0)


def calculate_goal_gap(projected_corpus: Real, target_amount: Real) -> float:
    """Return projected corpus minus target amount.

    A negative result is a shortfall; a positive result is a surplus.
    """

    projected = _nonnegative_float(projected_corpus, name="projected_corpus")
    target = _nonnegative_float(target_amount, name="target_amount")
    return projected - target
