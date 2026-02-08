import logging
import pandas as pd
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Schema constants (single source of truth) ────────────────────────────────
PRICE_REQUIRED_COLUMNS = {"Date", "Price"}
EVENTS_REQUIRED_COLUMNS = {"date", "event", "category", "description", "expected_impact"}
EVENTS_FILE = "key_events.csv"  # default filename inside data/


class DataLoadError(Exception):
    """Raised when data loading or validation fails."""


def _validate_columns(df: pd.DataFrame, required: set[str], filepath: str) -> None:
    """Check that *required* columns exist in *df*, raise DataLoadError if not."""
    actual = set(df.columns)
    missing = required - actual
    if missing:
        raise DataLoadError(
            f"Missing required columns in '{filepath}': {sorted(missing)}. "
            f"Found columns: {sorted(actual)}"
        )


def load_brent_oil_data(filepath: str | Path) -> pd.DataFrame:
    """Load Brent oil price CSV and parse dates robustly.

    Parameters
    ----------
    filepath : str or Path
        Path to BrentOilPrices.csv.

    Returns
    -------
    pd.DataFrame
        DataFrame with DatetimeIndex and 'Price' column, sorted by date.

    Raises
    ------
    FileNotFoundError
        If *filepath* does not exist.
    DataLoadError
        If required columns ('Date', 'Price') are missing or the file is
        malformed.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Price data file not found: {filepath}")

    try:
        df = pd.read_csv(filepath)
    except Exception as exc:
        raise DataLoadError(f"Failed to read CSV '{filepath}': {exc}") from exc

    df.columns = df.columns.str.strip()
    _validate_columns(df, PRICE_REQUIRED_COLUMNS, str(filepath))

    # The CSV has mixed date formats; use format="mixed" for pandas 2.x+
    try:
        df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True)
    except Exception as exc:
        raise DataLoadError(
            f"Failed to parse 'Date' column in '{filepath}': {exc}"
        ) from exc

    df = df.set_index("Date").sort_index()

    # Coerce Price to numeric (handle any stray strings)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

    n_null = df["Price"].isna().sum()
    if n_null > 0:
        logger.warning(
            "%d null Price values after coercion in '%s'; dropping them.", n_null, filepath
        )
        df = df.dropna(subset=["Price"])

    if df.empty:
        raise DataLoadError(f"No valid price rows remaining after loading '{filepath}'.")

    logger.info("Loaded %d price observations from '%s'.", len(df), filepath)
    return df


def load_events(filepath: str | Path) -> pd.DataFrame:
    """Load key geopolitical / economic events CSV.

    Parameters
    ----------
    filepath : str or Path
        Path to the events CSV (default name: ``key_events.csv``).

    Returns
    -------
    pd.DataFrame
        With 'date' as DatetimeIndex and columns: event, category,
        description, expected_impact.

    Raises
    ------
    FileNotFoundError
        If *filepath* does not exist.
    DataLoadError
        If required columns are missing or the file is malformed.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Events file not found: {filepath}")

    try:
        events = pd.read_csv(filepath)
    except Exception as exc:
        raise DataLoadError(f"Failed to read events CSV '{filepath}': {exc}") from exc

    events.columns = events.columns.str.strip()
    _validate_columns(events, EVENTS_REQUIRED_COLUMNS, str(filepath))

    try:
        events["date"] = pd.to_datetime(events["date"])
    except Exception as exc:
        raise DataLoadError(
            f"Failed to parse 'date' column in '{filepath}': {exc}"
        ) from exc

    events = events.set_index("date").sort_index()
    logger.info("Loaded %d events from '%s'.", len(events), filepath)
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

    Raises
    ------
    DataLoadError
        If 'Price' column is missing.
    """
    if "Price" not in df.columns:
        raise DataLoadError("DataFrame must contain a 'Price' column to compute returns.")

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

    Raises
    ------
    DataLoadError
        If 'Price' column is missing.
    """
    if "Price" not in df.columns:
        raise DataLoadError("DataFrame must contain a 'Price' column for rolling stats.")

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
    if not cols:
        raise DataLoadError(
            "DataFrame has none of the expected columns (Price, log_return, simple_return)."
        )
    return df[cols].describe()
