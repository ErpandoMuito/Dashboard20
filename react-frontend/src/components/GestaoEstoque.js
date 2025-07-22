import React, { useState } from 'react';
import { estoqueAPI } from '../services/api';
import { toast } from 'react-toastify';
import './GestaoEstoque.css';

function GestaoEstoque() {
  const [codigoProduto, setCodigoProduto] = useState('');
  const [quantidade, setQuantidade] = useState('');
  const [descricao, setDescricao] = useState('');
  const [produto, setProduto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [ajustando, setAjustando] = useState(false);

  const buscarProduto = async () => {
    if (!codigoProduto.trim()) {
      toast.error('Digite o código do produto');
      return;
    }

    setLoading(true);
    try {
      const data = await estoqueAPI.buscarProduto(codigoProduto.toUpperCase());
      setProduto(data);
      toast.success(`Produto ${data.nome} encontrado!`);
    } catch (error) {
      toast.error(`Produto ${codigoProduto} não encontrado`);
      setProduto(null);
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  const ajustarEstoque = async (tipo) => {
    if (!produto) {
      toast.error('Busque um produto primeiro');
      return;
    }

    if (!quantidade || quantidade <= 0) {
      toast.error('Digite uma quantidade válida');
      return;
    }

    setAjustando(true);
    try {
      const resultado = await estoqueAPI.ajustarEstoque(
        produto.id,
        parseInt(quantidade),
        tipo,
        descricao || `${tipo === 'E' ? 'Entrada' : 'Saída'} manual via Dashboard`
      );

      if (resultado.success) {
        toast.success(resultado.message);
        // Limpa os campos
        setQuantidade('');
        setDescricao('');
        // Busca o produto novamente para atualizar o estoque
        await buscarProduto();
      } else {
        toast.error(resultado.error || 'Erro ao ajustar estoque');
      }
    } catch (error) {
      toast.error('Erro ao ajustar estoque');
      console.error('Erro:', error);
    } finally {
      setAjustando(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      buscarProduto();
    }
  };

  return (
    <div className="gestao-estoque">
      <h1>Gestão de Estoque</h1>
      
      <div className="busca-produto">
        <div className="campo-busca">
          <label>Código do Produto:</label>
          <input
            type="text"
            value={codigoProduto}
            onChange={(e) => setCodigoProduto(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ex: PH-510"
            className="input-codigo"
          />
          <button 
            onClick={buscarProduto}
            disabled={loading}
            className="btn btn-buscar"
          >
            {loading ? 'Buscando...' : 'Buscar Produto'}
          </button>
        </div>
      </div>

      {produto && (
        <>
          <div className="produto-info">
            <h2>{produto.nome}</h2>
            <p>Código: {produto.codigo}</p>
            <p>Unidade: {produto.unidade}</p>
            
            <div className="estoque-atual">
              <h3>Estoque Atual</h3>
              <div className="saldo-total">
                <span>Total:</span>
                <strong>{produto.saldo_estoque?.Total || 0} {produto.unidade}</strong>
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

          <div className="ajuste-estoque">
            <h3>Ajustar Estoque</h3>
            
            <div className="campo">
              <label>Quantidade:</label>
              <input
                type="number"
                value={quantidade}
                onChange={(e) => setQuantidade(e.target.value)}
                placeholder="Digite a quantidade"
                min="1"
                className="input-quantidade"
              />
            </div>

            <div className="campo">
              <label>Descrição (opcional):</label>
              <input
                type="text"
                value={descricao}
                onChange={(e) => setDescricao(e.target.value)}
                placeholder="Ex: Compra de fornecedor X"
                className="input-descricao"
              />
            </div>

            <div className="acoes">
              <button 
                onClick={() => ajustarEstoque('E')}
                disabled={ajustando || !quantidade}
                className="btn btn-adicionar"
              >
                {ajustando ? 'Processando...' : `Adicionar ${quantidade || 0}`}
              </button>
              
              <button 
                onClick={() => ajustarEstoque('S')}
                disabled={ajustando || !quantidade || produto.saldo_estoque?.Total < quantidade}
                className="btn btn-remover"
              >
                {ajustando ? 'Processando...' : `Remover ${quantidade || 0}`}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default GestaoEstoque;