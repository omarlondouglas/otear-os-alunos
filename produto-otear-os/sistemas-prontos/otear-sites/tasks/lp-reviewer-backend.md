---
task: reviewBackendSecurity()
responsavel: "Shield"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: leadsApi
    tipo: file
    obrigatorio: true
    descricao: "Endpoints de captura de leads implementados (source: createLeadEndpoints())"
  - nome: adminPanel
    tipo: file
    obrigatorio: true
    descricao: "Painel administrativo para gestÃ£o de leads (source: buildAdminPanel())"
  - nome: adminAuth
    tipo: file
    obrigatorio: true
    descricao: "Sistema de autenticaÃ§Ã£o e autorizaÃ§Ã£o do painel admin (source: buildAdminPanel())"

Saida:
  - nome: backendReview
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio detalhado de revisÃ£o de seguranÃ§a do backend com issues e sugestÃµes (destination: lp-backend-dev para correÃ§Ãµes)"
  - nome: backendScore
    tipo: object
    obrigatorio: true
    descricao: "Score numÃ©rico de seguranÃ§a do backend por dimensÃ£o (destination: produceFinalReport())"

Checklist:
  pre-conditions:
    - "[ ] Endpoints de backend existem e foram gerados por createLeadEndpoints()"
    - "[ ] Painel admin existe e foi gerado por buildAdminPanel()"
    - "[ ] Sistema de autenticaÃ§Ã£o implementado"
  post-conditions:
    - "[ ] OWASP Top 10 verificado"
    - "[ ] ValidaÃ§Ã£o de input verificada (Pydantic)"
    - "[ ] PrevenÃ§Ã£o de SQL injection verificada (uso de ORM)"
    - "[ ] AutenticaÃ§Ã£o testada (JWT)"
    - "[ ] AutorizaÃ§Ã£o testada (endpoints admin-only)"
    - "[ ] Rate limiting em endpoints pÃºblicos"
    - "[ ] CORS restritivo configurado"
    - "[ ] Nenhum segredo hardcoded no cÃ³digo"
    - "[ ] Respostas de erro nÃ£o expÃµem informaÃ§Ãµes internas"
    - "[ ] Issues categorizados como BLOCKER/WARNING/INFO"

Performance:
  duration_expected: "15 minutes"
  cacheable: false
  parallelizable: false
---

# reviewBackendSecurity()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  leadsApi             â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  backendReview          â”‚
â”‚  (file)               â”‚       â”‚                      â”‚       â”‚  (file)                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  reviewBackend       â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  adminPanel           â”‚â”€â”€â”€â”€â”€â”€>â”‚  Security            â”‚â”€â”€â”€â”€â”€â”€>â”‚  backendScore           â”‚
â”‚  (file)               â”‚       â”‚  @Shield             â”‚       â”‚  (object)               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  adminAuth            â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚               â”‚
â”‚  (file)               â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜               â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                              â–¼                  â–¼
                                                               â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                               â”‚ lp-backend   â”‚   â”‚ produceFinal â”‚
                                                               â”‚ -dev (fixes) â”‚   â”‚ Report()     â”‚
                                                               â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `reviewBackendSecurity()` Ã© **CONDICIONAL** â€” sÃ³ Ã© executada quando `scopeDefinition` contÃ©m o flag `backend=true`. O agente **Shield** realiza uma **auditoria de seguranÃ§a abrangente** do backend, cobrindo o OWASP Top 10, validaÃ§Ã£o de inputs, prevenÃ§Ã£o de injeÃ§Ã£o, autenticaÃ§Ã£o, autorizaÃ§Ã£o, rate limiting e prÃ¡ticas de seguranÃ§a em geral.

O review analisa os endpoints da API de leads, o painel administrativo e o sistema de autenticaÃ§Ã£o, verificando que as melhores prÃ¡ticas de seguranÃ§a foram seguidas e que nÃ£o existem vulnerabilidades conhecidas no cÃ³digo.

## Passos

1. **Carregar todos os inputs** â€” Ler `leadsApi`, `adminPanel` e `adminAuth` para contexto completo.
2. **Verificar OWASP Top 10** â€” Analisar o cÃ³digo contra as 10 vulnerabilidades mais crÃ­ticas (Injection, Broken Authentication, Sensitive Data Exposure, XXE, Broken Access Control, Security Misconfiguration, XSS, Insecure Deserialization, Using Components with Known Vulnerabilities, Insufficient Logging).
3. **Auditar validaÃ§Ã£o de input** â€” Verificar que todos os endpoints utilizam Pydantic models para validaÃ§Ã£o de entrada, com tipos corretos, limites de tamanho e sanitizaÃ§Ã£o de dados.
4. **Verificar prevenÃ§Ã£o de SQL injection** â€” Confirmar uso exclusivo de ORM (SQLAlchemy) para queries ao banco, sem queries SQL raw ou string concatenation.
5. **Testar autenticaÃ§Ã£o JWT** â€” Verificar implementaÃ§Ã£o do JWT: algoritmo seguro (RS256 ou HS256 com secret forte), expiraÃ§Ã£o configurada, refresh token se aplicÃ¡vel, e armazenamento seguro de tokens.
6. **Testar autorizaÃ§Ã£o** â€” Verificar que endpoints admin-only possuem guards de autorizaÃ§Ã£o, que nÃ£o existem endpoints administrativos acessÃ­veis sem autenticaÃ§Ã£o, e que o princÃ­pio de menor privilÃ©gio Ã© seguido.
7. **Verificar rate limiting** â€” Confirmar que endpoints pÃºblicos (especialmente `/api/leads`) possuem rate limiting configurado para prevenir abuso e ataques de forÃ§a bruta.
8. **Auditar CORS** â€” Verificar que a configuraÃ§Ã£o CORS Ã© restritiva (origins especÃ­ficas, nÃ£o wildcard `*`), com mÃ©todos e headers limitados ao necessÃ¡rio.
9. **Buscar segredos hardcoded** â€” Escanear o cÃ³digo em busca de chaves de API, senhas, tokens ou outros segredos que estejam hardcoded ao invÃ©s de usar variÃ¡veis de ambiente.
10. **Verificar respostas de erro** â€” Confirmar que mensagens de erro em produÃ§Ã£o nÃ£o expÃµem stack traces, queries SQL, caminhos de arquivos ou outras informaÃ§Ãµes internas.
11. **Categorizar issues** â€” Classificar cada problema como BLOCKER (vulnerabilidade explorÃ¡vel), WARNING (risco de seguranÃ§a menor) ou INFO (melhoria de hardening).
12. **Calcular scores** â€” Computar score por dimensÃ£o (OWASP, validaÃ§Ã£o, auth, autorizaÃ§Ã£o, configuraÃ§Ã£o) e score geral ponderado.
13. **Gerar outputs** â€” Produzir `backendReview` com detalhamento completo e `backendScore` com os valores numÃ©ricos para o relatÃ³rio final.

