import React, { useState, useEffect } from 'react';
import { getProducts } from '../api';
import './ProductList.css';

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize, setPageSize] = useState(20);

  // Filters
  const [source, setSource] = useState('');
  const [brand, setBrand] = useState('');
  const [category, setCategory] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');

  useEffect(() => {
    fetchProducts();
  }, [page, source, brand, category, minPrice, maxPrice, pageSize]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const filters = {
        page,
        page_size: pageSize,
        ...(source && { source }),
        ...(brand && { brand }),
        ...(category && { category }),
        ...(minPrice && { min_price: parseFloat(minPrice) }),
        ...(maxPrice && { max_price: parseFloat(maxPrice) }),
      };

      const response = await getProducts(filters);
      setProducts(response.data.items);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Error fetching products:', error);
      alert('Error fetching products: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSource('');
    setBrand('');
    setCategory('');
    setMinPrice('');
    setMaxPrice('');
    setPage(1);
  };

  const maxPages = Math.ceil(total / pageSize);

  return (
    <div className="product-list">
      <div className="list-header">
        <h1>🛍️ Products</h1>
      </div>

      <div className="filters">
        <h3>Filters</h3>
        <div className="filter-row">
          <input
            type="text"
            placeholder="Brand"
            value={brand}
            onChange={(e) => { setBrand(e.target.value); setPage(1); }}
          />
          <input
            type="text"
            placeholder="Category"
            value={category}
            onChange={(e) => { setCategory(e.target.value); setPage(1); }}
          />
          <select value={source} onChange={(e) => { setSource(e.target.value); setPage(1); }}>
            <option value="">All Sources</option>
            <option value="1stdibs">1stDibs</option>
            <option value="fashionphile">Fashionphile</option>
            <option value="grailed">Grailed</option>
          </select>
        </div>
        <div className="filter-row">
          <input
            type="number"
            placeholder="Min Price"
            value={minPrice}
            onChange={(e) => { setMinPrice(e.target.value); setPage(1); }}
          />
          <input
            type="number"
            placeholder="Max Price"
            value={maxPrice}
            onChange={(e) => { setMaxPrice(e.target.value); setPage(1); }}
          />
          <button onClick={handleReset} className="reset-btn">Reset</button>
        </div>
      </div>

      {loading ? (
        <p>Loading products...</p>
      ) : products.length === 0 ? (
        <p>No products found</p>
      ) : (
        <>
          <div className="products-table">
            <table>
              <thead>
                <tr>
                  <th>Brand</th>
                  <th>Model</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>Source</th>
                  <th>Condition</th>
                </tr>
              </thead>
              <tbody>
                {products.map((product) => (
                  <tr key={product.id}>
                    <td>{product.brand}</td>
                    <td>{product.model}</td>
                    <td>{product.category}</td>
                    <td>${product.current_price.toFixed(2)}</td>
                    <td><span className="source-badge">{product.source}</span></td>
                    <td>{product.condition}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
            >
              ← Previous
            </button>
            <span>
              Page {page} of {maxPages} (Total: {total})
            </span>
            <button
              onClick={() => setPage(Math.min(maxPages, page + 1))}
              disabled={page === maxPages}
            >
              Next →
            </button>
          </div>
        </>
      )}
    </div>
  );
}
