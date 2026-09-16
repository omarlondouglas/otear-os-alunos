import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useLeads } from '@/hooks/useLeads'
import { AlertCircle, Building2, Flame, Megaphone, UserRoundCheck, Globe2 } from 'lucide-react'

function StatCard({ title, value, icon: Icon, accent }: { title: string; value: number | string; icon: React.ElementType; accent?: boolean }) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className={`text-3xl font-bold ${accent ? 'text-primary' : ''}`}>{value}</p>
          </div>
          <div className={`rounded-lg p-3 ${accent ? 'bg-primary/10' : 'bg-muted'}`}>
            <Icon className={`h-5 w-5 ${accent ? 'text-primary' : 'text-muted-foreground'}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function DashboardPage() {
  const { data, isLoading, isError, error, refetch } = useLeads({ per_page: 100 })
  const leads = data?.leads || []

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}><CardContent className="p-6"><Skeleton className="h-16 w-full" /></CardContent></Card>
        ))}
      </div>
    )
  }

  if (isError || !data) {
    return (
      <Card>
        <CardContent className="flex flex-col items-start gap-4 p-6">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-destructive/10 p-3">
              <AlertCircle className="h-5 w-5 text-destructive" />
            </div>
            <div>
              <p className="font-semibold">Nao foi possivel carregar o dashboard</p>
              <p className="text-sm text-muted-foreground">
                {error instanceof Error ? error.message : 'Verifique a API e a chave de acesso.'}
              </p>
            </div>
          </div>
          <Button onClick={() => refetch()}>Tentar novamente</Button>
        </CardContent>
      </Card>
    )
  }

  const withDecisionMaker = leads.filter((lead) => lead.decision_maker_name).length
  const withAdsSignals = leads.filter((lead) => lead.site_audit?.ads?.has_paid_ads_signals).length
  const withTracking = leads.filter((lead) => lead.site_audit?.ads?.has_tracking_pixels).length
  const badSites = leads.filter((lead) => lead.site_status === 'bad' || lead.site_status === 'missing').length
  const chart = [
    { name: 'Hot', value: data.hot },
    { name: 'Warm', value: data.warm },
    { name: 'Cold', value: data.cold },
    { name: 'Com decisor', value: withDecisionMaker },
    { name: 'Sinais ads', value: withAdsSignals },
  ]

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total de Leads" value={data.total} icon={Building2} accent />
        <StatCard title="Leads Hot" value={data.hot} icon={Flame} />
        <StatCard title="Com Decisor" value={withDecisionMaker} icon={UserRoundCheck} />
        <StatCard title="Sinais de Ads" value={withAdsSignals} icon={Megaphone} />
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardContent className="p-6">
          <p className="text-sm text-muted-foreground">Com tracking</p>
          <p className="text-2xl font-bold text-primary">{withTracking}</p>
        </CardContent></Card>
        <Card><CardContent className="p-6">
          <p className="text-sm text-muted-foreground">Sites ruins ou ausentes</p>
          <p className="text-2xl font-bold text-amber-500">{badSites}</p>
        </CardContent></Card>
        <Card><CardContent className="p-6">
          <p className="text-sm text-muted-foreground">Cobertura de decisores</p>
          <p className="text-2xl font-bold text-emerald-500">{leads.length ? Math.round((withDecisionMaker / leads.length) * 100) : 0}%</p>
        </CardContent></Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2 text-lg">
            <Globe2 className="h-5 w-5 text-primary" /> Perfil da Base
          </CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chart}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px', color: 'hsl(var(--foreground))' }} />
                <Bar dataKey="value" fill="hsl(82, 100%, 54%)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-lg">Resumo de Enriquecimento</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between"><span className="text-sm">Hot</span><Badge variant="destructive">{data.hot}</Badge></div>
            <div className="flex items-center justify-between"><span className="text-sm">Warm</span><Badge variant="warning">{data.warm}</Badge></div>
            <div className="flex items-center justify-between"><span className="text-sm">Cold</span><Badge variant="outline">{data.cold}</Badge></div>
            <div className="flex items-center justify-between"><span className="text-sm">Com decisor</span><Badge>{withDecisionMaker}</Badge></div>
            <div className="flex items-center justify-between"><span className="text-sm">Sinais de ads</span><Badge variant="outline">{withAdsSignals}</Badge></div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
