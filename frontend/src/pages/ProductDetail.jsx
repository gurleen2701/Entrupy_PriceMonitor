import React, { useState, useEffect } from 'react';
import { getProduct } from '../api';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import './ProductDetail.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function ProductDetail({ productId }) {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!productId) return;
    
    fetchProduct();
  }, [productId]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await getProduct(productId);
      setProduct(response.data);
    } catch (error) {
      console.error('Error fetching product:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!productId) {
    return <div className="product-detail"><p>Select a product to view details</p></div>;
  }

  if (loading) {
    return <div className="product-detail"><p>Loading product...</p></div>;
  }

  if (!product) {
    return <div className="product-detail"><p>Product not found</p></div>;
  }

  // Prepare chart data
  const chartData = {
    labels: product.price_history?.map(h => new Date(h.recorded_at).toLocaleDateString()) || [],
    datasets: [
      {
        label: 'Price',
        data: product.price_history?.map(h => h.new_price) || [],
        borderColor: '#007bff',
        backgroundColor: 'rgba(0, 123, 255, 0.1)',
        tension: 0.4,
      },
    ],
  };

  return (
    <div className="product-detail">
      <div className="product-header">
        <h1>{product.brand} - {product.model}</h1>
        <a href={product.product_url} target="_blank" rel="noopener noreferrer" className="source-link">
          View on {product.source}
        </a>
      </div>

      <div className="detail-grid">
        <div className="detail-card">
          <h3>Product Information</h3>
          <div className="detail-item">
            <span className="label">Brand:</span>
            <span>{product.brand}</span>
          </div>
          <div className="detail-item">
            <span className="label">Model:</span>
            <span>{product.model}</span>
          </div>
          <div className="detail-item">
            <span className="label">Category:</span>
            <span>{product.category}</span>
          </div>
          <div className="detail-item">
            <span className="label">Condition:</span>
            <span>{product.condition}</span>
          </div>
          <div className="detail-item">
            <span className="label">Source:</span>
            <span className="source-badge">{product.source}</span>
          </div>
        </div>

        <div className="detail-card">
          <h3>Pricing</h3>
          <div className="price-display">
            <div className="current-price">
              <span className="label">Current Price:</span>
              <span className="price">${product.current_price.toFixed(2)}</span>
            </div>
            <div className="detail-item">
              <span className="label">Currency:</span>
              <span>{product.currency}</span>
            </div>
            <div className="detail-item">
              <span className="label">Created:</span>
              <span>{new Date(product.created_at).toLocaleDateString()}</span>
            </div>
            <div className="detail-item">
              <span className="label">Updated:</span>
              <span>{new Date(product.updated_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
      </div>

      {product.image_url && (
        <div className="image-section">
          <img src={product.image_url} alt={product.model} />
        </div>
      )}

      <div className="price-history-section">
        <h2>Price History</h2>
        {product.price_history && product.price_history.length > 0 ? (
          <>
            <div className="chart-container">
              <Line data={chartData} options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  title: {
                    display: true,
                    text: 'Price Changes Over Time',
                  },
                },
              }} />
            </div>

            <div className="history-table">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Old Price</th>
                    <th>New Price</th>
                    <th>Change</th>
                    <th>Source</th>
                  </tr>
                </thead>
                <tbody>
                  {product.price_history.map((history) => {
                    const change = history.old_price ? history.new_price - history.old_price : 0;
                    const changePercent = history.old_price ? ((change / history.old_price) * 100).toFixed(1) : 0;
                    return (
                      <tr key={history.id}>
                        <td>{new Date(history.recorded_at).toLocaleDateString()}</td>
                        <td>${history.old_price?.toFixed(2) || 'N/A'}</td>
                        <td>${history.new_price.toFixed(2)}</td>
                        <td className={change >= 0 ? 'positive' : 'negative'}>
                          {change >= 0 ? '+' : ''}{change.toFixed(2)} ({changePercent}%)
                        </td>
                        <td>{history.source}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <p>No price history available</p>
        )}
      </div>
    </div>
  );
}
