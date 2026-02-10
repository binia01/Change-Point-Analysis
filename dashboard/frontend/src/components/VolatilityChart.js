import React, { useMemo } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";

function VolTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#1e293b", border: "1px solid #334155",
      borderRadius: 8, padding: "0.5rem 0.7rem", fontSize: "0.8rem",
    }}>
      <div style={{ fontWeight: 600, marginBottom: 3 }}>{label}</div>
      {payload.map((p) => (
        <div key={p.name} style={{ color: p.color }}>
          {p.name}: {p.value != null ? `${(p.value * 100).toFixed(1)}%` : "—"}
        </div>
      ))}
    </div>
  );
}

export default function VolatilityChart({ prices }) {
  const data = useMemo(() => {
    if (!prices?.length) return [];
    const step = Math.max(1, Math.floor(prices.length / 1200));
    return prices
      .filter((_, i) => i % step === 0)
      .map((d) => ({
        Date: d.Date,
        vol30: d.volatility_30d,
        vol90: d.volatility_90d,
      }));
  }, [prices]);

  if (!data.length) return null;

  return (
    <div className="card">
      <div className="card-title">Annualised Rolling Volatility</div>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ top: 10, right: 20, bottom: 0, left: 10 }}>
          <defs>
            <linearGradient id="vol30g" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="vol90g" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="Date" tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickFormatter={(v) => v?.substring(0, 7)} interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
          />
          <Tooltip content={<VolTooltip />} />
          <Legend verticalAlign="top" height={30} />
          <Area
            type="monotone" dataKey="vol30" stroke="#f59e0b"
            fill="url(#vol30g)" strokeWidth={1.5} name="30-day Vol" dot={false}
          />
          <Area
            type="monotone" dataKey="vol90" stroke="#8b5cf6"
            fill="url(#vol90g)" strokeWidth={1.5} name="90-day Vol" dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
