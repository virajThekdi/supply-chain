/**
 * Dashboard Page
 * Displays KPIs, charts, and key metrics
 */

import React, { useState, useEffect } from 'react';
import { kpiService, formatNumber, formatPercentage } from '../services/apiService';
import KPICard from '../components/KPICard';
import SimpleChart from '../components/SimpleChart';

function Dashboard() {
  const [kpis, setKpis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadKPIs();
    const interval = setInterval(loadKPIs, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const loadKPIs = async () => {
    try {
      setLoading(true);
      const data = await kpiService.getAllKPIs();
      setKpis(data);
      setError(null);
    } catch (err) {
      setError('Failed to load KPIs');
      console.error(err);
    } finally {
      setLoading(false);
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
          <h2 className="card-title">Dashboard</h2>
        </div>
        <div className="text-center text-muted" style={{ padding: '40px' }}>
          {error}
        </div>
      </div>
    );
  }

  if (!kpis) {
    return (
      <div className="card">
        <div className="empty-state">
          <div className="empty-state-icon">📊</div>
          <p>No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Page Header */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="card-header">
          <div>
            <h1 className="card-title">Supply Chain Control Tower Dashboard</h1>
            <p className="card-subtitle">
              Last updated: {new Date(kpis.calculated_at).toLocaleString()}
            </p>
          </div>
          <button className="btn btn-primary btn-sm" onClick={loadKPIs}>
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Delivery KPIs */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">📦 Delivery Performance</h2>
        </div>
        <div className="kpi-grid">
          <KPICard
            label="On-Time Rate"
            value={formatPercentage(kpis.delivery?.on_time_rate || 0)}
            status={kpis.delivery?.on_time_rate > 85 ? 'success' : kpis.delivery?.on_time_rate > 70 ? 'warning' : 'danger'}
            icon="✅"
          />
          <KPICard
            label="On-Time Shipments"
            value={formatNumber(kpis.delivery?.on_time_count || 0)}
            subtext={`of ${kpis.delivery?.total_shipped || 0}`}
          />
          <KPICard
            label="Average Delay"
            value={`${(kpis.delivery?.avg_delay_days || 0).toFixed(1)} days`}
            status={kpis.delivery?.avg_delay_days > 3 ? 'danger' : 'success'}
          />
          <KPICard
            label="Delayed Shipments"
            value={formatNumber(kpis.delivery?.delayed_count || 0)}
            status={'warning'}
          />
        </div>
      </div>

      {/* Quality KPIs */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">🔍 Quality Metrics</h2>
        </div>
        <div className="kpi-grid">
          <KPICard
            label="Average Defect Rate"
            value={formatPercentage(kpis.quality?.avg_defect_rate || 0)}
            status={kpis.quality?.avg_defect_rate < 1 ? 'success' : kpis.quality?.avg_defect_rate < 2 ? 'warning' : 'danger'}
          />
          <KPICard
            label="Total Defects"
            value={formatNumber(kpis.quality?.total_defects || 0)}
          />
          <KPICard
            label="Highest Defect Product"
            value={kpis.quality?.highest_defect_product || 'N/A'}
            subtext={`${(kpis.quality?.by_product?.[kpis.quality?.highest_defect_product]?.avg_defect_rate || 0).toFixed(2)}%`}
            status="warning"
          />
          <KPICard
            label="Max Defect Rate"
            value={formatPercentage(kpis.quality?.max_defect_rate || 0)}
            status={kpis.quality?.max_defect_rate > 3 ? 'danger' : 'warning'}
          />
        </div>
      </div>

      {/* Production KPIs */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">🏭 Production Metrics</h2>
        </div>
        <div className="kpi-grid">
          <KPICard
            label="Total Production"
            value={formatNumber(kpis.production?.total_volume || 0)}
            subtext="units"
          />
          <KPICard
            label="Efficiency"
            value={formatPercentage(kpis.production?.efficiency || 0)}
            status={kpis.production?.efficiency > 90 ? 'success' : kpis.production?.efficiency > 80 ? 'warning' : 'danger'}
          />
          <KPICard
            label="Average Downtime"
            value={`${(kpis.production?.avg_downtime || 0).toFixed(1)} min`}
            status={kpis.production?.avg_downtime > 30 ? 'warning' : 'success'}
          />
          <KPICard
            label="Avg Energy/Unit"
            value={`${(kpis.production?.avg_energy_per_unit || 0).toFixed(2)} kWh`}
          />
        </div>
      </div>

      {/* Supplier KPIs */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">🤝 Supplier Performance</h2>
        </div>
        <div className="kpi-grid">
          <KPICard
            label="Average Rating"
            value={`${(kpis.supplier?.avg_rating || 0).toFixed(1)}/100`}
            status={kpis.supplier?.avg_rating > 90 ? 'success' : kpis.supplier?.avg_rating > 80 ? 'warning' : 'danger'}
          />
          <KPICard
            label="On-Time Rate"
            value={formatPercentage(kpis.supplier?.on_time_rate || 0)}
            status={kpis.supplier?.on_time_rate > 85 ? 'success' : 'warning'}
          />
          <KPICard
            label="Average Delay"
            value={`${(kpis.supplier?.avg_delay_days || 0).toFixed(1)} days`}
          />
          <KPICard
            label="At-Risk Suppliers"
            value={formatNumber(kpis.supplier?.underperforming_suppliers?.length || 0)}
            status={kpis.supplier?.underperforming_suppliers?.length > 0 ? 'warning' : 'success'}
          />
        </div>
      </div>

      {/* Inventory KPIs */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">📦 Inventory Status</h2>
        </div>
        <div className="kpi-grid">
          <KPICard
            label="Inventory Turnover"
            value={`${(kpis.inventory?.avg_turnover || 0).toFixed(1)}x`}
            subtext="annually"
          />
          <KPICard
            label="Critical Stock Products"
            value={formatNumber(kpis.inventory?.low_stock_products?.length || 0)}
            status={kpis.inventory?.low_stock_products?.length > 0 ? 'warning' : 'success'}
          />
        </div>

        {/* Warehouse breakdown */}
        {kpis.inventory?.by_warehouse && Object.keys(kpis.inventory.by_warehouse).length > 0 && (
          <div style={{ marginTop: '20px' }}>
            <h3 style={{ marginBottom: '10px', fontSize: '14px', fontWeight: '600' }}>
              Stock by Warehouse
            </h3>
            <div className="kpi-grid">
              {Object.entries(kpis.inventory.by_warehouse).map(([warehouseId, data]) => (
                <div key={warehouseId} className="kpi-card">
                  <div className="kpi-label">{warehouseId}</div>
                  <div className="kpi-value">{formatNumber(data.total_stock)}</div>
                  <div className="kpi-label">units</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Summary Cards */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">⚠️ Alerts & Warnings</h2>
        </div>
        <div style={{ display: 'grid', gap: '10px' }}>
          {kpis.delivery?.on_time_rate < 80 && (
            <div style={{
              padding: '12px',
              backgroundColor: '#fef2f2',
              borderLeft: '4px solid #dc2626',
              borderRadius: '4px'
            }}>
              <strong>⚠️ Low On-Time Delivery Rate</strong>
              <p style={{ fontSize: '12px', margin: '4px 0 0 0' }}>
                Current rate: {formatPercentage(kpis.delivery.on_time_rate)}
              </p>
            </div>
          )}

          {kpis.quality?.avg_defect_rate > 2 && (
            <div style={{
              padding: '12px',
              backgroundColor: '#fef2f2',
              borderLeft: '4px solid #dc2626',
              borderRadius: '4px'
            }}>
              <strong>⚠️ High Defect Rate</strong>
              <p style={{ fontSize: '12px', margin: '4px 0 0 0' }}>
                Current rate: {formatPercentage(kpis.quality.avg_defect_rate)}
              </p>
            </div>
          )}

          {kpis.inventory?.low_stock_products && kpis.inventory.low_stock_products.length > 0 && (
            <div style={{
              padding: '12px',
              backgroundColor: '#fffbeb',
              borderLeft: '4px solid #ea580c',
              borderRadius: '4px'
            }}>
              <strong>⚠️ Low Stock Alert</strong>
              <p style={{ fontSize: '12px', margin: '4px 0 0 0' }}>
                Products: {kpis.inventory.low_stock_products.join(', ')}
              </p>
            </div>
          )}

          {kpis.supplier?.underperforming_suppliers && kpis.supplier.underperforming_suppliers.length > 0 && (
            <div style={{
              padding: '12px',
              backgroundColor: '#fffbeb',
              borderLeft: '4px solid #ea580c',
              borderRadius: '4px'
            }}>
              <strong>⚠️ Supplier Performance Issue</strong>
              <p style={{ fontSize: '12px', margin: '4px 0 0 0' }}>
                Suppliers: {kpis.supplier.underperforming_suppliers.join(', ')}
              </p>
            </div>
          )}

          {!kpis.delivery?.on_time_rate && !kpis.quality?.avg_defect_rate && !kpis.inventory?.low_stock_products?.length && (
            <div style={{
              padding: '12px',
              backgroundColor: '#f0fdf4',
              borderLeft: '4px solid #16a34a',
              borderRadius: '4px'
            }}>
              <strong>✅ All Systems Normal</strong>
              <p style={{ fontSize: '12px', margin: '4px 0 0 0' }}>
                No critical alerts detected
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
