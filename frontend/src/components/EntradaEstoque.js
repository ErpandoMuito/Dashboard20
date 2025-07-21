import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { estoqueAPI } from '../services/api';
import { format } from 'date-fns';

const EntradaEstoque = () => {
  const [formData, setFormData] = useState({
    codigo_produto: '',
    quantidade: '',
    descricao: '',
    data: format(new Date(), "yyyy-MM-dd'T'HH:mm"),
    deposito: 'Geral'
  });

  const [loading, setLoading] = useState(false);
  const [produtoInfo, setProdutoInfo] = useState(null);
  const [buscandoProduto, setBuscandoProduto] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const buscarProduto = async () => {
    if (!formData.codigo_produto) {
      toast.warning('Digite o código do produto');
      return;
    }

    setBuscandoProduto(true);
    try {
      const produto = await estoqueAPI.buscarProduto(formData.codigo_produto.toUpperCase());
      setProdutoInfo(produto);
      toast.success(`Produto encontrado: ${produto.nome}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Produto não encontrado');
      setProdutoInfo(null);
    } finally {
      setBuscandoProduto(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.codigo_produto || !formData.quantidade) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }

    setLoading(true);
    try {
      const dataToSend = {
        ...formData,
        codigo_produto: formData.codigo_produto.toUpperCase(),
        quantidade: parseInt(formData.quantidade),
        data: new Date(formData.data).toISOString()
      };

      const response = await estoqueAPI.entradaEstoque(dataToSend);
      
      toast.success(response.message);
      
      // Limpar formulário
      setFormData({
        codigo_produto: '',
        quantidade: '',
        descricao: '',
        data: format(new Date(), "yyyy-MM-dd'T'HH:mm"),
        deposito: 'Geral'
      });
      setProdutoInfo(null);

      // Mostrar saldo atualizado se disponível
      if (response.saldo_atual !== null) {
        toast.info(`Saldo atual: ${response.saldo_atual} unidades`, {
          autoClose: 5000
        });
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Erro ao processar entrada';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 style={{ marginBottom: '24px' }}>Entrada de Estoque</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="codigo_produto">
            Código do Produto (PH) *
          </label>
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              id="codigo_produto"
              name="codigo_produto"
              value={formData.codigo_produto}
              onChange={handleChange}
              placeholder="Ex: PH-510"
              style={{ flex: 1 }}
              required
            />
            <button
              type="button"
              className="btn btn-primary"
              onClick={buscarProduto}
              disabled={buscandoProduto}
            >
              {buscandoProduto ? 'Buscando...' : 'Buscar'}
            </button>
          </div>
        </div>

        {produtoInfo && (
          <div className="alert alert-success">
            <strong>Produto:</strong> {produtoInfo.nome}<br />
            <strong>Unidade:</strong> {produtoInfo.unidade}<br />
            <strong>Saldo Atual:</strong> {produtoInfo.saldo} unidades
          </div>
        )}

        <div className="form-group">
          <label htmlFor="quantidade">
            Quantidade *
          </label>
          <input
            type="number"
            id="quantidade"
            name="quantidade"
            value={formData.quantidade}
            onChange={handleChange}
            placeholder="100"
            min="1"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="descricao">
            Descrição/Observações
          </label>
          <textarea
            id="descricao"
            name="descricao"
            value={formData.descricao}
            onChange={handleChange}
            placeholder="Entrada de produção, NF 12345, etc..."
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="data">
            Data e Horário *
          </label>
          <input
            type="datetime-local"
            id="data"
            name="data"
            value={formData.data}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="deposito">
            Depósito
          </label>
          <select
            id="deposito"
            name="deposito"
            value={formData.deposito}
            onChange={handleChange}
          >
            <option value="Geral">Geral</option>
            <option value="Fundição">Fundição</option>
            <option value="Matriz">Matriz</option>
            <option value="Filial">Filial</option>
          </select>
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
          style={{ width: '100%', marginTop: '20px' }}
        >
          {loading ? (
            <>
              Processando
              <span className="loading"></span>
            </>
          ) : (
            'Confirmar Entrada'
          )}
        </button>
      </form>
    </div>
  );
};

export default EntradaEstoque;