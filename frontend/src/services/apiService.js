/**
 * API Service
 * Handles all backend API calls
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// KPI Endpoints
export const kpiService = {
  getAllKPIs: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/kpis`);
      if (!response.ok) throw new Error('Failed to fetch KPIs');
      return await response.json();
    } catch (error) {
      console.error('Error fetching KPIs:', error);
      throw error;
    }
  },

  getDeliveryKPIs: async () => {
    const response = await fetch(`${API_BASE_URL}/kpis/delivery`);
    if (!response.ok) throw new Error('Failed to fetch delivery KPIs');
    return await response.json();
  },

  getQualityKPIs: async () => {
    const response = await fetch(`${API_BASE_URL}/kpis/quality`);
    if (!response.ok) throw new Error('Failed to fetch quality KPIs');
    return await response.json();
  },

  getProductionKPIs: async () => {
    const response = await fetch(`${API_BASE_URL}/kpis/production`);
    if (!response.ok) throw new Error('Failed to fetch production KPIs');
    return await response.json();
  },

  getSupplierKPIs: async () => {
    const response = await fetch(`${API_BASE_URL}/kpis/supplier`);
    if (!response.ok) throw new Error('Failed to fetch supplier KPIs');
    return await response.json();
  },

  getInventoryKPIs: async () => {
    const response = await fetch(`${API_BASE_URL}/kpis/inventory`);
    if (!response.ok) throw new Error('Failed to fetch inventory KPIs');
    return await response.json();
  },
};

// Anomaly Endpoints
export const anomalyService = {
  getAnomalies: async (severity = null) => {
    try {
      let url = `${API_BASE_URL}/anomalies`;
      if (severity) {
        url += `?severity=${severity}`;
      }
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch anomalies');
      return await response.json();
    } catch (error) {
      console.error('Error fetching anomalies:', error);
      throw error;
    }
  },

  getAnomaliesByType: async (type) => {
    const response = await fetch(`${API_BASE_URL}/anomalies/by-type/${type}`);
    if (!response.ok) throw new Error('Failed to fetch anomalies');
    return await response.json();
  },
};

// Chat / LLM Endpoints
export const chatService = {
  askQuestion: async (query, context = null, conversationId = null) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          context,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) throw new Error('Failed to process question');
      return await response.json();
    } catch (error) {
      console.error('Error asking question:', error);
      throw error;
    }
  },

  createConversation: async () => {
    const response = await fetch(`${API_BASE_URL}/conversations`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to create conversation');
    return await response.json();
  },

  getConversation: async (conversationId) => {
    const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`);
    if (!response.ok) throw new Error('Failed to fetch conversation');
    return await response.json();
  },
};

// Data Endpoints
export const dataService = {
  getShipments: async (limit = 100, status = null) => {
    let url = `${API_BASE_URL}/data/shipments?limit=${limit}`;
    if (status) {
      url += `&status=${status}`;
    }
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch shipments');
    return await response.json();
  },

  getQuality: async (limit = 100, productId = null) => {
    let url = `${API_BASE_URL}/data/quality?limit=${limit}`;
    if (productId) {
      url += `&product_id=${productId}`;
    }
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch quality data');
    return await response.json();
  },

  getProduction: async (limit = 100) => {
    const response = await fetch(`${API_BASE_URL}/data/production?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch production data');
    return await response.json();
  },

  getInventory: async (limit = 100, warehouseId = null) => {
    let url = `${API_BASE_URL}/data/inventory?limit=${limit}`;
    if (warehouseId) {
      url += `&warehouse_id=${warehouseId}`;
    }
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch inventory data');
    return await response.json();
  },

  getSuppliers: async (limit = 100) => {
    const response = await fetch(`${API_BASE_URL}/data/suppliers?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch supplier data');
    return await response.json();
  },
};

// Health Check
export const healthService = {
  checkHealth: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error('Health check failed');
      return await response.json();
    } catch (error) {
      console.error('Health check error:', error);
      return { status: 'UNHEALTHY' };
    }
  },
};

// Utility function to format numbers
export const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

// Format percentage
export const formatPercentage = (num) => {
  return (num).toFixed(1) + '%';
};
