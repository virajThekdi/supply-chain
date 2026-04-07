/**
 * Simple Chart Component (placeholder)
 * In production, use React Chart.js or Recharts
 */

import React from 'react';

function SimpleChart({ title, data }) {
  return (
    <div className="chart-wrapper">
      <div className="chart-title">{title}</div>
      <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ccc' }}>
        📊 Chart visualization
      </div>
    </div>
  );
}

export default SimpleChart;
