"""
ClaudeCodeModel — Agno Model adapter usando claude CLI subprocess.

Não requer ANTHROPIC_API_KEY. Usa o OAuth do Claude Code instalado na máquina.
Compatível com o sistema de tool calling do agno via protocolo de texto.
"""
from __future__ import annotations

import asyncio
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional

from agno.models.base import Model
from agno.models.response import ModelResponse
from agno.utils.log import logger
from app.core.claude_cli_env import build_claude_cli_env, find_git_bash

_IS_WINDOWS = platform.system() == "Windows"


def _find_git_bash() -> Optional[str]:
    """Auto-detecta git-bash no Windows para o Claude Code CLI."""
    if not _IS_WINDOWS:
        return None
    candidates = [
        os.environ.get("CLAUDE_CODE_GIT_BASH_PATH", ""),
        r"D:\Git\usr\bin\bash.exe",
        r"D:\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


_GIT_BASH_PATH = find_git_bash()


def _stringify_content(content: Any) -> str:
    """Converte qualquer formato de content (str, list, None) para string."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                parts.append(block.get("text", block.get("content", str(block))))
            else:
                parts.append(str(block))
        return "\n".join(parts)
    return str(content)


def _is_auth_error(error: Any) -> bool:
    text = str(error).lower()
    return "failed to authenticate" in text or "invalid authentication credentials" in text


@dataclass
class ClaudeCodeModel(Model):
    """
    Agno Model adapter que usa `claude -p` subprocess como LLM backend.

    - Sem ANTHROPIC_API_KEY: usa OAuth do Claude Code instalado localmente
    - Suporta tool calling via protocolo de texto (TOOL_CALL: {...})
    - Remove CLAUDECODE do env para permitir subprocess dentro de sessão CC
    """

    id: str = "claude-sonnet-4-6"
    name: str = "ClaudeCode"
    provider: str = "ClaudeCodeCLI"

    # Timeout do subprocess em segundos
    timeout: int = 180

    # Retry config
    max_retries: int = 3
    retry_backoff_base: float = 2.0

    # Paths de credenciais
    credentials_path: str = os.path.expanduser("~/.claude/.credentials.json")
    credentials_backup: str = "/app/storage/.claude_credentials_backup.json"

    def get_provider(self) -> str:
        return self.provider

    def _build_tool_protocol(self, tools: List[Dict]) -> str:
        """Gera a seção de protocolo de tool calling para o system message."""
        tool_lines = []
        for t in tools:
            fn = t.get("function", {})
            name = fn.get("name", "")
            desc = fn.get("description", "")
            params = fn.get("parameters", {})
            props = params.get("properties", {})
            required = params.get("required", [])

            param_desc = []
            for pname, pinfo in props.items():
                req = "(required)" if pname in required else "(optional)"
                ptype = pinfo.get("type", "any")
                pdesc = pinfo.get("description", "")
                param_desc.append(f"    - {pname} ({ptype}) {req}: {pdesc}")

            param_str = "\n".join(param_desc) if param_desc else "    (no parameters)"
            tool_lines.append(f"  • {name}: {desc}\n{param_str}")

        tools_str = "\n".join(tool_lines)

        return f"""
TOOL CALLING PROTOCOL:
When you need to use a tool, output EXACTLY this on a single line (nothing else on that line):
TOOL_CALL: {{"name": "tool_name", "arguments": {{"arg1": "val1"}}}}
Then stop and wait for the tool result before continuing your response.

Available tools:
{tools_str}"""

    def _build_prompt(self, messages: List, tools: Optional[List[Dict]] = None) -> str:
        """Serializa a lista de messages do agno para texto do CLI."""
        system_parts = []
        conversation_parts = []

        for m in messages:
            role = getattr(m, "role", "user")
            content = _stringify_content(getattr(m, "content", ""))

            if role == "system":
                if content:
                    system_parts.append(content)
            elif role == "user":
                if content:
                    conversation_parts.append(f"Human: {content}")
            elif role == "assistant":
                # Pode ter tool_calls sem content textual
                tc = getattr(m, "tool_calls", None)
                if tc:
                    conversation_parts.append(f"Assistant: [called tool: {tc}]")
                elif content:
                    conversation_parts.append(f"Assistant: {content}")
            elif role == "tool":
                # Resultado de uma tool call
                tool_call_id = getattr(m, "tool_call_id", "")
                conversation_parts.append(f"Tool result: {content}")

        # Monta system block
        system_text = "\n\n".join(system_parts)

        # Adiciona protocolo de tools ao system
        if tools:
            system_text += self._build_tool_protocol(tools)

        parts = []
        if system_text.strip():
            parts.append(f"<system>\n{system_text.strip()}\n</system>")
        if conversation_parts:
            parts.extend(conversation_parts)
        parts.append("Assistant:")

        return "\n\n".join(parts)

    def _sync_credentials_to_backup(self):
        """Copia credenciais atualizadas (possivelmente refreshadas pelo CLI) para backup."""
        try:
            if os.path.isfile(self.credentials_path):
                backup_dir = os.path.dirname(self.credentials_backup)
                os.makedirs(backup_dir, exist_ok=True)
                shutil.copy2(self.credentials_path, self.credentials_backup)
                logger.debug("ClaudeCodeModel: credenciais sincronizadas para backup")
        except Exception as e:
            logger.warning(f"ClaudeCodeModel: falha ao sincronizar backup: {e}")

    def _restore_credentials_from_backup(self):
        """Restaura credenciais do backup se o arquivo principal está ausente ou corrompido."""
        try:
            if not os.path.isfile(self.credentials_backup):
                return False

            # Se o arquivo principal existe e é mais recente, não restaurar
            if os.path.isfile(self.credentials_path):
                main_mtime = os.path.getmtime(self.credentials_path)
                backup_mtime = os.path.getmtime(self.credentials_backup)
                if main_mtime >= backup_mtime:
                    return False

            creds_dir = os.path.dirname(self.credentials_path)
            os.makedirs(creds_dir, exist_ok=True)
            shutil.copy2(self.credentials_backup, self.credentials_path)
            logger.info("ClaudeCodeModel: credenciais restauradas do backup")
            return True
        except Exception as e:
            logger.warning(f"ClaudeCodeModel: falha ao restaurar credenciais: {e}")
            return False

    def _exec_cli(self, prompt: str, env: dict) -> str:
        """Executa uma única chamada ao CLI. Sem retry — usado internamente."""
        cmd = ["claude", "-p", "--output-format", "json"]

        logger.info(f"ClaudeCodeModel: executando CLI com prompt de {len(prompt)} chars")

        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=self.timeout,
            env=env,
            shell=_IS_WINDOWS,
        )

        if result.returncode != 0:
            # Captura AMBOS stdout e stderr — o CLI às vezes manda erro no stdout
            stderr = result.stderr.strip() if result.stderr else ""
            stdout = result.stdout.strip() if result.stdout else ""
            error_detail = stderr or stdout or "(sem output — CLI pode não estar autenticado)"

            logger.error(f"ClaudeCodeModel: CLI retornou code {result.returncode}")
            logger.error(f"  stderr: {stderr[:300]}")
            logger.error(f"  stdout: {stdout[:300]}")

            raise RuntimeError(
                f"Claude CLI erro (code {result.returncode}): {error_detail[:500]}"
            )

        raw_stdout = result.stdout.strip()
        if not raw_stdout:
            raise RuntimeError("Claude CLI retornou output vazio — possível problema de autenticação")

        try:
            data = json.loads(raw_stdout)
            return data.get("result", raw_stdout)
        except json.JSONDecodeError:
            return raw_stdout

    def _call_cli(self, prompt: str) -> str:
        """Executa claude -p com retry automático e recovery de credenciais."""
        env = os.environ.copy()
        env.pop("CLAUDECODE", None)  # evita erro "nested session"

        # Garante heap suficiente para o Node.js do CLI
        node_opts = env.get("NODE_OPTIONS", "")
        if "--max-old-space-size" not in node_opts:
            env["NODE_OPTIONS"] = f"{node_opts} --max-old-space-size=4096".strip()

        # Windows: Claude Code CLI requer git-bash
        if _IS_WINDOWS and _GIT_BASH_PATH:
            env["CLAUDE_CODE_GIT_BASH_PATH"] = _GIT_BASH_PATH

        logger.debug(f"ClaudeCodeModel: chamando subprocess claude -p (len={len(prompt)})")

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response_text = self._exec_cli(prompt, env)

                # Sucesso — sincronizar credenciais (podem ter sido refreshadas)
                from app.core.model_factory import report_cli_success
                report_cli_success()
                self._sync_credentials_to_backup()

                logger.debug(f"ClaudeCodeModel: resposta recebida (len={len(response_text)}) [tentativa {attempt}]")
                return response_text

            except (RuntimeError, subprocess.TimeoutExpired) as e:
                last_error = e
                logger.warning(
                    f"ClaudeCodeModel: tentativa {attempt}/{self.max_retries} falhou: {e}"
                )

                if _is_auth_error(e):
                    logger.warning("ClaudeCodeModel: erro de autenticacao detectado; pulando retries")
                    break

                if attempt < self.max_retries:
                    # Tentar restaurar credenciais do backup antes de retry
                    self._restore_credentials_from_backup()

                    # Backoff exponencial
                    wait_time = self.retry_backoff_base ** attempt
                    logger.info(f"ClaudeCodeModel: aguardando {wait_time}s antes de retry...")
                    time.sleep(wait_time)

        # Todas as tentativas falharam
        from app.core.model_factory import report_cli_failure
        report_cli_failure()
        raise RuntimeError(
            f"Claude CLI falhou após {self.max_retries} tentativas. "
            f"Último erro: {last_error}"
        )

    def _parse_tool_call(self, text: str) -> Optional[Dict]:
        """Detecta padrão TOOL_CALL: {...} na resposta e retorna o dict."""
        for line in text.split("\n"):
            line = line.strip()
            m = re.match(r"^TOOL_CALL:\s*(\{.*\})\s*$", line)
            if m:
                try:
                    return json.loads(m.group(1))
                except json.JSONDecodeError:
                    logger.warning(f"ClaudeCodeModel: tool_call JSON inválido: {m.group(1)}")
        return None

    def _make_tool_calls_list(self, tool_data: Dict) -> List[Dict]:
        """Converte nosso formato para o formato OpenAI que o agno espera."""
        return [
            {
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "type": "function",
                "function": {
                    "name": tool_data["name"],
                    "arguments": json.dumps(tool_data.get("arguments", {})),
                },
            }
        ]

    # ─── Métodos abstratos obrigatórios ───────────────────────────────────────

    def invoke(self, messages, assistant_message=None, tools=None, **kwargs) -> ModelResponse:
        tools_list = tools or []
        prompt = self._build_prompt(messages, tools_list if tools_list else None)

        try:
            raw = self._call_cli(prompt)
        except RuntimeError as e:
            error_msg = str(e)
            logger.error(f"ClaudeCodeModel: invoke falhou: {error_msg}")
            # Retorna resposta de erro ao invés de crashar toda a requisição
            return ModelResponse(
                content=(
                    f"Desculpe, o serviço de IA está temporariamente indisponível. "
                    f"Erro: {error_msg[:200]}. "
                    f"Verifique se ANTHROPIC_API_KEY está configurada ou se o Claude CLI está autenticado."
                )
            )

        tool_call = self._parse_tool_call(raw) if tools_list else None

        if tool_call:
            logger.info(f"ClaudeCodeModel: tool call detectado → {tool_call['name']}")
            return ModelResponse(
                content="",
                tool_calls=self._make_tool_calls_list(tool_call),
            )

        return ModelResponse(content=raw)

    async def ainvoke(self, messages, assistant_message=None, tools=None, **kwargs) -> ModelResponse:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.invoke(messages, assistant_message, tools, **kwargs),
        )

    def invoke_stream(self, messages, assistant_message=None, tools=None, **kwargs) -> Iterator[ModelResponse]:
        # Sem streaming real — retorna em um único chunk
        yield self.invoke(messages, assistant_message, tools, **kwargs)

    async def ainvoke_stream(
        self, messages, assistant_message=None, tools=None, **kwargs
    ) -> AsyncIterator[ModelResponse]:
        yield self.invoke(messages, assistant_message, tools, **kwargs)

    def _parse_provider_response(self, response: Any, **kwargs) -> ModelResponse:
        if isinstance(response, ModelResponse):
            return response
        return ModelResponse(content=str(response))

    def _parse_provider_response_delta(self, response: Any) -> ModelResponse:
        return self._parse_provider_response(response)
