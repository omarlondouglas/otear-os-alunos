from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

AGNO_AGENT_SOURCES = [
    ROOT / "app" / "agents" / "agno_agents.py",
    ROOT / "app" / "agents" / "squad_agents.py",
]

PY_AGENT_ALIASES = {
    "beast": "video_analyst",
    "nolan": "video_director",
    "ogilvy": "copywriter",
    "olivetto": "dona",
    "garyv": "carousel_agent",
    "scher": "designer",
    "erico": "stylist",
    "guard": "guard_agent",
    "clara_copy": "clara_copy",
    "news_carousel": "news_carousel",
    "youtuber_thumbnail": "youtuber_thumbnail",
    "neuro_cover": "neuro_cover",
    "insta_visual_ref": "insta_visual_ref",
}


@dataclass
class LocalAgent:
    agent_id: str
    name: str
    role: str
    instructions: list[str]
    source: str

    def system_prompt(self) -> str:
        parts = [
            f"Voce esta atuando como o agente local `{self.agent_id}`.",
            f"Nome: {self.name}",
        ]
        if self.role:
            parts.append(f"Papel: {self.role}")
        if self.instructions:
            parts.append("Instrucoes do agente:\n" + "\n".join(self.instructions))
        parts.extend(
            [
                "",
                "Modo local via CLI:",
                "- Siga a persona e as instrucoes acima como fonte de verdade.",
                "- Nao diga que chamou ferramentas externas se nenhuma ferramenta foi realmente executada.",
                "- Se a instrucao original exigir uma tool/API indisponivel neste modo, explique a limitacao e entregue a melhor versao textual possivel.",
                "- Responda em portugues do Brasil, salvo se o usuario pedir outro idioma.",
            ]
        )
        return "\n\n".join(parts).strip()


def _literal(node: ast.AST, constants: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(str(_literal(value, constants)) for value in node.values)
    if isinstance(node, ast.FormattedValue):
        value = _literal(node.value, constants)
        return "" if value is None else str(value)
    if isinstance(node, ast.List | ast.Tuple):
        return [_literal(item, constants) for item in node.elts]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _literal(node.left, constants)
        right = _literal(node.right, constants)
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        if isinstance(left, list) and isinstance(right, list):
            return left + right
        return None
    if isinstance(node, ast.Name):
        return constants.get(node.id, f"{{{node.id}}}")
    return None


def _agent_call_from_assign(node: ast.Assign) -> ast.Call | None:
    value = node.value
    if not isinstance(value, ast.Call):
        return None
    func = value.func
    if isinstance(func, ast.Name) and func.id == "Agent":
        return value
    return None


def _first_target_name(node: ast.Assign) -> str | None:
    if not node.targets:
        return None
    target = node.targets[0]
    if isinstance(target, ast.Name):
        return target.id
    return None


def _attr_assignment(node: ast.Assign) -> tuple[str, str] | None:
    if not node.targets:
        return None
    target = node.targets[0]
    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
        return target.value.id, target.attr
    return None


def _keyword(call: ast.Call, name: str) -> ast.AST | None:
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return []


def load_python_agents() -> dict[str, LocalAgent]:
    agents: dict[str, LocalAgent] = {}
    by_var: dict[str, LocalAgent] = {}

    for path in AGNO_AGENT_SOURCES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text, filename=str(path))
        constants: dict[str, Any] = {
            "PROJECT_MEMORY": "",
        }

        for node in tree.body:
            if isinstance(node, ast.Assign):
                target_name = _first_target_name(node)
                if target_name and target_name.isupper():
                    constants[target_name] = _literal(node.value, constants)

                call = _agent_call_from_assign(node)
                if call and target_name:
                    name = _literal(_keyword(call, "name") or ast.Constant(target_name), constants)
                    role = _literal(_keyword(call, "role") or ast.Constant(""), constants)
                    instructions = _strings(_literal(_keyword(call, "instructions") or ast.List(elts=[]), constants))
                    agent = LocalAgent(
                        agent_id=target_name,
                        name=str(name or target_name),
                        role=str(role or ""),
                        instructions=instructions,
                        source=str(path.relative_to(ROOT)),
                    )
                    by_var[target_name] = agent

                attr = _attr_assignment(node)
                if attr:
                    var_name, attr_name = attr
                    if var_name in by_var and attr_name in {"role", "instructions"}:
                        current = by_var[var_name]
                        value = _literal(node.value, constants)
                        if attr_name == "role":
                            current.role = str(value or "")
                        elif attr_name == "instructions":
                            current.instructions = _strings(value)

        for public_id, var_name in PY_AGENT_ALIASES.items():
            agent = by_var.get(var_name)
            if agent:
                agents[public_id] = LocalAgent(
                    agent_id=public_id,
                    name=agent.name,
                    role=agent.role,
                    instructions=agent.instructions,
                    source=agent.source,
                )

    return agents


def _agent_id_from_file(path: Path) -> str:
    stem = path.name
    stem = re.sub(r"\.agent\.md$", "", stem, flags=re.IGNORECASE)
    return stem.replace("_", "-").lower()


def load_markdown_agents() -> dict[str, LocalAgent]:
    agents: dict[str, LocalAgent] = {}
    for base in [ROOT / "squads", ROOT / "app" / "knowledge"]:
        if not base.exists():
            continue
        for path in base.glob("**/*.agent.md"):
            rel = path.relative_to(ROOT)
            agent_id = _agent_id_from_file(path)
            squad = path.parent.parent.name if path.parent.name == "agents" else path.parent.name
            public_id = f"{squad}:{agent_id}"
            body = path.read_text(encoding="utf-8", errors="replace").strip()
            title_match = re.search(r"^\s*#\s+(.+)$", body, re.MULTILINE)
            name = title_match.group(1).strip() if title_match else agent_id
            agents[public_id] = LocalAgent(
                agent_id=public_id,
                name=name,
                role=f"Agente markdown do squad {squad}",
                instructions=[body],
                source=str(rel),
            )
    return agents


def load_agents() -> dict[str, LocalAgent]:
    agents = load_markdown_agents()
    agents.update(load_python_agents())
    return dict(sorted(agents.items()))


def build_prompt(agent: LocalAgent, task: str, context: str = "") -> str:
    parts = [f"<system>\n{agent.system_prompt()}\n</system>"]
    if context.strip():
        parts.append(f"Contexto adicional:\n{context.strip()}")
    parts.append(f"Tarefa do usuario:\n{task.strip()}")
    parts.append("Resposta do agente:")
    return "\n\n".join(parts)


def run_codex(prompt: str, timeout: int) -> str:
    codex_bin = shutil.which("codex")
    if not codex_bin:
        raise RuntimeError("Codex CLI nao encontrado no PATH. Rode `codex login`/instale o CLI ou use `--engine claude`.")

    output_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".md",
            prefix="local-agent-",
            delete=False,
        ) as f:
            output_path = f.name

        cmd = [
            codex_bin,
            "exec",
            "--sandbox",
            "read-only",
            "--ephemeral",
            "--output-last-message",
            output_path,
            "--cd",
            str(ROOT),
            "-",
        ]
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(f"Codex CLI falhou ({result.returncode}): {detail[:800]}")
        content = Path(output_path).read_text(encoding="utf-8").strip()
        return content or (result.stdout or "").strip()
    finally:
        if output_path:
            Path(output_path).unlink(missing_ok=True)


def run_claude(prompt: str, timeout: int) -> str:
    claude_bin = shutil.which("claude")
    if not claude_bin:
        raise RuntimeError("Claude CLI nao encontrado no PATH. Rode `claude login`/instale o CLI ou use `--engine codex`.")

    result = subprocess.run(
        [claude_bin, "-p", "--output-format", "json"],
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        shell=os.name == "nt",
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"Claude CLI falhou ({result.returncode}): {detail[:800]}")
    raw = (result.stdout or "").strip()
    try:
        return str(json.loads(raw).get("result") or raw)
    except json.JSONDecodeError:
        return raw


def read_stdin_if_needed(value: str | None) -> str:
    if value:
        return value
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return ""


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Executa agentes locais lendo suas personas, sem FastAPI e sem Agno.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="Lista agentes locais disponiveis.")
    list_parser.add_argument("--json", action="store_true", help="Saida JSON.")

    show_parser = sub.add_parser("show", help="Mostra prompt/persona de um agente.")
    show_parser.add_argument("agent")

    run_parser = sub.add_parser("run", help="Executa um agente local via CLI LLM.")
    run_parser.add_argument("agent")
    run_parser.add_argument("task", nargs="?", help="Tarefa. Se omitida, le do stdin.")
    run_parser.add_argument("--context", default="", help="Contexto adicional para a execucao.")
    run_parser.add_argument(
        "--engine",
        choices=["codex", "claude", "print"],
        default=os.getenv("LOCAL_AGENT_ENGINE", "codex"),
        help="Motor local. `print` apenas imprime o prompt montado.",
    )
    run_parser.add_argument("--timeout", type=int, default=300, help="Timeout em segundos.")

    args = parser.parse_args()
    agents = load_agents()

    if args.command == "list":
        if args.json:
            print(json.dumps([
                {
                    "id": key,
                    "name": agent.name,
                    "role": agent.role,
                    "source": agent.source,
                }
                for key, agent in agents.items()
            ], ensure_ascii=False, indent=2))
        else:
            for key, agent in agents.items():
                role = (agent.role or "").replace("\n", " ")
                if len(role) > 110:
                    role = role[:107].rstrip() + "..."
                print(f"{key:42} {agent.name:24} {role}")
        return 0

    agent = agents.get(args.agent)
    if not agent:
        print(f"Agente '{args.agent}' nao encontrado.\n", file=sys.stderr)
        print("Disponiveis:", ", ".join(agents.keys()), file=sys.stderr)
        return 2

    if args.command == "show":
        print(agent.system_prompt())
        return 0

    task = read_stdin_if_needed(args.task)
    if not task:
        print("Informe a tarefa como argumento ou via stdin.", file=sys.stderr)
        return 2

    prompt = build_prompt(agent, task, args.context)
    if args.engine == "print":
        print(prompt)
        return 0
    if args.engine == "codex":
        print(run_codex(prompt, args.timeout))
        return 0
    if args.engine == "claude":
        print(run_claude(prompt, args.timeout))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
