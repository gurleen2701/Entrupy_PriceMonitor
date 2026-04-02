import React, { useState, useEffect } from 'react';
import { getAnalytics, refreshProducts } from '../api';
import './Dashboard.css';

export default function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await getAnalytics();
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      const response = await refreshProducts();
      alert(
        `Ingestion complete!\nProducts upserted: ${response.data.products_upserted}\n` +
        `Price changes: ${response.data.price_changes_detected}\n` +
        `Events created: ${response.data.events_created}`
      );
      fetchAnalytics();
    } catch (error) {
      alert('Error refreshing products: ' + error.message);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return <div className="dashboard"><p>Loading analytics...</p></div>;
  }

  if (!analytics) {
    return <div className="dashboard"><p>No analytics available</p></div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>📊 Dashboard</h1>
        <button onClick={handleRefresh} disabled={refreshing} className="refresh-btn">
          {refreshing ? 'Refreshing...' : '🔄 Refresh Products'}
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Products</div>
          <div className="stat-value">{analytics.total_products}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Total Price Changes</div>
          <div className="stat-value">{analytics.total_price_changes}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Average Price</div>
          <div className="stat-value">${analytics.price_stats.avg.toFixed(2)}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Price Range</div>
          <div className="stat-details">
            Min: ${analytics.price_stats.min.toFixed(2)}<br/>
            Max: ${analytics.price_stats.max.toFixed(2)}
          </div>
        </div>
      </div>

      <div className="analytics-section">
        <h2>Products by Source</h2>
        <div className="source-stats">
          {Object.entries(analytics.products_by_source).map(([source, count]) => (
            <div key={source} className="source-item">
              <span className="source-name">{source}</span>
              <span className="source-count">{count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="analytics-section">
        <h2>Average Price by Category</h2>
        <div className="category-stats">
          {Object.entries(analytics.average_price_by_category).map(([category, price]) => (
            <div key={category} className="category-item">
              <span className="category-name">{category}</span>
              <span className="category-price">${price.toFixed(2)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
