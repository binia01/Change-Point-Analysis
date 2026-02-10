import React from "react";

export default function KPIRow({ stats }) {
  if (!stats) return null;

  const kpis = [
    { label: "Observations", value: stats.count?.toLocaleString() },
    { label: "Date Range", value: `${stats.start_date} — ${stats.end_date}` },
    { label: "Min Price", value: `$${stats.min}` },
    { label: "Max Price", value: `$${stats.max}` },
    { label: "Mean Price", value: `$${stats.mean}` },
    { label: "Annualised Vol", value: `${(stats.annualised_volatility * 100).toFixed(1)}%` },
    { label: "Total Return", value: `${stats.total_return_pct > 0 ? "+" : ""}${stats.total_return_pct}%` },
  ];

  return (
    <div className="kpi-row">
      {kpis.map((k) => (
        <div key={k.label} className="card kpi">
          <div className="value">{k.value}</div>
          <div className="label">{k.label}</div>
        </div>
      ))}
    </div>
  );
}
