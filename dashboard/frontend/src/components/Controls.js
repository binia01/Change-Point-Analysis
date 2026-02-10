import React from "react";

export default function Controls({
  startDate, endDate, category, categories,
  onStartChange, onEndChange, onCategoryChange, onReset,
}) {
  return (
    <div className="controls">
      <label>From</label>
      <input
        type="date"
        value={startDate}
        onChange={(e) => onStartChange(e.target.value)}
      />
      <label>To</label>
      <input
        type="date"
        value={endDate}
        onChange={(e) => onEndChange(e.target.value)}
      />
      <label>Category</label>
      <select value={category} onChange={(e) => onCategoryChange(e.target.value)}>
        <option value="">All Events</option>
        {categories.map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </select>
      <button onClick={onReset}>Reset</button>
    </div>
  );
}
