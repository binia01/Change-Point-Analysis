import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, ReferenceLine,
} from "recharts";

function ImpactTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  return (
    <div style={{
      background: "#1e293b", border: "1px solid #334155",
      borderRadius: 8, padding: "0.6rem 0.8rem", fontSize: "0.78rem",
      maxWidth: 320,
    }}>
      <div style={{ fontWeight: 600, marginBottom: 4 }}>{d.event}</div>
      <div style={{ color: "#94a3b8" }}>{d.date} &middot; {d.category}</div>
      <div style={{ marginTop: 4 }}>
        Pre-event avg: <b>${d.pre_mean_30d ?? "—"}</b> &rarr; Post: <b>${d.post_mean_30d ?? "—"}</b>
      </div>
      <div>
        30-day change: <b style={{ color: d.pct_change_30d >= 0 ? "#22c55e" : "#ef4444" }}>
          {d.pct_change_30d != null ? `${d.pct_change_30d > 0 ? "+" : ""}${d.pct_change_30d}%` : "—"}
        </b>
      </div>
      <div style={{ color: "#94a3b8", marginTop: 3, fontSize: "0.72rem" }}>{d.description}</div>
    </div>
  );
}

export default function EventImpactChart({ impacts, onEventClick }) {
  if (!impacts?.length) return null;

  const data = impacts.map((e) => ({
    ...e,
    shortName: e.event.length > 30 ? e.event.substring(0, 28) + "..." : e.event,
  }));

  return (
    <div className="card">
      <div className="card-title">Price Impact by Event (30-day % Change)</div>
      <ResponsiveContainer width="100%" height={Math.max(360, data.length * 28)}>
        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, bottom: 5, left: 180 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
          <XAxis
            type="number" tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickFormatter={(v) => `${v}%`}
          />
          <YAxis
            type="category" dataKey="shortName" width={175}
            tick={{ fill: "#94a3b8", fontSize: 10.5 }}
          />
          <Tooltip content={<ImpactTooltip />} />
          <ReferenceLine x={0} stroke="#475569" />
          <Bar
            dataKey="pct_change_30d" name="% Change" radius={[0, 4, 4, 0]}
            cursor="pointer"
            onClick={(d) => onEventClick?.(d.event)}
          >
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.pct_change_30d >= 0 ? "#22c55e" : "#ef4444"}
                fillOpacity={0.75}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
