"""
Data validation utilities for the Finance Planner prototype.

This module validates:
1. Historical yearly asset data
2. Historical summary data
3. Synthetic customer profiles

All validation is deterministic.
No LLM or external API is used.
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent

HISTORICAL_FILE = DATA_DIR / "synthetic_historical_data.csv"
SUMMARY_FILE = DATA_DIR / "historical_data_summary.csv"
CUSTOMERS_FILE = DATA_DIR / "synthetic_customers.csv"


# ---------------------------------------------------------------------------
# Expected schemas
# ---------------------------------------------------------------------------

HISTORICAL_COLUMNS = [
    "year",
    "asset_category",
    "annual_return_pct",
    "volatility_pct",
]

SUMMARY_COLUMNS = [
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

EXPECTED_ASSETS = {
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
# Validation helpers
# ---------------------------------------------------------------------------

class ValidationError(Exception):
    """Raised when one or more dataset validations fail."""


def check_file_exists(path: Path) -> None:
    """Check that a required dataset exists."""
    if not path.exists():
        raise ValidationError(f"Missing required file: {path}")


def check_columns(
    dataframe: pd.DataFrame,
    expected_columns: list[str],
    dataset_name: str,
) -> None:
    """Check that a dataset contains exactly the expected columns."""

    actual_columns = list(dataframe.columns)

    if actual_columns != expected_columns:
        raise ValidationError(
            f"{dataset_name}: incorrect columns.\n"
            f"Expected: {expected_columns}\n"
            f"Found:    {actual_columns}"
        )


def check_no_missing_values(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> None:
    """Check that a dataset contains no missing values."""

    missing = dataframe.isnull().sum()

    missing_columns = missing[missing > 0]

    if not missing_columns.empty:
        raise ValidationError(
            f"{dataset_name}: missing values found:\n"
            f"{missing_columns.to_dict()}"
        )


# ---------------------------------------------------------------------------
# Historical data validation
# ---------------------------------------------------------------------------

def validate_historical_data() -> pd.DataFrame:
    """Validate the raw historical asset dataset."""

    check_file_exists(HISTORICAL_FILE)

    df = pd.read_csv(HISTORICAL_FILE)

    check_columns(
        df,
        HISTORICAL_COLUMNS,
        "synthetic_historical_data.csv",
    )

    check_no_missing_values(
        df,
        "synthetic_historical_data.csv",
    )

    # Expected number of rows
    if len(df) != 50:
        raise ValidationError(
            f"Historical data should contain 50 rows, found {len(df)}."
        )

    # Expected years
    expected_years = set(range(2015, 2025))
    actual_years = set(df["year"].astype(int))

    if actual_years != expected_years:
        raise ValidationError(
            f"Historical data should contain years 2015-2024. "
            f"Found: {sorted(actual_years)}"
        )

    # Expected asset categories
    actual_assets = set(df["asset_category"])

    if actual_assets != EXPECTED_ASSETS:
        raise ValidationError(
            f"Incorrect asset categories.\n"
            f"Expected: {EXPECTED_ASSETS}\n"
            f"Found: {actual_assets}"
        )

    # Every year must have exactly five assets
    rows_per_year = df.groupby("year")["asset_category"].count()

    invalid_years = rows_per_year[rows_per_year != 5]

    if not invalid_years.empty:
        raise ValidationError(
            f"Each year must contain exactly 5 asset categories. "
            f"Invalid years: {invalid_years.to_dict()}"
        )

    # No duplicate year + asset combinations
    duplicates = df.duplicated(
        subset=["year", "asset_category"]
    )

    if duplicates.any():
        duplicate_rows = df.loc[
            duplicates,
            ["year", "asset_category"],
        ]

        raise ValidationError(
            "Duplicate year + asset_category combinations found:\n"
            f"{duplicate_rows.to_dict('records')}"
        )

    # Numeric columns
    numeric_columns = [
        "year",
        "annual_return_pct",
        "volatility_pct",
    ]

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValidationError(
                f"Historical data column '{column}' must be numeric."
            )

    # Volatility cannot be negative
    if (df["volatility_pct"] < 0).any():
        raise ValidationError(
            "Historical data contains negative volatility values."
        )

    # Sanity range for synthetic returns
    if ((df["annual_return_pct"] < -100) |
            (df["annual_return_pct"] > 100)).any():
        raise ValidationError(
            "Historical annual returns contain unrealistic values "
            "outside -100% to +100%."
        )

    # Sanity range for volatility
    if ((df["volatility_pct"] < 0) |
            (df["volatility_pct"] > 100)).any():
        raise ValidationError(
            "Historical volatility contains values outside 0%-100%."
        )

    return df


# ---------------------------------------------------------------------------
# Historical summary validation
# ---------------------------------------------------------------------------

def validate_historical_summary(
    historical_df: pd.DataFrame,
) -> pd.DataFrame:
    """Validate summary data against the raw historical dataset."""

    check_file_exists(SUMMARY_FILE)

    summary_df = pd.read_csv(SUMMARY_FILE)

    check_columns(
        summary_df,
        SUMMARY_COLUMNS,
        "historical_data_summary.csv",
    )

    check_no_missing_values(
        summary_df,
        "historical_data_summary.csv",
    )

    # Exactly five asset categories
    if len(summary_df) != 5:
        raise ValidationError(
            f"Historical summary should contain 5 rows, "
            f"found {len(summary_df)}."
        )

    actual_assets = set(summary_df["asset_category"])

    if actual_assets != EXPECTED_ASSETS:
        raise ValidationError(
            f"Summary asset categories are incorrect.\n"
            f"Expected: {EXPECTED_ASSETS}\n"
            f"Found: {actual_assets}"
        )

    # Check numeric columns
    for column in ["avg_annual_return", "volatility"]:
        if not pd.api.types.is_numeric_dtype(summary_df[column]):
            raise ValidationError(
                f"Summary column '{column}' must be numeric."
            )

    # Calculate expected averages directly from raw data
    calculated_summary = (
        historical_df
        .groupby("asset_category")
        .agg(
            avg_annual_return=("annual_return_pct", "mean"),
            volatility=("volatility_pct", "mean"),
        )
        .reset_index()
    )

    # Sort before comparison
    calculated_summary = calculated_summary.sort_values(
        "asset_category"
    ).reset_index(drop=True)

    summary_df = summary_df.sort_values(
        "asset_category"
    ).reset_index(drop=True)

    # Compare values with a small tolerance
    return_columns = [
        "avg_annual_return",
        "volatility",
    ]

    for column in return_columns:
        if not (
            calculated_summary[column]
            .round(2)
            .eq(summary_df[column].round(2))
            .all()
        ):
            raise ValidationError(
                f"Historical summary mismatch in '{column}'.\n"
                f"Calculated:\n"
                f"{calculated_summary[['asset_category', column]]}\n"
                f"Provided:\n"
                f"{summary_df[['asset_category', column]]}"
            )

    return summary_df


# ---------------------------------------------------------------------------
# Customer data validation
# ---------------------------------------------------------------------------

def validate_customers() -> pd.DataFrame:
    """Validate synthetic customer profiles."""

    check_file_exists(CUSTOMERS_FILE)

    df = pd.read_csv(CUSTOMERS_FILE)

    check_columns(
        df,
        CUSTOMER_COLUMNS,
        "synthetic_customers.csv",
    )

    check_no_missing_values(
        df,
        "synthetic_customers.csv",
    )

    # Expected number of customers
    if len(df) != 8:
        raise ValidationError(
            f"Customer dataset should contain 8 customers, "
            f"found {len(df)}."
        )

    # Customer names must be unique
    if df["customer_name"].duplicated().any():
        raise ValidationError(
            "Customer names must be unique."
        )

    # Numeric columns
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
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValidationError(
                f"Customer column '{column}' must be numeric."
            )

    # Age validation
    if (df["age"] <= 0).any():
        raise ValidationError(
            "Customer age must be greater than zero."
        )

    if (df["age"] > 100).any():
        raise ValidationError(
            "Customer age cannot exceed 100."
        )

    # Income validation
    if (df["monthly_income"] <= 0).any():
        raise ValidationError(
            "Monthly income must be greater than zero."
        )

    # Expenses validation
    if (df["monthly_expenses"] < 0).any():
        raise ValidationError(
            "Monthly expenses cannot be negative."
        )

    # Income must cover expenses
    invalid_income_expense = (
        df["monthly_income"] < df["monthly_expenses"]
    )

    if invalid_income_expense.any():
        customers = df.loc[
            invalid_income_expense,
            "customer_name",
        ].tolist()

        raise ValidationError(
            "Monthly income is lower than monthly expenses for: "
            f"{customers}"
        )

    # Non-negative financial values
    non_negative_columns = [
        "savings",
        "total_assets",
        "total_liabilities",
        "target_amount",
        "current_goal_savings",
    ]

    for column in non_negative_columns:
        if (df[column] < 0).any():
            raise ValidationError(
                f"Column '{column}' cannot contain negative values."
            )

    # Goal savings cannot exceed target
    invalid_goal_savings = (
        df["current_goal_savings"] > df["target_amount"]
    )

    if invalid_goal_savings.any():
        customers = df.loc[
            invalid_goal_savings,
            "customer_name",
        ].tolist()

        raise ValidationError(
            "Current goal savings exceed target amount for: "
            f"{customers}"
        )

    # Time horizon
    if (df["time_horizon_years"] <= 0).any():
        raise ValidationError(
            "Time horizon must be greater than zero."
        )

    # Risk categories
    actual_risk_categories = set(
        df["likely_risk_category"]
    )

    invalid_risk_categories = (
        actual_risk_categories - EXPECTED_RISK_CATEGORIES
    )

    if invalid_risk_categories:
        raise ValidationError(
            f"Invalid risk categories: {invalid_risk_categories}"
        )

    # Financial sanity checks
    net_worth = (
        df["total_assets"] - df["total_liabilities"]
    )

    monthly_surplus = (
        df["monthly_income"] - df["monthly_expenses"]
    )

    if monthly_surplus.min() < 0:
        raise ValidationError(
            "At least one customer has a negative monthly surplus."
        )

    # These are calculated for validation/reporting purposes only.
    df["_net_worth"] = net_worth
    df["_monthly_surplus"] = monthly_surplus

    return df


# ---------------------------------------------------------------------------
# Main validation runner
# ---------------------------------------------------------------------------

def run_validation() -> None:
    """Run all dataset validations."""

    print("=" * 60)
    print("FINANCE PLANNER - DATA VALIDATION")
    print("=" * 60)

    try:
        print("\n[1] Validating historical data...")
        historical_df = validate_historical_data()
        print("  ✓ Historical dataset is valid")
        print(f"  ✓ Rows: {len(historical_df)}")
        print("  ✓ Years: 2015-2024")
        print("  ✓ Asset categories: 5")
        print("  ✓ No missing values")
        print("  ✓ No duplicate year/asset combinations")

        print("\n[2] Validating historical summary...")
        validate_historical_summary(historical_df)
        print("  ✓ Historical summary is valid")
        print("  ✓ Summary matches raw historical data")

        print("\n[3] Validating customer profiles...")
        customers_df = validate_customers()
        print("  ✓ Customer dataset is valid")
        print(f"  ✓ Customers: {len(customers_df)}")
        print("  ✓ No missing values")
        print("  ✓ Income/expense relationships valid")
        print("  ✓ Goal values valid")
        print("  ✓ Risk categories valid")

        print("\n[4] Financial consistency...")
        print("  ✓ Monthly surplus values are valid")
        print("  ✓ Net worth values calculated successfully")

        print("\n" + "=" * 60)
        print("ALL DATA VALIDATIONS PASSED ✓")
        print("=" * 60)

    except ValidationError as error:
        print("\n" + "=" * 60)
        print("DATA VALIDATION FAILED ✗")
        print("=" * 60)
        print(f"\nError:\n{error}")
        raise SystemExit(1)


if __name__ == "__main__":
    run_validation()