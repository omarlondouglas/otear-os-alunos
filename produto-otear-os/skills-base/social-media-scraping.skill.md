---
id: social-media-scraping
name: Scraping e Qualificação de Leads em Redes Sociais
trigger: Quando o usuário quiser mapear perfis do Instagram, LinkedIn ou X/Twitter em um nicho para identificar tomadores de decisão, ganchos e dados de contato
version: 1.0.0
---

# Scraping e Qualificação de Leads em Redes Sociais

Esta skill guia a extração ética e a qualificação de perfis públicos em redes sociais (Instagram, LinkedIn, X/Twitter) para alimentar pipelines de prospecção e vendas B2B.

## Princípios de Scraping Social Seguro

1. **Dados 100% Públicos:** Trabalhe apenas com dados expostos publicamente na bio, links da bio (Linktree, site próprio), títulos profissionais e postagens abertas.
2. **Respeito a Rate Limits:** Nunca faça requisições em massa em alta velocidade. Use delays humanos (3 a 8 segundos entre perfis) e navegação com limites por sessão (máximo de 30-50 perfis por lote).
3. **Foco no Gancho (Icebreaker):** Não extraia apenas telefones/e-mails. O maior valor está em ler o último post ou a bio para gerar uma mensagem personalizada e humana.

---

## Procedimento de Execução

### Passo 1: Mapeamento de Fontes e Hashtags
* **No Instagram:** Busque por hashtags do nicho (`#medicinaestetica`, `#advocaciabr`, `#arquiteturadeinteriores`) ou perfis âncora/associações do setor.
* **No LinkedIn:** Filtre por cargo (`Fundador`, `Sócio`, `Diretor Comercial`, `Head de Marketing`) + setor e cidade.
* **No X / Twitter:** Busque por palavras-chave com reclamações ou dúvidas do setor para encontrar dores em tempo real.

### Passo 2: Extração dos Dados do Perfil
Para cada perfil identificado, extraia:
* **Username / Handle**
* **Nome / Cargo do Responsável**
* **Texto da Bio:** O que a empresa ou profissional afirma que faz.
* **Link da Bio:** URL do site, WhatsApp ou Linktree.
* **Último Conteúdo Publicado:** Data e tema do post mais recente (para comprovar se a conta está ativa).
* **Dados de Contato Externos:** E-mail público ou número de WhatsApp disponível na página de destino do link da bio.

### Passo 3: Geração do Gancho de Abordagem Personalizado
Com base nos dados coletados, gere um gancho de 1 frase:
* Exemplo (Instagram ativo com link quebrado): *"Vi seu último post sobre [tema], tentei acessar o link da sua bio para conhecer o serviço e notei que a página demorou 10s para abrir..."*
* Exemplo (Empresa em expansão no LinkedIn): *"Vi que vocês estão abrindo vagas na área comercial em [Cidade], estão estruturando a automação desse fluxo de novos leads?"*

### Passo 4: Formato de Saída (Tabela de Oportunidades)
Entregue a lista organizada:
`Nome/Empresa | Rede/Handle | Link Bio | Contato Identificado | Gancho Personalizado`
