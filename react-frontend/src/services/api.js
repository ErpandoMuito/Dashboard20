import axios from 'axios';

// Em produção, usa a mesma origem (já que Flask serve tudo)
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  (window.location.hostname === 'localhost' ? 'http://localhost:8000' : '');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const estoqueAPI = {
  // Buscar produto por código
  buscarProduto: async (codigo) => {
    const response = await api.get(`/api/v2/estoque/produto/${codigo}`);
    return response.data;
  },

  // Ajustar estoque genérico
  ajustarEstoque: async (produtoId, quantidade, tipo, observacoes) => {
    const response = await api.post('/api/v2/estoque/ajustar', {
      produto_id: produtoId,
      quantidade,
      tipo,
      observacoes,
    });
    return response.data;
  },

  // Adicionar 1 unidade ao PH-510
  adicionarPH510: async () => {
    const response = await api.post('/api/v2/estoque/ph510/adicionar');
    return response.data;
  },

  // Remover 1 unidade do PH-510
  removerPH510: async () => {
    const response = await api.post('/api/v2/estoque/ph510/remover');
    return response.data;
  },
};

export default api;