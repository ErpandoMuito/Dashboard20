/**
 * API service configuration with axios
 */
import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request ID
    config.headers['X-Request-ID'] = generateRequestId();
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Extract request ID from response
    const requestId = response.headers['x-request-id'];
    if (requestId) {
      response.data.requestId = requestId;
    }
    
    return response;
  },
  (error) => {
    // Handle errors
    if (error.response) {
      // Server responded with error
      const { status, data } = error.response;
      const message = data?.message || 'An error occurred';
      const requestId = error.response.headers['x-request-id'];
      
      // Log error details
      console.error('API Error:', {
        status,
        message,
        requestId,
        url: error.config?.url,
      });
      
      // Handle specific status codes
      switch (status) {
        case 401:
          // Unauthorized - redirect to login
          localStorage.removeItem('authToken');
          window.location.href = '/login';
          break;
        
        case 403:
          toast.error('You do not have permission to perform this action');
          break;
        
        case 404:
          toast.error('Resource not found');
          break;
        
        case 429:
          toast.error('Too many requests. Please try again later.');
          break;
        
        case 500:
          toast.error(`Server error. Request ID: ${requestId || 'unknown'}`);
          break;
        
        default:
          toast.error(message);
      }
    } else if (error.request) {
      // Request made but no response
      toast.error('Network error. Please check your connection.');
    } else {
      // Something else happened
      toast.error('An unexpected error occurred');
    }
    
    return Promise.reject(error);
  }
);

// Helper function to generate request ID
function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// API methods
export const apiService = {
  // Generic methods
  get: (url, params) => api.get(url, { params }),
  post: (url, data) => api.post(url, data),
  put: (url, data) => api.put(url, data),
  patch: (url, data) => api.patch(url, data),
  delete: (url) => api.delete(url),
  
  // Health check
  healthCheck: () => api.get('/health'),
  detailedHealthCheck: () => api.get('/health/detailed'),
  
  // Notas Fiscais
  notas: {
    list: (params) => api.get('/notas', { params }),
    get: (id) => api.get(`/notas/${id}`),
    create: (data) => api.post('/notas', data),
    update: (id, data) => api.patch(`/notas/${id}`, data),
    delete: (id) => api.delete(`/notas/${id}`),
    sync: () => api.post('/notas/sync'),
  },
  
  // Pedidos (to be implemented)
  pedidos: {
    list: (params) => api.get('/pedidos', { params }),
    get: (id) => api.get(`/pedidos/${id}`),
    create: (data) => api.post('/pedidos', data),
    upload: (file) => {
      const formData = new FormData();
      formData.append('file', file);
      return api.post('/pedidos/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
  },
  
  // Produtos (to be implemented)
  produtos: {
    list: (params) => api.get('/produtos', { params }),
    get: (codigo) => api.get(`/produtos/${codigo}`),
    abatimento: (codigo) => api.get(`/produtos/${codigo}/abatimento`),
  },
};

export default api;