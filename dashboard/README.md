# Brent Oil Price Dashboard

Interactive dashboard for exploring Brent oil price change-point analysis results and event correlations.

## Architecture

```
dashboard/
├── backend/          # Flask REST API (port 5050)
│   ├── app.py        # Flask application & route definitions
│   ├── config.py     # Configuration (paths, CORS, ports)
│   └── data_service.py  # Data loading, preprocessing & analysis results
├── frontend/         # React SPA (port 3000)
│   ├── src/
│   │   ├── App.js           # Main application with tabs & state management
│   │   ├── api.js           # Axios API client
│   │   └── components/
│   │       ├── PriceChart.js       # Price + MA + events + change points (Recharts)
│   │       ├── VolatilityChart.js   # Rolling volatility (30d & 90d)
│   │       ├── EventImpactChart.js  # Horizontal bar chart of 30-day price impact
│   │       ├── ChangePointPanel.js  # Bayesian model results display
│   │       ├── EventTable.js        # Interactive sortable event table
│   │       ├── KPIRow.js            # Summary statistics cards
│   │       └── Controls.js          # Date range & category filters
│   └── public/
│       └── index.html
└── start.sh          # One-command launcher for both servers
```

## Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with [pnpm](https://pnpm.io/) (`npm install -g pnpm`)

## Quick Start (one command)

From the project root:

```bash
cd dashboard
chmod +x start.sh
./start.sh
```

This installs dependencies (if needed), starts the Flask backend on port **5050** and the React frontend on port **3000**, then opens the dashboard at **http://localhost:3000**.

Press `Ctrl+C` to stop both servers.

## Manual Start

### 1. Start the Backend

```bash
cd dashboard/backend
pip install -r requirements.txt
python app.py
```

The API will be available at `http://localhost:5050/api/`.

### 2. Start the Frontend

```bash
cd dashboard/frontend
pnpm install
pnpm start
```

Opens at `http://localhost:3000` and proxies API requests to the Flask backend on port 5050.

## API Endpoints

| Endpoint | Method | Params | Description |
|---|---|---|---|
| `/api/health` | GET | — | Health check |
| `/api/prices` | GET | `start`, `end` | Historical prices with MA & volatility |
| `/api/stats` | GET | `start`, `end` | Summary statistics for date range |
| `/api/events` | GET | `category` | Key geopolitical/economic events |
| `/api/events/categories` | GET | — | Distinct event categories |
| `/api/events/impacts` | GET | `category` | 30-day price impact per event |
| `/api/changepoints` | GET | — | Bayesian change point model results |

## Dashboard Features

- **Price Overview** — interactive time-series with price, 50/200-day moving averages, event markers, and change-point lines
- **Volatility** — 30-day and 90-day annualised rolling volatility
- **Event Analysis** — horizontal bar chart of 30-day price impact per event; clickable event table that highlights the event on the price chart
- **Change Points** — single and multi change point Bayesian model results with R-hat convergence indicators
- **Filters** — date range selectors and event category dropdown; responsive layout for desktop/tablet/mobile

## Responsive Design

The dashboard uses CSS flexbox with responsive breakpoints to adapt across devices:

| Breakpoint | Layout |
|---|---|
| **≥ 1024px** (desktop) | Full-width charts, 3+ column KPI row, side-by-side panels |
| **768–1023px** (tablet) | KPI row wraps to 2 columns, charts stack vertically |
| **< 768px** (mobile) | Single-column layout, compact cards, horizontally scrollable tables |

All interactive controls (date range pickers, category filter, reset button) remain visible and functional at every breakpoint. Charts use Recharts' `ResponsiveContainer` to resize automatically.

## Screenshots

See `reports/screenshots/` for dashboard screenshots at various screen sizes. To capture new screenshots:

1. Start the dashboard (see Quick Start above)
2. Open `http://localhost:3000` in a browser
3. Use browser DevTools device toolbar to simulate different screen sizes
4. Capture each tab (Overview, Events, Change Points) at desktop and mobile widths
