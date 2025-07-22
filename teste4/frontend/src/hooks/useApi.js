/**
 * Custom hooks for API operations with React Query
 */
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

// Query keys
export const queryKeys = {
  health: ['health'],
  healthDetailed: ['health', 'detailed'],
  notas: ['notas'],
  nota: (id) => ['notas', id],
  pedidos: ['pedidos'],
  pedido: (id) => ['pedidos', id],
  produtos: ['produtos'],
  produto: (codigo) => ['produtos', codigo],
  abatimento: (codigo) => ['produtos', codigo, 'abatimento'],
};

// Health hooks
export function useHealth() {
  return useQuery(
    queryKeys.health,
    () => apiService.healthCheck(),
    {
      refetchInterval: 60000, // Check every minute
      retry: 1,
    }
  );
}

export function useDetailedHealth() {
  return useQuery(
    queryKeys.healthDetailed,
    () => apiService.detailedHealthCheck(),
    {
      refetchInterval: 300000, // Check every 5 minutes
      retry: 1,
    }
  );
}

// Notas Fiscais hooks
export function useNotas(params = {}) {
  return useQuery(
    [...queryKeys.notas, params],
    () => apiService.notas.list(params),
    {
      keepPreviousData: true,
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );
}

export function useNota(id) {
  return useQuery(
    queryKeys.nota(id),
    () => apiService.notas.get(id),
    {
      enabled: !!id,
      staleTime: 5 * 60 * 1000,
    }
  );
}

export function useCreateNota() {
  const queryClient = useQueryClient();
  
  return useMutation(
    (data) => apiService.notas.create(data),
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(queryKeys.notas);
        toast.success(`Nota fiscal ${data.data.numero} criada com sucesso!`);
      },
      onError: (error) => {
        console.error('Error creating nota:', error);
      },
    }
  );
}

export function useUpdateNota(id) {
  const queryClient = useQueryClient();
  
  return useMutation(
    (data) => apiService.notas.update(id, data),
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(queryKeys.nota(id));
        queryClient.invalidateQueries(queryKeys.notas);
        toast.success('Nota fiscal atualizada com sucesso!');
      },
      onError: (error) => {
        console.error('Error updating nota:', error);
      },
    }
  );
}

export function useDeleteNota() {
  const queryClient = useQueryClient();
  
  return useMutation(
    (id) => apiService.notas.delete(id),
    {
      onSuccess: (_, id) => {
        queryClient.invalidateQueries(queryKeys.notas);
        queryClient.removeQueries(queryKeys.nota(id));
        toast.success('Nota fiscal excluída com sucesso!');
      },
      onError: (error) => {
        console.error('Error deleting nota:', error);
      },
    }
  );
}

export function useSyncNotas() {
  const queryClient = useQueryClient();
  
  return useMutation(
    () => apiService.notas.sync(),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(queryKeys.notas);
        toast.success('Sincronização iniciada em background!');
      },
      onError: (error) => {
        console.error('Error syncing notas:', error);
      },
    }
  );
}

// Pedidos hooks
export function usePedidos(params = {}) {
  return useQuery(
    [...queryKeys.pedidos, params],
    () => apiService.pedidos.list(params),
    {
      keepPreviousData: true,
      staleTime: 5 * 60 * 1000,
    }
  );
}

export function useUploadPedido() {
  const queryClient = useQueryClient();
  
  return useMutation(
    (file) => apiService.pedidos.upload(file),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(queryKeys.pedidos);
        toast.success('Pedido enviado com sucesso!');
      },
      onError: (error) => {
        console.error('Error uploading pedido:', error);
      },
    }
  );
}

// Produtos hooks
export function useProdutos(params = {}) {
  return useQuery(
    [...queryKeys.produtos, params],
    () => apiService.produtos.list(params),
    {
      keepPreviousData: true,
      staleTime: 5 * 60 * 1000,
    }
  );
}

export function useAbatimento(codigo) {
  return useQuery(
    queryKeys.abatimento(codigo),
    () => apiService.produtos.abatimento(codigo),
    {
      enabled: !!codigo,
      staleTime: 2 * 60 * 1000, // 2 minutes
    }
  );
}

// Generic error handler
export function handleApiError(error, defaultMessage = 'Ocorreu um erro') {
  const message = error?.response?.data?.message || defaultMessage;
  toast.error(message);
  return message;
}