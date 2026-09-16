export interface DashboardStats {
  total_leads: number
  leads_hot: number
  leads_warm: number
  leads_cold: number
  total_campaigns: number
  active_campaigns: number
  messages_sent_today: number
  messages_sent_week: number
  messages_sent_month: number
  delivery_rate: number
  read_rate: number
  reply_rate: number
  unread_conversations: number
  numbers_active: number
  numbers_warming_up: number
}

export interface FunnelData {
  imported: number
  queued: number
  contacted: number
  replied: number
  converted: number
}
