import React, { useState } from 'react';
import NotasTable from './NotasTable';
import PedidosSection from './PedidosSection';
import HealthStatus from './HealthStatus';
import SyncButton from './SyncButton';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('notas');
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              Dashboard v2.0
            </h1>
            <div className="flex items-center gap-4">
              <HealthStatus />
              <SyncButton />
            </div>
          </div>
        </div>
      </header>
      
      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="container mx-auto px-4">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('notas')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'notas'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Notas Fiscais
            </button>
            <button
              onClick={() => setActiveTab('pedidos')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'pedidos'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Pedidos
            </button>
            <button
              onClick={() => setActiveTab('produtos')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'produtos'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Produtos
            </button>
          </div>
        </div>
      </nav>
      
      {/* Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'notas' && <NotasTable />}
        {activeTab === 'pedidos' && <PedidosSection />}
        {activeTab === 'produtos' && (
          <div className="card">
            <p className="text-gray-500">Seção de produtos em desenvolvimento...</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;