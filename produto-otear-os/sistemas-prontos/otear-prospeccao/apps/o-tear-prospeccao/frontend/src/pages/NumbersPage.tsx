import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { Plus, AlertTriangle } from 'lucide-react'
import { useNumbersHealth, useCreateNumber } from '@/hooks/useNumbers'

const statusVariants: Record<string, 'success' | 'warning' | 'destructive' | 'outline'> = {
  active: 'success', warming_up: 'warning', resting: 'outline', banned: 'destructive', disabled: 'outline',
}
const statusLabels: Record<string, string> = {
  active: 'Ativo', warming_up: 'Aquecendo', resting: 'Descansando', banned: 'Banido', disabled: 'Desativado',
}

export function NumbersPage() {
  const { data, isLoading } = useNumbersHealth()
  const createMutation = useCreateNumber()
  const [addOpen, setAddOpen] = useState(false)
  const [form, setForm] = useState({ label: '', phone_number: '', daily_limit: 20 })

  const handleAdd = async () => {
    await createMutation.mutateAsync(form)
    setAddOpen(false)
    setForm({ label: '', phone_number: '', daily_limit: 20 })
  }

  if (isLoading || !data) return <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-48" />)}</div>

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Números WhatsApp</h2>
        <Button onClick={() => setAddOpen(true)}><Plus className="mr-2 h-4 w-4" /> Adicionar</Button>
      </div>

      <div className="flex flex-wrap gap-2">
        <Badge variant="success">Ativos: {data.active}</Badge>
        <Badge variant="warning">Aquecendo: {data.warming_up}</Badge>
        <Badge variant="outline">Descansando: {data.resting}</Badge>
        {data.banned > 0 && <Badge variant="destructive">Banidos: {data.banned}</Badge>}
        <Badge variant="secondary">Capacidade: {data.total_sent_today}/{data.total_capacity_today}</Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data.numbers.map((num) => (
          <Card key={num.id}>
            <CardContent className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">{num.label}</h3>
                <Badge variant={statusVariants[num.status]}>{statusLabels[num.status]}</Badge>
              </div>
              <p className="font-mono text-sm text-muted-foreground">{num.phone_number}</p>

              {num.status === 'warming_up' && (
                <div>
                  <div className="flex justify-between text-xs text-muted-foreground mb-1">
                    <span>Warmup</span><span>Dia {num.warmup_day}/14</span>
                  </div>
                  <Progress value={Math.min((num.warmup_day / 14) * 100, 100)} />
                </div>
              )}

              <div>
                <div className="flex justify-between text-xs text-muted-foreground mb-1">
                  <span>Hoje</span><span>{num.current_daily_sent}/{num.daily_limit}</span>
                </div>
                <Progress value={(num.current_daily_sent / num.daily_limit) * 100} className={num.current_daily_sent >= num.daily_limit ? '[&>div]:bg-destructive' : ''} />
              </div>

              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Risco Ban: {num.ban_risk_score}/100</span>
                <Badge variant={num.ban_risk_score < 30 ? 'success' : num.ban_risk_score < 60 ? 'warning' : 'destructive'}>
                  {num.ban_risk_score < 30 ? 'Baixo' : num.ban_risk_score < 60 ? 'Médio' : 'Alto'}
                </Badge>
              </div>

              {num.last_error && (
                <div className="flex items-center gap-1 text-xs text-destructive">
                  <AlertTriangle className="h-3 w-3" /> {num.last_error}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Adicionar Número</DialogTitle>
            <DialogDescription>Configure um novo número WhatsApp para disparo</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div><Label>Label</Label><Input value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} /></div>
            <div><Label>Número (ex: 5511999998888)</Label><Input value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} /></div>
            <div><Label>Limite diário inicial</Label><Input type="number" value={form.daily_limit} onChange={(e) => setForm({ ...form, daily_limit: Number(e.target.value) })} /></div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAddOpen(false)}>Cancelar</Button>
            <Button onClick={handleAdd} disabled={!form.label || !form.phone_number}>Adicionar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
