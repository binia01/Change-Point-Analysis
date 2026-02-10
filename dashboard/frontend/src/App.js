import React, { useState, useEffect, useCallback } from "react";
import {
  fetchPrices, fetchStats, fetchEvents, fetchCategories,
  fetchImpacts, fetchChangePoints,
} from "./api";

import KPIRow from "./components/KPIRow";
import Controls from "./components/Controls";
import PriceChart from "./components/PriceChart";
import VolatilityChart from "./components/VolatilityChart";
import EventImpactChart from "./components/EventImpactChart";
import ChangePointPanel from "./components/ChangePointPanel";
import EventTable from "./components/EventTable";

const DEFAULT_START = "1987-05-20";
const DEFAULT_END = "2022-11-14";

export default function App() {
  // ── Filters ──────────────────────────────────────────────────────────────
  const [startDate, setStartDate] = useState(DEFAULT_START);
  const [endDate, setEndDate] = useState(DEFAULT_END);
  const [category, setCategory] = useState("");

  // ── Data ─────────────────────────────────────────────────────────────────
  const [prices, setPrices] = useState([]);
  const [stats, setStats] = useState(null);
  const [events, setEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [impacts, setImpacts] = useState([]);
  const [changePoints, setChangePoints] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ── UI state ─────────────────────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState("overview");
  const [highlightEvent, setHighlightEvent] = useState(null);

  // ── Data fetching ────────────────────────────────────────────────────────
  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [p, s, e, c, imp, cp] = await Promise.all([
        fetchPrices(startDate, endDate),
        fetchStats(startDate, endDate),
        fetchEvents(category),
        fetchCategories(),
        fetchImpacts(category),
        fetchChangePoints(),
      ]);
      setPrices(p);
      setStats(s);
      setEvents(e);
      setCategories(c);
      setImpacts(imp);
      setChangePoints(cp);
    } catch (err) {
      setError("Failed to load data. Is the backend running on port 5000?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, category]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleReset = () => {
    setStartDate(DEFAULT_START);
    setEndDate(DEFAULT_END);
    setCategory("");
    setHighlightEvent(null);
  };

  const handleEventClick = (eventName) => {
    setHighlightEvent((prev) => (prev === eventName ? null : eventName));
  };

  // ── Render ───────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="app">
        <header>
          <div>
            <h1>Brent Oil Price Dashboard</h1>
            <span className="subtitle">Change-Point Analysis & Event Correlation</span>
          </div>
        </header>
        <main>
          <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
            <p style={{ color: "#ef4444", fontSize: "1.1rem" }}>{error}</p>
            <button onClick={loadData} style={{
              marginTop: "1rem", background: "#0ea5e9", color: "white",
              border: "none", padding: "0.5rem 1.2rem", borderRadius: 6,
              cursor: "pointer", fontWeight: 500,
            }}>Retry</button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="app">
      <header>
        <div>
          <h1>Brent Oil Price Dashboard</h1>
          <span className="subtitle">Change-Point Analysis & Event Correlation</span>
        </div>
      </header>

      <main>
        {/* Controls */}
        <Controls
          startDate={startDate} endDate={endDate}
          category={category} categories={categories}
          onStartChange={setStartDate} onEndChange={setEndDate}
          onCategoryChange={setCategory} onReset={handleReset}
        />

        {loading ? (
          <div className="loading"><span className="spinner" />Loading dashboard...</div>
        ) : (
          <>
            {/* KPIs */}
            <KPIRow stats={stats} />

            {/* Tabs */}
            <div className="tabs">
              {["overview", "events", "changepoints"].map((t) => (
                <button
                  key={t}
                  className={`tab-btn ${activeTab === t ? "active" : ""}`}
                  onClick={() => setActiveTab(t)}
                >
                  {t === "overview" ? "Price Overview" :
                   t === "events" ? "Event Analysis" : "Change Points"}
                </button>
              ))}
            </div>

            {/* Tab content */}
            {activeTab === "overview" && (
              <>
                <div className="chart-grid full">
                  <PriceChart
                    prices={prices} events={events}
                    changePoints={changePoints}
                    highlightEvent={highlightEvent}
                  />
                </div>
                <div className="chart-grid full">
                  <VolatilityChart prices={prices} />
                </div>
              </>
            )}

            {activeTab === "events" && (
              <>
                <div className="chart-grid full">
                  <PriceChart
                    prices={prices} events={events}
                    changePoints={changePoints}
                    highlightEvent={highlightEvent}
                  />
                </div>
                <div className="chart-grid full">
                  <EventImpactChart impacts={impacts} onEventClick={handleEventClick} />
                </div>
                <div className="chart-grid full" style={{ marginTop: "0.5rem" }}>
                  <EventTable
                    impacts={impacts}
                    onEventClick={handleEventClick}
                    highlightEvent={highlightEvent}
                  />
                </div>
              </>
            )}

            {activeTab === "changepoints" && (
              <>
                <div className="chart-grid full">
                  <PriceChart
                    prices={prices} events={events}
                    changePoints={changePoints}
                    highlightEvent={highlightEvent}
                  />
                </div>
                <div className="chart-grid full">
                  <ChangePointPanel changePoints={changePoints} />
                </div>
              </>
            )}
          </>
        )}
      </main>
    </div>
  );
}
