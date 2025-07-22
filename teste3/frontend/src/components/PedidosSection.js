import React, { useState } from 'react';
import { usePedidos, useUploadPedido } from '../hooks/usePedidos';
import toast from 'react-hot-toast';

const PedidosSection = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [cliente, setCliente] = useState('');
  
  const { data: pedidos, isLoading } = usePedidos();
  const uploadMutation = useUploadPedido();
  
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        toast.error('Arquivo muito grande. Máximo: 10MB');
        return;
      }
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        toast.error('Apenas arquivos PDF são aceitos');
        return;
      }
      setSelectedFile(file);
    }
  };
  
  const handleUpload = () => {
    if (!selectedFile) {
      toast.error('Selecione um arquivo PDF');
      return;
    }
    
    uploadMutation.mutate(
      { file: selectedFile, cliente },
      {
        onSuccess: () => {
          setSelectedFile(null);
          setCliente('');
          // Reset file input
          document.getElementById('file-input').value = '';
        }
      }
    );
  };
  
  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Upload de Pedido</h3>
        
        <div className="space-y-4">
          <div className="form-group">
            <label className="form-label">Cliente</label>
            <input
              type="text"
              className="form-input"
              value={cliente}
              onChange={(e) => setCliente(e.target.value)}
              placeholder="Ex: VIBRACOUSTIC"
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Arquivo PDF</label>
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="form-input"
            />
            {selectedFile && (
              <p className="mt-2 text-sm text-gray-600">
                Selecionado: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)}MB)
              </p>
            )}
          </div>
          
          <button
            onClick={handleUpload}
            disabled={uploadMutation.isLoading || !selectedFile}
            className="btn btn-primary"
          >
            {uploadMutation.isLoading ? (
              <>
                <div className="spinner mr-2" />
                Processando...
              </>
            ) : (
              'Enviar Pedido'
            )}
          </button>
        </div>
      </div>
      
      {/* Pedidos List */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Pedidos Cadastrados</h3>
        
        {isLoading ? (
          <div className="flex justify-center py-8">
            <div className="spinner" />
          </div>
        ) : pedidos && pedidos.length > 0 ? (
          <div className="space-y-4">
            {pedidos.map((pedido) => (
              <div key={pedido.id} className="border rounded-lg p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium">
                      Pedido {pedido.numero || pedido.id}
                    </h4>
                    <p className="text-sm text-gray-600">
                      Cliente: {pedido.cliente}
                    </p>
                    {pedido.data_pedido && (
                      <p className="text-sm text-gray-600">
                        Data: {pedido.data_pedido}
                      </p>
                    )}
                    {pedido.itens && pedido.itens.length > 0 && (
                      <p className="text-sm text-gray-600">
                        {pedido.itens.length} itens
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">
                      {pedido.filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      Enviado em: {new Date(pedido.upload_date).toLocaleString('pt-BR')}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            Nenhum pedido cadastrado
          </p>
        )}
      </div>
    </div>
  );
};

export default PedidosSection;