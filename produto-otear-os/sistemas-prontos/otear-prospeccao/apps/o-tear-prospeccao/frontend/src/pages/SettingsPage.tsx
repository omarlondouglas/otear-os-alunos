import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Database, Search, Users, Megaphone } from 'lucide-react'

export function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Configuracoes</h2>
        <p className="mt-1 text-sm text-muted-foreground">Aplicacao focada em prospeccao, enriquecimento e priorizacao de leads.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2 text-lg"><Search className="h-5 w-5 text-primary" /> Extração</CardTitle></CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <div className="flex items-center justify-between"><span>Fonte principal</span><Badge variant="outline">Google Maps</Badge></div>
            <div className="flex items-center justify-between"><span>Deduplicacao</span><Badge variant="success">Ativa</Badge></div>
            <p>Novas buscas ignoram empresas ja salvas por link do Maps, telefone ou nome + endereco.</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2 text-lg"><Users className="h-5 w-5 text-primary" /> Enriquecimento</CardTitle></CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <div className="flex items-center justify-between"><span>CNPJ e socios</span><Badge variant="success">Ativo</Badge></div>
            <div className="flex items-center justify-between"><span>Auditoria de site</span><Badge variant="success">Ativa</Badge></div>
            <p>Leads importados novamente atualizam registros existentes com dados mais completos.</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2 text-lg"><Megaphone className="h-5 w-5 text-primary" /> Sinais de Ads</CardTitle></CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <div className="flex items-center justify-between"><span>Pixels e tags</span><Badge variant="success">Detectando</Badge></div>
            <div className="flex items-center justify-between"><span>Bibliotecas publicas</span><Badge variant="outline">Links</Badge></div>
            <p>A deteccao indica estrutura de trafego. A confirmacao de anuncios ativos e feita pelos links Meta Ads e Google Ads.</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2 text-lg"><Database className="h-5 w-5 text-primary" /> Base</CardTitle></CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <div className="flex items-center justify-between"><span>Destino</span><Badge variant="outline">Supabase</Badge></div>
            <div className="flex items-center justify-between"><span>Atualizacao de duplicados</span><Badge variant="success">Ativa</Badge></div>
            <p>A pagina Leads mostra a base consolidada, ja enriquecida com decisores, site e sinais de ads.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
