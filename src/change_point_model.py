import logging
import pymc as pm
import numpy as np
import pandas as pd
import arviz as az
from typing import Optional

logger = logging.getLogger(__name__)


class ChangePointModelError(Exception):
    """Raised when model construction or sampling fails."""


def _validate_prices(arr: np.ndarray, name: str = "prices") -> np.ndarray:
    """Ensure the input array is 1-D, non-empty, and free of NaN / Inf."""
    arr = np.asarray(arr, dtype=float).ravel()
    if arr.size == 0:
        raise ChangePointModelError(f"Input '{name}' is empty — nothing to model.")
    n_bad = np.count_nonzero(~np.isfinite(arr))
    if n_bad > 0:
        logger.warning(
            "%d non-finite values found in '%s'; dropping them before modelling.",
            n_bad,
            name,
        )
        arr = arr[np.isfinite(arr)]
        if arr.size == 0:
            raise ChangePointModelError(
                f"All values in '{name}' are non-finite after cleaning."
            )
    if arr.std() == 0:
        raise ChangePointModelError(
            f"Input '{name}' has zero variance (constant). Cannot detect change points."
        )
    return arr


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

    Raises
    ------
    ChangePointModelError
        If data validation or MCMC sampling fails.
    """
    prices = _validate_prices(prices, "prices")
    n = len(prices)
    mu_prior = prices.mean()
    sigma_prior = prices.std() * 2

    try:
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
    except ChangePointModelError:
        raise
    except Exception as exc:
        raise ChangePointModelError(
            f"Single change point model failed during sampling: {exc}"
        ) from exc

    # Quick convergence summary
    try:
        rhat_max = float(az.rhat(trace).max().to_array().max())
        if rhat_max > 1.05:
            logger.warning(
                "Max R-hat = %.3f (> 1.05). Consider increasing tune/draws.", rhat_max
            )
        else:
            logger.info("Sampling complete. Max R-hat = %.3f — chains converged.", rhat_max)
    except Exception:
        logger.info("Sampling complete (could not compute R-hat summary).")

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

    Raises
    ------
    ChangePointModelError
        If data validation or MCMC sampling fails.
    """
    returns = _validate_prices(returns, "returns")
    n = len(returns)

    if n_changepoints < 1:
        raise ChangePointModelError("n_changepoints must be >= 1.")
    if n_changepoints >= n:
        raise ChangePointModelError(
            f"n_changepoints ({n_changepoints}) must be less than the number of "
            f"observations ({n})."
        )

    n_segments = n_changepoints + 1
    mu_prior = returns.mean()
    sigma_prior = returns.std() * 3

    try:
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
    except ChangePointModelError:
        raise
    except Exception as exc:
        raise ChangePointModelError(
            f"Multiple change point model failed during sampling: {exc}"
        ) from exc

    # Quick convergence summary
    try:
        rhat_max = float(az.rhat(trace).max().to_array().max())
        if rhat_max > 1.05:
            logger.warning(
                "Max R-hat = %.3f (> 1.05). Consider increasing tune/draws.", rhat_max
            )
        else:
            logger.info("Sampling complete. Max R-hat = %.3f — chains converged.", rhat_max)
    except Exception:
        logger.info("Sampling complete (could not compute R-hat summary).")

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
    dict with 'map_index', 'map_date', 'hdi_indices', 'hdi_dates',
    'posterior_samples'.

    Raises
    ------
    ChangePointModelError
        If the requested variable is not found in the posterior or the
        index mapping fails.
    """
    if var_name not in trace.posterior:
        available = list(trace.posterior.data_vars)
        raise ChangePointModelError(
            f"Variable '{var_name}' not found in posterior. Available: {available}"
        )

    try:
        posterior = trace.posterior[var_name].values.flatten()
        map_idx = int(np.round(np.median(posterior)))
        map_idx = np.clip(map_idx, 0, len(date_index) - 1)
        hdi = az.hdi(trace, var_names=[var_name], hdi_prob=0.94)[var_name].values

        result = {
            "map_index": map_idx,
            "map_date": date_index[map_idx],
            "hdi_indices": hdi,
            "hdi_dates": (
                (date_index[int(np.clip(hdi[0], 0, len(date_index) - 1))],
                 date_index[int(np.clip(hdi[1], 0, len(date_index) - 1))])
                if hdi.ndim == 1
                else None
            ),
            "posterior_samples": posterior,
        }
    except ChangePointModelError:
        raise
    except Exception as exc:
        raise ChangePointModelError(
            f"Failed to extract change point dates for '{var_name}': {exc}"
        ) from exc

    return result


def model_comparison(traces: dict[str, az.InferenceData]) -> pd.DataFrame:
    """Compare multiple models using LOO-CV.

    Parameters
    ----------
    traces : dict
        Mapping of model name -> InferenceData.

    Returns
    -------
    pd.DataFrame
        Comparison table.

    Raises
    ------
    ChangePointModelError
        If the comparison computation fails (e.g. if log-likelihood
        is missing from the traces).
    """
    if not traces:
        raise ChangePointModelError("No traces provided for comparison.")

    try:
        comparison = az.compare(traces, ic="loo")
    except Exception as exc:
        raise ChangePointModelError(
            f"Model comparison failed: {exc}. "
            "Ensure traces contain log_likelihood groups "
            "(pass idata_kwargs={'log_likelihood': True} during sampling)."
        ) from exc
    return comparison
