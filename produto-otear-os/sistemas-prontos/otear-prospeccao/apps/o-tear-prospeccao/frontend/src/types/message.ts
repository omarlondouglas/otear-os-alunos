export interface Conversation {
  id: string
  lead_id: string
  lead_name: string
  whatsapp_number: string
  last_message_at?: string
  last_message_preview?: string
  unread_count: number
  sentiment?: string
}

export interface ConversationMessage {
  id: string
  direction: 'inbound' | 'outbound'
  message_body: string
  message_type: string
  status?: string
  created_at?: string
}
