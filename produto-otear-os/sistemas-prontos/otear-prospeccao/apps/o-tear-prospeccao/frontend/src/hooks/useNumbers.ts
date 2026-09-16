import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import type { WhatsAppNumber, NumberHealth } from '@/types/number'

export function useNumbers() {
  return useQuery({
    queryKey: ['numbers'],
    queryFn: () => api.get<WhatsAppNumber[]>('/numbers'),
  })
}

export function useNumbersHealth() {
  return useQuery({
    queryKey: ['numbers-health'],
    queryFn: () => api.get<NumberHealth>('/numbers/health'),
    refetchInterval: 30_000,
  })
}

export function useCreateNumber() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { label: string; phone_number: string; daily_limit?: number }) =>
      api.post('/numbers', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['numbers'] }),
  })
}
