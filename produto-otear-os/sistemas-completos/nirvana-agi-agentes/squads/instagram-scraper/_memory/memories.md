# Squad Memory — Instagram Carousel Scraper

## Aprendizados

### 2026-03-18 — Run @brandsdecoded__
- **Perfil**: @brandsdecoded__ (272K seguidores, verificado)
- **Posts coletados**: 3 de 5 solicitados (conflito de browser)
- **Total de imagens**: 37 slides
- **Problema identificado**: Agentes subagent em background competem pelo controle do browser Playwright, causando conflitos de navegação. Solução: nunca usar subagentes paralelos para scraping — executar tudo inline/sequencial.
- **Padrão visual do perfil**: Template escuro com header "Powered by Content Machine", fotos humanas nas capas, conteúdo editorial analítico sobre marketing e cultura.
- **Sessão do browser**: Precisou de login manual na primeira vez. Sessão ficou salva no perfil persistente.
- **Instagram SPA routing**: Navegar entre posts requer cuidado — o Instagram intercepta `page.goto()` via client-side routing. Usar `about:blank` intermediário ou esperar a estabilização.
