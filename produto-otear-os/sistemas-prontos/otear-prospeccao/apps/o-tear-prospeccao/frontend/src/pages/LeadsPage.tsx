import { useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Progress } from '@/components/ui/progress'
import { Download, Upload, AlertCircle, CheckCircle2, Loader2, Megaphone, ExternalLink, Instagram, MapPin, Phone, MessageSquareText, BarChart3, Building2 } from 'lucide-react'
import { useLeads, useImportLeads, useImportLatestProspectLeads, useBulkAction } from '@/hooks/useLeads'
import type { Lead } from '@/types/lead'

const classificationVariants: Record<string, 'destructive' | 'warning' | 'outline'> = {
  hot: 'destructive', warm: 'warning', cold: 'outline',
}

const siteStatusLabels: Record<string, string> = {
  missing: 'Sem site',
  bad: 'Site ruim',
  ok: 'OK',
}

const adsStatusLabels: Record<string, string> = {
  tracking_detected: 'Pixel pago',
  analytics_only: 'Analytics',
  unknown: 'Sem sinal',
}

function formatCnpj(value?: string) {
  const digits = (value || '').replace(/\D/g, '')
  if (digits.length !== 14) return value || '-'
  return digits.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}

function normalizeExternalUrl(url?: string) {
  const trimmed = (url || '').trim()
  if (!trimmed) return ''
  if (/^https?:\/\//i.test(trimmed)) return trimmed
  return `https://${trimmed}`
}

function formatNumber(value?: number) {
  if (typeof value !== 'number') return '-'
  return new Intl.NumberFormat('pt-BR', { notation: value >= 10000 ? 'compact' : 'standard' }).format(value)
}

function DetailMetric({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div className="rounded-md border bg-muted/30 p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-sm font-semibold">{value ?? '-'}</p>
    </div>
  )
}

function LeadDetailDialog({ lead, open, onOpenChange }: { lead?: Lead; open: boolean; onOpenChange: (open: boolean) => void }) {
  if (!lead) return null

  const ads = lead.site_audit?.ads || {}
  const adsStatus = ads.status || 'unknown'
  const adsBadgeVariant = ads.has_paid_ads_signals ? 'destructive' : ads.has_tracking_pixels ? 'warning' : 'outline'
  const siteUrl = normalizeExternalUrl(lead.site_final_url || lead.website)
  const instagramUrl = normalizeExternalUrl(lead.instagram_url || (lead.instagram_handle ? `https://www.instagram.com/${lead.instagram_handle}/` : ''))
  const mapsUrl = normalizeExternalUrl(lead.maps_url)
  const scoreItems = [
    ['Sem site', lead.score_no_website],
    ['Site ruim', lead.score_bad_website],
    ['Sem Instagram', lead.score_no_instagram],
    ['Baixo engajamento', lead.score_low_engagement],
    ['Postagem irregular', lead.score_irregular_posting],
    ['Poucas reviews', lead.score_few_reviews],
    ['Baixa nota', lead.score_low_rating],
    ['Bio fraca', lead.score_no_professional_bio],
    ['Sem link na bio', lead.score_no_bio_link],
  ].filter(([, value]) => typeof value === 'number' && value > 0)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-5xl">
        <DialogHeader>
          <DialogTitle className="flex flex-wrap items-center gap-2">
            <span>{lead.name}</span>
            {lead.score_classification ? (
              <Badge variant={classificationVariants[lead.score_classification] || 'outline'}>
                {lead.score_classification.toUpperCase()}
              </Badge>
            ) : null}
          </DialogTitle>
          <DialogDescription>{lead.category || 'Lead importado'} {lead.address ? `- ${lead.address}` : ''}</DialogDescription>
        </DialogHeader>

        <div className="grid gap-3 sm:grid-cols-4">
          <DetailMetric label="Score" value={`${lead.score_total || 0}/20`} />
          <DetailMetric label="Google" value={lead.rating ? `${lead.rating} estrelas` : '-'} />
          <DetailMetric label="Seguidores" value={formatNumber(lead.instagram_followers)} />
          <DetailMetric label="Engajamento" value={typeof lead.engagement_rate === 'number' ? `${lead.engagement_rate}%` : '-'} />
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <section className="rounded-md border p-4">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <Building2 className="h-4 w-4 text-primary" />
              Empresa e contato
            </div>
            <div className="grid gap-2 text-sm text-muted-foreground">
              <span>Telefone: <strong className="text-foreground">{lead.phone || lead.whatsapp_number || '-'}</strong></span>
              <span>WhatsApp: <strong className="text-foreground">{lead.whatsapp_number || '-'}</strong></span>
              <span>Categoria: <strong className="text-foreground">{lead.category || '-'}</strong></span>
              <span>Endereco: <strong className="text-foreground">{lead.address || '-'}</strong></span>
              <div className="mt-2 flex flex-wrap gap-2">
                {siteUrl ? (
                  <Button size="sm" variant="outline" asChild>
                    <a href={siteUrl} target="_blank" rel="noreferrer"><ExternalLink className="h-3 w-3" /> Site</a>
                  </Button>
                ) : null}
                {mapsUrl ? (
                  <Button size="sm" variant="outline" asChild>
                    <a href={mapsUrl} target="_blank" rel="noreferrer"><MapPin className="h-3 w-3" /> Maps</a>
                  </Button>
                ) : null}
                {(lead.phone || lead.whatsapp_number) ? (
                  <Button size="sm" variant="outline" asChild>
                    <a href={`tel:${lead.phone || lead.whatsapp_number}`}><Phone className="h-3 w-3" /> Ligar</a>
                  </Button>
                ) : null}
              </div>
            </div>
          </section>

          <section className="rounded-md border p-4">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <Instagram className="h-4 w-4 text-primary" />
              Instagram
            </div>
            <div className="grid gap-2 text-sm text-muted-foreground">
              <span>Perfil: <strong className="text-foreground">{lead.instagram_handle ? `@${lead.instagram_handle}` : '-'}</strong></span>
              <span>Bio: <strong className="text-foreground">{lead.instagram_bio || '-'}</strong></span>
              <span>Link da bio: <strong className="text-foreground">{lead.instagram_bio_link || '-'}</strong></span>
              <div className="grid gap-2 sm:grid-cols-3">
                <DetailMetric label="Posts" value={lead.instagram_posts ?? '-'} />
                <DetailMetric label="Curtidas medias" value={formatNumber(lead.avg_likes)} />
                <DetailMetric label="Comentarios medios" value={formatNumber(lead.avg_comments)} />
              </div>
              {instagramUrl ? (
                <div>
                  <Button size="sm" variant="outline" asChild>
                    <a href={instagramUrl} target="_blank" rel="noreferrer"><Instagram className="h-3 w-3" /> Abrir Instagram</a>
                  </Button>
                </div>
              ) : null}
            </div>
          </section>

          <section className="rounded-md border p-4">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <Megaphone className="h-4 w-4 text-primary" />
              Site, anuncios e tracking
            </div>
            <div className="space-y-3 text-sm text-muted-foreground">
              <div className="flex flex-wrap gap-2">
                <Badge variant={lead.site_status === 'bad' || lead.site_status === 'missing' ? 'warning' : 'outline'}>
                  {siteStatusLabels[lead.site_status || ''] || lead.site_status || 'Sem diagnostico'}
                  {typeof lead.site_score === 'number' ? ` ${lead.site_score}` : ''}
                </Badge>
                <Badge variant={adsBadgeVariant}>{adsStatusLabels[adsStatus] || adsStatus}</Badge>
                {(ads.platforms || []).map((platform) => <Badge key={platform} variant="outline">{platform}</Badge>)}
              </div>
              {(lead.site_problems || []).length > 0 ? (
                <div>
                  <p className="mb-1 text-xs font-medium text-foreground">Problemas detectados</p>
                  <div className="flex flex-wrap gap-1">
                    {(lead.site_problems || []).map((problem) => <Badge key={problem} variant="outline">{problem}</Badge>)}
                  </div>
                </div>
              ) : null}
              {(ads.signals || []).length > 0 ? (
                <p>{(ads.signals || []).join(' | ')}</p>
              ) : (
                <p>Nenhum pixel de trafego pago detectado no HTML inicial.</p>
              )}
              <div className="flex flex-wrap gap-2">
                {ads.meta_ads_library_url ? (
                  <Button size="sm" variant="outline" asChild>
                    <a href={ads.meta_ads_library_url} target="_blank" rel="noreferrer"><Instagram className="h-3 w-3" /> Meta Ads</a>
                  </Button>
                ) : null}
                {ads.google_ads_transparency_url ? (
                  <Button size="sm" variant="outline" asChild>
                    <a href={ads.google_ads_transparency_url} target="_blank" rel="noreferrer"><ExternalLink className="h-3 w-3" /> Google Ads</a>
                  </Button>
                ) : null}
              </div>
            </div>
          </section>

          <section className="rounded-md border p-4">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <BarChart3 className="h-4 w-4 text-primary" />
              Score e CNPJ
            </div>
            <div className="space-y-3 text-sm text-muted-foreground">
              <div className="flex flex-wrap gap-1">
                {scoreItems.length > 0 ? scoreItems.map(([label, value]) => (
                  <Badge key={label as string} variant="outline">{label}: {value}</Badge>
                )) : <span>Nenhum fator de score detalhado registrado.</span>}
              </div>
              <div className="grid gap-1">
                <span>CNPJ: <strong className="text-foreground">{formatCnpj(lead.cnpj)}</strong></span>
                <span>Razao social: <strong className="text-foreground">{lead.razao_social || '-'}</strong></span>
                <span>Nome fantasia: <strong className="text-foreground">{lead.nome_fantasia || '-'}</strong></span>
              </div>
              {(lead.cnpj_owners || []).length > 0 ? (
                <div className="space-y-1">
                  {(lead.cnpj_owners || []).map((owner, index) => (
                    <p key={`${owner.name || 'owner'}-${index}`}>
                      <strong className="text-foreground">{owner.name || 'Sem nome'}</strong>
                      {owner.role ? ` - ${owner.role}` : ''}
                    </p>
                  ))}
                </div>
              ) : (
                <span>Sem socios retornados pela fonte.</span>
              )}
            </div>
          </section>
        </div>

        {lead.approach_script ? (
          <section className="rounded-md border p-4">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <MessageSquareText className="h-4 w-4 text-primary" />
              Hook de abordagem
            </div>
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">{lead.approach_script}</p>
          </section>
        ) : null}
      </DialogContent>
    </Dialog>
  )
}

export function LeadsPage() {
  const [filters, setFilters] = useState({ classification: '', search: '', page: 1 })
  const [selected, setSelected] = useState<string[]>([])
  const [detailLead, setDetailLead] = useState<Lead | undefined>()
  const [importOpen, setImportOpen] = useState(false)

  const { data, isLoading } = useLeads({
    classification: filters.classification || undefined,
    search: filters.search || undefined,
    page: filters.page,
  })
  const importMutation = useImportLeads()
  const importLatestMutation = useImportLatestProspectLeads()
  const bulkMutation = useBulkAction()

  const handleImport = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      await importMutation.mutateAsync(file)
      setImportOpen(false)
    }
  }, [importMutation])

  const handleBulk = (action: string, value?: string) => {
    if (selected.length === 0) return
    bulkMutation.mutate({ lead_ids: selected, action, value })
    setSelected([])
  }

  const toggleSelect = (id: string) => {
    setSelected((prev) => prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id])
  }

  const leads = data?.leads || []
  const total = data?.total || 0
  const totalPages = Math.ceil(total / 25)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Leads ({total})</h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => importLatestMutation.mutate('enriched')}
            disabled={importLatestMutation.isPending}
          >
            {importLatestMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Download className="mr-2 h-4 w-4" />
            )}
            Atualizar enriquecidos
          </Button>
          <Button onClick={() => setImportOpen(true)}><Upload className="mr-2 h-4 w-4" /> Importar arquivo</Button>
        </div>
      </div>

      {importLatestMutation.isSuccess && (
        <div className="flex items-center gap-2 rounded-lg bg-emerald-500/10 p-3 text-sm text-emerald-500">
          <CheckCircle2 className="h-4 w-4" />
          <span>
            Importados: {importLatestMutation.data.total_imported} | Atualizados: {importLatestMutation.data.updated_existing || 0} | Erros: {importLatestMutation.data.errors}
          </span>
        </div>
      )}

      {importLatestMutation.isError && (
        <div className="flex items-center gap-2 rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
          <AlertCircle className="h-4 w-4" />
          <span>{importLatestMutation.error.message}</span>
        </div>
      )}

      {data && (
        <div className="flex gap-2">
          <Badge variant="destructive">Hot: {data.hot}</Badge>
          <Badge variant="warning">Mornos: {data.warm}</Badge>
          <Badge variant="outline">Cold: {data.cold}</Badge>
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        <Input placeholder="Buscar..." className="max-w-[200px]" value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })} />
        <Select value={filters.classification || 'all'} onValueChange={(v) => setFilters({ ...filters, classification: v === 'all' ? '' : v, page: 1 })}>
          <SelectTrigger className="w-[140px]"><SelectValue placeholder="Classifica\u00e7\u00e3o" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos</SelectItem>
            <SelectItem value="hot">Hot</SelectItem>
            <SelectItem value="warm">Mornos</SelectItem>
            <SelectItem value="cold">Cold</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {selected.length > 0 && (
        <div className="flex items-center gap-2 rounded-lg bg-muted p-2">
          <span className="text-sm font-medium">{selected.length} selecionados</span>
          <Button size="sm" variant="outline" onClick={() => handleBulk('archive')}>Arquivar</Button>
          <Button size="sm" variant="outline" onClick={() => handleBulk('tag', 'prioridade')}>Tag: Prioridade</Button>
        </div>
      )}

      {isLoading ? (
        <div className="space-y-2">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}</div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-10">
                  <Checkbox checked={selected.length === leads.length && leads.length > 0}
                    onCheckedChange={() => setSelected(selected.length === leads.length ? [] : leads.map((l) => l.id))} />
                </TableHead>
                <TableHead>Nome</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Site</TableHead>
                <TableHead>Anuncios</TableHead>
                <TableHead>Class.</TableHead>
                <TableHead>Telefone</TableHead>
                <TableHead>Decisor</TableHead>
                <TableHead>Instagram</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {leads.map((lead) => {
                const ads = lead.site_audit?.ads || {}
                const adsStatus = ads.status || 'unknown'
                const adsBadgeVariant = ads.has_paid_ads_signals ? 'destructive' : ads.has_tracking_pixels ? 'warning' : 'outline'

                return (
                  <TableRow key={lead.id} className="cursor-pointer" onClick={() => setDetailLead(lead)}>
                    <TableCell onClick={(event) => event.stopPropagation()}><Checkbox checked={selected.includes(lead.id)} onCheckedChange={() => toggleSelect(lead.id)} /></TableCell>
                    <TableCell className="font-medium">{lead.name}</TableCell>
                    <TableCell className="text-muted-foreground">{lead.category || '-'}</TableCell>
                    <TableCell className="font-mono">{lead.score_total}</TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <Badge variant={lead.site_status === 'bad' || lead.site_status === 'missing' ? 'warning' : 'outline'}>
                          {siteStatusLabels[lead.site_status || ''] || '-'}
                          {typeof lead.site_score === 'number' ? ` ${lead.site_score}` : ''}
                        </Badge>
                        {(lead.site_problems || []).length > 0 && (
                          <p className="max-w-[220px] truncate text-xs text-muted-foreground" title={(lead.site_problems || []).join(', ')}>
                            {(lead.site_problems || [])[0]}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="max-w-[180px]">
                      <div className="space-y-1">
                        <Badge variant={adsBadgeVariant}>
                          <Megaphone className="mr-1 h-3 w-3" />
                          {adsStatusLabels[adsStatus] || adsStatus}
                        </Badge>
                        {(ads.platforms || []).length > 0 ? (
                          <p className="truncate text-xs text-muted-foreground" title={(ads.platforms || []).join(', ')}>
                            {(ads.platforms || []).join(', ')}
                          </p>
                        ) : null}
                        <div className="flex gap-1">
                          {ads.meta_ads_library_url ? (
                            <Button size="sm" variant="outline" asChild title="Abrir Meta Ads Library" onClick={(event) => event.stopPropagation()}>
                              <a href={ads.meta_ads_library_url} target="_blank" rel="noreferrer"><Instagram className="h-3 w-3" /></a>
                            </Button>
                          ) : null}
                          {ads.google_ads_transparency_url ? (
                            <Button size="sm" variant="outline" asChild title="Abrir Google Ads Transparency" onClick={(event) => event.stopPropagation()}>
                              <a href={ads.google_ads_transparency_url} target="_blank" rel="noreferrer"><ExternalLink className="h-3 w-3" /></a>
                            </Button>
                          ) : null}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell><Badge variant={classificationVariants[lead.score_classification || ''] || 'outline'}>{lead.score_classification?.toUpperCase() || '-'}</Badge></TableCell>
                    <TableCell className="font-mono text-xs">{lead.phone || lead.whatsapp_number || '-'}</TableCell>
                    <TableCell className="max-w-[220px]">
                      {lead.decision_maker_name ? (
                        <div className="space-y-1">
                          <p className="truncate text-sm font-medium" title={lead.decision_maker_name}>{lead.decision_maker_name}</p>
                          <p className="truncate text-xs text-muted-foreground" title={lead.decision_maker_role || 'Socio'}>{lead.decision_maker_role || 'Socio'}</p>
                          {lead.cnpj ? <p className="font-mono text-[11px] text-muted-foreground">{formatCnpj(lead.cnpj)}</p> : null}
                        </div>
                      ) : lead.cnpj ? (
                        <div className="space-y-1">
                          <Badge variant="outline">CNPJ</Badge>
                          <p className="font-mono text-[11px] text-muted-foreground">{formatCnpj(lead.cnpj)}</p>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>{lead.instagram_handle ? `@${lead.instagram_handle}` : '-'}</TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex justify-center gap-1">
          {Array.from({ length: Math.min(totalPages, 10) }, (_, i) => (
            <Button key={i} size="sm" variant={filters.page === i + 1 ? 'default' : 'outline'}
              onClick={() => setFilters({ ...filters, page: i + 1 })}>{i + 1}</Button>
          ))}
        </div>
      )}

      <Dialog open={importOpen} onOpenChange={setImportOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Importar Leads do ProspectPro</DialogTitle>
            <DialogDescription>Selecione um arquivo JSON ou CSV exportado pelo ProspectPro.</DialogDescription>
          </DialogHeader>
          {importMutation.isPending && <Progress value={50} className="animate-pulse" />}
          {importMutation.isSuccess && (
            <div className="flex items-center gap-2 rounded-lg bg-emerald-500/10 p-3 text-emerald-500">
              <CheckCircle2 className="h-4 w-4" />
              <span className="text-sm">
                Importados: {importMutation.data?.total_imported} | Atualizados: {importMutation.data?.updated_existing || 0} | Erros: {importMutation.data?.errors}
              </span>
            </div>
          )}
          {importMutation.isError && (
            <div className="flex items-center gap-2 rounded-lg bg-destructive/10 p-3 text-destructive">
              <AlertCircle className="h-4 w-4" /><span className="text-sm">Erro ao importar</span>
            </div>
          )}
          <Button variant="outline" className="relative h-20 w-full border-dashed" asChild>
            <label>Selecionar arquivo (.json ou .csv)<input type="file" className="hidden" accept=".json,.csv" onChange={handleImport} /></label>
          </Button>
          <DialogFooter><Button variant="outline" onClick={() => setImportOpen(false)}>Fechar</Button></DialogFooter>
        </DialogContent>
      </Dialog>

      <LeadDetailDialog lead={detailLead} open={!!detailLead} onOpenChange={(open) => !open && setDetailLead(undefined)} />
    </div>
  )
}

