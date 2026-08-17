import pandas as pd

from app.data.data_loader import (
    load_demo_customers,
    load_historical_data,
)


def test_historical_data_contract():
    """Verify the interface provided to the plan generator."""

    data = load_historical_data()

    assert isinstance(data, pd.DataFrame)

    assert list(data.columns) == [
        "asset_category",
        "avg_annual_return",
        "volatility",
    ]

    assert len(data) == 5


def test_customer_data_contract():
    """Verify the interface provided to backend modules."""

    customers = load_demo_customers()

    assert isinstance(customers, list)
    assert len(customers) == 8

    expected_fields = {
        "customer_name",
        "age",
        "monthly_income",
        "monthly_expenses",
        "savings",
        "total_assets",
        "total_liabilities",
        "goal_type",
        "target_amount",
        "current_goal_savings",
        "time_horizon_years",
        "likely_risk_category",
    }

    for customer in customers:
        assert set(customer.keys()) == expected_fields