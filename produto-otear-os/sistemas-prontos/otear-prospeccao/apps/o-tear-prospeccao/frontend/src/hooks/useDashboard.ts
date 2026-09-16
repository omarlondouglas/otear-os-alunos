import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import type { DashboardStats, FunnelData } from '@/types/dashboard'

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.get<DashboardStats>('/dashboard/stats'),
    refetchInterval: 30_000,
  })
}

export function useFunnelData() {
  return useQuery({
    queryKey: ['dashboard-funnel'],
    queryFn: () => api.get<FunnelData>('/dashboard/funnel'),
    refetchInterval: 60_000,
  })
}
