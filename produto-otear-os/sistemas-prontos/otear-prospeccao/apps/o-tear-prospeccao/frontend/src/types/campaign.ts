export interface Campaign {
  id: string
  name: string
  description?: string
  status: 'draft' | 'active' | 'paused' | 'completed' | 'cancelled'
  target_filters: Record<string, unknown>
  start_date?: string
  end_date?: string
  time_window_start?: string
  time_window_end?: string
  daily_limit: number
  min_delay_seconds: number
  max_delay_seconds: number
  total_leads: number
  total_sent: number
  total_delivered: number
  total_read: number
  total_replied: number
  total_failed: number
  created_at?: string
  updated_at?: string
  messages: MessageTemplate[]
}

export interface MessageTemplate {
  id: string
  variant_name: string
  template_body: string
  weight: number
  times_sent: number
  times_delivered: number
  times_read: number
  times_replied: number
}

export interface CampaignStats {
  campaign_id: string
  name: string
  status: string
  total_leads: number
  sent: number
  delivered: number
  read: number
  replied: number
  failed: number
  delivery_rate: number
  read_rate: number
  reply_rate: number
  variants: MessageTemplate[]
}
