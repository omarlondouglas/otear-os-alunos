import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, prospectApi } from '@/services/api'
import type { LeadListResponse, ImportResponse } from '@/types/lead'

export function useLeads(params?: {
  classification?: string
  outreach_status?: string
  min_score?: number
  search?: string
  page?: number
  per_page?: number
}) {
  const qs = new URLSearchParams()
  if (params?.classification) qs.set('classification', params.classification)
  if (params?.outreach_status) qs.set('outreach_status', params.outreach_status)
  if (params?.min_score) qs.set('min_score', String(params.min_score))
  if (params?.search) qs.set('search', params.search)
  qs.set('page', String(params?.page || 1))
  qs.set('per_page', String(params?.per_page || 25))

  return useQuery({
    queryKey: ['leads', params],
    queryFn: () => api.get<LeadListResponse>(`/leads?${qs}`),
  })
}

export function useImportLeads() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (file: File) => api.upload<ImportResponse>('/leads/import', file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leads'] }),
  })
}

export function useImportLatestProspectLeads() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (stage: 'leads' | 'enriched' = 'enriched') => {
      const status = stage === 'leads' ? 'raw' : 'enriched'
      const data = await prospectApi.get<{ leads: unknown[] }>(`/leads?status=${status}`)
      const file = new File([JSON.stringify({ leads: data.leads || [] })], `${stage}.json`, {
        type: 'application/json',
      })
      return api.upload<ImportResponse>('/leads/import', file)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leads'] }),
  })
}

export function useBulkAction() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { lead_ids: string[]; action: string; value?: string }) =>
      api.post('/leads/bulk', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leads'] }),
  })
}
