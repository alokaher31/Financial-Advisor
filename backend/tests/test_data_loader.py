"""
Tests for backend.app.data.data_loader.

These tests verify that the Data Engineer's data-loading layer:
- loads the correct files
- returns the expected schemas
- returns the expected number of records
- preserves numeric types
- exposes the expected asset categories and risk categories
"""

import sys
from pathlib import Path

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Make the backend directory importable when running pytest from project root
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from app.data.data_loader import (  # noqa: E402
    load_demo_customers,
    load_historical_data,
)


# ---------------------------------------------------------------------------
# Expected values
# ---------------------------------------------------------------------------

EXPECTED_HISTORICAL_COLUMNS = [
    "asset_category",
    "avg_annual_return",
    "volatility",
]

EXPECTED_CUSTOMER_COLUMNS = [
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
]

EXPECTED_ASSET_CATEGORIES = {
    "Equity",
    "Debt",
    "Gold",
    "Real_Estate",
    "Cash",
}

EXPECTED_RISK_CATEGORIES = {
    "Conservative",
    "Moderate",
    "Aggressive",
}


# ---------------------------------------------------------------------------
# Historical data tests
# ---------------------------------------------------------------------------


def test_load_historical_data_returns_dataframe():
    """Historical data loader should return a pandas DataFrame."""

    result = load_historical_data()

    assert isinstance(result, pd.DataFrame)


def test_historical_data_has_expected_columns():
    """Historical data should have the exact expected schema."""

    result = load_historical_data()

    assert list(result.columns) == EXPECTED_HISTORICAL_COLUMNS


def test_historical_data_has_five_asset_categories():
    """Historical summary should contain exactly five asset categories."""

    result = load_historical_data()

    assert set(result["asset_category"]) == EXPECTED_ASSET_CATEGORIES


def test_historical_data_has_five_rows():
    """Historical summary should contain one row per asset category."""

    result = load_historical_data()

    assert len(result) == 5


def test_historical_data_has_no_missing_values():
    """Historical summary should contain no missing values."""

    result = load_historical_data()

    assert not result.isnull().any().any()


def test_historical_numeric_columns_are_numeric():
    """Historical return and volatility columns must be numeric."""

    result = load_historical_data()

    assert pd.api.types.is_numeric_dtype(
        result["avg_annual_return"]
    )

    assert pd.api.types.is_numeric_dtype(
        result["volatility"]
    )


def test_historical_data_has_valid_volatility():
    """Volatility should never be negative."""

    result = load_historical_data()

    assert (result["volatility"] >= 0).all()


# ---------------------------------------------------------------------------
# Customer data tests
# ---------------------------------------------------------------------------

def test_load_demo_customers_returns_list():
    """Customer loader should return a list."""

    result = load_demo_customers()

    assert isinstance(result, list)


def test_load_demo_customers_returns_eight_customers():
    """Demo dataset should contain exactly eight customers."""

    result = load_demo_customers()

    assert len(result) == 8


def test_customer_records_are_dictionaries():
    """Every customer should be represented as a dictionary."""

    result = load_demo_customers()

    assert all(
        isinstance(customer, dict)
        for customer in result
    )


def test_customer_schema_is_correct():
    """Every customer should contain all expected fields."""

    result = load_demo_customers()

    for customer in result:
        assert list(customer.keys()) == EXPECTED_CUSTOMER_COLUMNS


def test_customer_names_are_unique():
    """Customer names should be unique."""

    result = load_demo_customers()

    names = [
        customer["customer_name"]
        for customer in result
    ]

    assert len(names) == len(set(names))


def test_customer_values_are_not_missing():
    """Customer records should not contain missing values."""

    result = load_demo_customers()

    for customer in result:
        assert all(
            value is not None
            for value in customer.values()
        )


def test_customer_income_covers_expenses():
    """Every customer should have income >= expenses."""

    result = load_demo_customers()

    for customer in result:
        assert (
            customer["monthly_income"]
            >= customer["monthly_expenses"]
        )


def test_customer_goal_savings_do_not_exceed_target():
    """Current goal savings must not exceed the target."""

    result = load_demo_customers()

    for customer in result:
        assert (
            customer["current_goal_savings"]
            <= customer["target_amount"]
        )


def test_customer_time_horizon_is_positive():
    """Every customer must have a positive goal horizon."""

    result = load_demo_customers()

    for customer in result:
        assert customer["time_horizon_years"] > 0


def test_customer_risk_categories_are_valid():
    """Risk categories must use the approved values."""

    result = load_demo_customers()

    actual_categories = {
        customer["likely_risk_category"]
        for customer in result
    }

    assert actual_categories <= EXPECTED_RISK_CATEGORIES


def test_customer_numeric_fields_are_numeric():
    """Important customer financial fields should be numeric."""

    result = load_demo_customers()

    numeric_fields = [
        "age",
        "monthly_income",
        "monthly_expenses",
        "savings",
        "total_assets",
        "total_liabilities",
        "target_amount",
        "current_goal_savings",
        "time_horizon_years",
    ]

    for customer in result:
        for field in numeric_fields:
            assert isinstance(
                customer[field],
                (int, float),
            )


# ---------------------------------------------------------------------------
# Financial consistency tests
# ---------------------------------------------------------------------------

def test_customer_monthly_surplus_is_non_negative():
    """Every customer should have a non-negative monthly surplus."""

    result = load_demo_customers()

    for customer in result:
        monthly_surplus = (
            customer["monthly_income"]
            - customer["monthly_expenses"]
        )

        assert monthly_surplus >= 0


def test_customer_net_worth_can_be_calculated():
    """Net worth should be calculable from assets and liabilities."""

    result = load_demo_customers()

    for customer in result:
        net_worth = (
            customer["total_assets"]
            - customer["total_liabilities"]
        )

        assert isinstance(net_worth, (int, float))


def test_load_raw_historical_data_returns_dataframe():
    """Raw historical data should return a pandas DataFrame."""

    from app.data.data_loader import load_raw_historical_data

    result = load_raw_historical_data()

    assert isinstance(result, pd.DataFrame)


def test_raw_historical_data_has_50_rows():
    """Raw historical dataset should contain 50 records."""

    from app.data.data_loader import load_raw_historical_data

    result = load_raw_historical_data()

    assert len(result) == 50


def test_raw_historical_data_has_expected_columns():
    """Raw historical data should have the expected schema."""

    from app.data.data_loader import load_raw_historical_data

    result = load_raw_historical_data()

    expected_columns = [
        "year",
        "asset_category",
        "annual_return_pct",
        "volatility_pct",
    ]

    assert list(result.columns) == expected_columns


def test_raw_historical_data_covers_2015_to_2024():
    """Raw historical data should cover exactly 2015-2024."""

    from app.data.data_loader import load_raw_historical_data

    result = load_raw_historical_data()

    years = set(result["year"])

    assert years == set(range(2015, 2025))


def test_raw_historical_data_has_expected_assets():
    """Raw historical data should contain five asset classes."""

    from app.data.data_loader import load_raw_historical_data

    result = load_raw_historical_data()

    assets = set(result["asset_category"])

    expected_assets = {
        "Equity",
        "Debt",
        "Gold",
        "Real_Estate",
        "Cash",
    }

    assert assets == expected_assets


def test_raw_historical_data_has_no_duplicates():
    """Each year and asset combination should be unique."""

    from app.data.data_loader import load_raw_historical_data

    result = load_raw_historical_data()

    duplicate_count = result.duplicated(
        subset=["year", "asset_category"]
    ).sum()

    assert duplicate_count == 0


def test_raw_historical_numeric_columns_are_numeric():
    """Historical return and volatility fields should be numeric."""

    from app.data.data_loader import load_raw_historical_data

    result = load_raw_historical_data()

    assert pd.api.types.is_numeric_dtype(
        result["year"]
    )

    assert pd.api.types.is_numeric_dtype(
        result["annual_return_pct"]
    )

    assert pd.api.types.is_numeric_dtype(
        result["volatility_pct"]
    )