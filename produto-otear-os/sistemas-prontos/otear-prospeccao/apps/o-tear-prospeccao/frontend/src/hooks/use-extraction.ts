import { useQuery, useMutation } from '@tanstack/react-query'
import { prospectApi } from '@/services/api'

export type ProspectLead = {
  google?: {
    name?: string
    category?: string
    rating?: number
    address?: string
    phone?: string
    website?: string
    maps_url?: string
  }
  instagram?: {
    handle?: string
    profile_url?: string
    bio?: string
    bio_link?: string
    followers?: number
    following?: number
    posts_count?: number
    engagement_rate?: number
    avg_likes?: number
    avg_comments?: number
    recent_posts?: Array<{
      url?: string
      type?: string
      likes?: number
      comments?: number
      caption?: string
      hashtags?: string[]
    }>
    content_metrics?: {
      video_count?: number
      photo_count?: number
      carousel_count?: number
      video_ratio?: number
      top_hashtags?: string[]
      avg_caption_length?: number
      posts_with_cta?: number
      cta_ratio?: number
    }
  } | null
  website_audit?: {
    status?: string
    score?: number
    final_url?: string
    problems?: string[]
    ads?: {
      status?: 'tracking_detected' | 'analytics_only' | 'unknown'
      has_tracking_pixels?: boolean
      has_paid_ads_signals?: boolean
      platforms?: string[]
      signals?: string[]
      meta_ads_library_url?: string
      google_ads_transparency_url?: string
      domain?: string
      note?: string
    }
  } | null
  cnpj_info?: {
    cnpj?: string
    razao_social?: string
    nome_fantasia?: string
    owners?: Array<{
      name?: string
      role?: string
    }>
  } | null
  score?: {
    total?: number
    classification?: 'hot' | 'warm' | 'cold'
  }
  status?: string
  approach_script?: string
}

export function useScrapeGoogleMaps() {
  return useMutation({
    mutationFn: (data: { query: string; location: string; limit: number }) =>
      prospectApi.post<{ job_id: string; status: string }>('/scrape/maps', data),
  })
}

export function useScrapeGoogleMapsSync() {
  return useMutation({
    mutationFn: (data: { query: string; location: string; limit: number }) =>
      prospectApi.post<{ status: string; total: number; total_found?: number; duplicates_skipped?: number; leads: ProspectLead[] }>('/scrape/maps/sync', data),
  })
}

export function useJobStatus(jobId: string) {
  return useQuery({
    queryKey: ['job-status', jobId],
    queryFn: () => prospectApi.get<{ status: string; result?: unknown; error?: string }>(`/scrape/status/${jobId}`),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const data = query.state.data
      if (data && (data.status === 'completed' || data.status === 'failed')) return false
      return 2000
    },
  })
}

export function useEnrichLeads() {
  return useMutation({
    mutationFn: (data: { leads_file?: string }) =>
      prospectApi.post<{ status: string; total: number; json_path: string; leads: ProspectLead[] }>('/enrich', data),
  })
}

export function useAnalyzeInstagram() {
  return useMutation({
    mutationFn: (data: { leads_file?: string; posts_to_analyze?: number }) =>
      prospectApi.post<{ status: string; total: number; hot: number; warm: number; cold: number; json_path: string; leads: ProspectLead[] }>('/analyze', data),
  })
}

export function useGenerateReport() {
  return useMutation({
    mutationFn: (data: { leads_file?: string; title?: string }) =>
      prospectApi.post<{ status: string; report_path: string; csv_path: string; summary: unknown }>('/reports/generate', data),
  })
}

export function useListReports() {
  return useQuery({
    queryKey: ['prospect-reports'],
    queryFn: () => prospectApi.get<{ total: number; reports: Array<{ id: string; title: string; generated_at: string; summary: unknown }> }>('/reports/'),
  })
}

export function useProspectLeads(params?: { status?: string; classification?: string; min_score?: number }) {
  const qs = new URLSearchParams()
  if (params?.status) qs.set('status', params.status)
  if (params?.classification) qs.set('classification', params.classification)
  if (params?.min_score !== undefined) qs.set('min_score', String(params.min_score))

  return useQuery({
    queryKey: ['prospect-leads', params],
    queryFn: () => prospectApi.get<{ total: number; hot: number; warm: number; cold: number; leads: ProspectLead[] }>(`/leads?${qs}`),
  })
}
