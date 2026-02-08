# Brent Oil Price Change Point Analysis — Planned Analysis Steps

**Author:** Birhan Energies Data Science Team  
**Date:** February 2026  
**Project:** Change Point Analysis and Statistical Modeling of Time Series Data

---

## 1. Objective

Identify structural breaks in Brent oil prices (1987–2022), associate them with major geopolitical and economic events, and quantify their price impact using Bayesian change point detection to support investors, policymakers, and energy companies.

---

## 2. Analysis Workflow

### Step 1: Data Loading and Preprocessing
- Load the Brent oil price dataset (`BrentOilPrices.csv`) containing ~9,011 daily observations (May 1987 – November 2022)
- Parse heterogeneous date formats (e.g., `20-May-87` and `Nov 08, 2022`)
- Handle missing values, ensure numeric Price column (USD/barrel)
- Sort chronologically, set DatetimeIndex
- Compute derived features: log returns, simple returns, rolling statistics

### Step 2: External Event Data Compilation
- Research and compile 15–20 major events across categories:
  - **Geopolitical conflicts** (Gulf War, Iraq War, Libya, Russia-Ukraine)
  - **OPEC decisions** (production cuts, OPEC+ formation, price wars)
  - **Economic shocks** (Asian crisis 1997, GFC 2008, COVID-19 2020)
  - **Political/sanctions** (Iran nuclear deal, US sanctions, Russian oil ban)
- Store in structured CSV (`data/key_events.csv`) with fields: date, event, category, description, expected_impact

### Step 3: Exploratory Data Analysis (EDA)
- Plot the full price time series to visually identify regime shifts
- Compute descriptive statistics (mean, median, std, min, max, skewness, kurtosis)
- Plot price distribution (histogram + KDE) to assess distributional properties
- Overlay key events on the price series for qualitative assessment

### Step 4: Time Series Properties Analysis
- **Trend analysis:** Multiplicative seasonal decomposition (trend, seasonal, residual)
- **Stationarity testing:**
  - Augmented Dickey-Fuller (ADF) test — null: unit root (non-stationary)
  - KPSS test — null: stationary
  - Test both raw prices (expected: non-stationary) and log returns (expected: stationary)
- **Rolling statistics:** 30-day, 90-day, 252-day rolling mean and standard deviation
- Document how non-stationarity motivates the use of change point models

### Step 5: Volatility Pattern Analysis
- Compute daily log returns and absolute returns
- Visualize volatility clustering patterns
- Calculate rolling annualized volatility (30-day, 90-day windows)
- Identify high-volatility and low-volatility regimes
- Assess return distribution: histogram, Q-Q plot, fat-tail analysis

### Step 6: Bayesian Change Point Detection (Single CP)
- **Model specification:**
  - Likelihood: $y_t \sim \text{Normal}(\mu_t, \sigma_t)$ where parameters switch at $\tau$
  - Prior on $\tau$: DiscreteUniform(0, N-1)
  - Priors on $\mu_1, \mu_2$: Normal(data_mean, 2 × data_std) — weakly informative
  - Priors on $\sigma_1, \sigma_2$: HalfNormal(2 × data_std) — positive-constrained
- **Sampling:** MCMC via PyMC (2000 draws, 1000 tune, 2+ chains)
- **Diagnostics:** Trace plots, R-hat, ESS, autocorrelation, divergences
- **Results:** Posterior of $\tau$, $\mu_1$, $\mu_2$, $\sigma_1$, $\sigma_2$; 94% HDI

### Step 7: Multi-Change Point Extension
- Extend to K=3 change points using ordered Uniform priors
- Each of K+1 segments gets its own mean and variance
- Sample with higher target_accept (0.9) for complex geometry
- Extract posterior of all change point locations and regime parameters

### Step 8: Model Comparison
- Compute LOO-CV (Leave-One-Out cross-validation) and/or WAIC for both models
- Compare predictive performance vs. model complexity
- Select the preferred model based on information criteria

### Step 9: Event–Change Point Association
- Map each detected change point (with HDI) to nearby historical events
- Create summary table: CP date, HDI, associated events, regime parameters before/after
- Explicitly discuss correlation vs. causation distinction

### Step 10: Impact Quantification
- For each change point, compute posterior distribution of Δμ and Δσ
- Report mean, median, credible intervals for price shift magnitude
- Visualize as forest plots / bar charts with uncertainty bands

### Step 11: Stakeholder Communication
- Generate comprehensive summary visualizations with regime shading
- Prepare targeted insights for: investors, policymakers, energy companies
- Export figures and results for dashboard integration

---

## 3. Communication Channels

| Channel | Audience | Format |
|---------|----------|--------|
| Executive Report (PDF) | Senior management, investors | 2-4 page summary with key findings and visuals |
| Interactive Dashboard | Analysts, portfolio managers | Streamlit/Flask app with interactive price/event exploration |
| Technical Notebook | Data science team, peer review | Jupyter notebook with full methodology and code |
| Policy Brief | Government bodies, regulators | 1-page focused on policy-relevant findings |
| Presentation Slides | Board meetings, conferences | 10-15 slides with key visualizations and takeaways |

---

## 4. Tools and Technologies

- **Python 3.10+** with pandas, numpy, matplotlib, seaborn
- **PyMC 5.x** for Bayesian modeling
- **ArviZ** for posterior diagnostics and model comparison
- **statsmodels** for stationarity tests and decomposition
- **scipy** for statistical computations
