import os
from pathlib import Path

def get_project_consciousness() -> str:
    """Carrega o contexto e a memória do projeto + USER.md/MEMORY.md do vault Obsidian."""

    # Root dir é 2 níveis acima de app/agents/
    root_dir = Path(__file__).parent.parent.parent
    consciousness_parts = []

    # 0. Carregar memoria do vault Obsidian (USER.md + MEMORY.md)
    # Eh injetada PRIMEIRO para que o perfil do usuario tenha prioridade no prompt.
    try:
        from app.services.user_memory import get_memory_prompt
        memory_prompt = get_memory_prompt()
        if memory_prompt:
            consciousness_parts.append(f"=== USER & AGENT MEMORY (Obsidian Vault) ===\n{memory_prompt}")
    except Exception as e:
        # Vault offline ou path errado - nao bloqueia inicializacao
        print(f"[consciousness] vault memory unavailable: {e}")

    # 1. Carregar CLAUDE.md (O que o projeto é)
    claude_path = root_dir / "CLAUDE.md"
    if claude_path.exists():
        with open(claude_path, "r", encoding="utf-8") as f:
            consciousness_parts.append(f"=== PROJECT CONSCIOUSNESS (CLAUDE.md) ===\n{f.read()}")

    # 2. Carregar Stories Recentes (O que está sendo feito)
    stories_dir = root_dir / "docs" / "stories"
    if stories_dir.exists():
        story_files = list(stories_dir.glob("*.md"))
        story_files.sort(reverse=True) # Pegar as mais recentes primeiro

        stories_content = ["=== RECENT STORIES ==="]
        for s_file in story_files[:3]: # Pegar as 3 últimas stories
            with open(s_file, "r", encoding="utf-8") as f:
                stories_content.append(f"Story {s_file.stem}:\n{f.read()}")
        consciousness_parts.append("\n".join(stories_content))

    # 3. Carregar Regras Adicionais (Como se comportar)
    rules_dir = root_dir / ".claude" / "rules"
    if rules_dir.exists():
        rules_files = list(rules_dir.glob("*.md"))
        rules_content = ["=== PROJECT RULES ==="]
        for r_file in rules_files:
            with open(r_file, "r", encoding="utf-8") as f:
                rules_content.append(f.read())
        consciousness_parts.append("\n".join(rules_content))

    return "\n\n".join(consciousness_parts)

if __name__ == "__main__":
    # Teste de leitura
    print(get_project_consciousness())
