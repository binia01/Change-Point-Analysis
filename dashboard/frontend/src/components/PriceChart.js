import React, { useMemo } from "react";
import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine, Legend,
} from "recharts";

const CATEGORY_COLORS = {
  OPEC: "#a78bfa",
  Conflict: "#f87171",
  Economic: "#fbbf24",
  Political: "#60a5fa",
  "Natural Disaster": "#4ade80",
};

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  return (
    <div style={{
      background: "#1e293b", border: "1px solid #334155",
      borderRadius: 8, padding: "0.6rem 0.8rem", fontSize: "0.8rem",
    }}>
      <div style={{ fontWeight: 600, marginBottom: 4 }}>{label}</div>
      {d?.Price != null && <div>Price: <b>${d.Price.toFixed(2)}</b></div>}
      {d?.ma_50 != null && <div style={{ color: "#f59e0b" }}>MA-50: ${d.ma_50.toFixed(2)}</div>}
      {d?.ma_200 != null && <div style={{ color: "#22c55e" }}>MA-200: ${d.ma_200.toFixed(2)}</div>}
    </div>
  );
}

export default function PriceChart({ prices, events, changePoints, highlightEvent }) {
  // Downsample for performance (max 1500 points)
  const data = useMemo(() => {
    if (!prices?.length) return [];
    const step = Math.max(1, Math.floor(prices.length / 1500));
    return prices.filter((_, i) => i % step === 0);
  }, [prices]);

  const cpDates = useMemo(() => {
    if (!changePoints) return [];
    const dates = [];
    if (changePoints.single?.change_date) dates.push(changePoints.single.change_date);
    if (changePoints.multi?.change_dates) dates.push(...changePoints.multi.change_dates);
    return dates;
  }, [changePoints]);

  if (!data.length) return <div className="loading"><span className="spinner" />Loading chart...</div>;

  return (
    <div className="card">
      <div className="card-title">Historical Brent Oil Prices with Events & Change Points</div>
      <ResponsiveContainer width="100%" height={420}>
        <ComposedChart data={data} margin={{ top: 10, right: 20, bottom: 0, left: 10 }}>
          <defs>
            <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="Date" tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickFormatter={(v) => v?.substring(0, 7)} interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickFormatter={(v) => `$${v}`} domain={["auto", "auto"]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend verticalAlign="top" height={30} />
          <Area
            type="monotone" dataKey="Price" stroke="#38bdf8" strokeWidth={1.5}
            fill="url(#priceGrad)" name="Price"
          />
          <Line
            type="monotone" dataKey="ma_50" stroke="#f59e0b"
            dot={false} strokeWidth={1} strokeDasharray="4 2" name="MA-50"
          />
          <Line
            type="monotone" dataKey="ma_200" stroke="#22c55e"
            dot={false} strokeWidth={1} strokeDasharray="4 2" name="MA-200"
          />

          {/* Change point lines */}
          {cpDates.map((d) => (
            <ReferenceLine
              key={`cp-${d}`} x={d} stroke="#ef4444"
              strokeDasharray="6 3" strokeWidth={2}
              label={{ value: `CP ${d}`, position: "top", fill: "#ef4444", fontSize: 10 }}
            />
          ))}

          {/* Event markers */}
          {events?.map((e) => (
            <ReferenceLine
              key={e.date + e.event}
              x={e.date}
              stroke={CATEGORY_COLORS[e.category] || "#94a3b8"}
              strokeDasharray="2 4"
              strokeWidth={highlightEvent === e.event ? 3 : 1}
              strokeOpacity={highlightEvent && highlightEvent !== e.event ? 0.2 : 0.8}
            />
          ))}
        </ComposedChart>
      </ResponsiveContainer>
      <div className="cp-legend">
        <div className="item">
          <span className="swatch" style={{ background: "#ef4444" }} /> Change Point
        </div>
        {Object.entries(CATEGORY_COLORS).map(([cat, col]) => (
          <div key={cat} className="item">
            <span className="swatch" style={{ background: col }} /> {cat}
          </div>
        ))}
      </div>
    </div>
  );
}
