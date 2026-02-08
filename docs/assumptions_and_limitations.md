# Assumptions and Limitations

**Project:** Brent Oil Price Change Point Analysis  
**Birhan Energies** — February 2026

---

## Assumptions

### Data Assumptions

1. **Data accuracy:** We assume the Brent oil price data from the source is accurate and represents closing/settlement prices for each trading day.

2. **No structural data errors:** We assume the dataset is free of systematic recording errors beyond parseable format inconsistencies (which we handle programmatically).

3. **Trading days only:** The dataset contains prices for trading days only (weekdays excluding holidays). We treat this as a continuous daily series without imputing non-trading days.

4. **USD denomination stability:** Prices are in nominal USD per barrel. We do not adjust for inflation or currency fluctuations, which means real price changes may differ from nominal ones.

### Modeling Assumptions

5. **Normal likelihood:** We assume oil prices within each regime approximately follow a Normal distribution. While financial returns often exhibit fat tails (leptokurtosis), the Normal provides a tractable first-order approximation for price *levels* over sustained regimes. A Student-t likelihood could be explored as a robustness check.

6. **Abrupt change points:** The change point model assumes regime transitions are *instantaneous* — the parameters switch at a single time step. In reality, many regime transitions unfold gradually over weeks or months. This is a simplification inherent in discrete change point models.

7. **Independent observations (conditional on regime):** Within each regime, we assume observations are independent given the regime parameters. This ignores serial autocorrelation in prices. For short-term dynamics this is a limitation, but for regime-level analysis it provides a reasonable baseline.

8. **Number of change points (K):** The number of change points must be pre-specified. Different values of K will yield different segmentations. We compare K=1 and K=3 models, but the "true" number of regimes is unknown.

9. **Weakly informative priors:** We use priors centred on data statistics (sample mean, 2× sample std). These are intentionally weak to let the data drive posterior estimates, but they do encode the assumption that parameters are roughly in the range of observed data.

### Event Association Assumptions

10. **Event list completeness:** Our curated list of 18 events is representative but not exhaustive. Other events (e.g., technology changes, regulatory shifts, natural disasters) may also influence prices.

11. **Event dating precision:** We assign single dates to events that may have unfolded over days or weeks. The actual market impact may spread across a window around the listed date.

12. **Independent events:** We treat events as independent for association purposes. In reality, events can be interconnected (e.g., sanctions leading to OPEC responses).

---

## Limitations

### Methodological Limitations

1. **Correlation ≠ Causation:**  
   **This is a critical limitation.** Finding that a statistically detected change point coincides temporally with a geopolitical event does not prove that the event *caused* the price shift. Multiple confounding factors operate simultaneously in global oil markets:
   - Supply-demand fundamentals (inventories, production capacity, demand growth)
   - Speculative activity and market sentiment
   - Currency movements (USD strength)
   - Concurrent events not in our list
   
   Formal causal inference would require methodologies such as difference-in-differences, synthetic control methods, or instrumental variable approaches, combined with careful identification strategies. Our analysis establishes *temporal associations in time*, which is a necessary but not sufficient condition for causal claims.

2. **Model misspecification:** The Normal likelihood is an approximation. Oil prices exhibit:
   - Heavy tails (extreme events more frequent than Normal predicts)
   - Volatility clustering (GARCH effects)
   - Potential asymmetry in returns
   A Student-t likelihood or a model with stochastic volatility could improve fit.

3. **Fixed number of segments:** Bayesian change point models with a fixed K cannot adapt to the true (unknown) number of regimes. Reversible-jump MCMC or non-parametric approaches could address this but add significant complexity.

4. **Computational constraints:** MCMC sampling with discrete change points can be slow and prone to mixing issues. We mitigate this by using a subset (2000–2022) and moderate chain lengths, but longer runs may improve posterior estimates.

5. **Stationarity within regimes:** The model assumes each regime is stationary (constant mean, constant variance). Within-regime trends or drift are not captured.

### Data Limitations

6. **No intraday data:** Daily prices miss intraday dynamics. Some events (e.g., flash crashes, breaking news) may have immediate impacts that are smoothed in daily data.

7. **Single price series:** We analyze only the Brent crude benchmark. Other oil benchmarks (WTI, Dubai) and related commodities (natural gas, coal) may provide additional context.

8. **No volume or open interest data:** Trading volume and market participation metrics could help validate the significance of detected change points.

9. **Survivorship bias in event selection:** Our event list is compiled with hindsight, knowing which events turned out to be significant. This introduces selection bias — we may miss events that seemed important at the time but had little lasting price impact.

### Communication Limitations

10. **Uncertainty communication:** Posterior credible intervals provide meaningful uncertainty ranges, but they depend on model assumptions. Misspecified models can produce confident but wrong intervals.

11. **Stakeholder interpretation:** Non-technical stakeholders may conflate temporal association with causation unless carefully guided. Clear communication of the correlation-causation distinction is essential.

---

## Mitigation Strategies

| Limitation | Mitigation |
|-----------|-----------|
| Normal likelihood | Compare with Student-t; check posterior predictive distributions |
| Fixed K | Run models with K = 1, 2, 3, 4 and compare via LOO/WAIC |
| Correlation ≠ Causation | Explicit disclaimers; supplementary event studies if time permits |
| Event list completeness | Cross-reference with multiple sources; allow for unknown drivers |
| MCMC convergence | Multiple chains, R-hat diagnostics, longer runs if needed |
