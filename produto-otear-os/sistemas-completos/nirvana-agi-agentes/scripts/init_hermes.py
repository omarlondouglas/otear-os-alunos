#!/usr/bin/env python3
"""
Inicializa ~/.hermes/ (config.yaml, SOUL.md, .env minimo) para o engine Hermes
embutido no projeto O Tear.

Idempotente â€” se os arquivos ja existem, preserva o conteudo do usuario.
Roda uma vez no primeiro boot (ou manualmente: python scripts/init_hermes.py).
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

HERMES_HOME = Path(os.path.expanduser("~/.hermes"))
VAULT_SYSTEM = Path(os.environ.get("VAULT_PATH", "{OTEAR_VAULT_ROOT}")) / ".system"

# â”€â”€â”€ Templates â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

DEFAULT_CONFIG_YAML = """\
# Hermes config - O Tear edition
# Gerado automaticamente por scripts/init_hermes.py
# Edite manualmente para customizar (precedence: CLI > config.yaml > .env > defaults)

model:
  # NAO usa API key â€” fala com nosso proxy local que executa `claude -p` (OAuth do Claude Max).
  # Mude para anthropic/openai/openrouter etc. se preferir API direta.
  provider: custom
  default: claude-sonnet-4-6
  base_url: "{proxy_base_url}"

# Modelos auxiliares (visao, compressao, web extract). Vazio = usa o principal.
auxiliary:
  vision:
    provider: ""
    model: ""
  compression:
    provider: ""
    model: ""
  web_extract:
    provider: ""
    model: ""

# Agente budget de iteracoes de tool-calling por turno
max_iterations: 60
tool_delay: 0.5

# Toolsets habilitados (subset das skills built-in + nossas custom)
# Vazio = todos. Ajuste conforme necessario.
enabled_toolsets: []
disabled_toolsets: []

# Skills custom do projeto
skills_extra_dirs:
  - {skills_dir}
"""

DEFAULT_SOUL_MD = """\
# Hermes â€” O Tear edition

Voce eh o agente conversacional principal da plataforma O Tear (https://github.com/omarlondouglas/o-tear-vault).

## Identidade

- Nome de codigo: Hermes
- Papel: orquestrador frontal â€” voce conversa com o cliente e DELEGA tarefas tecnicas para os agentes especializados (Beast, Nolan, Ogilvy, Olivetto, GaryV, Scher, Erico, Neumeier).
- Lingua: portugues do Brasil por default (a menos que o usuario fale outra).
- Tom: direto, sem rodeios. Acoes antes de explicacoes longas. Nao escreva resumos antes de fazer; nao escreva resumos depois.

## Principio operacional

1. Leia o USER.md (perfil do cliente) e o MEMORY.md (memoria do agente) antes de responder.
2. Se a tarefa eh tecnica de video/copy/carrossel/branding, use a skill `agno-bridge` para delegar ao agente certo.
3. Nunca invente fatos sobre criadores. Use `agno-bridge -> beast/list_creators_tool` ou consulte o vault em {OTEAR_VAULT_ROOT}/references/.
4. Atualize MEMORY.md sempre que aprender algo nao-trivial sobre o ambiente, decisao tomada, ou workaround.
5. Respeite o limite de tamanho do USER.md (1500 chars) e MEMORY.md (2200 chars).

## Como delegar

A skill `agno-bridge` aceita `agent_name` em {beast, nolan, ogilvy, olivetto, garyv, scher, erico, neumeier} e `task` (texto da tarefa).
Use exatamente esse formato â€” nada de inventar nomes de agentes.

## Quando NAO delegar

- Conversas pessoais (perguntas sobre o usuario, preferencias, planos).
- Quando o cliente so quer pensar em voz alta.
- Quando a resposta exata ja esta no MEMORY.md (responda direto).
"""

DEFAULT_ENV = """\
# Hermes secrets â€” chaves de API
# Gerado por scripts/init_hermes.py. Edite manualmente.
#
# OBS: por padrao Hermes usa o nosso proxy local (claude_cli_proxy) que executa
# o CLI do Claude Code. Voce NAO precisa preencher ANTHROPIC_API_KEY se ja
# estiver autenticado no Claude Code (~/.claude/.credentials.json).
#
# Use a chave dummy abaixo â€” qualquer valor nao vazio basta pro LiteLLM aceitar.
ANTHROPIC_API_KEY=cli-via-proxy-no-key-needed

# Auxiliares opcionais (modelos secundarios â€” visao, compressao etc.)
OPENAI_API_KEY=
OPENROUTER_API_KEY=
GOOGLE_API_KEY=
GROQ_API_KEY=
"""


# â”€â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _write_if_missing(path: Path, content: str, label: str) -> bool:
    if path.exists():
        print(f"  [skip] {label} ja existe: {path}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  [ok]   {label} criado: {path}")
    return True


def _sync_vault_to_hermes_memories():
    """Copia USER.md / MEMORY.md do vault Obsidian para ~/.hermes/memories/.

    Estrategia atual: COPIA (nao symlink) na primeira vez. O hermes_engine
    re-injeta o vault no system prompt em runtime, entao a copia em
    ~/.hermes/memories/ serve apenas como fallback se o engine nao puder ler o vault.
    """
    memories_dir = HERMES_HOME / "memories"
    memories_dir.mkdir(parents=True, exist_ok=True)
    for fname in ("USER.md", "MEMORY.md"):
        src = VAULT_SYSTEM / fname
        if not src.exists():
            print(f"  [warn] vault nao tem {fname} (vault path: {VAULT_SYSTEM})")
            continue
        dst = memories_dir / fname
        if dst.exists():
            print(f"  [skip] memories/{fname} ja existe")
            continue
        shutil.copy2(src, dst)
        print(f"  [ok]   memories/{fname} sincronizado do vault")


# â”€â”€â”€ Main â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main():
    print(f"=== Init Hermes em {HERMES_HOME} ===")
    HERMES_HOME.mkdir(parents=True, exist_ok=True)

    # config.yaml â€” referencia o diretorio de skills custom do projeto
    skills_dir = (Path(__file__).parent.parent / "hermes_skills").resolve()
    skills_dir.mkdir(parents=True, exist_ok=True)

    # Proxy base URL â€” apontamos pro proxy local que executa `claude -p`.
    # Em prod (atras de gateway), use o endereco interno do servico FastAPI.
    proxy_base_url = os.environ.get("HERMES_LLM_PROXY_URL", "http://localhost:8000/llm-proxy/v1")

    config_text = DEFAULT_CONFIG_YAML.format(
        skills_dir=str(skills_dir).replace("\\", "/"),
        proxy_base_url=proxy_base_url,
    )
    _write_if_missing(HERMES_HOME / "config.yaml", config_text, "config.yaml")

    # SOUL.md â€” identidade do agente
    _write_if_missing(HERMES_HOME / "SOUL.md", DEFAULT_SOUL_MD, "SOUL.md")

    # .env â€” secrets vazios para o usuario preencher
    _write_if_missing(HERMES_HOME / ".env", DEFAULT_ENV, ".env")

    # Sincroniza memorias do vault (USER.md + MEMORY.md)
    _sync_vault_to_hermes_memories()

    # Diretorios secundarios criados pelo runtime do Hermes (nao precisa preencher)
    for sub in ("sessions", "logs", "skills"):
        (HERMES_HOME / sub).mkdir(parents=True, exist_ok=True)

    print()
    print(f"Hermes inicializado.")
    print(f"  - Edite {HERMES_HOME / '.env'} com suas chaves.")
    print(f"  - Skills custom em: {skills_dir}")


if __name__ == "__main__":
    main()
