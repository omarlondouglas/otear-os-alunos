export interface WhatsAppNumber {
  id: string
  label: string
  phone_number: string
  status: 'warming_up' | 'active' | 'resting' | 'banned' | 'disabled'
  warmup_day: number
  daily_limit: number
  current_daily_sent: number
  ban_risk_score: number
  total_sent_today: number
  total_sent_week: number
  total_sent_month: number
  is_available: boolean
  last_sent_at?: string
  last_error?: string
  consecutive_errors: number
  rest_until?: string
  created_at?: string
}

export interface NumberHealth {
  total_numbers: number
  active: number
  warming_up: number
  resting: number
  banned: number
  total_capacity_today: number
  total_sent_today: number
  numbers: WhatsAppNumber[]
}
