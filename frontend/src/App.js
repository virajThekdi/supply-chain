/**
 * Supply Chain Control Tower - React Frontend
 *
 * Main App Component with routing
 * Pages: Dashboard, Chat, Anomalies
 */

import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Anomalies from './pages/Anomalies';
import Navigation from './components/Navigation';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    // Check API health on load
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      const data = await response.json();
      setHealthStatus(data);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus({ status: 'UNHEALTHY' });
    }
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'chat':
        return <Chat />;
      case 'anomalies':
        return <Anomalies />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Navigation 
        currentPage={currentPage} 
        onPageChange={setCurrentPage}
        healthStatus={healthStatus}
      />
      
      <main className="main-content">
        {renderPage()}
      </main>

      <footer className="app-footer">
        <p>Supply Chain Control Tower • v1.0.0</p>
        {healthStatus && (
          <p className={`health-indicator ${healthStatus.status.toLowerCase()}`}>
            API Status: {healthStatus.status}
          </p>
        )}
      </footer>
    </div>
  );
}

export default App;
