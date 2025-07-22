import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pedidosAPI } from '../services/api';
import toast from 'react-hot-toast';

export const usePedidos = (cliente = null) => {
  return useQuery({
    queryKey: ['pedidos', cliente],
    queryFn: () => pedidosAPI.listar({ cliente }),
    select: (response) => response.data.pedidos || [],
  });
};

export const usePedido = (id) => {
  return useQuery({
    queryKey: ['pedido', id],
    queryFn: () => pedidosAPI.obter(id),
    select: (response) => response.data.data,
    enabled: !!id,
  });
};

export const useUploadPedido = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ file, cliente }) => pedidosAPI.upload(file, cliente),
    onSuccess: (response) => {
      const data = response.data;
      toast.success(`Pedido ${data.pedido_id} processado com sucesso!`);
      
      // Invalida cache
      queryClient.invalidateQueries({ queryKey: ['pedidos'] });
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Erro ao processar pedido';
      toast.error(message);
    },
  });
};