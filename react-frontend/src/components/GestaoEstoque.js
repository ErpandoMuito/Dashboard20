import React, { useState, useEffect } from 'react';
import { estoqueAPI } from '../services/api';
import { toast } from 'react-toastify';
import './GestaoEstoque.css';

function GestaoEstoque() {
  const [showModal, setShowModal] = useState(false);
  const [codigoProduto, setCodigoProduto] = useState('');
  const [produto, setProduto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [ajustando, setAjustando] = useState(false);
  
  // Form fields
  const [tipo, setTipo] = useState('E'); // E=Entrada, S=Saída
  const [data, setData] = useState('');
  const [hora, setHora] = useState('');
  const [quantidade, setQuantidade] = useState('');
  const [precoUnitario, setPrecoUnitario] = useState('');
  const [observacoes, setObservacoes] = useState('');

  // Set data e hora para ontem
  useEffect(() => {
    const ontem = new Date();
    ontem.setDate(ontem.getDate() - 1);
    
    const dataFormatada = ontem.toLocaleDateString('pt-BR', {
      day: '2d',
      month: '2d',
      year: 'numeric'
    });
    setData(dataFormatada);
    
    const horaFormatada = ontem.toLocaleTimeString('pt-BR', {
      hour: '2d',
      minute: '2d',
      hour12: false
    });
    setHora(horaFormatada);
  }, [showModal]);

  // Atualizar preço quando produto for selecionado
  useEffect(() => {
    if (produto && produto.preco) {
      const precoFormatado = produto.preco.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).replace('.', ',');
      setPrecoUnitario(precoFormatado);
    }
  }, [produto]);

  const buscarProduto = async () => {
    if (!codigoProduto.trim()) {
      toast.error('Digite o código do produto');
      return;
    }

    setLoading(true);
    try {
      const data = await estoqueAPI.buscarProduto(codigoProduto.toUpperCase());
      setProduto(data);
      setShowModal(true);
    } catch (error) {
      toast.error(`Produto ${codigoProduto} não encontrado`);
      setProduto(null);
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSalvar = async () => {
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
        observacoes || `${tipo === 'E' ? 'Entrada' : 'Saída'} manual - ${data} ${hora}`
      );

      if (resultado.success) {
        toast.success(resultado.message);
        handleFechar();
        // Limpar campos
        setCodigoProduto('');
        setProduto(null);
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

  const handleFechar = () => {
    setShowModal(false);
    setQuantidade('');
    setObservacoes('');
    setTipo('E');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !showModal) {
      buscarProduto();
    }
  };

  return (
    <div className="gestao-estoque-container">
      <div className="busca-section">
        <h1>Gestão de Estoque</h1>
        <div className="busca-form">
          <input
            type="text"
            value={codigoProduto}
            onChange={(e) => setCodigoProduto(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite o código do produto (ex: PH-510)"
            className="input-busca"
          />
          <button 
            onClick={buscarProduto}
            disabled={loading}
            className="btn-buscar"
          >
            {loading ? 'Buscando...' : 'Buscar Produto'}
          </button>
        </div>
      </div>

      {showModal && produto && (
        <div className="modal-overlay" onClick={handleFechar}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Lançamento de estoque</h2>
              <button className="btn-fechar" onClick={handleFechar}>
                fechar ×
              </button>
            </div>

            <div className="produto-info-modal">
              <h3>{produto.nome}</h3>
              <p>Código: {produto.codigo} | Unidade: {produto.unidade}</p>
              <p className="estoque-atual">Estoque atual: {produto.saldo_estoque?.Total || 0} {produto.unidade}</p>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label>Tipo</label>
                <select 
                  value={tipo} 
                  onChange={(e) => setTipo(e.target.value)}
                  className="select-tipo"
                >
                  <option value="E">Entrada</option>
                  <option value="S">Saída</option>
                </select>
              </div>

              <div className="form-group">
                <label>Data</label>
                <div className="input-with-icon">
                  <input
                    type="text"
                    value={data}
                    onChange={(e) => setData(e.target.value)}
                    className="input-data"
                  />
                  <span className="icon-calendar">📅</span>
                </div>
              </div>

              <div className="form-group">
                <label>Hora</label>
                <input
                  type="text"
                  value={hora}
                  onChange={(e) => setHora(e.target.value)}
                  className="input-hora"
                />
              </div>

              <div className="form-group">
                <label>Quantidade</label>
                <input
                  type="number"
                  value={quantidade}
                  onChange={(e) => setQuantidade(e.target.value)}
                  placeholder=""
                  className="input-quantidade"
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label>Preço unitário</label>
                <input
                  type="text"
                  value={precoUnitario}
                  onChange={(e) => setPrecoUnitario(e.target.value)}
                  className="input-preco"
                />
              </div>
            </div>

            <div className="form-group full-width">
              <label>Observações</label>
              <textarea
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
                className="textarea-observacoes"
                rows="4"
              />
            </div>

            <div className="modal-footer">
              <button 
                onClick={handleSalvar}
                disabled={ajustando || !quantidade}
                className="btn-salvar"
              >
                {ajustando ? 'Salvando...' : 'salvar'}
              </button>
              <button 
                onClick={handleFechar}
                className="btn-cancelar"
              >
                cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default GestaoEstoque;