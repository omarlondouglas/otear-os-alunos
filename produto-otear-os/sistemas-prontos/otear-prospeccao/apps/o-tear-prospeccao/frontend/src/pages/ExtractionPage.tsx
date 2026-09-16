import { Fragment, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Search, Instagram, BarChart3, FileText, Workflow, Loader2, CheckCircle2, AlertCircle, Download, ExternalLink, MapPin, Phone, Upload, MessageSquareText, Megaphone } from 'lucide-react'
import { ProspectLead, useScrapeGoogleMapsSync, useEnrichLeads, useAnalyzeInstagram, useGenerateReport, useListReports, useProspectLeads } from '@/hooks/use-extraction'
import { useImportLeads } from '@/hooks/useLeads'

function cleanGoogleText(value?: string) {
  return (value || '').replace(/[\ue000-\uf8ff]/g, '').replace(/\s+/g, ' ').trim()
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

function formatCnpj(value?: string) {
  const digits = (value || '').replace(/\D/g, '')
  if (digits.length !== 14) return value || '-'
  return digits.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}

function getDecisionMaker(lead: ProspectLead) {
  const owners = lead.cnpj_info?.owners || []
  const preferred = owners.find((owner) => /administrador|titular|diretor|presidente|empres/i.test(owner.role || ''))
  return preferred || owners[0]
}

const classificationVariants: Record<string, 'destructive' | 'warning' | 'outline'> = {
  hot: 'destructive',
  warm: 'warning',
  cold: 'outline',
}

const adsStatusLabels: Record<string, string> = {
  tracking_detected: 'Pixel pago',
  analytics_only: 'Analytics',
  unknown: 'Sem sinal',
}

function ProspectResultsList({ leads }: { leads: ProspectLead[] }) {
  const withPhone = leads.filter((lead) => cleanGoogleText(lead.google?.phone)).length
  const withWebsite = leads.filter((lead) => lead.google?.website).length
  const withDecisionMaker = leads.filter((lead) => getDecisionMaker(lead)?.name).length
  const withAdsSignals = leads.filter((lead) => lead.website_audit?.ads?.has_paid_ads_signals).length

  return (
    <div className="space-y-3">
      <div className="grid gap-2 sm:grid-cols-5">
        <div className="rounded-md border bg-muted/30 p-3">
          <p className="text-xs text-muted-foreground">Encontrados</p>
          <p className="text-xl font-bold">{leads.length}</p>
        </div>
        <div className="rounded-md border bg-muted/30 p-3">
          <p className="text-xs text-muted-foreground">Com telefone</p>
          <p className="text-xl font-bold">{withPhone}</p>
        </div>
        <div className="rounded-md border bg-muted/30 p-3">
          <p className="text-xs text-muted-foreground">Com site</p>
          <p className="text-xl font-bold">{withWebsite}</p>
        </div>
        <div className="rounded-md border bg-muted/30 p-3">
          <p className="text-xs text-muted-foreground">Com decisor</p>
          <p className="text-xl font-bold">{withDecisionMaker}</p>
        </div>
        <div className="rounded-md border bg-muted/30 p-3">
          <p className="text-xs text-muted-foreground">Sinais de ads</p>
          <p className="text-xl font-bold">{withAdsSignals}</p>
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Empresa</TableHead>
              <TableHead>Categoria</TableHead>
              <TableHead>Score</TableHead>
              <TableHead>Instagram</TableHead>
              <TableHead>Site</TableHead>
              <TableHead>Anuncios</TableHead>
              <TableHead>Contato</TableHead>
              <TableHead>Decisor</TableHead>
              <TableHead>Links</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {leads.map((lead, index) => {
              const google = lead.google || {}
              const instagram = lead.instagram || {}
              const siteAudit = lead.website_audit || {}
              const ads = siteAudit.ads || {}
              const contentMetrics = instagram.content_metrics || {}
              const phone = cleanGoogleText(google.phone)
              const address = cleanGoogleText(google.address)
              const siteUrl = normalizeExternalUrl(siteAudit.final_url || google.website)
              const mapsUrl = normalizeExternalUrl(google.maps_url)
              const instagramUrl = instagram.handle
                ? normalizeExternalUrl(instagram.profile_url || `https://www.instagram.com/${instagram.handle}/`)
                : ''
              const decisionMaker = getDecisionMaker(lead)
              const analyzedPosts = instagram.recent_posts?.length || 0
              const topHashtags = (contentMetrics.top_hashtags || []).slice(0, 3)
              const adsStatus = ads.status || 'unknown'
              const adsBadgeVariant = ads.has_paid_ads_signals ? 'destructive' : ads.has_tracking_pixels ? 'warning' : 'outline'

              return (
                <Fragment key={`${google.name || 'lead'}-${index}`}>
                  <TableRow>
                    <TableCell className="max-w-[320px]">
                      <div className="space-y-1">
                        <p className="font-medium leading-tight">{google.name || 'Sem nome'}</p>
                        <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                          {google.rating ? <Badge variant="outline">{google.rating.toFixed(1)} estrelas</Badge> : null}
                          {address ? (
                            <span className="inline-flex items-center gap-1">
                              <MapPin className="h-3 w-3" />
                              <span className="line-clamp-1">{address}</span>
                            </span>
                          ) : null}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{google.category || '-'}</TableCell>
                    <TableCell>
                      {lead.score?.classification ? (
                        <div className="flex items-center gap-2">
                          <Badge variant={classificationVariants[lead.score.classification] || 'outline'}>
                            {lead.score.classification.toUpperCase()}
                          </Badge>
                          <span className="font-mono text-xs">{lead.score.total ?? 0}/20</span>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="max-w-[190px]">
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
                      </div>
                    </TableCell>
                    <TableCell>
                      {instagram.handle ? (
                        <div className="space-y-1">
                          <Button size="sm" variant="outline" asChild title={`Abrir Instagram @${instagram.handle}`}>
                            <a href={instagramUrl} target="_blank" rel="noreferrer">
                              <Instagram className="h-3 w-3" /> @{instagram.handle}
                            </a>
                          </Button>
                          <div className="flex flex-wrap gap-1 text-xs text-muted-foreground">
                            <span>{formatNumber(instagram.followers)} seg.</span>
                            {typeof instagram.engagement_rate === 'number' ? <span>{instagram.engagement_rate}% eng.</span> : null}
                          </div>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="max-w-[260px]">
                      <div className="space-y-1">
                        {siteUrl ? (
                          <a className="inline-flex max-w-full items-center gap-1 truncate text-xs text-primary underline-offset-4 hover:underline" href={siteUrl} target="_blank" rel="noreferrer">
                            <ExternalLink className="h-3 w-3 shrink-0" />
                            <span className="truncate">{siteUrl}</span>
                          </a>
                        ) : (
                          <span className="text-muted-foreground">Sem site</span>
                        )}
                        {siteAudit.status ? (
                          <div className="flex flex-wrap items-center gap-1">
                            <Badge variant={siteAudit.status === 'bad' || siteAudit.status === 'missing' ? 'warning' : 'outline'}>
                              {siteAudit.status}
                              {typeof siteAudit.score === 'number' ? ` ${siteAudit.score}` : ''}
                            </Badge>
                            {(siteAudit.problems || []).slice(0, 1).map((problem) => (
                              <span key={problem} className="max-w-[180px] truncate text-xs text-muted-foreground" title={(siteAudit.problems || []).join(', ')}>
                                {problem}
                              </span>
                            ))}
                          </div>
                        ) : null}
                      </div>
                    </TableCell>
                    <TableCell>
                      {phone ? (
                        <span className="inline-flex items-center gap-1 font-mono text-xs">
                          <Phone className="h-3 w-3" />
                          {phone}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="max-w-[220px]">
                      {decisionMaker?.name ? (
                        <div className="space-y-1">
                          <p className="truncate text-sm font-medium" title={decisionMaker.name}>{decisionMaker.name}</p>
                          <p className="truncate text-xs text-muted-foreground" title={decisionMaker.role || 'Socio'}>{decisionMaker.role || 'Socio'}</p>
                          {lead.cnpj_info?.cnpj ? <p className="font-mono text-[11px] text-muted-foreground">{formatCnpj(lead.cnpj_info.cnpj)}</p> : null}
                        </div>
                      ) : lead.cnpj_info?.cnpj ? (
                        <div className="space-y-1">
                          <Badge variant="outline">CNPJ encontrado</Badge>
                          <p className="font-mono text-[11px] text-muted-foreground">{formatCnpj(lead.cnpj_info.cnpj)}</p>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-2">
                        {lead.approach_script ? (
                          <Button size="sm" variant="outline" title={lead.approach_script}>
                            <MessageSquareText className="h-3 w-3" /> Hook
                          </Button>
                        ) : null}
                        {analyzedPosts > 0 ? (
                          <Button size="sm" variant="outline" title={`${analyzedPosts} posts analisados`}>
                            <BarChart3 className="h-3 w-3" /> Analise
                          </Button>
                        ) : null}
                        {siteUrl ? (
                          <Button size="sm" variant="outline" asChild>
                            <a href={siteUrl} target="_blank" rel="noreferrer" title={siteUrl}>
                              <ExternalLink className="h-3 w-3" /> Abrir site
                            </a>
                          </Button>
                        ) : null}
                        {instagramUrl ? (
                          <Button size="sm" variant="outline" asChild>
                            <a href={instagramUrl} target="_blank" rel="noreferrer" title={instagramUrl}>
                              <Instagram className="h-3 w-3" /> Instagram
                            </a>
                          </Button>
                        ) : null}
                        {mapsUrl ? (
                          <Button size="sm" variant="outline" asChild>
                            <a href={mapsUrl} target="_blank" rel="noreferrer" title={mapsUrl}>
                              <MapPin className="h-3 w-3" /> Maps
                            </a>
                          </Button>
                        ) : null}
                      </div>
                    </TableCell>
                  </TableRow>
                  {(lead.approach_script || analyzedPosts > 0 || lead.cnpj_info?.cnpj || ads.meta_ads_library_url || ads.google_ads_transparency_url) ? (
                    <TableRow className="bg-muted/20">
                      <TableCell colSpan={9}>
                        <div className="grid gap-3 md:grid-cols-2">
                          {(ads.meta_ads_library_url || ads.google_ads_transparency_url) ? (
                            <div className="rounded-md border bg-background p-3">
                              <div className="mb-2 flex items-center gap-2 text-sm font-medium">
                                <Megaphone className="h-4 w-4 text-primary" />
                                Anuncios e tracking
                              </div>
                              <div className="space-y-2 text-xs text-muted-foreground">
                                <div className="flex flex-wrap gap-1">
                                  <Badge variant={adsBadgeVariant}>{adsStatusLabels[adsStatus] || adsStatus}</Badge>
                                  {(ads.platforms || []).map((platform) => <Badge key={platform} variant="outline">{platform}</Badge>)}
                                </div>
                                {(ads.signals || []).length > 0 ? (
                                  <p className="line-clamp-2" title={(ads.signals || []).join(' | ')}>{(ads.signals || []).join(' | ')}</p>
                                ) : (
                                  <p>Nenhum pixel de trafego pago detectado no HTML inicial.</p>
                                )}
                                <div className="flex flex-wrap gap-2">
                                  {ads.meta_ads_library_url ? (
                                    <Button size="sm" variant="outline" asChild>
                                      <a href={ads.meta_ads_library_url} target="_blank" rel="noreferrer">
                                        <Instagram className="h-3 w-3" /> Meta Ads
                                      </a>
                                    </Button>
                                  ) : null}
                                  {ads.google_ads_transparency_url ? (
                                    <Button size="sm" variant="outline" asChild>
                                      <a href={ads.google_ads_transparency_url} target="_blank" rel="noreferrer">
                                        <ExternalLink className="h-3 w-3" /> Google Ads
                                      </a>
                                    </Button>
                                  ) : null}
                                </div>
                              </div>
                            </div>
                          ) : null}
                          {lead.cnpj_info?.cnpj ? (
                            <div className="rounded-md border bg-background p-3">
                              <div className="mb-2 text-sm font-medium">CNPJ e decisores</div>
                              <div className="grid gap-2 text-xs text-muted-foreground">
                                <span>CNPJ: <strong className="text-foreground">{formatCnpj(lead.cnpj_info.cnpj)}</strong></span>
                                {lead.cnpj_info.razao_social ? <span>Razao social: <strong className="text-foreground">{lead.cnpj_info.razao_social}</strong></span> : null}
                                {(lead.cnpj_info.owners || []).length > 0 ? (
                                  <div className="space-y-1">
                                    {(lead.cnpj_info.owners || []).map((owner, ownerIndex) => (
                                      <p key={`${owner.name || 'owner'}-${ownerIndex}`}>
                                        <strong className="text-foreground">{owner.name || 'Sem nome'}</strong>
                                        {owner.role ? ` - ${owner.role}` : ''}
                                      </p>
                                    ))}
                                  </div>
                                ) : (
                                  <span>CNPJ encontrado, mas sem socios retornados pela fonte.</span>
                                )}
                              </div>
                            </div>
                          ) : null}
                          {lead.approach_script ? (
                            <div className="rounded-md border bg-background p-3">
                              <div className="mb-2 flex items-center gap-2 text-sm font-medium">
                                <MessageSquareText className="h-4 w-4 text-primary" />
                                Hook de abordagem
                              </div>
                              <p className="whitespace-pre-wrap text-xs leading-relaxed text-muted-foreground">{lead.approach_script}</p>
                            </div>
                          ) : null}
                          {analyzedPosts > 0 ? (
                            <div className="rounded-md border bg-background p-3">
                              <div className="mb-2 flex items-center gap-2 text-sm font-medium">
                                <BarChart3 className="h-4 w-4 text-primary" />
                                Analise do Instagram
                              </div>
                              <div className="grid gap-2 text-xs text-muted-foreground sm:grid-cols-2">
                                <span>Posts analisados: <strong className="text-foreground">{analyzedPosts}</strong></span>
                                <span>Videos/Reels: <strong className="text-foreground">{contentMetrics.video_ratio ?? 0}%</strong></span>
                                <span>Posts com CTA: <strong className="text-foreground">{contentMetrics.cta_ratio ?? 0}%</strong></span>
                                <span>Media curtidas: <strong className="text-foreground">{formatNumber(instagram.avg_likes)}</strong></span>
                              </div>
                              {topHashtags.length > 0 ? (
                                <div className="mt-2 flex flex-wrap gap-1">
                                  {topHashtags.map((tag) => <Badge key={tag} variant="outline">#{tag}</Badge>)}
                                </div>
                              ) : null}
                            </div>
                          ) : null}
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : null}
                </Fragment>
              )
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}

export function ExtractionPage() {
  return (
    <div className="space-y-4">
      <Tabs defaultValue="scrape" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="scrape" className="gap-1"><Search className="h-3 w-3" /> Google Maps</TabsTrigger>
          <TabsTrigger value="enrich" className="gap-1"><Instagram className="h-3 w-3" /> Enriquecer</TabsTrigger>
          <TabsTrigger value="analyze" className="gap-1"><BarChart3 className="h-3 w-3" /> Analisar</TabsTrigger>
          <TabsTrigger value="reports" className="gap-1"><FileText className="h-3 w-3" /> Relatórios</TabsTrigger>
          <TabsTrigger value="pipeline" className="gap-1"><Workflow className="h-3 w-3" /> Pipeline</TabsTrigger>
        </TabsList>

        <TabsContent value="scrape"><ScrapeTab /></TabsContent>
        <TabsContent value="enrich"><EnrichTab /></TabsContent>
        <TabsContent value="analyze"><AnalyzeTab /></TabsContent>
        <TabsContent value="reports"><ReportsTab /></TabsContent>
        <TabsContent value="pipeline"><PipelineTab /></TabsContent>
      </Tabs>
    </div>
  )
}

function ScrapeTab() {
  const [form, setForm] = useState({ query: '', location: 'São Paulo', limit: 20 })
  const scrapeMutation = useScrapeGoogleMapsSync()

  const handleScrape = () => {
    if (!form.query) return
    scrapeMutation.mutate(form)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Search className="h-5 w-5 text-primary" /> Buscar Leads no Google Maps</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-3">
          <div><Label>Categoria / Busca</Label><Input placeholder="Ex: restaurantes, salões de beleza" value={form.query} onChange={(e) => setForm({ ...form, query: e.target.value })} /></div>
          <div><Label>Localização</Label><Input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} /></div>
          <div><Label>Limite</Label><Input type="number" min={1} max={50} value={form.limit} onChange={(e) => setForm({ ...form, limit: Number(e.target.value) })} /></div>
        </div>

        <Button onClick={handleScrape} disabled={scrapeMutation.isPending || !form.query}>
          {scrapeMutation.isPending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Buscando...</> : <><Search className="mr-2 h-4 w-4" /> Iniciar Busca</>}
        </Button>

        {scrapeMutation.isPending && <Progress value={33} className="animate-pulse" />}

        {scrapeMutation.isSuccess && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-emerald-500">
              <CheckCircle2 className="h-4 w-4" />
              <span className="text-sm font-medium">
                Novos: {scrapeMutation.data.total} leads
                {typeof scrapeMutation.data.duplicates_skipped === 'number' && scrapeMutation.data.duplicates_skipped > 0
                  ? ` | Repetidos ignorados: ${scrapeMutation.data.duplicates_skipped}`
                  : ''}
              </span>
            </div>
            <ProspectResultsList leads={scrapeMutation.data.leads || []} />
          </div>
        )}

        {scrapeMutation.isError && (
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-4 w-4" /><span className="text-sm">{scrapeMutation.error.message}</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function EnrichTab() {
  const [leadsFile, setLeadsFile] = useState('')
  const enrichMutation = useEnrichLeads()
  const latestLeads = useProspectLeads({ status: 'enriched' })
  const displayedLeads = enrichMutation.data?.leads?.length ? enrichMutation.data.leads : latestLeads.data?.leads || []

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Instagram className="h-5 w-5 text-primary" /> Enriquecer Leads com Instagram</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div><Label>Arquivo de Leads (opcional - usa o mais recente se vazio)</Label><Input placeholder="data/leads/arquivo.json" value={leadsFile} onChange={(e) => setLeadsFile(e.target.value)} /></div>

        <Button onClick={() => enrichMutation.mutate({ leads_file: leadsFile || undefined })} disabled={enrichMutation.isPending}>
          {enrichMutation.isPending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Enriquecendo...</> : <><Instagram className="mr-2 h-4 w-4" /> Enriquecer</>}
        </Button>

        {enrichMutation.isPending && <Progress value={50} className="animate-pulse" />}

        {enrichMutation.isSuccess && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-emerald-500">
              <CheckCircle2 className="h-4 w-4" />
              <span className="text-sm font-medium">Enriquecidos: {enrichMutation.data.total} leads</span>
            </div>
            <ProspectResultsList leads={displayedLeads} />
          </div>
        )}

        {!enrichMutation.isSuccess && displayedLeads.length > 0 && (
          <div className="space-y-3">
            <p className="text-sm font-medium text-muted-foreground">Ultimos leads enriquecidos</p>
            <ProspectResultsList leads={displayedLeads} />
          </div>
        )}

        {enrichMutation.isError && (
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-4 w-4" /><span className="text-sm">{enrichMutation.error.message}</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function AnalyzeTab() {
  const [leadsFile, setLeadsFile] = useState('')
  const [postsCount, setPostsCount] = useState(12)
  const analyzeMutation = useAnalyzeInstagram()
  const latestLeads = useProspectLeads({ status: 'enriched' })
  const displayedLeads = analyzeMutation.data?.leads?.length ? analyzeMutation.data.leads : latestLeads.data?.leads || []

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><BarChart3 className="h-5 w-5 text-primary" /> Analisar Perfis Instagram</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div><Label>Arquivo de Leads (opcional)</Label><Input placeholder="data/enriched/arquivo.json" value={leadsFile} onChange={(e) => setLeadsFile(e.target.value)} /></div>
          <div><Label>Posts para Analisar</Label><Input type="number" min={1} max={30} value={postsCount} onChange={(e) => setPostsCount(Number(e.target.value))} /></div>
        </div>

        <Button onClick={() => analyzeMutation.mutate({ leads_file: leadsFile || undefined, posts_to_analyze: postsCount })} disabled={analyzeMutation.isPending}>
          {analyzeMutation.isPending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Analisando...</> : <><BarChart3 className="mr-2 h-4 w-4" /> Analisar</>}
        </Button>

        {analyzeMutation.isPending && <Progress value={50} className="animate-pulse" />}

        {analyzeMutation.isSuccess && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-emerald-500">
              <CheckCircle2 className="h-4 w-4" />
              <span className="text-sm font-medium">Analisados: {analyzeMutation.data.total} leads</span>
            </div>
            <div className="flex gap-2">
              <Badge variant="destructive">Hot: {analyzeMutation.data.hot}</Badge>
              <Badge variant="warning">Warm: {analyzeMutation.data.warm}</Badge>
              <Badge variant="outline">Cold: {analyzeMutation.data.cold}</Badge>
            </div>
            <ProspectResultsList leads={displayedLeads} />
          </div>
        )}

        {!analyzeMutation.isSuccess && displayedLeads.length > 0 && (
          <div className="space-y-3">
            <p className="text-sm font-medium text-muted-foreground">Ultimos leads analisados/enriquecidos</p>
            <ProspectResultsList leads={displayedLeads} />
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function ReportsTab() {
  const [leadsFile, setLeadsFile] = useState('')
  const [title, setTitle] = useState('Relatório de Prospecção')
  const reportMutation = useGenerateReport()
  const { data: reportsData, isLoading } = useListReports()

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><FileText className="h-5 w-5 text-primary" /> Gerar Relatório</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div><Label>Arquivo de Leads (opcional)</Label><Input placeholder="data/enriched/arquivo.json" value={leadsFile} onChange={(e) => setLeadsFile(e.target.value)} /></div>
            <div><Label>Título</Label><Input value={title} onChange={(e) => setTitle(e.target.value)} /></div>
          </div>
          <Button onClick={() => reportMutation.mutate({ leads_file: leadsFile || undefined, title })} disabled={reportMutation.isPending}>
            {reportMutation.isPending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Gerando...</> : <><FileText className="mr-2 h-4 w-4" /> Gerar Relatório</>}
          </Button>
          {reportMutation.isSuccess && (
            <div className="flex items-center gap-2 text-emerald-500">
              <CheckCircle2 className="h-4 w-4" /><span className="text-sm font-medium">Relatório gerado com sucesso!</span>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-lg">Relatórios Existentes</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? <Skeleton className="h-20 w-full" /> : (
            <div className="space-y-2">
              {(reportsData?.reports || []).map((r) => (
                <div key={r.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <p className="font-medium text-sm">{r.title}</p>
                    <p className="text-xs text-muted-foreground">{r.generated_at ? new Date(r.generated_at).toLocaleString('pt-BR') : ''}</p>
                  </div>
                  <Button size="sm" variant="outline"><Download className="mr-1 h-3 w-3" /> Download</Button>
                </div>
              ))}
              {(reportsData?.reports || []).length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">Nenhum relatório gerado ainda</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function PipelineTab() {
  const [form, setForm] = useState({ query: '', location: 'São Paulo', limit: 20 })
  const [step, setStep] = useState(0)
  const [running, setRunning] = useState(false)
  const [results, setResults] = useState<Record<string, any>>({})

  const scrapeMutation = useScrapeGoogleMapsSync()
  const enrichMutation = useEnrichLeads()
  const analyzeMutation = useAnalyzeInstagram()
  const reportMutation = useGenerateReport()
  const importMutation = useImportLeads()

  const steps = [
    { label: 'Scout', desc: 'Buscar no Google Maps', icon: Search },
    { label: 'Enrich', desc: 'Encontrar Instagram', icon: Instagram },
    { label: 'Analyze', desc: 'Analisar perfis', icon: BarChart3 },
    { label: 'Report', desc: 'Gerar relatório', icon: FileText },
    { label: 'Import', desc: 'Salvar na base de leads', icon: Upload },
  ]

  const runPipeline = async () => {
    if (!form.query) return
    setRunning(true)
    setStep(0)
    setResults({})

    try {
      setStep(1)
      const scrapeResult = await scrapeMutation.mutateAsync(form)
      setResults((r) => ({ ...r, scrape: scrapeResult }))

      setStep(2)
      const enrichResult = await enrichMutation.mutateAsync({})
      setResults((r) => ({ ...r, enrich: enrichResult }))

      setStep(3)
      const analyzeResult = await analyzeMutation.mutateAsync({})
      setResults((r) => ({ ...r, analyze: analyzeResult }))

      setStep(4)
      const reportResult = await reportMutation.mutateAsync({ title: `Pipeline - ${form.query} em ${form.location}` })
      setResults((r) => ({ ...r, report: reportResult }))

      setStep(5)
      const importFile = new File(
        [JSON.stringify({ leads: analyzeResult.leads || [] })],
        `pipeline-${Date.now()}.json`,
        { type: 'application/json' },
      )
      const importResult = await importMutation.mutateAsync(importFile)
      setResults((r) => ({ ...r, import: importResult }))

      setStep(6)
    } catch {
      // Step stays at current failed step
    } finally {
      setRunning(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Workflow className="h-5 w-5 text-primary" /> Pipeline Completo</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-4 md:grid-cols-3">
          <div><Label>Categoria</Label><Input placeholder="Ex: restaurantes" value={form.query} onChange={(e) => setForm({ ...form, query: e.target.value })} /></div>
          <div><Label>Localização</Label><Input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} /></div>
          <div><Label>Limite</Label><Input type="number" min={1} max={50} value={form.limit} onChange={(e) => setForm({ ...form, limit: Number(e.target.value) })} /></div>
        </div>

        <Button onClick={runPipeline} disabled={running || !form.query} className="w-full">
          {running ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Executando Pipeline...</> : <><Workflow className="mr-2 h-4 w-4" /> Executar Pipeline Completo</>}
        </Button>

        {/* Stepper */}
        {step > 0 && (
          <div className="space-y-3">
            {steps.map((s, i) => {
              const Icon = s.icon
              const isActive = step === i + 1
              const isDone = step > i + 1
              const isFailed = !running && step === i + 1 && !isDone

              return (
                <div key={i} className={`flex items-center gap-3 rounded-lg border p-3 transition-colors ${isDone ? 'border-emerald-500/50 bg-emerald-500/5' : isActive ? 'border-primary/50 bg-primary/5' : isFailed ? 'border-destructive/50 bg-destructive/5' : 'opacity-50'}`}>
                  <div className={`rounded-full p-2 ${isDone ? 'bg-emerald-500/20 text-emerald-500' : isActive ? 'bg-primary/20 text-primary' : 'bg-muted'}`}>
                    {isDone ? <CheckCircle2 className="h-4 w-4" /> : isActive && running ? <Loader2 className="h-4 w-4 animate-spin" /> : isFailed ? <AlertCircle className="h-4 w-4 text-destructive" /> : <Icon className="h-4 w-4" />}
                  </div>
                  <div>
                    <p className="text-sm font-semibold">{s.label}</p>
                    <p className="text-xs text-muted-foreground">{s.desc}</p>
                  </div>
                  {isDone && results[['scrape', 'enrich', 'analyze', 'report', 'import'][i]] && (
                    <Badge variant="success" className="ml-auto">OK</Badge>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {step === 6 && (
          <div className="rounded-lg border border-emerald-500/50 bg-emerald-500/5 p-4 text-center">
            <CheckCircle2 className="h-8 w-8 text-emerald-500 mx-auto mb-2" />
            <p className="font-semibold text-emerald-500">Pipeline concluído com sucesso!</p>
            <p className="text-sm text-muted-foreground mt-1">Leads prospectados, enriquecidos, analisados, reportados e importados para a base.</p>
            {results.import && (
              <p className="mt-2 text-xs text-muted-foreground">
                Importados: {results.import.total_imported} | Duplicatas: {results.import.duplicates_skipped} | Erros: {results.import.errors}
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
