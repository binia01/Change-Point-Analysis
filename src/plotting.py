import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Optional


def plot_price_series(
    df: pd.DataFrame,
    events: Optional[pd.DataFrame] = None,
    title: str = "Brent Oil Prices (1987-2022)",
    figsize: tuple = (16, 6),
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Plot the full Brent oil price time series with optional event annotations."""
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    ax.plot(df.index, df["Price"], linewidth=0.8, color="steelblue", alpha=0.9)
    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD/barrel)")
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, alpha=0.3)

    if events is not None:
        for date, row in events.iterrows():
            ax.axvline(x=date, color="red", alpha=0.4, linestyle="--", linewidth=0.8)
            ax.annotate(
                row["event"],
                xy=(date, df["Price"].loc[:date].iloc[-1] if date in df.index or True else 0),
                xytext=(10, 30),
                textcoords="offset points",
                fontsize=6,
                rotation=45,
                arrowprops=dict(arrowstyle="->", color="red", alpha=0.5),
                color="red",
                alpha=0.8,
            )

    plt.tight_layout()
    return ax


def plot_returns(
    df: pd.DataFrame,
    col: str = "log_return",
    title: str = "Brent Oil Log Returns",
    figsize: tuple = (16, 4),
) -> plt.Axes:
    """Plot returns time series."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(df.index, df[col], linewidth=0.5, color="navy", alpha=0.7)
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel(col)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return ax


def plot_rolling_stats(
    df: pd.DataFrame,
    windows: list[int] | None = None,
    figsize: tuple = (16, 10),
) -> plt.Figure:
    """Plot rolling mean and rolling std for given windows."""
    if windows is None:
        windows = [30, 90, 252]

    fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)

    # Rolling Mean
    axes[0].plot(df.index, df["Price"], linewidth=0.5, alpha=0.4, label="Price", color="grey")
    colors = ["#e74c3c", "#2ecc71", "#3498db"]
    for w, c in zip(windows, colors):
        col = f"rolling_mean_{w}d"
        if col in df.columns:
            axes[0].plot(df.index, df[col], linewidth=1.2, label=f"{w}-day MA", color=c)
    axes[0].set_title("Brent Oil Price with Rolling Means")
    axes[0].set_ylabel("Price (USD/barrel)")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Rolling Std
    for w, c in zip(windows, colors):
        col = f"rolling_std_{w}d"
        if col in df.columns:
            axes[1].plot(df.index, df[col], linewidth=1.0, label=f"{w}-day Volatility", color=c)
    axes[1].set_title("Rolling Volatility (Standard Deviation)")
    axes[1].set_ylabel("Std Dev (USD)")
    axes[1].set_xlabel("Date")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_return_distribution(
    df: pd.DataFrame,
    col: str = "log_return",
    figsize: tuple = (12, 5),
) -> plt.Figure:
    """Plot histogram of returns with overlaid normal distribution."""
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    data = df[col].dropna()

    # Histogram
    axes[0].hist(data, bins=100, density=True, alpha=0.7, color="steelblue", edgecolor="white")
    # Overlay normal
    from scipy import stats
    mu, std = data.mean(), data.std()
    x = np.linspace(data.min(), data.max(), 300)
    axes[0].plot(x, stats.norm.pdf(x, mu, std), "r-", linewidth=2, label="Normal fit")
    axes[0].set_title(f"Distribution of {col}")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # QQ plot
    stats.probplot(data, dist="norm", plot=axes[1])
    axes[1].set_title("Q-Q Plot")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_change_points(
    df: pd.DataFrame,
    change_points: list,
    expected_means: Optional[list] = None,
    title: str = "Detected Change Points in Brent Oil Prices",
    figsize: tuple = (16, 6),
) -> plt.Axes:
    """Plot price series with detected change points as vertical lines."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(df.index, df["Price"], linewidth=0.8, color="steelblue", alpha=0.8, label="Price")

    colors_cp = plt.cm.Set1(np.linspace(0, 1, len(change_points)))
    for i, cp in enumerate(change_points):
        ax.axvline(x=cp, color=colors_cp[i], linestyle="--", linewidth=1.5, alpha=0.8,
                    label=f"CP: {cp.strftime('%Y-%m-%d')}")

    if expected_means is not None and len(expected_means) == len(change_points) + 1:
        boundaries = [df.index[0]] + list(change_points) + [df.index[-1]]
        for i in range(len(boundaries) - 1):
            mask = (df.index >= boundaries[i]) & (df.index < boundaries[i + 1])
            ax.hlines(
                expected_means[i],
                boundaries[i],
                boundaries[i + 1],
                colors="red",
                linewidth=2,
                alpha=0.7,
            )

    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD/barrel)")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return ax
