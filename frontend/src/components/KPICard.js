/**
 * KPI Card Component
 */

import React from 'react';

function KPICard({ label, value, subtext, status = 'info', icon = '📈' }) {
  return (
    <div className={`kpi-card ${status}`}>
      <div className="kpi-label">{icon} {label}</div>
      <div className="kpi-value">{value}</div>
      {subtext && <div className="kpi-label" style={{ marginTop: '4px' }}>{subtext}</div>}
    </div>
  );
}

export default KPICard;
