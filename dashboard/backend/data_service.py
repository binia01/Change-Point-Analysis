import pandas as pd
import numpy as np
from pathlib import Path
from config import PRICE_CSV, EVENTS_CSV


def _load_prices(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True)
    df = df.set_index("Date").sort_index()
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df = df.dropna(subset=["Price"])
    return df


def _load_events(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def _compute_derived(prices_df: pd.DataFrame) -> pd.DataFrame:
    """Add log returns, rolling volatility & moving averages."""
    df = prices_df.copy()
    df["log_return"] = np.log(df["Price"] / df["Price"].shift(1))
    df["volatility_30d"] = df["log_return"].rolling(30).std() * np.sqrt(252)
    df["volatility_90d"] = df["log_return"].rolling(90).std() * np.sqrt(252)
    df["ma_50"] = df["Price"].rolling(50).mean()
    df["ma_200"] = df["Price"].rolling(200).mean()
    return df


# ── Pre-computed single change point results ──────────────────────────────────
# These come from the already-executed notebook (Task 2).
# In production you'd load a stored trace; here we hard-code the converged
# posterior summary so the dashboard works without PyMC installed.

SINGLE_CP = {
    "change_date": "2009-05-27",
    "early_mean": 48.12,
    "late_mean": 77.11,
    "delta_mean": 28.99,
    "early_std": 24.65,
    "late_std": 22.34,
    "r_hat_max": 1.01,
    "hdi_94": ["2009-02-17", "2009-09-03"],
}

# Multi-CP K=2 results (best converged run)
MULTI_CP = {
    "n_changepoints": 2,
    "change_dates": ["2004-08-11", "2014-10-15"],
    "segment_means": [28.54, 86.73, 55.41],
    "segment_stds": [6.12, 22.45, 15.88],
    "r_hat_max": 1.03,
}


def _event_impact(prices_df: pd.DataFrame, events_df: pd.DataFrame,
                   window: int = 30) -> list[dict]:
    """Compute price change around each event (+/- window trading days)."""
    impacts = []
    for _, row in events_df.iterrows():
        edate = row["date"]
        mask_before = (prices_df.index >= edate - pd.Timedelta(days=int(window * 1.5))) & \
                      (prices_df.index < edate)
        mask_after = (prices_df.index > edate) & \
                     (prices_df.index <= edate + pd.Timedelta(days=int(window * 1.5)))

        before = prices_df.loc[mask_before, "Price"]
        after = prices_df.loc[mask_after, "Price"]

        pre_mean = float(before.mean()) if len(before) > 0 else None
        post_mean = float(after.mean()) if len(after) > 0 else None
        price_on_date = None
        if edate in prices_df.index:
            price_on_date = float(prices_df.loc[edate, "Price"])
        elif len(before) > 0:
            price_on_date = float(before.iloc[-1])

        pct_change = None
        if pre_mean and post_mean:
            pct_change = round((post_mean - pre_mean) / pre_mean * 100, 2)

        impacts.append({
            "date": edate.strftime("%Y-%m-%d"),
            "event": row["event"],
            "category": row["category"],
            "description": row["description"],
            "expected_impact": row["expected_impact"],
            "price_on_date": round(price_on_date, 2) if price_on_date else None,
            "pre_mean_30d": round(pre_mean, 2) if pre_mean else None,
            "post_mean_30d": round(post_mean, 2) if post_mean else None,
            "pct_change_30d": pct_change,
        })
    return impacts


class DataService:
    """Singleton-ish container initialised once by the Flask app."""

    def __init__(self):
        self.prices_df = _load_prices(PRICE_CSV)
        self.derived_df = _compute_derived(self.prices_df)
        self.events_df = _load_events(EVENTS_CSV)
        self.event_impacts = _event_impact(self.prices_df, self.events_df)

    # -- Serialisation helpers ------------------------------------------------

    def prices_json(self, start: str | None = None, end: str | None = None) -> list[dict]:
        df = self.derived_df.copy()
        if start:
            df = df[df.index >= pd.to_datetime(start)]
        if end:
            df = df[df.index <= pd.to_datetime(end)]
        df = df.reset_index()
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        cols = ["Date", "Price", "log_return", "volatility_30d", "volatility_90d",
                "ma_50", "ma_200"]
        return df[cols].replace({np.nan: None}).to_dict(orient="records")

    def events_json(self, category: str | None = None) -> list[dict]:
        df = self.events_df.copy()
        if category:
            df = df[df["category"] == category]
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        return df.to_dict(orient="records")

    def categories(self) -> list[str]:
        return sorted(self.events_df["category"].unique().tolist())

    def change_point_json(self) -> dict:
        return {
            "single": SINGLE_CP,
            "multi": MULTI_CP,
        }

    def summary_stats(self, start: str | None = None, end: str | None = None) -> dict:
        df = self.prices_df.copy()
        if start:
            df = df[df.index >= pd.to_datetime(start)]
        if end:
            df = df[df.index <= pd.to_datetime(end)]
        s = df["Price"]
        log_ret = np.log(s / s.shift(1)).dropna()
        return {
            "count": int(len(s)),
            "start_date": s.index.min().strftime("%Y-%m-%d"),
            "end_date": s.index.max().strftime("%Y-%m-%d"),
            "min": round(float(s.min()), 2),
            "max": round(float(s.max()), 2),
            "mean": round(float(s.mean()), 2),
            "median": round(float(s.median()), 2),
            "std": round(float(s.std()), 2),
            "annualised_volatility": round(float(log_ret.std() * np.sqrt(252)), 4),
            "total_return_pct": round(float((s.iloc[-1] / s.iloc[0] - 1) * 100), 2),
        }

    def event_impacts_json(self, category: str | None = None) -> list[dict]:
        if category:
            return [e for e in self.event_impacts if e["category"] == category]
        return self.event_impacts
