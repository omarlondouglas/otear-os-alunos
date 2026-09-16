---
task: setupDomain()
responsavel: "Anchor"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: deployResult
    tipo: object
    obrigatorio: true
    descricao: "Resultado do deploy com URL Vercel e project ID (source: deployVercel())"
  - nome: clientDomain
    tipo: string
    obrigatorio: false
    descricao: "DomÃ­nio customizado do cliente (ex: www.cliente.com.br) â€” OPCIONAL"

Saida:
  - nome: domainConfig
    tipo: object
    obrigatorio: true
    descricao: "ConfiguraÃ§Ã£o do domÃ­nio: URL final (Vercel grÃ¡tis ou domÃ­nio prÃ³prio), SSL status (destination: lp-versioner)"

Checklist:
  pre-conditions:
    - "[ ] Deploy na Vercel bem-sucedido"
    - "[ ] URL grÃ¡tis .vercel.app acessÃ­vel"
  post-conditions:
    - "[ ] URL grÃ¡tis funcionando: {cliente}-lp.vercel.app"
    - "[ ] SSL ativo (automÃ¡tico na Vercel)"
    - "[ ] SE domÃ­nio prÃ³prio: configurado na Vercel"
    - "[ ] SE domÃ­nio prÃ³prio: DNS records documentados para o cliente"
    - "[ ] SE domÃ­nio prÃ³prio: SSL provisonado automaticamente"
    - "[ ] SE domÃ­nio prÃ³prio: Redirect www â†” apex configurado"

Performance:
  duration_expected: "3 minutes (+ tempo de propagaÃ§Ã£o DNS se domÃ­nio prÃ³prio)"
  cacheable: false
  parallelizable: false
---

# setupDomain()

## DescriÃ§Ã£o

Configura o domÃ­nio do cliente na Vercel. Dois caminhos: (A) URL grÃ¡tis da Vercel que jÃ¡ vem pronta, ou (B) domÃ­nio prÃ³prio com SSL automÃ¡tico. Os dois podem coexistir.

## Passos

### Caminho A: URL grÃ¡tis Vercel (padrÃ£o â€” automÃ¡tico)
1. **JÃ¡ pronto** â€” Ao fazer deploy, a Vercel gera `{projeto}.vercel.app` automaticamente.
2. **SSL ativo** â€” HTTPS jÃ¡ funciona sem configuraÃ§Ã£o.
3. **CDN global** â€” Edge network da Vercel ativa por padrÃ£o.
4. **Registrar URL** â€” Salvar como URL principal do cliente.

### Caminho B: DomÃ­nio prÃ³prio (opcional)
1. **Adicionar domÃ­nio na Vercel** â€” `vercel domains add www.cliente.com.br`.
2. **Gerar instruÃ§Ãµes DNS** â€” A Vercel mostra exatamente o que configurar:
   - **Apex domain (cliente.com.br)**: `A record â†’ 76.76.21.21`
   - **Subdomain (www.cliente.com.br)**: `CNAME â†’ cname.vercel-dns.com`
3. **Enviar instruÃ§Ãµes ao cliente** â€” DNS records + guia passo a passo.
4. **Aguardar propagaÃ§Ã£o DNS** â€” Vercel verifica automaticamente.
5. **SSL automÃ¡tico** â€” Certificado provisionado apÃ³s DNS propagado.
6. **Redirect www â†” apex** â€” Configurar na Vercel (Settings â†’ Domains).
7. **Testar** â€” Acessar `https://www.cliente.com.br` e verificar.

## ConfiguraÃ§Ã£o DNS â€” InstruÃ§Ãµes para o Cliente

```markdown
## ConfiguraÃ§Ã£o de DNS â€” {domÃ­nio do cliente}

Configure os seguintes registros DNS no seu provedor:

| Tipo | Nome | Valor |
|------|------|-------|
| A | @ | 76.76.21.21 |
| CNAME | www | cname.vercel-dns.com |

ApÃ³s configurar, a propagaÃ§Ã£o pode levar de 5 minutos a 48 horas.
O certificado SSL serÃ¡ provisionado automaticamente pela Vercel.
```

## Vercel Domains â€” CLI

```bash
# Adicionar domÃ­nio customizado
vercel domains add www.cliente.com.br

# Verificar status do domÃ­nio
vercel domains inspect www.cliente.com.br

# Listar domÃ­nios
vercel domains ls

# Remover domÃ­nio
vercel domains rm www.cliente.com.br
```

## Nota
- A URL grÃ¡tis `.vercel.app` SEMPRE funciona, mesmo com domÃ­nio prÃ³prio
- O cliente pode comeÃ§ar com a URL grÃ¡tis e migrar para domÃ­nio prÃ³prio depois
- A Vercel suporta mÃºltiplos domÃ­nios por projeto (com e sem www, apex, subdomÃ­nios)

