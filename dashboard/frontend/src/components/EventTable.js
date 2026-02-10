import React from "react";

export default function EventTable({ impacts, onEventClick, highlightEvent }) {
  if (!impacts?.length) return <p style={{ color: "#94a3b8" }}>No events to display.</p>;

  return (
    <div className="card">
      <div className="card-title">Event Impact Table (click row to highlight on chart)</div>
      <div className="event-table-wrap">
        <table className="event-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Event</th>
              <th>Category</th>
              <th>Price</th>
              <th>Pre-30d Avg</th>
              <th>Post-30d Avg</th>
              <th>30d Change</th>
              <th>Expected</th>
            </tr>
          </thead>
          <tbody>
            {impacts.map((e) => (
              <tr
                key={e.date + e.event}
                onClick={() => onEventClick?.(e.event)}
                style={{
                  cursor: "pointer",
                  background: highlightEvent === e.event ? "#334155" : undefined,
                }}
              >
                <td>{e.date}</td>
                <td style={{ whiteSpace: "normal", maxWidth: 260 }}>{e.event}</td>
                <td><span className={`badge ${e.category}`}>{e.category}</span></td>
                <td>{e.price_on_date != null ? `$${e.price_on_date}` : "—"}</td>
                <td>{e.pre_mean_30d != null ? `$${e.pre_mean_30d}` : "—"}</td>
                <td>{e.post_mean_30d != null ? `$${e.post_mean_30d}` : "—"}</td>
                <td>
                  {e.pct_change_30d != null ? (
                    <span className={e.pct_change_30d >= 0 ? "pct-positive" : "pct-negative"}>
                      {e.pct_change_30d > 0 ? "+" : ""}{e.pct_change_30d}%
                    </span>
                  ) : "—"}
                </td>
                <td style={{ color: "#94a3b8" }}>{e.expected_impact}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
