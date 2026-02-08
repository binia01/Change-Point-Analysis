import pandas as pd
import numpy as np
from pathlib import Path


def load_brent_oil_data(filepath: str | Path) -> pd.DataFrame:
    """Load Brent oil price CSV and parse dates robustly.

    Parameters
    ----------
    filepath : str or Path
        Path to BrentOilPrices.csv

    Returns
    -------
    pd.DataFrame
        DataFrame with DatetimeIndex and 'Price' column, sorted by date.
    """
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()

    # The CSV has mixed date formats; use format="mixed" for pandas 2.x+
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True)
    df = df.set_index("Date").sort_index()

    # Coerce Price to numeric (handle any stray strings)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

    return df


def load_events(filepath: str | Path) -> pd.DataFrame:
    """Load key geopolitical / economic events CSV.

    Returns
    -------
    pd.DataFrame
        With 'date' as DatetimeIndex and columns: event, category, description, expected_impact.
    """
    events = pd.read_csv(filepath, parse_dates=["date"])
    events = events.set_index("date").sort_index()
    return events


def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Add log-returns and simple returns columns.

    Parameters
    ----------
    df : pd.DataFrame
        Must have a 'Price' column.

    Returns
    -------
    pd.DataFrame
        Original dataframe with 'log_return' and 'simple_return' added.
    """
    df = df.copy()
    df["log_return"] = np.log(df["Price"]).diff()
    df["simple_return"] = df["Price"].pct_change()
    return df


def add_rolling_stats(df: pd.DataFrame, windows: list[int] | None = None) -> pd.DataFrame:
    """Add rolling mean and rolling standard deviation columns.

    Parameters
    ----------
    df : pd.DataFrame
        Must have a 'Price' column.
    windows : list of int, optional
        Rolling window sizes in days. Default [30, 90, 252].

    Returns
    -------
    pd.DataFrame
    """
    if windows is None:
        windows = [30, 90, 252]

    df = df.copy()
    for w in windows:
        df[f"rolling_mean_{w}d"] = df["Price"].rolling(window=w).mean()
        df[f"rolling_std_{w}d"] = df["Price"].rolling(window=w).std()
    return df


def compute_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for Price, log_return, simple_return."""
    cols = [c for c in ["Price", "log_return", "simple_return"] if c in df.columns]
    return df[cols].describe()
