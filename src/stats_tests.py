import logging
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss

logger = logging.getLogger(__name__)

_MIN_OBS = 20  # practical minimum for meaningful ADF / KPSS results


class StationarityTestError(Exception):
    """Raised when a stationarity test cannot be completed."""


def _check_series(series: pd.Series, test_name: str) -> pd.Series:
    """Drop NaN, validate length and variance."""
    series = series.dropna()
    if len(series) < _MIN_OBS:
        raise StationarityTestError(
            f"{test_name}: series has only {len(series)} non-null observations "
            f"(need at least {_MIN_OBS})."
        )
    if series.std() == 0:
        raise StationarityTestError(
            f"{test_name}: series has zero variance (constant). "
            "Cannot perform stationarity test on a constant series."
        )
    return series


def adf_test(series: pd.Series, significance: float = 0.05) -> dict:
    """Augmented Dickey-Fuller test for stationarity.

    Parameters
    ----------
    series : pd.Series
        The time series to test.
    significance : float
        Significance level for the test.

    Returns
    -------
    dict
        Test statistic, p-value, lags used, critical values, and conclusion.

    Raises
    ------
    StationarityTestError
        If the series is too short, constant, or the underlying ADF
        computation fails.
    """
    series = _check_series(series, "ADF")
    try:
        result = adfuller(series, autolag="AIC")
    except Exception as exc:
        raise StationarityTestError(f"ADF test failed: {exc}") from exc

    output = {
        "test_statistic": result[0],
        "p_value": result[1],
        "lags_used": result[2],
        "n_observations": result[3],
        "critical_values": result[4],
        "stationary": result[1] < significance,
        "conclusion": (
            f"Series IS stationary (p={result[1]:.4f} < {significance})"
            if result[1] < significance
            else f"Series is NOT stationary (p={result[1]:.4f} >= {significance})"
        ),
    }
    return output


def kpss_test(series: pd.Series, regression: str = "ct", significance: float = 0.05) -> dict:
    """KPSS test for stationarity.

    Parameters
    ----------
    series : pd.Series
        The time series to test.
    regression : str
        'c' for level stationarity, 'ct' for trend stationarity.
    significance : float
        Significance level.

    Returns
    -------
    dict

    Raises
    ------
    StationarityTestError
        If the series is too short, constant, or the underlying KPSS
        computation fails.
    """
    series = _check_series(series, "KPSS")
    try:
        result = kpss(series, regression=regression, nlags="auto")
    except Exception as exc:
        raise StationarityTestError(f"KPSS test failed: {exc}") from exc

    output = {
        "test_statistic": result[0],
        "p_value": result[1],
        "lags_used": result[2],
        "critical_values": result[3],
        "stationary": result[1] > significance,  # KPSS: null is stationary
        "conclusion": (
            f"Series IS stationary (p={result[1]:.4f} > {significance})"
            if result[1] > significance
            else f"Series is NOT stationary (p={result[1]:.4f} <= {significance})"
        ),
    }
    return output


def stationarity_summary(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Run ADF and KPSS tests on specified columns and return summary table.

    Parameters
    ----------
    df : pd.DataFrame
    columns : list of str, optional
        Columns to test. Defaults to ['Price', 'log_return'].

    Returns
    -------
    pd.DataFrame
        Summary of stationarity tests.

    Notes
    -----
    If a test fails for a given column (e.g. too few observations), the
    row will contain the error message instead of raising an exception,
    so that the summary for other columns is still produced.
    """
    if columns is None:
        columns = [c for c in ["Price", "log_return"] if c in df.columns]

    if not columns:
        logger.warning("No testable columns found in DataFrame.")
        return pd.DataFrame()

    records = []
    for col in columns:
        if col not in df.columns:
            logger.warning("Column '%s' not found in DataFrame — skipping.", col)
            continue

        row: dict = {"Series": col}
        # ADF
        try:
            adf = adf_test(df[col])
            row.update({
                "ADF Statistic": round(adf["test_statistic"], 4),
                "ADF p-value": round(adf["p_value"], 4),
                "ADF Stationary": adf["stationary"],
            })
        except StationarityTestError as exc:
            logger.warning("ADF test failed for '%s': %s", col, exc)
            row.update({
                "ADF Statistic": None,
                "ADF p-value": None,
                "ADF Stationary": f"ERROR: {exc}",
            })

        # KPSS
        try:
            kp = kpss_test(df[col])
            row.update({
                "KPSS Statistic": round(kp["test_statistic"], 4),
                "KPSS p-value": round(kp["p_value"], 4),
                "KPSS Stationary": kp["stationary"],
            })
        except StationarityTestError as exc:
            logger.warning("KPSS test failed for '%s': %s", col, exc)
            row.update({
                "KPSS Statistic": None,
                "KPSS p-value": None,
                "KPSS Stationary": f"ERROR: {exc}",
            })

        records.append(row)

    return pd.DataFrame(records)
