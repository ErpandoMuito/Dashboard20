import axios from 'axios';

// Em produção, usar URL relativa. Em desenvolvimento, usar localhost
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api/v2' 
  : 'http://localhost:8000/api/v2';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para logs
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method.toUpperCase(), config.url, config.data);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const estoqueAPI = {
  // Entrada de estoque
  entradaEstoque: async (data) => {
    const response = await api.post('/estoque/entrada', data);
    return response.data;
  },

  // Buscar informações do produto
  buscarProduto: async (codigo) => {
    const response = await api.get(`/estoque/produto/${codigo}`);
    return response.data;
  },

  // Histórico de movimentações
  historicoProduto: async (codigo, limit = 10) => {
    const response = await api.get(`/estoque/historico/${codigo}?limit=${limit}`);
    return response.data;
  }
};

export default api;