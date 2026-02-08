import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss


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
    """
    series = series.dropna()
    result = adfuller(series, autolag="AIC")
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
    """
    series = series.dropna()
    result = kpss(series, regression=regression, nlags="auto")
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
    """
    if columns is None:
        columns = [c for c in ["Price", "log_return"] if c in df.columns]

    records = []
    for col in columns:
        adf = adf_test(df[col])
        kp = kpss_test(df[col])
        records.append(
            {
                "Series": col,
                "ADF Statistic": round(adf["test_statistic"], 4),
                "ADF p-value": round(adf["p_value"], 4),
                "ADF Stationary": adf["stationary"],
                "KPSS Statistic": round(kp["test_statistic"], 4),
                "KPSS p-value": round(kp["p_value"], 4),
                "KPSS Stationary": kp["stationary"],
            }
        )
    return pd.DataFrame(records)
