"""Sanity-bounds regression tests for plan generation.

These tests document expected behavior for realistic customer scenarios and
serve as regression checks against calculation bugs that might produce
implausible results (e.g., crore-scale corpus with near-zero required
investment for ordinary goals, or incorrectly flagging valid long-horizon
scenarios as broken).
"""

import pandas as pd
import pytest

from app.core.plan_generator import generate_plans


@pytest.fixture
def historical_data() -> pd.DataFrame:
    """Historical returns matching the actual data used in production.
    
    These are the same average annual returns used by other tests in this
    suite to ensure consistency.
    """
    return pd.DataFrame(
        {
            "asset_category": ["Equity", "Debt", "Gold", "Real_Estate", "Cash"],
            "avg_annual_return": [11.98, 6.75, 8.61, 7.53, 5.26],
            "volatility": [18.0, 4.0, 12.0, 8.0, 1.0],
        }
    )


def test_ordinary_goal_produces_plausible_figures(
    historical_data: pd.DataFrame,
) -> None:
    """An ordinary 15-year goal with ₹60k monthly surplus produces realistic plans.
    
    This documents that for a typical customer with moderate income and a
    mid-term goal, all three plans should produce:
    - Projected corpus in the crores range (₹10L - ₹10Cr)
    - Required monthly investment between ₹500 and ₹2L
    - Higher expected returns require LESS monthly saving (not more)
    
    If this test fails, it likely indicates:
    - Return rates passed in wrong units (decimal 0.12 instead of 12.0)
    - Compounding formula broken
    - Time horizon or contribution amount calculation error
    """
    customer_profile = {
        "monthly_income": 150_000,
        "monthly_expenses": 90_000,
    }
    goal = {
        "target_amount": 5_000_000,
        "current_amount": 300_000,
        "time_horizon_years": 15,
    }
    
    plans = generate_plans(customer_profile, "Moderate", goal, historical_data)
    
    # Sanity bounds: corpus should be in realistic range
    for plan in plans:
        projected = plan["projected_corpus"]
        required = plan["required_monthly_investment"]
        
        # Projected corpus should be between ₹10 lakhs and ₹10 crores
        # (not ₹100 crores which would indicate a calculation bug)
        assert 1_000_000 <= projected <= 100_000_000, (
            f"{plan['plan_name']}: projected_corpus {projected:,.0f} "
            f"is outside realistic bounds (₹10L - ₹10Cr)"
        )
        
        # Required monthly investment should be reasonable
        # (not ₹20 which would indicate a rate-units bug)
        assert 500 <= required <= 200_000, (
            f"{plan['plan_name']}: required_monthly_investment ₹{required:,.0f} "
            f"is outside realistic bounds (₹500 - ₹2L)"
        )
    
    # Verify relationship: higher returns → less monthly saving needed
    # Conservative has lowest return, so requires highest monthly investment
    # Growth has highest return, so requires lowest monthly investment
    conservative_required = plans[0]["required_monthly_investment"]
    balanced_required = plans[1]["required_monthly_investment"]
    growth_required = plans[2]["required_monthly_investment"]
    
    assert conservative_required > balanced_required > growth_required, (
        f"Required monthly investment should decrease as returns increase: "
        f"Conservative ₹{conservative_required:,.0f} > "
        f"Balanced ₹{balanced_required:,.0f} > "
        f"Growth ₹{growth_required:,.0f}"
    )


def test_long_horizon_large_corpus_is_not_flagged_as_broken(
    historical_data: pd.DataFrame,
) -> None:
    """A 32-year horizon with ₹1.5Cr existing savings correctly produces large corpus.
    
    This documents CORRECT behavior that might look like a bug at first glance:
    when a customer has substantial existing savings and a very long time
    horizon, the growth plan can produce a corpus far exceeding the target
    with near-zero required additional monthly investment. This is mathematically
    correct due to compounding over decades.
    
    Example: ₹1.5Cr growing at 10.5% annually for 32 years → ~₹38Cr even with
    zero additional contributions. A ₹5Cr target is easily exceeded, so required
    monthly investment is near-zero or even zero.
    
    If this test fails, it means someone "fixed" this thinking it was a bug,
    when in fact it's correct behavior for long-horizon wealthy customers.
    """
    customer_profile = {
        "monthly_income": 200_000,
        "monthly_expenses": 100_000,
    }
    goal = {
        "target_amount": 50_000_000,  # ₹5 crore target
        "current_amount": 15_000_000,  # ₹1.5 crore existing
        "time_horizon_years": 32,
    }
    
    plans = generate_plans(customer_profile, "Moderate", goal, historical_data)
    growth_plan = plans[2]  # Growth plan has highest return
    
    # With 32 years and ₹1.5Cr existing, Growth plan should:
    # 1. Exceed the ₹5Cr target significantly (due to long compounding)
    assert growth_plan["projected_corpus"] > 50_000_000, (
        f"Growth plan corpus ₹{growth_plan['projected_corpus']:,.0f} "
        f"should exceed ₹5Cr target with 32-year horizon and ₹1.5Cr existing"
    )
    
    # 2. Require very little additional monthly investment (target already achievable)
    assert growth_plan["required_monthly_investment"] < 50_000, (
        f"Growth plan required investment ₹{growth_plan['required_monthly_investment']:,.0f} "
        f"should be low (<₹50k) since existing savings already achieve target"
    )
    
    # This is CORRECT behavior, not a bug. Do not "fix" this.
