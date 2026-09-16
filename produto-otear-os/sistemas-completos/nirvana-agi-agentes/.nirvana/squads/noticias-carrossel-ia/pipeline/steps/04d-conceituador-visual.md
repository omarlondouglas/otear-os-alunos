---
id: conceituador-visual
type: step
execution: inline
agent: conceituador-visual
label: "Criar conceito visual unico para cada slide"
inputFile: "squads/noticias-carrossel-ia/output/carousel-content.md"
outputFile: "squads/noticias-carrossel-ia/output/visual-concept.md"
---

# Conceituador Visual — Conceito de Imagem por Slide

## Contexto

Voce recebeu o conteudo completo do carrossel e o brief de imagens do Curador.

## Processo

### FAST EXIT (verificar ANTES de qualquer trabalho)

1. Ler o image-brief.md do Curador
2. Se NÃO contiver a palavra "FALLBACK" e o usuario NÃO pediu "gerar com IA":
   - Escrever no outputFile APENAS estas 2 linhas e PARAR:
     ```
     CONCEITO VISUAL: banco R2 em uso
     Imagens selecionadas pelo Curador — nenhuma geração de IA necessária.
     ```
   - NÃO pesquisar logos. NÃO criar prompts. NÃO usar web_search. Apenas salvar e sair.

### CRIAÇÃO DE CONCEITOS (só se necessário)

Executar SOMENTE se: o usuario pediu "gerar com IA" (opção 2), OU o image-brief.md contiver "FALLBACK".

1. Ler o conteudo do carrossel (carousel-content.md)
2. Identificar PESSOAS-CHAVE da noticia (CEO, politico, celebridade, fundador)
3. **Buscar foto de referencia** para cada pessoa-chave via API (busca no Supabase, se nao tiver busca no Google e salva automaticamente):
   ```bash
   # Para cada pessoa identificada:
   NOME="Nome Completo"
   
   # POST busca no cache Supabase → se nao tiver, busca Google CSE → salva no Supabase Storage
   RESULT=$(curl -s -X POST http://localhost:3000/api/banco-pessoas \
     -H "Content-Type: application/json" \
     -d "{\"nome\": \"$NOME\"}")
   
   FOUND=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('found', False))" 2>/dev/null)
   URL=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('url_publica', ''))" 2>/dev/null)
   
   if [ "$FOUND" = "True" ] && [ -n "$URL" ]; then
     echo "OK: Foto de $NOME disponivel em $URL"
   else
     echo "WARN: Nenhuma foto encontrada para $NOME"
   fi
   ```
4. Pesquisar as logos e identidade visual das marcas mencionadas na noticia
5. Identificar os simbolos e metaforas da historia
6. Criar conceito visual para cada slide (capa + internos)
7. Gerar prompts de imagem otimizados para Gemini
8. **Incluir no visual-concept.md** o campo "Foto referencia" com o caminho de cada foto encontrada
9. Salvar em visual-concept.md

## Input

- Conteudo do carrossel (do Redator)
- Brief de imagens (do Curador)
- Pesquisa de logos/marcas (via web_search)

## Output

- Conceito visual para cada slide com justificativa
- Prompts de geracao de imagem (DALL-E 3 / Gemini / Midjourney)
- Especificacoes tecnicas (aspect ratio, estilo, paleta)

## Veto Conditions

- Conceito generico que funcionaria para qualquer noticia
- Todos os slides com o mesmo tipo de imagem
- Nenhuma logo/marca da noticia incorporada nos conceitos
- Prompts sem especificacoes tecnicas (aspect ratio, estilo)
