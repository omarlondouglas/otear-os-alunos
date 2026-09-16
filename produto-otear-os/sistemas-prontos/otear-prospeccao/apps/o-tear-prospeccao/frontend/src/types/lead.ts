export interface Lead {
  id: string
  prospect_pro_id?: string
  name: string
  category?: string
  phone?: string
  website?: string
  address?: string
  rating?: number
  reviews_count?: number
  maps_url?: string
  latitude?: number
  longitude?: number
  instagram_handle?: string
  instagram_url?: string
  instagram_bio?: string
  instagram_bio_link?: string
  instagram_followers?: number
  instagram_following?: number
  instagram_posts?: number
  instagram_is_business?: boolean
  instagram_is_verified?: boolean
  engagement_rate?: number
  avg_likes?: number
  avg_comments?: number
  posting_frequency_days?: number
  last_post_date?: string
  cnpj?: string
  razao_social?: string
  nome_fantasia?: string
  decision_maker_name?: string
  decision_maker_role?: string
  cnpj_owners?: Array<{
    name?: string
    role?: string
  }>
  score_total: number
  score_classification?: 'hot' | 'warm' | 'cold'
  score_no_website?: number
  score_bad_website?: number
  score_no_instagram?: number
  score_low_engagement?: number
  score_irregular_posting?: number
  score_few_reviews?: number
  score_low_rating?: number
  score_no_professional_bio?: number
  score_no_bio_link?: number
  site_status?: 'missing' | 'bad' | 'ok' | string
  site_score?: number
  site_final_url?: string
  site_problems?: string[]
  site_missing_items?: string[]
  site_present_items?: string[]
  site_response_time_seconds?: number
  site_http_status?: number
  site_audit?: {
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
    [key: string]: unknown
  }
  approach_script?: string
  outreach_status: string
  whatsapp_number?: string
  tags: string[]
  notes?: string
  created_at?: string
  updated_at?: string
}

export interface LeadListResponse {
  total: number
  hot: number
  warm: number
  cold: number
  leads: Lead[]
}

export interface ImportResponse {
  batch_id: string
  total_imported: number
  duplicates_skipped: number
  updated_existing?: number
  errors: number
  error_details: string[]
}
