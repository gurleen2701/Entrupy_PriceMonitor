import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import ProductList from './pages/ProductList';
import ProductDetail from './pages/ProductDetail';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedProductId, setSelectedProductId] = useState(null);

  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-brand">
          💎 Entrupy - Price Monitor
        </div>
        <div className="nav-links">
          <button
            className={currentPage === 'dashboard' ? 'active' : ''}
            onClick={() => setCurrentPage('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={currentPage === 'products' ? 'active' : ''}
            onClick={() => setCurrentPage('products')}
          >
            Products
          </button>
          <button
            className={currentPage === 'detail' ? 'active' : ''}
            onClick={() => setCurrentPage('detail')}
            disabled={!selectedProductId}
          >
            Product Detail
          </button>
        </div>
      </nav>

      <main className="main-content">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'products' && <ProductList />}
        {currentPage === 'detail' && <ProductDetail productId={selectedProductId} />}
      </main>

      <footer className="footer">
        <p>Entrupy © 2024 - Luxury Product Price Monitoring System</p>
      </footer>
    </div>
  );
}

export default App;
