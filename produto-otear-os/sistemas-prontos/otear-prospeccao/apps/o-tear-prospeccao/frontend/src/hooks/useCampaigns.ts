import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import type { Campaign, CampaignStats } from '@/types/campaign'

export function useCampaigns(status?: string) {
  const qs = status ? `?status=${status}` : ''
  return useQuery({
    queryKey: ['campaigns', status],
    queryFn: () => api.get<Campaign[]>(`/campaigns${qs}`),
  })
}

export function useCampaign(id: string) {
  return useQuery({
    queryKey: ['campaign', id],
    queryFn: () => api.get<Campaign>(`/campaigns/${id}`),
    enabled: !!id,
  })
}

export function useCampaignStats(id: string) {
  return useQuery({
    queryKey: ['campaign-stats', id],
    queryFn: () => api.get<CampaignStats>(`/campaigns/${id}/stats`),
    enabled: !!id,
  })
}

export function useCreateCampaign() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: unknown) => api.post('/campaigns', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
}

export function useActivateCampaign() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.post(`/campaigns/${id}/activate`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
}

export function usePauseCampaign() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.post(`/campaigns/${id}/pause`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
}
