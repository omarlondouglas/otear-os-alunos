# Extraction Quality Checklist

> Usado na validação pós-extração de conteúdo para knowledge-base.

## Content Quality

- [ ] Texto legível (sem artefatos de OCR ou caracteres corrompidos)
- [ ] Conteúdo completo (não cortou no meio de uma seção)
- [ ] Estrutura preservada (headings, listas, parágrafos)
- [ ] Encoding UTF-8 correto
- [ ] Imagens/gráficos descritos em texto (quando relevante)

## Metadata Quality

- [ ] Copywriter identificado corretamente
- [ ] Pelo menos 1 framework principal identificado
- [ ] Pelo menos 2 técnicas específicas listadas
- [ ] Nível de consciência Schwartz coerente com o conteúdo
- [ ] Pelo menos 3 tags relevantes
- [ ] Tipo original correto (sales-letter, email, ad, etc.)
- [ ] Frontmatter YAML válido e completo

## Organization

- [ ] Arquivo na pasta correta (por-copywriter/{copywriter}/)
- [ ] Nome do arquivo descritivo e em kebab-case
- [ ] Referências em por-formato/ e por-framework/ criadas

## Decision Matrix

| Resultado | Ação |
|-----------|------|
| Todos OK | APROVADO → entra na base |
| Content quality falha | REJEITADO → _rejected/ com log |
| Metadata quality falha parcial | MANUAL REVIEW → _review/ |
| Metadata quality falha total | REJEITADO → _rejected/ |
