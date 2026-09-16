import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { Send, MessageSquare } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useConversations, useConversationMessages, useReply } from '@/hooks/useMessages'

export function MessagesPage() {
  const { data: convData, isLoading } = useConversations()
  const [selectedId, setSelectedId] = useState('')
  const { data: msgData } = useConversationMessages(selectedId)
  const replyMutation = useReply()
  const [replyText, setReplyText] = useState('')

  const conversations = convData?.conversations || []
  const messages = msgData?.messages || []

  const handleSend = () => {
    if (!replyText.trim() || !selectedId) return
    replyMutation.mutate({ conversationId: selectedId, message: replyText })
    setReplyText('')
  }

  if (isLoading) return <div className="space-y-2">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-16 w-full" />)}</div>

  return (
    <div className="flex gap-4 h-[calc(100vh-8rem)]">
      {/* Conversation List */}
      <div className="w-80 rounded-lg border bg-card flex flex-col">
        <div className="p-3 font-semibold text-sm border-b">Conversas ({conversations.length})</div>
        <ScrollArea className="flex-1">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              className={cn(
                'flex w-full items-center justify-between p-3 text-left hover:bg-muted/50 transition-colors border-b border-border/50',
                selectedId === conv.id && 'bg-muted'
              )}
              onClick={() => setSelectedId(conv.id)}
            >
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold truncate">{conv.lead_name}</p>
                <p className="text-xs text-muted-foreground truncate">{conv.last_message_preview || 'Sem mensagens'}</p>
              </div>
              {conv.unread_count > 0 && (
                <Badge className="ml-2 shrink-0">{conv.unread_count}</Badge>
              )}
            </button>
          ))}
          {conversations.length === 0 && (
            <div className="flex flex-col items-center justify-center p-8 text-muted-foreground">
              <MessageSquare className="h-8 w-8 mb-2" />
              <p className="text-sm">Nenhuma conversa</p>
            </div>
          )}
        </ScrollArea>
      </div>

      {/* Chat Window */}
      <div className="flex-1 rounded-lg border bg-card flex flex-col">
        {selectedId ? (
          <>
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-3">
                {messages.map((msg) => (
                  <div key={msg.id} className={cn('flex', msg.direction === 'outbound' ? 'justify-end' : 'justify-start')}>
                    <div className={cn(
                      'max-w-[70%] rounded-lg px-4 py-2',
                      msg.direction === 'outbound' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                    )}>
                      <p className="text-sm">{msg.message_body}</p>
                      <p className={cn('text-[10px] mt-1', msg.direction === 'outbound' ? 'text-primary-foreground/70' : 'text-muted-foreground')}>
                        {msg.created_at ? new Date(msg.created_at).toLocaleTimeString('pt-BR') : ''}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
            <Separator />
            <div className="flex items-center gap-2 p-3">
              <Input
                placeholder="Digite sua resposta..."
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                className="flex-1"
              />
              <Button size="icon" onClick={handleSend} disabled={!replyText.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </>
        ) : (
          <div className="flex flex-1 items-center justify-center text-muted-foreground">
            <div className="text-center">
              <MessageSquare className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>Selecione uma conversa</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
