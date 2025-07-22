import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance with defaults
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor with retry logic
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Retry on network errors
    if (!error.response && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        return api(originalRequest);
      } catch (retryError) {
        toast.error('Erro de conexão. Verifique sua internet.');
        return Promise.reject(retryError);
      }
    }
    
    // Handle specific error codes
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Unauthorized - redirect to login
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 404:
          toast.error('Recurso não encontrado');
          break;
        case 500:
          toast.error('Erro no servidor. Tente novamente mais tarde.');
          break;
        default:
          toast.error(error.response.data?.detail || 'Erro ao processar requisição');
      }
    }
    
    return Promise.reject(error);
  }
);

// API endpoints
export const notasAPI = {
  listar: (params) => api.get('/api/v2/notas', { params }),
  obter: (id) => api.get(`/api/v2/notas/${id}`),
  sincronizar: (dias = 7) => api.post('/api/v2/notas/sync', null, { params: { dias } }),
};

export const pedidosAPI = {
  listar: (params) => api.get('/api/v2/pedidos', { params }),
  obter: (id) => api.get(`/api/v2/pedidos/${id}`),
  upload: (file, cliente) => {
    const formData = new FormData();
    formData.append('file', file);
    if (cliente) formData.append('cliente', cliente);
    
    return api.post('/api/v2/pedidos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const produtosAPI = {
  listar: (params) => api.get('/api/v2/produtos', { params }),
  buscar: (params) => api.get('/api/v2/produtos/buscar', { params }),
  obter: (id) => api.get(`/api/v2/produtos/${id}`),
  sincronizar: () => api.post('/api/v2/produtos/sync'),
};

export const healthAPI = {
  check: () => api.get('/health'),
  detailed: () => api.get('/health/detailed'),
};

export default api;