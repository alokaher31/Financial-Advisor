"""
Data loader for historical market data.
Provides asset class return data for plan generation.
"""

import pandas as pd
from pathlib import Path


def load_historical_data() -> pd.DataFrame:
    """
    Load historical asset class return data.
    
    Returns:
        DataFrame with columns: asset_category, avg_annual_return, volatility
    """
    # For now, return hardcoded historical averages
    # In production, this could load from a CSV file or database
    data = {
        "asset_category": ["Equity", "Debt", "Gold", "Real_Estate", "Cash"],
        "avg_annual_return": [12.0, 7.5, 8.0, 9.0, 4.0],  # Annual returns in percentage
        "volatility": [18.0, 5.0, 12.0, 10.0, 1.0],  # Standard deviation in percentage
    }
    
    return pd.DataFrame(data)


def load_historical_data_from_file(file_path: str) -> pd.DataFrame:
    """
    Load historical data from a CSV file.
    
    Args:
        file_path: Path to CSV file with columns: asset_category, avg_annual_return, volatility
        
    Returns:
        DataFrame with historical data
    """
    df = pd.read_csv(file_path)
    
    # Validate required columns
    required_columns = {"asset_category", "avg_annual_return", "volatility"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_columns}")
    
    return df
