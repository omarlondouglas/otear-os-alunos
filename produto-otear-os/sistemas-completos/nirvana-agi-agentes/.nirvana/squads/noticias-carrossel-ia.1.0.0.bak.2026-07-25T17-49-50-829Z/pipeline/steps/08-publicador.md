---
id: publicador
type: step
execution: inline
agent: publicador
label: "Publicar no Instagram"
inputFile: "squads/noticias-carrossel-ia/output/carousel-content.md"
outputFile: "squads/noticias-carrossel-ia/output/publish-result.md"
---

# Publicador — Publicação no Instagram

## Contexto

Marlon aprovou o carrossel no checkpoint anterior.
Sua missão: publicar o carrossel no Instagram @marlonlima.ia seguindo o protocolo completo.

## Processo

1. Verificar se a skill `instagram-publisher` está instalada:
   - Checar se `skills/instagram-publisher/` existe
   - Se não existir: informar Marlon e salvar conteúdo para publicação manual
2. Verificar os slides gerados (HTMLs no diretório output/slides/)
3. Validar requisitos do Instagram:
   - Imagens em JPEG (converter se necessário)
   - 2-10 slides
   - Legenda dentro de 2.200 caracteres
4. Apresentar preview completo da publicação
5. Executar dry-run com a skill instagram-publisher
6. Aguardar confirmação final de Marlon
7. Publicar e reportar resultado com URL do post
8. Salvar resultado no outputFile

## Se a skill não estiver instalada

Informar ao Marlon:

```
⚠️ Skill instagram-publisher não encontrada.

Para habilitar publicação automática, instale a skill:
  /opensquad install instagram-publisher

Por enquanto, o conteúdo foi salvo em:
  squads/noticias-carrossel-ia/output/{run_id}/

Você pode publicar manualmente no Instagram copiando:
  - O conteúdo dos slides (carousel-content.md)
  - A legenda completa
  - As hashtags
```

## Veto Conditions

- Publicar sem dry-run bem-sucedido
- Publicar sem confirmação explícita do usuário
- Reportar sucesso sem URL do post
