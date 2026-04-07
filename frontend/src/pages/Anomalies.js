/**
 * Anomalies Page
 * Displays detected anomalies in supply chain
 */

import React, { useState, useEffect } from 'react';
import { anomalyService } from '../services/apiService';

function Anomalies() {
  const [anomalies, setAnomalies] = useState(null);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnomalies();
    const interval = setInterval(loadAnomalies, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [filter]);

  const loadAnomalies = async () => {
    try {
      setLoading(true);
      const severity = filter !== 'all' ? filter : null;
      const data = await anomalyService.getAnomalies(severity);
      setAnomalies(data);
      setError(null);
    } catch (err) {
      setError('Failed to load anomalies');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return '#dc2626';
      case 'HIGH':
        return '#ea580c';
      case 'MEDIUM':
        return '#eab308';
      case 'LOW':
        return '#0284c7';
      default:
        return '#64748b';
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Anomalies</h2>
        </div>
        <div className="text-center text-muted" style={{ padding: '40px' }}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="card-header">
          <div>
            <h1 className="card-title">⚠️ Anomaly Detection</h1>
            <p className="card-subtitle">
              Detected {anomalies?.total_anomalies || 0} anomalies
            </p>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn btn-primary btn-sm" onClick={loadAnomalies}>
              🔄 Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="kpi-grid" style={{ marginBottom: '20px' }}>
        <div className="kpi-card danger" style={{ borderLeftColor: '#dc2626' }}>
          <div className="kpi-label">🔴 Critical</div>
          <div className="kpi-value">{anomalies?.critical_count || 0}</div>
        </div>
        <div className="kpi-card warning" style={{ borderLeftColor: '#ea580c' }}>
          <div className="kpi-label">🟠 High</div>
          <div className="kpi-value">{anomalies?.high_count || 0}</div>
        </div>
        <div className="kpi-card" style={{ borderLeftColor: '#0284c7' }}>
          <div className="kpi-label">🔵 Total</div>
          <div className="kpi-value">{anomalies?.total_anomalies || 0}</div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {['all', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((severity) => (
            <button
              key={severity}
              className={`btn ${filter === severity ? 'btn-primary' : 'btn-secondary'} btn-sm`}
              onClick={() => setFilter(severity)}
            >
              {severity === 'all' ? 'All' : severity}
            </button>
          ))}
        </div>
      </div>

      {/* Anomalies List */}
      <div className="card">
        {anomalies?.recent_anomalies && anomalies.recent_anomalies.length > 0 ? (
          <div>
            {anomalies.recent_anomalies.map((anomaly, index) => (
              <div
                key={index}
                style={{
                  padding: '16px',
                  borderBottom: '1px solid #e2e8f0',
                  borderLeft: `4px solid ${getSeverityColor(anomaly.severity)}`,
                }}
              >
                <div style={{ marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div>
                    <h3 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: '600' }}>
                      {anomaly.title}
                    </h3>
                    <p style={{ margin: '0', fontSize: '12px', color: '#64748b' }}>
                      {anomaly.description}
                    </p>
                  </div>
                  <span className={`severity-badge severity-${anomaly.severity.toLowerCase()}`}>
                    {anomaly.severity}
                  </span>
                </div>

                {/* Anomaly Details */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '12px',
                  marginTop: '12px',
                  fontSize: '12px',
                }}>
                  <div>
                    <strong>Type:</strong> {anomaly.type}
                  </div>
                  <div>
                    <strong>Entity:</strong> {anomaly.affected_entity} ({anomaly.entity_type})
                  </div>
                  <div>
                    <strong>Detected:</strong> {new Date(anomaly.detected_date).toLocaleDateString()}
                  </div>
                  <div>
                    <strong>Value:</strong> {anomaly.detected_value?.toFixed(2)}
                  </div>
                </div>

                {/* AI Explanation */}
                {anomaly.ai_explanation && (
                  <div style={{
                    marginTop: '12px',
                    padding: '10px',
                    backgroundColor: '#f1f5f9',
                    borderRadius: '6px',
                    fontSize: '12px',
                    lineHeight: '1.5',
                  }}>
                    <strong>🤖 AI Insight:</strong> {anomaly.ai_explanation}
                  </div>
                )}

                {/* Recommendations */}
                {anomaly.recommended_action && (
                  <div style={{
                    marginTop: '8px',
                    padding: '10px',
                    backgroundColor: '#fef3c7',
                    borderRadius: '6px',
                    fontSize: '12px',
                    color: '#92400e',
                  }}>
                    <strong>✓ Action:</strong> {anomaly.recommended_action}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">✅</div>
            <p>No anomalies detected</p>
            <p style={{ fontSize: '12px', marginTop: '8px' }}>
              All systems operating normally
            </p>
          </div>
        )}
      </div>

      {/* Summary */}
      {anomalies?.summary && (
        <div className="card" style={{ marginTop: '20px', backgroundColor: '#f0fdf4', borderLeft: '4px solid #16a34a' }}>
          <p style={{ fontSize: '14px', fontWeight: '600', margin: '0' }}>
            📊 Summary: {anomalies.summary}
          </p>
        </div>
      )}
    </div>
  );
}

export default Anomalies;
