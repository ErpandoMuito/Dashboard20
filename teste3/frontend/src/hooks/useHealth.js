import { useQuery } from '@tanstack/react-query';
import { healthAPI } from '../services/api';

export const useHealth = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: healthAPI.check,
    refetchInterval: 30000, // Check every 30s
    retry: 1,
    select: (response) => response.data,
  });
};

export const useDetailedHealth = () => {
  return useQuery({
    queryKey: ['health-detailed'],
    queryFn: healthAPI.detailed,
    refetchInterval: 60000, // Check every minute
    retry: 1,
    select: (response) => response.data,
  });
};