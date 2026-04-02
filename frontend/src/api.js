import axios from 'axios';

const API_KEY = localStorage.getItem('api_key') || 'test_key_12345';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'X-API-Key': API_KEY,
  },
});

export const getProducts = (filters = {}) => {
  return api.get('/products', { params: filters });
};

export const getProduct = (id) => {
  return api.get(`/products/${id}`);
};

export const refreshProducts = () => {
  return api.post('/refresh');
};

export const getAnalytics = () => {
  return api.get('/analytics');
};

export const getEvents = (filters = {}) => {
  return api.get('/events', { params: filters });
};

export const createWebhook = (data) => {
  return api.post('/webhooks', data);
};

export const getWebhooks = () => {
  return api.get('/webhooks');
};

export const deleteWebhook = (id) => {
  return api.delete(`/webhooks/${id}`);
};

export default api;
