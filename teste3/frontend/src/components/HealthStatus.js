import React from 'react';
import { useHealth } from '../hooks/useHealth';

const HealthStatus = () => {
  const { data: health, isLoading, error } = useHealth();
  
  const getStatusColor = () => {
    if (isLoading) return 'bg-gray-400';
    if (error || !health) return 'bg-red-500';
    if (health.status === 'healthy') return 'bg-green-500';
    if (health.status === 'degraded') return 'bg-yellow-500';
    return 'bg-red-500';
  };
  
  const getStatusText = () => {
    if (isLoading) return 'Verificando...';
    if (error || !health) return 'Offline';
    return health.status === 'healthy' ? 'Online' : 'Degradado';
  };
  
  return (
    <div className="flex items-center space-x-2">
      <div className={`w-3 h-3 rounded-full ${getStatusColor()} animate-pulse`} />
      <span className="text-sm text-gray-600">{getStatusText()}</span>
    </div>
  );
};

export default HealthStatus;