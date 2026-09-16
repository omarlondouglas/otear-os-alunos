import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import type { Conversation, ConversationMessage } from '@/types/message'

export function useConversations(unreadOnly = false) {
  return useQuery({
    queryKey: ['conversations', unreadOnly],
    queryFn: () =>
      api.get<{ total: number; conversations: Conversation[] }>(
        `/conversations?unread_only=${unreadOnly}`
      ),
    refetchInterval: 15_000,
  })
}

export function useConversationMessages(conversationId: string) {
  return useQuery({
    queryKey: ['conversation-messages', conversationId],
    queryFn: () =>
      api.get<{ total: number; messages: ConversationMessage[] }>(
        `/conversations/${conversationId}/messages`
      ),
    enabled: !!conversationId,
    refetchInterval: 10_000,
  })
}

export function useReply() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ conversationId, message }: { conversationId: string; message: string }) =>
      api.post(`/conversations/${conversationId}/reply`, { message_body: message }),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['conversation-messages', vars.conversationId] })
      qc.invalidateQueries({ queryKey: ['conversations'] })
    },
  })
}
