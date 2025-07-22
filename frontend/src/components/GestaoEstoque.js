import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { estoqueAPI } from '../services/api';
import { format } from 'date-fns';

const GestaoEstoque = () => {
  const [formData, setFormData] = useState({
    codigo_produto: '',
    quantidade: '',
    tipo: 'E', // E=Entrada, S=Saída
    descricao: '',
    data: format(new Date(), "yyyy-MM-dd'T'HH:mm"),
    deposito: 'FUNDIÇÃO'
  });

  const [loading, setLoading] = useState(false);
  const [produtoInfo, setProdutoInfo] = useState(null);
  const [buscandoProduto, setBuscandoProduto] = useState(false);
  const [produtosCache, setProdutosCache] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Carregar produtos do cache ao montar
  useEffect(() => {
    carregarProdutosCache();
  }, []);

  const carregarProdutosCache = async () => {
    try {
      const response = await estoqueAPI.listarProdutosCache();
      setProdutosCache(response.produtos || []);
    } catch (error) {
      console.error('Erro ao carregar cache:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    if (name === 'codigo_produto') {
      setFormData(prev => ({ ...prev, [name]: value.toUpperCase() }));
      
      // Mostrar sugestões se começar com PH
      if (value.toUpperCase().startsWith('PH')) {
        setShowSuggestions(true);
      } else {
        setShowSuggestions(false);
      }
    } else if (name === 'quantidade') {
      const numero = value.replace(/\D/g, '');
      setFormData(prev => ({ ...prev, [name]: numero }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const selecionarProduto = (produto) => {
    setFormData(prev => ({ ...prev, codigo_produto: produto.codigo }));
    setProdutoInfo(produto);
    setShowSuggestions(false);
    toast.success(`Produto selecionado: ${produto.nome}`);
  };

  const buscarProduto = async () => {
    if (!formData.codigo_produto) {
      toast.warning('Digite o código do produto');
      return;
    }

    setBuscandoProduto(true);
    try {
      const produto = await estoqueAPI.buscarProduto(formData.codigo_produto);
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

    if (!formData.codigo_produto || !formData.quantidade || !formData.descricao) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }
    
    if (parseInt(formData.quantidade) <= 0) {
      toast.error('A quantidade deve ser maior que zero');
      return;
    }

    setLoading(true);
    try {
      const dataToSend = {
        ...formData,
        quantidade: parseInt(formData.quantidade),
        data: new Date(formData.data).toISOString()
      };

      let response;
      if (formData.tipo === 'E') {
        response = await estoqueAPI.entradaEstoque(dataToSend);
      } else {
        response = await estoqueAPI.saidaEstoque(dataToSend);
      }
      
      toast.success(response.message);
      
      // Limpar formulário mantendo o tipo
      setFormData(prev => ({
        codigo_produto: '',
        quantidade: '',
        tipo: prev.tipo,
        descricao: '',
        data: format(new Date(), "yyyy-MM-dd'T'HH:mm"),
        deposito: 'FUNDIÇÃO'
      }));
      setProdutoInfo(null);

      // Mostrar saldo atualizado
      if (response.saldo_atual !== null) {
        toast.info(`Saldo atualizado: ${response.saldo_atual} unidades`, {
          autoClose: 5000
        });
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Erro ao processar operação';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const popularCache = async () => {
    if (!window.confirm('Deseja popular o cache com produtos PH-001 até PH-999? Isso pode demorar alguns minutos.')) {
      return;
    }

    setLoading(true);
    try {
      const response = await estoqueAPI.popularCache(1, 999);
      toast.success(response.message);
      
      // Recarregar lista
      await carregarProdutosCache();
    } catch (error) {
      toast.error('Erro ao popular cache');
    } finally {
      setLoading(false);
    }
  };

  // Filtrar sugestões
  const sugestoes = produtosCache.filter(p => 
    p.codigo.includes(formData.codigo_produto)
  ).slice(0, 10);

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2>Gestão de Estoque</h2>
        <button
          className="btn btn-secondary"
          onClick={popularCache}
          disabled={loading}
          title="Popular cache com produtos PH"
        >
          Popular Cache PH
        </button>
      </div>
      
      <form onSubmit={handleSubmit}>
        {/* Tipo de Operação */}
        <div className="form-group">
          <label>Tipo de Operação *</label>
          <div className="radio-group">
            <label className="radio-label">
              <input
                type="radio"
                name="tipo"
                value="E"
                checked={formData.tipo === 'E'}
                onChange={handleChange}
              />
              <span>Entrada (Adicionar)</span>
            </label>
            <label className="radio-label">
              <input
                type="radio"
                name="tipo"
                value="S"
                checked={formData.tipo === 'S'}
                onChange={handleChange}
              />
              <span>Saída (Remover)</span>
            </label>
          </div>
        </div>

        {/* Código do Produto */}
        <div className="form-group">
          <label htmlFor="codigo_produto">
            Código do Produto *
          </label>
          <div style={{ display: 'flex', gap: '10px', position: 'relative' }}>
            <input
              type="text"
              id="codigo_produto"
              name="codigo_produto"
              value={formData.codigo_produto}
              onChange={handleChange}
              placeholder="Ex: PH-510"
              style={{ flex: 1 }}
              autoComplete="off"
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

            {/* Sugestões */}
            {showSuggestions && sugestoes.length > 0 && (
              <div className="suggestions">
                {sugestoes.map(produto => (
                  <div
                    key={produto.codigo}
                    className="suggestion-item"
                    onClick={() => selecionarProduto(produto)}
                  >
                    <strong>{produto.codigo}</strong> - {produto.nome}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Info do Produto */}
        {produtoInfo && (
          <div className="alert alert-info">
            <strong>Produto:</strong> {produtoInfo.nome}<br />
            <strong>Código:</strong> {produtoInfo.codigo}<br />
            <strong>Unidade:</strong> {produtoInfo.unidade}<br />
            <strong>Saldo Atual:</strong> {produtoInfo.saldo} unidades
          </div>
        )}

        {/* Quantidade */}
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
            placeholder="Ex: 100"
            min="1"
            step="1"
            required
          />
        </div>

        {/* Descrição */}
        <div className="form-group">
          <label htmlFor="descricao">
            Descrição/Observações *
          </label>
          <textarea
            id="descricao"
            name="descricao"
            value={formData.descricao}
            onChange={handleChange}
            placeholder={formData.tipo === 'E' 
              ? "Ex: Produção - 22/07 - Segunda - Rodrigo" 
              : "Ex: Envio para cliente XYZ"}
            rows="3"
            required
          />
        </div>

        {/* Data e Hora */}
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

        {/* Botão Submit */}
        <button
          type="submit"
          className={`btn ${formData.tipo === 'E' ? 'btn-success' : 'btn-danger'}`}
          disabled={loading}
          style={{ width: '100%', marginTop: '20px' }}
        >
          {loading ? (
            <>
              Processando
              <span className="loading"></span>
            </>
          ) : (
            formData.tipo === 'E' ? 'Confirmar Entrada' : 'Confirmar Saída'
          )}
        </button>
      </form>
    </div>
  );
};

export default GestaoEstoque;