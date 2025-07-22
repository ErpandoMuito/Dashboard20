import React, { useState } from 'react';
import { useNotas } from '../hooks/useNotas';
import { format, parseISO } from 'date-fns';

const NotasTable = () => {
  const [filtros, setFiltros] = useState({
    data_inicial: null,
    data_final: null,
  });
  
  const { data: notas, isLoading, error } = useNotas(filtros);
  
  const formatDate = (dateString) => {
    try {
      return format(parseISO(dateString), 'dd/MM/yyyy');
    } catch {
      return dateString;
    }
  };
  
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };
  
  if (isLoading) {
    return (
      <div className="card">
        <div className="flex justify-center items-center py-8">
          <div className="spinner" />
          <span className="ml-2">Carregando notas...</span>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="card">
        <div className="text-red-600">
          Erro ao carregar notas: {error.message}
        </div>
      </div>
    );
  }
  
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Notas Fiscais</h2>
      
      {/* Filtros */}
      <div className="mb-6 flex gap-4">
        <div className="form-group">
          <label className="form-label">Data Inicial</label>
          <input
            type="date"
            className="form-input"
            onChange={(e) => setFiltros(prev => ({ 
              ...prev, 
              data_inicial: e.target.value ? format(new Date(e.target.value), 'dd/MM/yyyy') : null 
            }))}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Data Final</label>
          <input
            type="date"
            className="form-input"
            onChange={(e) => setFiltros(prev => ({ 
              ...prev, 
              data_final: e.target.value ? format(new Date(e.target.value), 'dd/MM/yyyy') : null 
            }))}
          />
        </div>
      </div>
      
      {/* Tabela */}
      <div className="overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>Número</th>
              <th>Data</th>
              <th>Cliente</th>
              <th>Valor</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {notas && notas.length > 0 ? (
              notas.map((item) => {
                const nota = item.nota_fiscal || item;
                return (
                  <tr key={nota.id}>
                    <td>{nota.numero}</td>
                    <td>{formatDate(nota.data_emissao)}</td>
                    <td>{nota.nome || nota.cliente?.nome || 'N/A'}</td>
                    <td>{formatCurrency(nota.valor_total || nota.totais?.total)}</td>
                    <td>
                      <span className={`badge ${
                        nota.situacao === 1 ? 'badge-success' : 
                        nota.situacao === 2 ? 'badge-error' : 
                        'badge-warning'
                      }`}>
                        {nota.situacao === 1 ? 'Autorizada' : 
                         nota.situacao === 2 ? 'Cancelada' : 
                         'Pendente'}
                      </span>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="5" className="text-center text-gray-500 py-8">
                  Nenhuma nota encontrada
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      {notas && notas.length > 0 && (
        <div className="mt-4 text-sm text-gray-600">
          Total: {notas.length} notas
        </div>
      )}
    </div>
  );
};

export default NotasTable;