import React, { useState, useEffect } from 'react';
import { estoqueAPI } from '../services/api';
import { toast } from 'react-toastify';
import './GestaoEstoque.css';

function GestaoEstoque() {
  const [produto, setProduto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [ajustando, setAjustando] = useState(false);

  // Busca inicial do produto PH-510
  useEffect(() => {
    buscarProdutoPH510();
  }, []);

  const buscarProdutoPH510 = async () => {
    setLoading(true);
    try {
      const data = await estoqueAPI.buscarProduto('PH-510');
      setProduto(data);
    } catch (error) {
      toast.error('Erro ao buscar produto PH-510');
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  const adicionarEstoque = async () => {
    setAjustando(true);
    try {
      const resultado = await estoqueAPI.adicionarPH510();
      if (resultado.success) {
        toast.success(resultado.message);
        // Atualiza dados do produto
        await buscarProdutoPH510();
      } else {
        toast.error(resultado.error || 'Erro ao adicionar estoque');
      }
    } catch (error) {
      toast.error('Erro ao adicionar estoque');
      console.error('Erro:', error);
    } finally {
      setAjustando(false);
    }
  };

  const removerEstoque = async () => {
    setAjustando(true);
    try {
      const resultado = await estoqueAPI.removerPH510();
      if (resultado.success) {
        toast.success(resultado.message);
        // Atualiza dados do produto
        await buscarProdutoPH510();
      } else {
        toast.error(resultado.error || 'Erro ao remover estoque');
      }
    } catch (error) {
      toast.error('Erro ao remover estoque');
      console.error('Erro:', error);
    } finally {
      setAjustando(false);
    }
  };

  if (loading) {
    return <div className="loading">Carregando produto...</div>;
  }

  if (!produto) {
    return <div className="error">Produto PH-510 não encontrado</div>;
  }

  const estoqueTotal = produto.saldo_estoque?.Total || 0;

  return (
    <div className="gestao-estoque">
      <h1>Gestão de Estoque - PH-510</h1>
      
      <div className="produto-info">
        <h2>{produto.nome}</h2>
        <p>Código: {produto.codigo}</p>
        <p>Unidade: {produto.unidade}</p>
        
        <div className="estoque-atual">
          <h3>Estoque Atual</h3>
          <div className="saldo-total">
            <span>Total:</span>
            <strong>{estoqueTotal} {produto.unidade}</strong>
          </div>
          
          {Object.entries(produto.saldo_estoque || {}).map(([deposito, saldo]) => {
            if (deposito === 'Total') return null;
            return (
              <div key={deposito} className="deposito">
                <span>{deposito}:</span>
                <span>{saldo} {produto.unidade}</span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="acoes">
        <button 
          onClick={adicionarEstoque}
          disabled={ajustando}
          className="btn btn-adicionar"
        >
          {ajustando ? 'Processando...' : 'Adicionar +1'}
        </button>
        
        <button 
          onClick={removerEstoque}
          disabled={ajustando || estoqueTotal <= 0}
          className="btn btn-remover"
        >
          {ajustando ? 'Processando...' : 'Remover -1'}
        </button>
      </div>

      <button 
        onClick={buscarProdutoPH510}
        disabled={loading}
        className="btn btn-atualizar"
      >
        Atualizar Dados
      </button>
    </div>
  );
}

export default GestaoEstoque;