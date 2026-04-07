/**
 * Navigation Component
 */

import React from 'react';

function Navigation({ currentPage, onPageChange, healthStatus }) {
  return (
    <nav className="nav-bar">
      <div className="nav-brand">
        <span className="nav-brand-icon">🏭</span>
        <span>Supply Chain Control Tower</span>
      </div>

      <ul className="nav-links">
        <li>
          <button
            className={`nav-link ${currentPage === 'dashboard' ? 'active' : ''}`}
            onClick={() => onPageChange('dashboard')}
          >
            📊 Dashboard
          </button>
        </li>
        <li>
          <button
            className={`nav-link ${currentPage === 'anomalies' ? 'active' : ''}`}
            onClick={() => onPageChange('anomalies')}
          >
            ⚠️ Anomalies
          </button>
        </li>
        <li>
          <button
            className={`nav-link ${currentPage === 'chat' ? 'active' : ''}`}
            onClick={() => onPageChange('chat')}
          >
            💬 Chat
          </button>
        </li>
      </ul>

      <div className="nav-status">
        {healthStatus && (
          <span className={`health-indicator ${healthStatus.status.toLowerCase()}`}>
            {healthStatus.status === 'HEALTHY' && '✓ Connected'}
            {healthStatus.status === 'DEGRADED' && '⚠ Limited'}
            {healthStatus.status === 'UNHEALTHY' && '✕ Offline'}
          </span>
        )}
      </div>
    </nav>
  );
}

export default Navigation;
