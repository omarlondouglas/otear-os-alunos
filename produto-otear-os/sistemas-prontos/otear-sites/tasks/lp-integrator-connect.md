---
task: connectFrontendBackend()
responsavel: "Bridge"
responsavel_type: Agente
atomic_layer: Molecule

Entrada:
  - nome: landingPage
    tipo: file
    obrigatorio: true
    descricao: "Landing page montada com todos os componentes (source: assemblePage())"
  - nome: leadsApi
    tipo: file
    obrigatorio: true
    descricao: "Endpoints de captura de leads implementados (source: createLeadEndpoints())"
  - nome: backendConfig
    tipo: object
    obrigatorio: true
    descricao: "ConfiguraÃ§Ã£o do projeto backend â€” URL, porta, framework (source: setupBackendProject())"

Saida:
  - nome: apiClient
    tipo: file
    obrigatorio: true
    descricao: "Client TypeScript para comunicaÃ§Ã£o com a API backend em src/lib/api.ts (destination: lp-reviewer)"
  - nome: envConfig
    tipo: file
    obrigatorio: true
    descricao: "Arquivos de configuraÃ§Ã£o de variÃ¡veis de ambiente para frontend e backend (destination: lp-reviewer)"
  - nome: connectionTestReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio de teste de conexÃ£o frontendâ†”backend (destination: lp-reviewer)"

Checklist:
  pre-conditions:
    - "[ ] Projeto frontend existe e estÃ¡ em execuÃ§Ã£o"
    - "[ ] Projeto backend existe e estÃ¡ em execuÃ§Ã£o"
    - "[ ] leadsApi foi gerado por createLeadEndpoints()"
    - "[ ] backendConfig contÃ©m URL e porta do backend"
  post-conditions:
    - "[ ] API client TypeScript (fetch wrapper) criado em src/lib/api.ts"
    - "[ ] CORS configurado no backend para a URL do frontend"
    - "[ ] VariÃ¡veis de ambiente configuradas (.env.local para frontend com NEXT_PUBLIC_API_URL, .env para backend)"
    - "[ ] SubmissÃ£o de formulÃ¡rio funcionando end-to-end"
    - "[ ] Tratamento de erros com mensagens amigÃ¡veis ao usuÃ¡rio"
    - "[ ] Backup em localStorage quando backend estiver offline"

Performance:
  duration_expected: "18 minutes"
  cacheable: false
  parallelizable: false
---

# connectFrontendBackend()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  landingPage          â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  apiClient              â”‚
â”‚  (file)               â”‚       â”‚                      â”‚       â”‚  (file)                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  connectFrontend     â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  leadsApi             â”‚â”€â”€â”€â”€â”€â”€>â”‚  Backend             â”‚â”€â”€â”€â”€â”€â”€>â”‚  envConfig              â”‚
â”‚  (file)               â”‚       â”‚  @Bridge             â”‚       â”‚  (file)                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  backendConfig        â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  connectionTestReport   â”‚
â”‚  (object)             â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â”‚  (file)                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                                                        â”‚
                                                                        â–¼
                                                               â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                               â”‚  lp-reviewer            â”‚
                                                               â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `connectFrontendBackend()` Ã© **CONDICIONAL** â€” sÃ³ Ã© executada quando `scopeDefinition` contÃ©m o flag `backend=true`. O agente **Bridge** cria a camada de comunicaÃ§Ã£o entre o frontend (landing page Next.js) e o backend (API Python/FastAPI), garantindo que os formulÃ¡rios da landing page enviem dados corretamente para os endpoints de captura de leads.

A task produz um API client TypeScript tipado, configura CORS no backend, estabelece variÃ¡veis de ambiente em ambos os projetos e implementa mecanismos de resiliÃªncia como tratamento de erros amigÃ¡vel e backup em localStorage quando o backend estiver indisponÃ­vel.

## Passos

1. **Verificar prÃ©-condiÃ§Ãµes** â€” Confirmar que ambos os projetos (frontend e backend) existem e estÃ£o em execuÃ§Ã£o, e que `leadsApi` e `backendConfig` estÃ£o disponÃ­veis.
2. **Configurar variÃ¡veis de ambiente do frontend** â€” Criar/atualizar `.env.local` com `NEXT_PUBLIC_API_URL` apontando para o backend.
3. **Configurar variÃ¡veis de ambiente do backend** â€” Criar/atualizar `.env` com as variÃ¡veis necessÃ¡rias, incluindo `ALLOWED_ORIGINS` para CORS.
4. **Implementar CORS no backend** â€” Configurar middleware CORS no FastAPI para aceitar requisiÃ§Ãµes da URL do frontend, com headers e mÃ©todos adequados.
5. **Criar API client TypeScript** â€” Implementar `src/lib/api.ts` com fetch wrapper tipado, incluindo:
   - MÃ©todos para cada endpoint do `leadsApi`
   - Tipagem TypeScript para request/response
   - Interceptors para headers (Content-Type, Authorization se necessÃ¡rio)
   - Timeout configurÃ¡vel
6. **Implementar tratamento de erros** â€” Adicionar lÃ³gica de erro que traduz status HTTP em mensagens amigÃ¡veis para o usuÃ¡rio (ex: 422 â†’ "Verifique os campos", 500 â†’ "Tente novamente").
7. **Implementar fallback localStorage** â€” Criar mecanismo que detecta falha de conexÃ£o com o backend e salva os dados do formulÃ¡rio em localStorage, com retry automÃ¡tico quando a conexÃ£o for restaurada.
8. **Conectar formulÃ¡rios da landing page** â€” Integrar os formulÃ¡rios de captura de lead com o API client, substituindo qualquer lÃ³gica mock existente.
9. **Testar conexÃ£o end-to-end** â€” Executar teste completo: preencher formulÃ¡rio â†’ enviar â†’ verificar no backend â†’ gerar `connectionTestReport`.
10. **Gerar outputs** â€” Disponibilizar `apiClient`, `envConfig` e `connectionTestReport` para o reviewer.

