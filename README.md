# Change Point Analysis — Brent Oil Prices

**Birhan Energies** | Bayesian Change Point Detection & Statistical Modeling

## Overview

This project analyzes how major geopolitical and economic events affect Brent crude oil prices (1987–2022) using Bayesian change point detection with PyMC. The analysis identifies structural breaks in the price series, associates them with known historical events, and quantifies their impact.

## Project Structure

```
├── data/
│   ├── BrentOilPrices.csv          # Daily Brent oil prices (May 1987 – Nov 2022)
│   └── key_events.csv              # 18 curated geopolitical/economic events
├── docs/
│   ├── analysis_workflow.md        # Planned analysis steps (1-2 page document)
│   └── assumptions_and_limitations.md  # Documented assumptions & limitations
├── notebooks/
│   └── change_point_analysis.ipynb # Main analysis notebook (EDA → Modeling → Insights)
├── src/
│   ├── data_loader.py              # Data loading & preprocessing utilities
│   ├── plotting.py                 # Visualization functions
│   ├── stats_tests.py              # Stationarity tests (ADF, KPSS)
│   └── change_point_model.py       # PyMC Bayesian change point models
├── tests/
├── requirements.txt
└── README.md
```

## Quick Start

```bash
pip install -r requirements.txt
jupyter notebook notebooks/change_point_analysis.ipynb
```

## Key Methods

- **Bayesian Change Point Detection** (PyMC): Single and multi-change point models
- **MCMC Sampling** with convergence diagnostics (R-hat, ESS, trace plots)
- **Model Comparison**: LOO-CV and WAIC via ArviZ
- **Stationarity Testing**: ADF and KPSS tests
- **Volatility Analysis**: Rolling volatility, return distributions

## Deliverables (Task 1)

1.  Analysis workflow document → `docs/analysis_workflow.md`
2.  Structured events CSV (18 events) → `reports/key_events.csv`
3.  Assumptions & limitations → `docs/assumptions_and_limitations.md`
4.  Full analysis notebook → `notebooks/change_point_analysis.ipynb`