# Frontend Rebuild Plan — O Tear Prospecção

## Resumo
Rebuild completo do frontend: remover MUI, adotar shadcn/ui + Radix + Tailwind CSS com o design system neon green, adicionar página de Extração de Leads (ProspectPro), e criar Dockerfile para EasyPanel.

---

## Fase 1: Setup do Projeto (config + dependências)

### 1.1 Atualizar `package.json`
- **Remover**: `@mui/*`, `@emotion/*`, `recharts`
- **Adicionar**: `shadcn/ui` deps (`class-variance-authority`, `clsx`, `tailwind-merge`, `lucide-react`, `@radix-ui/react-*`, `tailwindcss-animate`, `next-themes` ou `theme-provider` manual, `three` + `@types/three` para WebGL shader, `recharts` manter para gráficos)
- Manter: `react`, `react-dom`, `react-router-dom`, `@tanstack/react-query`, `framer-motion`, `react-hook-form`, `zod`, `@hookform/resolvers`

### 1.2 Atualizar `tailwind.config.ts`
- Habilitar preflight (remover `corePlugins: { preflight: false }`)
- Configurar design system HSL tokens:
  - `--primary: 82 100% 54%` (neon green)
  - `--background`, `--foreground`, `--card`, `--muted`, `--destructive`, `--border`
  - `--radius: 1rem`
  - Sidebar tokens dedicados (`--sidebar-*`)
- Adicionar `tailwindcss-animate` plugin
- Configurar fonte `Urbanist`

### 1.3 Atualizar `vite.config.ts`
- Adicionar path alias `@/` → `./src`

### 1.4 Atualizar `tsconfig.json`
- Confirmar paths alias `@/*` → `src/*`

### 1.5 Atualizar `index.html`
- Adicionar Google Fonts `Urbanist` (400,500,600,700,800)
- Favicon atualizado

### 1.6 Criar CSS global (`src/index.css`)
- CSS variables HSL para light e dark mode
- `.dark` class no `<html>` para toggle
- Base styles com Urbanist
- Sidebar tokens

---

## Fase 2: Componentes Base (shadcn/ui style)

### 2.1 Utility `src/lib/utils.ts`
- `cn()` helper (clsx + tailwind-merge)

### 2.2 Componentes UI (`src/components/ui/`)
Criar manualmente no estilo shadcn/ui:
- `button.tsx` — CVA variants (default, destructive, outline, ghost, link)
- `card.tsx` — Card, CardHeader, CardContent, CardTitle, CardDescription
- `badge.tsx` — Badge com variants (default, destructive, outline, secondary)
- `input.tsx` — Input estilizado
- `textarea.tsx`
- `label.tsx`
- `select.tsx` — usando Radix Select
- `dialog.tsx` — usando Radix Dialog
- `table.tsx` — Table, TableHeader, TableBody, TableRow, TableHead, TableCell
- `checkbox.tsx` — usando Radix Checkbox
- `tabs.tsx` — usando Radix Tabs
- `progress.tsx` — usando Radix Progress
- `separator.tsx`
- `sheet.tsx` — para mobile sidebar
- `tooltip.tsx`
- `toast.tsx` + `toaster.tsx` + `use-toast.ts`
- `dropdown-menu.tsx`
- `skeleton.tsx` — loading states
- `avatar.tsx`
- `scroll-area.tsx`
- `popover.tsx`
- `command.tsx` — search/command palette (opcional)

### 2.3 Theme Provider (`src/components/theme-provider.tsx`)
- Toggle dark/light via classe `.dark` no `<html>`
- Persistir preferência no localStorage

---

## Fase 3: Layout e Navegação

### 3.1 `src/components/layout/sidebar.tsx`
- Sidebar responsiva com shadcn style
- Logo "O Tear" com primary neon green
- 7 nav items: Dashboard, Leads, Extração, Campanhas, Mensagens, Números, Config
- Collapsible em mobile (Sheet)
- Tokens `--sidebar-*`
- Ícones via Lucide React

### 3.2 `src/components/layout/app-shell.tsx`
- Flex layout com Sidebar + main content
- Header com theme toggle (sun/moon)
- Mobile hamburger menu

### 3.3 `src/components/layout/header.tsx`
- Breadcrumb/título da página
- Theme toggle button
- Perfil/avatar (futuro)

---

## Fase 4: WebGL Shader Background

### 4.1 `src/components/webgl-shader.tsx`
- Three.js com fragment shader GLSL
- Ondas luminosas com distorção cromática RGB
- Uniforms: time, xScale(1.0), yScale(0.5), distortion(0.05), resolution
- Canvas fullscreen fixo z-index: -10, fundo preto
- Cleanup no unmount
- Responsivo via resize listener
- Usado em telas de auth (futuro) e como opção decorativa

---

## Fase 5: Rebuild das Páginas

### 5.1 `src/pages/dashboard.tsx`
- Stat cards com Card component (neon green accents)
- Funnel chart com Recharts (cores do design system)
- Resumo cards
- Skeleton loading states
- Grid responsivo com Tailwind

### 5.2 `src/pages/leads.tsx`
- Table component com shadcn style
- Filtros: search Input, Select para classificação e status
- Bulk actions bar
- Pagination
- Import dialog (Dialog component)
- Badges para classificação (Hot=destructive, Warm=warning, Cold=default)

### 5.3 `src/pages/extraction.tsx` ← **NOVA PÁGINA**
- **Aba 1: Google Maps Scraper**
  - Form: query (categoria), location, limit
  - Botão "Iniciar Busca" → POST `/api/prospect/scrape/maps`
  - Status do job em tempo real (polling)
  - Resultados em tabela
- **Aba 2: Enriquecer Leads**
  - Selecionar arquivo de leads raw
  - Botão "Enriquecer com Instagram" → POST `/api/prospect/enrich`
  - Progress/status
- **Aba 3: Analisar Instagram**
  - Selecionar arquivo enriched
  - Config: posts_to_analyze
  - Botão "Analisar" → POST `/api/prospect/analyze`
  - Resultados com scoring
- **Aba 4: Relatórios**
  - Gerar relatório → POST `/api/prospect/reports/generate`
  - Listar relatórios existentes
  - Download MD/JSON
- **Aba 5: Pipeline Completo**
  - Executar scout→enrich→analyze→report em sequência
  - Progress tracker visual (stepper)

### 5.4 `src/pages/campaigns.tsx`
- Card grid com status badges
- Create campaign Dialog
- Template editor com variáveis
- Activate/Pause buttons

### 5.5 `src/pages/messages.tsx`
- Split pane: conversation list + chat window
- Message bubbles (outbound = primary bg, inbound = muted bg)
- Reply input com send button
- Unread badges
- ScrollArea para lista e chat

### 5.6 `src/pages/numbers.tsx`
- Health summary badges
- Number cards com Progress bars (warmup, daily usage)
- Ban risk indicator
- Add number Dialog

### 5.7 `src/pages/settings.tsx`
- Cards para cada seção de config
- Business hours, Anti-ban, Warmup schedule, Opt-out keywords
- Toast de sucesso ao salvar

---

## Fase 6: Hooks e Services

### 6.1 Novos hooks para ProspectPro
- `src/hooks/use-extraction.ts`
  - `useScrapeGoogleMaps()` — mutation POST `/api/prospect/scrape/maps`
  - `useJobStatus(jobId)` — query GET `/api/prospect/scrape/status/{id}` com polling
  - `useEnrichLeads()` — mutation POST `/api/prospect/enrich`
  - `useAnalyzeInstagram()` — mutation POST `/api/prospect/analyze`
  - `useGenerateReport()` — mutation POST `/api/prospect/reports/generate`
  - `useListReports()` — query GET `/api/prospect/reports/`
  - `useProspectLeads(params)` — query GET `/api/prospect/leads`

### 6.2 Atualizar `src/services/api.ts`
- Adicionar suporte a base URL configurável para ProspectPro API
- Proxy no vite.config: `/api/prospect` → `http://localhost:8001` (prospect-pro backend)

### 6.3 Manter hooks existentes
- `useDashboard.ts`, `useLeads.ts`, `useCampaigns.ts`, `useMessages.ts`, `useNumbers.ts`
- Apenas atualizar imports (sem MUI types)

---

## Fase 7: Routing

### 7.1 Atualizar `src/App.tsx`
- Adicionar rota `/extraction` → ExtractionPage
- Manter todas as rotas existentes

### 7.2 Atualizar `src/main.tsx`
- Remover MUI ThemeProvider, CssBaseline
- Adicionar ThemeProvider custom (dark/light)
- Importar `index.css` ao invés de `tailwind.css`

---

## Fase 8: Docker + EasyPanel

### 8.1 `Dockerfile` (frontend — multi-stage)
```
Stage 1: Build (node:20-alpine)
- npm install
- npm run build
- Output: /app/dist

Stage 2: Serve (nginx:alpine)
- Copy dist to /usr/share/nginx/html
- Nginx config com SPA fallback (try_files)
- Proxy pass /api → backend
- Proxy pass /api/prospect → prospect-pro
- Expose 80
```

### 8.2 `nginx.conf`
- SPA fallback (try_files $uri /index.html)
- Proxy /api → backend:8000
- Proxy /api/prospect → prospect-pro:8001
- Gzip on
- Cache static assets

### 8.3 Atualizar `docker-compose.yml`
- Adicionar service `prospect-pro` (Python/FastAPI porta 8001)
- Atualizar frontend service para usar nginx (porta 80)
- Network compartilhada

### 8.4 `Dockerfile` para ProspectPro
- Python 3.11-slim
- Install playwright + browsers
- uvicorn na porta 8001

---

## Fase 9: Validação e Polish

- Verificar dark/light mode em todas as páginas
- Responsividade (mobile, tablet, desktop)
- Loading states (Skeleton)
- Error states
- Toast notifications
- Animações com tailwindcss-animate e Framer Motion

---

## Arquivos Criados/Modificados

### Novos (~35 arquivos):
- `src/index.css` — CSS variables + global styles
- `src/lib/utils.ts` — cn() utility
- `src/components/ui/` — ~18 componentes shadcn/ui
- `src/components/theme-provider.tsx`
- `src/components/layout/sidebar.tsx` (reescrito)
- `src/components/layout/app-shell.tsx` (reescrito)
- `src/components/layout/header.tsx` (novo)
- `src/components/webgl-shader.tsx`
- `src/pages/extraction.tsx` (novo)
- `src/hooks/use-extraction.ts` (novo)
- `Dockerfile` (frontend)
- `nginx.conf`
- `agents/prospect-pro/Dockerfile`

### Modificados:
- `package.json` — deps swap
- `tailwind.config.ts` — design system tokens
- `vite.config.ts` — path alias + proxy
- `tsconfig.json` — paths confirm
- `index.html` — fonts
- `src/main.tsx` — providers swap
- `src/App.tsx` — nova rota
- `src/services/api.ts` — prospect proxy
- `src/pages/*.tsx` — todas reescritas (MUI → shadcn/Tailwind)
- `src/hooks/*.ts` — imports cleanup
- `docker-compose.yml` — novos services

### Removidos:
- `src/theme/muiTheme.ts`
- `src/theme/tailwind.css`

---

## Ordem de Execução
1. Fase 1 (Setup) → 2 (UI Components) → 3 (Layout) → 4 (WebGL)
2. Fase 5 (Pages) → 6 (Hooks) → 7 (Routing)
3. Fase 8 (Docker)
4. Fase 9 (Polish)
