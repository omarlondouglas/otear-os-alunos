import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Skeleton } from '@/components/ui/skeleton'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { Play, Pause, Plus } from 'lucide-react'
import { useCampaigns, useCreateCampaign, useActivateCampaign, usePauseCampaign } from '@/hooks/useCampaigns'

const statusVariants: Record<string, 'success' | 'default' | 'warning' | 'outline' | 'destructive'> = {
  active: 'success', draft: 'outline', paused: 'warning', completed: 'default', cancelled: 'destructive',
}

export function CampaignsPage() {
  const { data: campaigns, isLoading } = useCampaigns()
  const createMutation = useCreateCampaign()
  const activateMutation = useActivateCampaign()
  const pauseMutation = usePauseCampaign()
  const [createOpen, setCreateOpen] = useState(false)
  const [form, setForm] = useState({ name: '', description: '', template: '', daily_limit: 50 })

  const handleCreate = async () => {
    await createMutation.mutateAsync({
      name: form.name, description: form.description, daily_limit: form.daily_limit,
      target_filters: { classification: ['hot', 'warm'], outreach_status: 'imported' },
      messages: [{ variant_name: 'A', template_body: form.template, weight: 100 }],
    })
    setCreateOpen(false)
    setForm({ name: '', description: '', template: '', daily_limit: 50 })
  }

  if (isLoading) return <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-48" />)}</div>

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Campanhas</h2>
        <Button onClick={() => setCreateOpen(true)}><Plus className="mr-2 h-4 w-4" /> Nova Campanha</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {(campaigns || []).map((c: any) => (
          <Card key={c.id}>
            <CardContent className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">{c.name}</h3>
                <Badge variant={statusVariants[c.status] || 'outline'}>{c.status}</Badge>
              </div>
              {c.description && <p className="text-sm text-muted-foreground">{c.description}</p>}
              <div className="grid grid-cols-3 gap-2 text-center">
                <div><p className="text-xs text-muted-foreground">Leads</p><p className="text-xl font-bold">{c.total_leads}</p></div>
                <div><p className="text-xs text-muted-foreground">Enviadas</p><p className="text-xl font-bold">{c.total_sent}</p></div>
                <div><p className="text-xs text-muted-foreground">Respostas</p><p className="text-xl font-bold">{c.total_replied}</p></div>
              </div>
              <div className="flex gap-2">
                {(c.status === 'draft' || c.status === 'paused') && (
                  <Button size="sm" onClick={() => activateMutation.mutate(c.id)}>
                    <Play className="mr-1 h-3 w-3" /> {c.status === 'paused' ? 'Retomar' : 'Ativar'}
                  </Button>
                )}
                {c.status === 'active' && (
                  <Button size="sm" variant="outline" onClick={() => pauseMutation.mutate(c.id)}>
                    <Pause className="mr-1 h-3 w-3" /> Pausar
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Nova Campanha</DialogTitle>
            <DialogDescription>Configure a campanha de disparo WhatsApp</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div><Label>Nome da Campanha</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
            <div><Label>Descrição</Label><Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={2} /></div>
            <div><Label>Limite Diário</Label><Input type="number" value={form.daily_limit} onChange={(e) => setForm({ ...form, daily_limit: Number(e.target.value) })} /></div>
            <div>
              <Label>Template da Mensagem</Label>
              <Textarea value={form.template} onChange={(e) => setForm({ ...form, template: e.target.value })} rows={6} />
              <p className="text-xs text-muted-foreground mt-1">Variáveis: {'{{nome}}'}, {'{{primeiro_nome}}'}, {'{{categoria}}'}, {'{{cidade}}'}, {'{{problema}}'}, {'{{saudacao}}'}, {'{{intro}}'}</p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancelar</Button>
            <Button onClick={handleCreate} disabled={!form.name || !form.template}>Criar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
