"""
Data loading utilities for the Financial Advisor backend.

Provides:
- load_historical_data(): hardcoded asset class averages (default, no file needed)
- load_historical_data_from_file(): CSV-based historical data loader
- load_raw_historical_data(): full synthetic historical dataset from CSV
- load_demo_customers(): synthetic demo customer profiles from CSV
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent

HISTORICAL_SUMMARY_FILE = DATA_DIR / "historical_data_summary.csv"
CUSTOMERS_FILE = DATA_DIR / "synthetic_customers.csv"


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
# Historical data loaders
# ---------------------------------------------------------------------------

def load_historical_data() -> pd.DataFrame:
    """
    Load historical asset class return data.

    Returns hardcoded averages by default so the application works
    without any data files present.

    Returns:
        DataFrame with columns: asset_category, avg_annual_return, volatility
    """
    data = {
        "asset_category": ["Equity", "Debt", "Gold", "Real_Estate", "Cash"],
        "avg_annual_return": [12.0, 7.5, 8.0, 9.0, 4.0],   # Annual returns in %
        "volatility": [18.0, 5.0, 12.0, 10.0, 1.0],          # Std deviation in %
    }
    return pd.DataFrame(data)


def load_historical_data_from_file(file_path: str) -> pd.DataFrame:
    """
    Load historical data from a CSV file.

    Args:
        file_path: Path to CSV file with columns:
                   asset_category, avg_annual_return, volatility

    Returns:
        DataFrame with historical data
    """
    df = pd.read_csv(file_path)

    required_columns = {"asset_category", "avg_annual_return", "volatility"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_columns}")

    return df


def load_raw_historical_data() -> pd.DataFrame:
    """
    Load the complete synthetic historical dataset from CSV.

    Returns:
        pd.DataFrame with columns: year, asset_category,
        annual_return_pct, volatility_pct
    """
    historical_file = DATA_DIR / "synthetic_historical_data.csv"

    if not historical_file.exists():
        raise FileNotFoundError(
            f"Raw historical data file not found: {historical_file}"
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

    for column in ["year", "annual_return_pct", "volatility_pct"]:
        df[column] = pd.to_numeric(df[column], errors="raise")

    return df


# ---------------------------------------------------------------------------
# Demo customer loader
# ---------------------------------------------------------------------------

def load_demo_customers() -> list:
    """
    Load synthetic demo customer profiles from CSV.

    Returns:
        list[dict]: One dictionary per customer row.
    """
    if not CUSTOMERS_FILE.exists():
        raise FileNotFoundError(
            f"Customer dataset not found: {CUSTOMERS_FILE}"
        )

    df = pd.read_csv(CUSTOMERS_FILE)

    if list(df.columns) != CUSTOMER_COLUMNS:
        raise ValueError(
            "Customer dataset has an unexpected schema. "
            f"Expected: {CUSTOMER_COLUMNS}, "
            f"Found: {list(df.columns)}"
        )

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
        df[column] = pd.to_numeric(df[column], errors="raise")

    return df.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Simple manual test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Loading historical data (hardcoded defaults)...")
    hist = load_historical_data()
    print(hist)
    print()

    print("Loading demo customers from CSV...")
    customers = load_demo_customers()
    print(f"Loaded {len(customers)} customers.")
