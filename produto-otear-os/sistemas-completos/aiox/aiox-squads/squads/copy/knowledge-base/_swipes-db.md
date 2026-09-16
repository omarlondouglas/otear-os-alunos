# Swipes DB — Retrieval Semantico

Base vetorial com **~20.500 chunks** de copy real dos maiores copywriters, pesquisavel por similaridade semantica.

## Quando Usar

OBRIGATORIO consultar antes de gerar qualquer draft de copy:

- Headlines, leads, bullets, closes, offers, PS
- Emails, VSLs, landing pages, ads
- Quando briefing menciona autor especifico ou estilo

## Como Consultar

### CLI (padrao — agentes usam via bash)

```bash
# Busca geral
python squads/copy/tools/swipes_search.py "lead saude masculina urgencia" --count 5

# Filtrar por autor
python squads/copy/tools/swipes_search.py "headline curiosidade" --author clayton_makepeace --count 8

# Filtrar por idioma (pt para mercado BR)
python squads/copy/tools/swipes_search.py "promessa financeira" --language pt --count 10

# Listar autores disponiveis
python squads/copy/tools/swipes_search.py --list-authors

# Output JSON (pra parsing)
python squads/copy/tools/swipes_search.py "close urgencia" --format json --count 3
```

### Autores Disponiveis

| Autor | Chunks | Especialidade |
|---|---|---|
| `chris_haddad` | 8.804 | Relacionamento, emails |
| `parris_lampropoulos` | 2.984 | Health, financial |
| `ben_settle` | 1.496 | Email copywriting |
| `clayton_makepeace` | 1.288 | Financial, health |
| `ultimate_investment_swipes` | 1.084 | Financial |
| `empiricus` | 913 | Financial BR (pt) |
| `john_carlton` | 808 | Direct response, diverse |
| `kyle_miligan` | 685 | Copywriting general |
| `craig_clemens` | 483 | VSL, health |
| `gary_bencivenga` | 468 | Direct response |
| `gary_halbert` | 296 | Direct mail |
| `claude_hopkins` | 53 | Scientific advertising |

## Padrao de Uso Obrigatorio (Agentes)

### Antes de gerar copy

1. **Identificar query relevante** do briefing:
   - Nicho + formato (ex: "lead financeiro brasileiro")
   - Emocao/angle (ex: "headline medo escassez")
   - Estrutura (ex: "close com garantia risco zero")

2. **Executar busca** (minimo 3, maximo 10 resultados):
   ```bash
   python squads/copy/tools/swipes_search.py "{query}" --count 5
   ```

3. **Se briefing menciona autor especifico**, filtrar:
   ```bash
   python squads/copy/tools/swipes_search.py "{query}" --author {autor} --count 5
   ```

4. **Se mercado BR**, filtrar pt:
   ```bash
   python squads/copy/tools/swipes_search.py "{query}" --language pt --count 5
   ```

### Durante geracao

- Usar os chunks retornados como **ancoragem concreta**, nao como template a copiar
- Extrair padroes: estrutura, ritmo, gatilhos, escolhas lexicais
- Citar os sources nos metadados do output (autor + source_file)

### Anti-padroes

- NAO copiar chunks literalmente
- NAO usar resultados com `similarity < 0.3` sem validar
- NAO ignorar esta consulta (knowledge-base MD sozinha nao tem exemplos reais suficientes)

## Complementaridade com Knowledge-Base MD

| Fonte | Papel |
|---|---|
| `knowledge-base/por-framework/` | **COMO fazer** — estruturas, frameworks, principios |
| `knowledge-base/por-tema/` | **SOBRE o que** — nichos, angles, avatars |
| `knowledge-base/por-copywriter/` | **No estilo de** — perfis dos autores |
| **Swipes DB (esta base)** | **ASSIM se fez** — exemplos reais, anclagem concreta |

As 4 fontes se complementam. Usar TODAS quando gerar copy de alta qualidade.

## Atualizar a Base

Pra adicionar novos swipes:

1. Colocar arquivos `.md` em `d:/AIOX/ocr_results/`
2. Rodar: `python d:/AIOX/_ingest_swipes.py`
3. Script e incremental — pula o que ja foi ingerido

## Troubleshooting

- **Erro `Missing env vars`**: conferir `aiox-core/.env` tem `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- **Zero resultados**: baixar `--threshold` (default 0.3 → tenta 0.2) ou reformular query
- **Resultados irrelevantes**: adicionar `--author` ou `--language` pra filtrar
