import React from "react";

export default function ChangePointPanel({ changePoints }) {
  if (!changePoints) return null;
  const { single, multi } = changePoints;

  return (
    <div className="card">
      <div className="card-title">Bayesian Change Point Detection Results</div>

      {/* Single CP */}
      <div style={{ marginBottom: "1.2rem" }}>
        <h3 style={{ fontSize: "0.95rem", fontWeight: 600, marginBottom: "0.5rem", color: "#38bdf8" }}>
          Single Change Point Model
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "0.75rem" }}>
          <Stat label="Change Date" value={single.change_date} />
          <Stat label="Early Mean" value={`$${single.early_mean}`} />
          <Stat label="Late Mean" value={`$${single.late_mean}`} />
          <Stat label="Price Shift" value={`+$${single.delta_mean}`} accent="green" />
          <Stat label="94% HDI" value={`${single.hdi_94[0]} — ${single.hdi_94[1]}`} />
          <Stat label="Max R-hat" value={single.r_hat_max} accent={single.r_hat_max <= 1.05 ? "green" : "red"} />
        </div>
      </div>

      {/* Multi CP */}
      <div>
        <h3 style={{ fontSize: "0.95rem", fontWeight: 600, marginBottom: "0.5rem", color: "#a78bfa" }}>
          Multi Change Point Model (K={multi.n_changepoints})
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "0.75rem" }}>
          {multi.change_dates.map((d, i) => (
            <Stat key={d} label={`CP ${i + 1}`} value={d} />
          ))}
          {multi.segment_means.map((m, i) => (
            <Stat key={`seg-${i}`} label={`Segment ${i + 1} Mean`} value={`$${m}`} />
          ))}
          <Stat label="Max R-hat" value={multi.r_hat_max} accent={multi.r_hat_max <= 1.05 ? "green" : "red"} />
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, accent }) {
  const colorMap = { green: "#22c55e", red: "#ef4444" };
  return (
    <div style={{ padding: "0.5rem 0.75rem", background: "#0f172a", borderRadius: 8 }}>
      <div style={{ fontSize: "0.7rem", color: "#94a3b8", marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: "0.92rem", fontWeight: 600, color: accent ? colorMap[accent] : "#f1f5f9" }}>
        {value}
      </div>
    </div>
  );
}
