"""
Data loading utilities for the Finance Planner prototype.

This module provides a single, reusable interface for loading
synthetic historical financial data and demo customer profiles.

No financial calculations or LLM operations should be performed here.
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent

HISTORICAL_SUMMARY_FILE = (
    DATA_DIR / "historical_data_summary.csv"
)

CUSTOMERS_FILE = (
    DATA_DIR / "synthetic_customers.csv"
)


# ---------------------------------------------------------------------------
# Expected schemas
# ---------------------------------------------------------------------------

HISTORICAL_COLUMNS = [
    "asset_category",
    "avg_annual_return",
    "volatility",
]

CUSTOMER_COLUMNS = [
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


# ---------------------------------------------------------------------------
# Historical data loader
# ---------------------------------------------------------------------------

def load_raw_historical_data() -> pd.DataFrame:
    """
    Load the complete synthetic historical dataset.

    Returns:
        pd.DataFrame:
            Columns:
            - year
            - asset_category
            - annual_return_pct
            - volatility_pct
    """

    historical_file = DATA_DIR / "synthetic_historical_data.csv"

    if not historical_file.exists():
        raise FileNotFoundError(
            f"Raw historical data file not found: "
            f"{historical_file}"
        )

    df = pd.read_csv(historical_file)

    expected_columns = [
        "year",
        "asset_category",
        "annual_return_pct",
        "volatility_pct",
    ]

    if list(df.columns) != expected_columns:
        raise ValueError(
            "Raw historical dataset has an unexpected schema. "
            f"Expected: {expected_columns}, "
            f"Found: {list(df.columns)}"
        )

    numeric_columns = [
        "year",
        "annual_return_pct",
        "volatility_pct",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="raise",
        )

    return df


def load_historical_data() -> pd.DataFrame:
    """
    Load the historical asset-performance summary.

    Returns:
        pd.DataFrame:
            DataFrame containing:

            asset_category
            avg_annual_return
            volatility
    """

    if not HISTORICAL_SUMMARY_FILE.exists():
        raise FileNotFoundError(
            f"Historical summary file not found: "
            f"{HISTORICAL_SUMMARY_FILE}"
        )

    df = pd.read_csv(HISTORICAL_SUMMARY_FILE)

    # Verify expected schema
    if list(df.columns) != HISTORICAL_COLUMNS:
        raise ValueError(
            "Historical summary has an unexpected schema. "
            f"Expected: {HISTORICAL_COLUMNS}, "
            f"Found: {list(df.columns)}"
        )

    # Ensure numeric columns are actually numeric
    numeric_columns = [
        "avg_annual_return",
        "volatility",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="raise",
        )

    return df


# ---------------------------------------------------------------------------
# Demo customer loader
# ---------------------------------------------------------------------------

def load_demo_customers() -> list[dict]:
    """
    Load synthetic demo customer profiles.

    Returns:
        list[dict]:
            A list containing one dictionary per customer.
    """

    if not CUSTOMERS_FILE.exists():
        raise FileNotFoundError(
            f"Customer dataset not found: {CUSTOMERS_FILE}"
        )

    df = pd.read_csv(CUSTOMERS_FILE)

    # Verify expected schema
    if list(df.columns) != CUSTOMER_COLUMNS:
        raise ValueError(
            "Customer dataset has an unexpected schema. "
            f"Expected: {CUSTOMER_COLUMNS}, "
            f"Found: {list(df.columns)}"
        )

    # Convert numeric columns explicitly
    numeric_columns = [
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

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="raise",
        )

    return df.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Simple manual test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Loading raw historical data...")

    raw_historical_data = load_raw_historical_data()

    print(
        f"Loaded {len(raw_historical_data)} historical records."
    )
    print(raw_historical_data.head())
    print()

    print("Loading historical summary...")

    historical_data = load_historical_data()

    print(historical_data)
    print()

    print("Loading demo customers...")

    customers = load_demo_customers()

    print(f"Loaded {len(customers)} customers.")