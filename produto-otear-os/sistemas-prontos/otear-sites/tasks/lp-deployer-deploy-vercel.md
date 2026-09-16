---
task: deployVercel()
responsavel: "Anchor"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: clientRepo
    tipo: string
    obrigatorio: true
    descricao: "URL do repositÃ³rio GitHub do cliente (source: initClientRepo())"
  - nome: qaReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio final de QA com PASS >= 8.0 (source: finalReport())"
  - nome: clientName
    tipo: string
    obrigatorio: true
    descricao: "Nome do cliente para nomear o projeto na Vercel"

Saida:
  - nome: deployResult
    tipo: object
    obrigatorio: true
    descricao: "Resultado do deploy: URL Vercel (.vercel.app), project ID, status (destination: setupDomain())"
  - nome: vercelProject
    tipo: object
    obrigatorio: true
    descricao: "ConfiguraÃ§Ã£o do projeto na Vercel (destination: lp-versioner)"

Checklist:
  pre-conditions:
    - "[ ] QA report com PASS e score >= 8.0"
    - "[ ] Repo GitHub do cliente criado com cÃ³digo fonte"
    - "[ ] Vercel CLI instalada e autenticada (vercel login)"
    - "[ ] Conta Vercel (Free/Hobby) ativa"
  post-conditions:
    - "[ ] Projeto criado na Vercel conectado ao repo GitHub"
    - "[ ] Build passando sem erros"
    - "[ ] Auto-deploy configurado (push no main = deploy)"
    - "[ ] URL grÃ¡tis acessÃ­vel: {cliente}-lp.vercel.app"
    - "[ ] VariÃ¡veis de ambiente configuradas na Vercel"
    - "[ ] Preview deploys ativos para branches"

Performance:
  duration_expected: "5 minutes"
  cacheable: false
  parallelizable: false
---

# deployVercel()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ clientRepo       â”‚â”€â”€â”€â”
â”‚ (string)         â”‚   â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                  â”‚   â”œâ”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€>â”‚ deployResult        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â”‚  deployVercel        â”‚     â”‚ (object)            â”‚
                       â”‚     â”‚  @Anchor             â”‚     â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚     â”‚                      â”‚â”€â”€â”€â”€>â”‚ vercelProject       â”‚
â”‚ qaReport         â”‚â”€â”€â”€â”¤     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â”‚ (object)            â”‚
â”‚ (file)           â”‚   â”‚                                  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚                                         â”‚
                       â”‚                                         â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚                            â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ clientName       â”‚â”€â”€â”€â”˜                            â”‚ setupDomain()          â”‚
â”‚ (string)         â”‚                                â”‚ lp-deployer            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

Deploy do frontend Next.js na Vercel conectando o repositÃ³rio GitHub do cliente. A Vercel detecta Next.js automaticamente, configura o build e deploy sem necessidade de Dockerfile ou configuraÃ§Ã£o extra. Cada cliente ganha um projeto na Vercel com URL grÃ¡tis e auto-deploy.

## Passos

1. **Validar QA gate** â€” Confirmar que qaReport tem PASS com score >= 8.0.
2. **Importar projeto na Vercel** â€” Via dashboard ou CLI: conectar o repo GitHub do cliente.
3. **Vercel auto-detect** â€” Framework Next.js detectado automaticamente (zero config).
4. **Configurar variÃ¡veis de ambiente** â€” Setar variÃ¡veis na Vercel (se houver).
5. **Primeiro deploy** â€” Vercel faz build e deploy automaticamente.
6. **Verificar build** â€” Confirmar que build passou sem erros.
7. **Testar URL grÃ¡tis** â€” Acessar `{cliente}-lp.vercel.app` e verificar resposta.
8. **Confirmar auto-deploy** â€” Push no main = deploy automÃ¡tico configurado.
9. **Registrar resultado** â€” Salvar URL, project ID e status.

## Vercel â€” Import via CLI

```bash
# OpÃ§Ã£o 1: Import via CLI (rÃ¡pido)
cd /path/to/client-repo
vercel link --yes
vercel --prod

# OpÃ§Ã£o 2: Import via Dashboard (recomendado para clientes)
# 1. Abrir vercel.com/new
# 2. Importar repo GitHub do cliente
# 3. Vercel detecta Next.js automaticamente
# 4. Clicar "Deploy"
```

## VariÃ¡veis de Ambiente na Vercel

```bash
# Setar variÃ¡veis via CLI
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_SITE_URL production

# Ou via dashboard: Settings â†’ Environment Variables
```

## Framework Settings (Auto-detectado)

```
Framework Preset: Next.js
Build Command: next build (ou npm run build)
Output Directory: .next
Install Command: npm install
Node.js Version: 20.x
```

