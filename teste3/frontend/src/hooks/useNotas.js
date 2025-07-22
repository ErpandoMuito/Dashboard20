import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notasAPI } from '../services/api';
import toast from 'react-hot-toast';

export const useNotas = (filtros = {}) => {
  return useQuery({
    queryKey: ['notas', filtros],
    queryFn: () => notasAPI.listar(filtros),
    select: (response) => response.data.data || [],
    onError: (error) => {
      console.error('Erro ao carregar notas:', error);
    },
  });
};

export const useNota = (id) => {
  return useQuery({
    queryKey: ['nota', id],
    queryFn: () => notasAPI.obter(id),
    select: (response) => response.data.data,
    enabled: !!id,
  });
};

export const useSincronizarNotas = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (dias) => notasAPI.sincronizar(dias),
    onSuccess: (response) => {
      const data = response.data;
      toast.success(`${data.notas_salvas} notas sincronizadas com sucesso!`);
      
      // Invalida cache de notas
      queryClient.invalidateQueries({ queryKey: ['notas'] });
    },
    onError: (error) => {
      toast.error('Erro ao sincronizar notas');
      console.error('Erro:', error);
    },
  });
};