import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { estoqueAPI } from '../services/api';
import { format } from 'date-fns';

const AjusteEstoquePH510 = () => {
  const CODIGO_PRODUTO = 'PH-510';
  const [produtoInfo, setProdutoInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingInfo, setLoadingInfo] = useState(true);

  // Buscar informações do produto ao carregar
  useEffect(() => {
    buscarInfoProduto();
  }, []);

  const buscarInfoProduto = async () => {
    setLoadingInfo(true);
    try {
      const produto = await estoqueAPI.buscarProduto(CODIGO_PRODUTO);
      setProdutoInfo(produto);
    } catch (error) {
      console.error('Erro ao buscar produto:', error);
      toast.error('Erro ao buscar informações do produto PH-510');
    } finally {
      setLoadingInfo(false);
    }
  };

  const ajustarEstoque = async (quantidade, tipo) => {
    setLoading(true);
    try {
      const dataToSend = {
        codigo_produto: CODIGO_PRODUTO,
        quantidade: quantidade,
        tipo: tipo, // 'E' para entrada, 'S' para saída
        descricao: tipo === 'E' 
          ? `Adição de ${quantidade} unidade(s) via Dashboard` 
          : `Remoção de ${quantidade} unidade(s) via Dashboard`,
        data: new Date().toISOString(),
        deposito: 'FUNDIÇÃO'
      };

      let response;
      if (tipo === 'E') {
        response = await estoqueAPI.entradaEstoque(dataToSend);
      } else {
        response = await estoqueAPI.saidaEstoque(dataToSend);
      }
      
      toast.success(response.message);
      
      // Atualizar informações do produto
      await buscarInfoProduto();

      // Mostrar saldo atualizado
      if (response.saldo_atual !== null) {
        toast.info(`Saldo atualizado: ${response.saldo_atual} unidades`, {
          autoClose: 5000
        });
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Erro ao ajustar estoque';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleAdicionar = () => ajustarEstoque(1, 'E');
  const handleRemover = () => ajustarEstoque(1, 'S');

  if (loadingInfo) {
    return (
      <div className="card">
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <span className="loading"></span>
          <p>Carregando informações do produto...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 style={{ marginBottom: '24px', textAlign: 'center' }}>
        Ajuste de Estoque - {CODIGO_PRODUTO}
      </h2>
      
      {produtoInfo ? (
        <>
          <div className="product-info">
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Produto:</span>
                <span className="value">{produtoInfo.nome}</span>
              </div>
              <div className="info-item">
                <span className="label">Código:</span>
                <span className="value">{produtoInfo.codigo}</span>
              </div>
              <div className="info-item">
                <span className="label">Unidade:</span>
                <span className="value">{produtoInfo.unidade}</span>
              </div>
            </div>
            
            <div className="stock-display">
              <h3>Saldo Atual</h3>
              <div className="stock-value">{produtoInfo.saldo}</div>
              <div className="stock-label">unidades</div>
            </div>
          </div>

          <div className="action-buttons">
            <button
              className="btn btn-success"
              onClick={handleAdicionar}
              disabled={loading}
              title="Adicionar 1 unidade ao estoque"
            >
              <span className="btn-icon">+</span>
              Adicionar 1
            </button>
            
            <button
              className="btn btn-danger"
              onClick={handleRemover}
              disabled={loading || produtoInfo.saldo === 0}
              title="Remover 1 unidade do estoque"
            >
              <span className="btn-icon">-</span>
              Remover 1
            </button>
          </div>

          {loading && (
            <div className="loading-overlay">
              <span className="loading"></span>
              <p>Processando...</p>
            </div>
          )}
        </>
      ) : (
        <div className="alert alert-error">
          <p>Produto PH-510 não encontrado no sistema.</p>
          <button 
            className="btn btn-primary" 
            onClick={buscarInfoProduto}
            style={{ marginTop: '10px' }}
          >
            Tentar Novamente
          </button>
        </div>
      )}
    </div>
  );
};

export default AjusteEstoquePH510;