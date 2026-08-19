"""Generate three deterministic financial plans from preloaded return data.

This module performs calculations only. The historical DataFrame is injected
by the caller; no file, database, API, environment, or LLM access occurs here.
Average annual returns are expected in percentage points (for example, 12.0
means 12 percent).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext
from numbers import Real
from typing import Any

import pandas as pd

from .goal_calculator import (
    calculate_future_value,
    calculate_goal_gap,
    calculate_required_monthly_investment,
)
from .net_worth_calculator import calculate_monthly_surplus


@dataclass(frozen=True, slots=True)
class _PlanSpec:
    """Immutable internal definition of one plan template."""

    name: str
    risk_level: str
    allocation: tuple[tuple[str, int], ...]


_PLAN_SPECS: tuple[_PlanSpec, ...] = (
    _PlanSpec(
        name="Conservative",
        risk_level="Conservative",
        allocation=(
            ("Equity", 20),
            ("Debt", 50),
            ("Gold", 15),
            ("Real_Estate", 10),
            ("Cash", 5),
        ),
    ),
    _PlanSpec(
        name="Balanced",
        risk_level="Moderate",
        allocation=(
            ("Equity", 50),
            ("Debt", 25),
            ("Gold", 15),
            ("Real_Estate", 10),
            ("Cash", 0),
        ),
    ),
    _PlanSpec(
        name="Growth",
        risk_level="Aggressive",
        allocation=(
            ("Equity", 70),
            ("Debt", 10),
            ("Gold", 10),
            ("Real_Estate", 10),
            ("Cash", 0),
        ),
    ),
)

_ASSET_CATEGORIES = frozenset(
    asset for plan in _PLAN_SPECS for asset, _percentage in plan.allocation
)
_REQUIRED_DATA_COLUMNS = frozenset(
    {"asset_category", "avg_annual_return", "volatility"}
)
_VALID_RISK_CATEGORIES = frozenset({"Conservative", "Moderate", "Aggressive"})
_TWO_DECIMAL_PLACES = Decimal("0.01")


def _personalize_allocation(
    base_allocation: tuple[tuple[str, int], ...],
    *,
    risk_category: str,
    profile: Mapping[str, Any],
    goal: Mapping[str, Any],
    years: Real,
) -> tuple[tuple[str, int], ...]:
    """Tilt a plan template using inputs that materially affect risk capacity.

    Contribution and target amounts affect the corpus calculation, not the
    strategic asset mix. Risk tolerance, time horizon, age, and goal liquidity
    needs adjust equity, with the opposite adjustment applied to debt so every
    returned allocation still totals exactly 100 percent.
    """

    equity_shift = {
        # Assessed willingness/capacity to take risk is the primary signal.
        # Age and horizon refine it, but should not normally cancel it out.
        "Conservative": -10,
        "Moderate": 0,
        "Aggressive": 10,
    }[risk_category]

    horizon = _finite_float(years, name="time_horizon_years")
    if horizon <= 3:
        equity_shift -= 10
    elif horizon >= 15:
        equity_shift += 5

    age_value = profile.get("age")
    if age_value is not None:
        age = _finite_float(age_value, name="age")
        if not 18 <= age <= 100:
            raise ValueError("age must be between 18 and 100")
        if age <= 30:
            equity_shift += 5
        elif age >= 55:
            equity_shift -= 10
        elif age >= 45:
            equity_shift -= 5

    goal_type = str(goal.get("goal_type", "")).lower()
    if goal_type in {"emergency_fund", "debt_payoff"}:
        equity_shift -= 10
    elif goal_type in {"vehicle", "vacation"}:
        equity_shift -= 5

    equity_shift = max(-20, min(equity_shift, 15))

    allocation = dict(base_allocation)
    base_equity = allocation["Equity"]
    base_debt = allocation["Debt"]
    desired_equity = max(5, min(85, base_equity + equity_shift))
    personalized_equity = min(desired_equity, base_equity + base_debt)
    actual_shift = personalized_equity - base_equity
    allocation["Equity"] = personalized_equity
    allocation["Debt"] = base_debt - actual_shift

    return tuple((asset, allocation[asset]) for asset, _ in base_allocation)


def _finite_float(value: Real, *, name: str) -> float:
    """Return a finite float while rejecting booleans and non-real values."""

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
    """Return a finite nonnegative float while rejecting booleans."""

    result = _finite_float(value, name=name)
    if result < 0:
        raise ValueError(f"{name} must be greater than or equal to zero")
    return result


def _require_mapping(value: object, *, name: str) -> Mapping[str, Any]:
    """Validate a string-keyed input mapping without mutating it."""

    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    if any(not isinstance(key, str) for key in value):
        raise TypeError(f"all {name} keys must be strings")
    return value


def _required_value(mapping: Mapping[str, Any], key: str, *, name: str) -> Any:
    """Return a required mapping value with a contract-focused error."""

    if key not in mapping:
        raise ValueError(f"{name} is missing required field {key!r}")
    return mapping[key]


def _round_for_output(value: float) -> float:
    """Round a finite calculation to two decimals using conventional half-up."""

    decimal_value = Decimal(str(value))
    integer_digits = max(decimal_value.adjusted() + 1, 1)
    with localcontext() as context:
        context.prec = max(28, integer_digits + 2)
        rounded = float(
            decimal_value.quantize(_TWO_DECIMAL_PLACES, rounding=ROUND_HALF_UP)
        )
    return 0.0 if rounded == 0 else rounded


def _validate_historical_data(historical_data: pd.DataFrame) -> dict[str, float]:
    """Validate the summary-data contract and return annual returns by asset."""

    if not isinstance(historical_data, pd.DataFrame):
        raise TypeError("historical_data must be a pandas DataFrame")

    duplicate_columns = sorted(
        str(column)
        for column in historical_data.columns[
            historical_data.columns.duplicated(keep=False)
        ].unique()
    )
    if duplicate_columns:
        raise ValueError(
            "historical_data contains duplicate columns: "
            + ", ".join(duplicate_columns)
        )

    missing_columns = _REQUIRED_DATA_COLUMNS - set(historical_data.columns)
    if missing_columns:
        raise ValueError(
            "historical_data is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    categories = historical_data["asset_category"].tolist()
    if any(not isinstance(category, str) for category in categories):
        raise TypeError("every asset_category must be a string")

    category_set = set(categories)
    missing_categories = _ASSET_CATEGORIES - category_set
    unexpected_categories = category_set - _ASSET_CATEGORIES
    if missing_categories:
        raise ValueError(
            "historical_data is missing asset categories: "
            + ", ".join(sorted(missing_categories))
        )
    if unexpected_categories:
        raise ValueError(
            "historical_data contains unexpected asset categories: "
            + ", ".join(sorted(unexpected_categories))
        )

    duplicate_categories = sorted(
        historical_data.loc[
            historical_data["asset_category"].duplicated(keep=False),
            "asset_category",
        ].unique()
    )
    if duplicate_categories:
        raise ValueError(
            "historical_data contains duplicate asset categories: "
            + ", ".join(duplicate_categories)
        )

    returns_by_asset: dict[str, float] = {}
    for row in historical_data.itertuples(index=False):
        row_data = dict(zip(historical_data.columns, row, strict=True))
        category = row_data["asset_category"]
        average_return = _finite_float(
            row_data["avg_annual_return"],
            name=f"avg_annual_return for {category}",
        )
        volatility = _finite_float(
            row_data["volatility"],
            name=f"volatility for {category}",
        )
        if average_return <= -100:
            raise ValueError(
                f"avg_annual_return for {category} must be greater than -100 percent"
            )
        if volatility < 0:
            raise ValueError(f"volatility for {category} must be nonnegative")
        returns_by_asset[category] = average_return

    return returns_by_asset


def _blended_return(
    allocation: tuple[tuple[str, int], ...],
    returns_by_asset: Mapping[str, float],
) -> float:
    """Calculate a weighted-average annual return in percentage points."""

    allocation_total = sum(percentage for _asset, percentage in allocation)
    if allocation_total != 100:
        raise RuntimeError("internal plan allocation must total 100 percent")
    return sum(
        percentage / 100 * returns_by_asset[asset]
        for asset, percentage in allocation
    )


def generate_plans(
    customer_profile: Mapping[str, Any],
    risk_category: str,
    goal: Mapping[str, Any],
    historical_data: pd.DataFrame,
) -> list[dict[str, object]]:
    """Generate Conservative, Balanced, and Growth plan dictionaries.

    Args:
        customer_profile: Mapping containing at least ``monthly_income`` and
            ``monthly_expenses``. An optional ``monthly_investment`` controls
            the recurring contribution used by the projection. When omitted,
            the nonnegative monthly surplus is used for backwards
            compatibility.
        risk_category: Customer classification: Conservative, Moderate, or
            Aggressive. It personalizes each plan's asset mix but does not
            remove alternatives, because all three are shown for comparison.
        goal: Mapping containing ``target_amount``, ``current_amount``, and
            ``time_horizon_years``.
        historical_data: Preloaded summary DataFrame with one row per required
            asset category and columns ``asset_category``,
            ``avg_annual_return``, and ``volatility``.

    Returns:
        Three newly allocated dictionaries in stable plan order. Display-facing
        numeric values are rounded to two decimal places.
    """

    profile = _require_mapping(customer_profile, name="customer_profile")
    goal_data = _require_mapping(goal, name="goal")

    if not isinstance(risk_category, str):
        raise TypeError("risk_category must be a string")
    if risk_category not in _VALID_RISK_CATEGORIES:
        raise ValueError(
            "risk_category must be Conservative, Moderate, or Aggressive"
        )

    monthly_income = _required_value(
        profile,
        "monthly_income",
        name="customer_profile",
    )
    monthly_expenses = _required_value(
        profile,
        "monthly_expenses",
        name="customer_profile",
    )
    target_amount = _required_value(goal_data, "target_amount", name="goal")
    current_amount = _required_value(goal_data, "current_amount", name="goal")
    years = _required_value(goal_data, "time_horizon_years", name="goal")

    monthly_surplus = calculate_monthly_surplus(monthly_income, monthly_expenses)
    projection_contribution = _nonnegative_float(
        profile.get("monthly_investment", max(monthly_surplus, 0.0)),
        name="monthly_investment",
    )
    returns_by_asset = _validate_historical_data(historical_data)

    plans: list[dict[str, object]] = []
    for spec in _PLAN_SPECS:
        allocation = _personalize_allocation(
            spec.allocation,
            risk_category=risk_category,
            profile=profile,
            goal=goal_data,
            years=years,
        )
        expected_return = _blended_return(allocation, returns_by_asset)
        projected_corpus = calculate_future_value(
            current_amount,
            projection_contribution,
            expected_return,
            years,
        )
        gap = calculate_goal_gap(projected_corpus, target_amount)
        required_investment = calculate_required_monthly_investment(
            target_amount,
            current_amount,
            expected_return,
            years,
        )
        future_value_of_current_savings = calculate_future_value(
            current_amount,
            0,
            expected_return,
            years,
        )
        contribution_months = round(float(years) * 12)

        plans.append(
            {
                "plan_name": spec.name,
                "allocation": dict(allocation),
                "blended_expected_return": _round_for_output(expected_return),
                "monthly_investment": _round_for_output(projection_contribution),
                "current_savings": _round_for_output(float(current_amount)),
                "future_value_of_current_savings": _round_for_output(
                    future_value_of_current_savings
                ),
                "total_planned_contributions": _round_for_output(
                    projection_contribution * contribution_months
                ),
                "total_required_contributions": _round_for_output(
                    required_investment * contribution_months
                ),
                "projected_corpus": _round_for_output(projected_corpus),
                "gap_vs_target": _round_for_output(gap),
                "required_monthly_investment": _round_for_output(
                    required_investment
                ),
                "additional_monthly_investment_needed": _round_for_output(
                    max(required_investment - projection_contribution, 0)
                ),
                "risk_level": spec.risk_level,
                "is_goal_achievable": projected_corpus >= float(target_amount),
            }
        )

    return plans
