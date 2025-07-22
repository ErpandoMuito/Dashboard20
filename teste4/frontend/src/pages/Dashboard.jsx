/**
 * Dashboard page with overview metrics
 */
import React from 'react';
import { useNotas, usePedidos, useProdutos } from '../hooks/useApi';
import { CardSkeleton } from '../components/common/LoadingState';
import { 
  DocumentTextIcon, 
  ClipboardDocumentListIcon,
  CubeIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';

function Dashboard() {
  const { data: notasData, isLoading: notasLoading } = useNotas({ page_size: 1 });
  const { data: pedidosData, isLoading: pedidosLoading } = usePedidos({ page_size: 1 });
  const { data: produtosData, isLoading: produtosLoading } = useProdutos({ page_size: 1 });
  
  const stats = [
    {
      name: 'Total de Notas',
      value: notasData?.data?.total || 0,
      icon: DocumentTextIcon,
      color: 'bg-blue-500',
      loading: notasLoading,
    },
    {
      name: 'Pedidos Ativos',
      value: pedidosData?.data?.total || 0,
      icon: ClipboardDocumentListIcon,
      color: 'bg-green-500',
      loading: pedidosLoading,
    },
    {
      name: 'Produtos',
      value: produtosData?.data?.total || 0,
      icon: CubeIcon,
      color: 'bg-purple-500',
      loading: produtosLoading,
    },
    {
      name: 'Faturamento',
      value: 'R$ 0,00',
      icon: CurrencyDollarIcon,
      color: 'bg-yellow-500',
      loading: false,
    },
  ];
  
  if (notasLoading && pedidosLoading && produtosLoading) {
    return (
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <CardSkeleton count={4} />
      </div>
    );
  }
  
  return (
    <div>
      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className={`flex-shrink-0 ${stat.color} rounded-md p-3`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.name}
                    </dt>
                    <dd className="text-lg font-semibold text-gray-900">
                      {stat.loading ? (
                        <span className="animate-pulse bg-gray-200 rounded h-6 w-20 inline-block" />
                      ) : (
                        stat.value
                      )}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Recent activity */}
      <div className="mt-8 grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Recent Notas */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Notas Recentes</h3>
          </div>
          <div className="p-6">
            <p className="text-sm text-gray-500">
              Visualização de notas recentes em desenvolvimento
            </p>
          </div>
        </div>
        
        {/* Recent Pedidos */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Pedidos Recentes</h3>
          </div>
          <div className="p-6">
            <p className="text-sm text-gray-500">
              Visualização de pedidos recentes em desenvolvimento
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;