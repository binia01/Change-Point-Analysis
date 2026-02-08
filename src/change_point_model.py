import pymc as pm
import numpy as np
import pandas as pd
import arviz as az
from typing import Optional


def detect_single_change_point(
    prices: np.ndarray,
    draws: int = 2000,
    tune: int = 1000,
    chains: int = 2,
    random_seed: int = 42,
) -> az.InferenceData:
    """Bayesian single change point model for price series.

    Model:
        switchpoint ~ DiscreteUniform(0, N)
        early_mean ~ Normal(mu_prior, sigma_prior)
        late_mean ~ Normal(mu_prior, sigma_prior)
        early_std ~ HalfNormal(sigma_prior)
        late_std ~ HalfNormal(sigma_prior)
        y ~ Normal(mean_t, std_t)  where mean_t switches at switchpoint

    Parameters
    ----------
    prices : np.ndarray
        1-D array of prices.
    draws, tune, chains : int
        PyMC sampler parameters.
    random_seed : int

    Returns
    -------
    az.InferenceData
    """
    n = len(prices)
    mu_prior = prices.mean()
    sigma_prior = prices.std() * 2

    with pm.Model() as model:
        # Priors
        switchpoint = pm.DiscreteUniform("switchpoint", lower=0, upper=n - 1)
        early_mean = pm.Normal("early_mean", mu=mu_prior, sigma=sigma_prior)
        late_mean = pm.Normal("late_mean", mu=mu_prior, sigma=sigma_prior)
        early_std = pm.HalfNormal("early_std", sigma=sigma_prior)
        late_std = pm.HalfNormal("late_std", sigma=sigma_prior)

        # Switching logic
        idx = np.arange(n)
        mean_t = pm.math.switch(switchpoint >= idx, early_mean, late_mean)
        std_t = pm.math.switch(switchpoint >= idx, early_std, late_std)

        # Likelihood
        obs = pm.Normal("obs", mu=mean_t, sigma=std_t, observed=prices)

        # Sampling
        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            random_seed=random_seed,
            return_inferencedata=True,
            progressbar=True,
        )

    return trace


def detect_multiple_change_points_returns(
    returns: np.ndarray,
    n_changepoints: int = 3,
    draws: int = 2000,
    tune: int = 1000,
    chains: int = 2,
    random_seed: int = 42,
) -> az.InferenceData:
    """Bayesian multiple change point model on log-returns.

    Uses an ordered set of change points to segment the series into
    (n_changepoints + 1) regimes, each with its own mean and volatility.

    Parameters
    ----------
    returns : np.ndarray
        1-D array of log returns (NaN-free).
    n_changepoints : int
        Number of change points to detect.
    draws, tune, chains : int
        PyMC sampler parameters.
    random_seed : int

    Returns
    -------
    az.InferenceData
    """
    n = len(returns)
    n_segments = n_changepoints + 1
    mu_prior = returns.mean()
    sigma_prior = returns.std() * 3

    with pm.Model() as model:
        # Ordered change points
        cp_raw = pm.Uniform(
            "cp_raw", lower=0, upper=n - 1, shape=n_changepoints
        )
        changepoints = pm.Deterministic(
            "changepoints", pm.math.sort(cp_raw)
        )

        # Per-segment parameters
        segment_means = pm.Normal(
            "segment_means", mu=mu_prior, sigma=sigma_prior, shape=n_segments
        )
        segment_stds = pm.HalfNormal(
            "segment_stds", sigma=np.abs(sigma_prior), shape=n_segments
        )

        # Assign each observation to a segment
        idx = np.arange(n).astype("float64")
        # segment_idx: for each data point, count how many changepoints it exceeds
        segment_idx = pm.math.sum(
            [pm.math.ge(idx, changepoints[j]) for j in range(n_changepoints)],
            axis=0,
        ).astype("int64")

        mean_t = segment_means[segment_idx]
        std_t = segment_stds[segment_idx]

        obs = pm.Normal("obs", mu=mean_t, sigma=std_t, observed=returns)

        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            random_seed=random_seed,
            return_inferencedata=True,
            progressbar=True,
        )

    return trace


def extract_change_point_dates(
    trace: az.InferenceData,
    date_index: pd.DatetimeIndex,
    var_name: str = "switchpoint",
) -> dict:
    """Extract MAP and HDI for change point(s) and map to dates.

    Parameters
    ----------
    trace : az.InferenceData
    date_index : pd.DatetimeIndex
        The date index corresponding to the data.
    var_name : str
        Name of the change point variable in the trace.

    Returns
    -------
    dict with 'map_index', 'map_date', 'hdi_indices', 'hdi_dates', 'posterior_samples'.
    """
    posterior = trace.posterior[var_name].values.flatten()
    map_idx = int(np.round(np.median(posterior)))
    hdi = az.hdi(trace, var_names=[var_name], hdi_prob=0.94)[var_name].values

    result = {
        "map_index": map_idx,
        "map_date": date_index[map_idx],
        "hdi_indices": hdi,
        "hdi_dates": (date_index[int(hdi[0])], date_index[int(hdi[1])]) if hdi.ndim == 1 else None,
        "posterior_samples": posterior,
    }
    return result


def model_comparison(traces: dict[str, az.InferenceData]) -> pd.DataFrame:
    """Compare multiple models using WAIC or LOO.

    Parameters
    ----------
    traces : dict
        Mapping of model name -> InferenceData.

    Returns
    -------
    pd.DataFrame
        Comparison table.
    """
    comparison = az.compare(traces, ic="loo")
    return comparison
