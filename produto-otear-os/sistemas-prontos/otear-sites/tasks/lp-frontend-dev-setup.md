---
task: setupFrontendProject()
responsavel: "Pixel"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: dsSelection
    tipo: file
    obrigatorio: true
    descricao: "Design system selecionado com componentes e configuraÃ§Ã£o base (source: selectDesignSystem())"
  - nome: scopeDefinition
    tipo: file
    obrigatorio: true
    descricao: "DefiniÃ§Ã£o de escopo do projeto com features habilitadas (source: defineScope())"

Saida:
  - nome: frontendProject
    tipo: file
    obrigatorio: true
    descricao: "Projeto Next.js inicializado com toda a infraestrutura configurada (destination: implementDesignSystem())"
  - nome: projectConfig
    tipo: object
    obrigatorio: true
    descricao: "ConfiguraÃ§Ãµes do projeto â€” paths, ports, scripts disponÃ­veis (destination: lp-integrator)"

Checklist:
  pre-conditions:
    - "[ ] dsSelection existe com design system escolhido (shadcn/ui)"
    - "[ ] scopeDefinition existe com features habilitadas definidas"
  post-conditions:
    - "[ ] Next.js 15 App Router inicializado"
    - "[ ] Tailwind CSS 4 configurado e funcional"
    - "[ ] shadcn/ui instalado com componentes base"
    - "[ ] TypeScript strict mode habilitado"
    - "[ ] next-themes configurado para dark mode"
    - "[ ] Estrutura de diretÃ³rios criada (src/components, src/sections, src/lib, src/styles)"
    - "[ ] Projeto roda com npm run dev sem erros"

Performance:
  duration_expected: "10 minutes"
  cacheable: true
  parallelizable: false
---

# setupFrontendProject()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ dsSelection      â”‚â”€â”€â”€â”
â”‚ (file)           â”‚   â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                  â”‚   â”œâ”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€>â”‚ frontendProject     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â”‚  setupFrontendProjectâ”‚     â”‚ (file)              â”‚
                       â”‚     â”‚  @Pixel              â”‚     â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚     â”‚                      â”‚â”€â”€â”€â”€>â”‚ projectConfig       â”‚
â”‚ scopeDefinition  â”‚â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â”‚ (object)            â”‚
â”‚ (file)           â”‚                                      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                             â”‚
                                                                 â–¼
                                                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                    â”‚ implementDesignSystem()â”‚
                                                    â”‚ lp-integrator          â”‚
                                                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `setupFrontendProject()` estabelece a fundaÃ§Ã£o tÃ©cnica do frontend da landing page. O agente **Pixel** inicializa um projeto Next.js 15 com App Router, configura Tailwind CSS 4, instala o shadcn/ui como design system, habilita TypeScript strict mode e prepara a infraestrutura de dark mode com next-themes.

Esta Ã© uma task de configuraÃ§Ã£o (Config) que precisa rodar uma Ãºnica vez e produz o scaffold sobre o qual todo o design system e as seÃ§Ãµes serÃ£o construÃ­dos. O projectConfig exportado permite que o integrador saiba onde encontrar arquivos, portas e scripts disponÃ­veis.

## Passos

1. **Validar inputs** â€” Confirmar que dsSelection contÃ©m a escolha de design system e que scopeDefinition define as features habilitadas.
2. **Inicializar Next.js 15** â€” Executar `npx create-next-app@latest` com App Router, TypeScript, Tailwind CSS e ESLint habilitados.
3. **Configurar TypeScript strict** â€” Atualizar `tsconfig.json` com `strict: true`, `noUncheckedIndexedAccess: true` e paths aliases (`@/`).
4. **Configurar Tailwind CSS 4** â€” Verificar a configuraÃ§Ã£o do Tailwind CSS 4 com `@import "tailwindcss"` e CSS-first config.
5. **Instalar shadcn/ui** â€” Executar `npx shadcn@latest init` com as opÃ§Ãµes adequadas e instalar componentes base (button, card, input, dialog).
6. **Configurar next-themes** â€” Instalar next-themes, criar ThemeProvider, configurar layout root com `suppressHydrationWarning` e adicionar toggle de dark mode.
7. **Criar estrutura de diretÃ³rios** â€” Criar `src/components/` (atoms, molecules, organisms), `src/sections/`, `src/lib/`, `src/styles/`.
8. **Configurar scripts** â€” Garantir que `package.json` tenha scripts para `dev`, `build`, `lint`, `typecheck`.
9. **Testar setup** â€” Executar `npm run dev` e verificar que o projeto inicia sem erros e o hot reload funciona.
10. **Exportar projectConfig** â€” Documentar paths, porta de dev, scripts disponÃ­veis e versÃµes instaladas.

