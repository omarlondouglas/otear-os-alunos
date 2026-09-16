"""
CodexCliModel - Agno Model adapter using `codex exec`.

This is intended for private/trusted server workflows where Codex CLI is already
authenticated. It keeps Agno agents unchanged while routing LLM calls through
the Codex CLI non-interactive interface.
"""
from __future__ import annotations

import asyncio
import json
import os
import platform
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional

from agno.models.base import Model
from agno.models.response import ModelResponse
from agno.utils.log import logger

_IS_WINDOWS = platform.system() == "Windows"


def _stringify_content(content: Any) -> str:
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


@dataclass
class CodexCliModel(Model):
    """Agno adapter backed by `codex exec`.

    Notes:
    - Uses the Codex CLI's current auth in CODEX_HOME / ~/.codex.
    - Uses Codex's default model unless `id` is set to a non-empty model slug.
    - Supports Agno tool calls through the same text protocol used by the
      Claude CLI adapter: `TOOL_CALL: {...}`.
    """

    id: str = ""
    name: str = "CodexCLI"
    provider: str = "CodexCLI"
    timeout: int = 240
    max_retries: int = 2
    retry_backoff_base: float = 2.0
    sandbox: str = "read-only"
    cwd: str = ""
    ephemeral: bool = True

    def get_provider(self) -> str:
        return self.provider

    def _build_tool_protocol(self, tools: List[Dict]) -> str:
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
            tool_lines.append(f"  - {name}: {desc}\n{param_str}")

        return f"""
TOOL CALLING PROTOCOL:
When you need to use a tool, output EXACTLY this on a single line and stop:
TOOL_CALL: {{"name": "tool_name", "arguments": {{"arg1": "val1"}}}}

Do not execute shell commands, edit files, or use Codex repository tools for
product tasks. The application runtime will execute the declared tool call.

Available tools:
{chr(10).join(tool_lines)}"""

    def _build_prompt(self, messages: List, tools: Optional[List[Dict]] = None) -> str:
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
                    conversation_parts.append(f"User: {content}")
            elif role == "assistant":
                tc = getattr(m, "tool_calls", None)
                if tc:
                    conversation_parts.append(f"Assistant: [called tool: {tc}]")
                elif content:
                    conversation_parts.append(f"Assistant: {content}")
            elif role == "tool":
                if content:
                    conversation_parts.append(f"Tool result: {content}")

        system_text = "\n\n".join(system_parts)
        if tools:
            system_text += self._build_tool_protocol(tools)

        parts = []
        if system_text.strip():
            parts.append(f"<system>\n{system_text.strip()}\n</system>")
        parts.extend(conversation_parts)
        parts.append("Assistant:")
        return "\n\n".join(parts)

    def _exec_cli_once(self, prompt: str, env: dict) -> str:
        output_path = ""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                suffix=".md",
                prefix="codex-last-message-",
                delete=False,
            ) as f:
                output_path = f.name

            codex_bin = shutil.which("codex") or "codex"
            cmd = [codex_bin, "exec", "--sandbox", self.sandbox, "--output-last-message", output_path]
            if self.ephemeral:
                cmd.append("--ephemeral")

            model_id = (self.id or "").strip()
            if model_id:
                cmd.extend(["--model", model_id])

            cwd = self.cwd or os.getcwd()
            cmd.extend(["--cd", cwd, "-"])

            logger.info(
                f"CodexCliModel: running codex exec "
                f"(prompt={len(prompt)} chars, model={model_id or 'codex-default'}, sandbox={self.sandbox})"
            )

            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
                env=env,
                shell=False,
            )

            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                stdout = (result.stdout or "").strip()
                detail = stderr or stdout or "no output"
                raise RuntimeError(f"Codex CLI error code {result.returncode}: {detail[:800]}")

            if os.path.exists(output_path):
                content = open(output_path, "r", encoding="utf-8").read().strip()
                if content:
                    return content

            stdout = (result.stdout or "").strip()
            if stdout:
                return stdout
            raise RuntimeError("Codex CLI returned empty output")
        finally:
            if output_path and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception:
                    pass

    def _call_cli(self, prompt: str) -> str:
        env = os.environ.copy()
        env.pop("CLAUDECODE", None)

        sandbox = os.getenv("CODEX_CLI_SANDBOX")
        if sandbox:
            self.sandbox = sandbox
        timeout = os.getenv("CODEX_CLI_TIMEOUT_S")
        if timeout:
            try:
                self.timeout = int(timeout)
            except ValueError:
                pass

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return self._exec_cli_once(prompt, env)
            except (RuntimeError, subprocess.SubprocessError, OSError) as e:
                last_error = e
                logger.warning(f"CodexCliModel: attempt {attempt}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_backoff_base ** attempt)

        raise RuntimeError(f"Codex CLI failed after {self.max_retries} attempts. Last error: {last_error}")

    def _parse_tool_call(self, text: str) -> Optional[Dict]:
        for line in text.splitlines():
            line = line.strip()
            m = re.match(r"^TOOL_CALL:\s*(\{.*\})\s*$", line)
            if m:
                try:
                    return json.loads(m.group(1))
                except json.JSONDecodeError:
                    logger.warning(f"CodexCliModel: invalid tool call JSON: {m.group(1)}")
        return None

    def _make_tool_calls_list(self, tool_data: Dict) -> List[Dict]:
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

    def invoke(self, messages, assistant_message=None, tools=None, **kwargs) -> ModelResponse:
        tools_list = tools or []
        prompt = self._build_prompt(messages, tools_list if tools_list else None)

        try:
            raw = self._call_cli(prompt)
        except RuntimeError as e:
            error_msg = str(e)
            logger.error(f"CodexCliModel: invoke failed: {error_msg}")
            return ModelResponse(
                content=(
                    "O servico de IA via Codex CLI esta indisponivel. "
                    f"Erro: {error_msg[:300]}. Verifique `codex login` na VPS "
                    "ou use MODEL_PROVIDER=anthropic como fallback."
                )
            )

        tool_call = self._parse_tool_call(raw) if tools_list else None
        if tool_call:
            logger.info(f"CodexCliModel: tool call detected -> {tool_call['name']}")
            return ModelResponse(content="", tool_calls=self._make_tool_calls_list(tool_call))

        return ModelResponse(content=raw)

    async def ainvoke(self, messages, assistant_message=None, tools=None, **kwargs) -> ModelResponse:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.invoke(messages, assistant_message, tools, **kwargs),
        )

    def invoke_stream(self, messages, assistant_message=None, tools=None, **kwargs) -> Iterator[ModelResponse]:
        yield self.invoke(messages, assistant_message, tools, **kwargs)

    async def ainvoke_stream(self, messages, assistant_message=None, tools=None, **kwargs) -> AsyncIterator[ModelResponse]:
        yield self.invoke(messages, assistant_message, tools, **kwargs)

    def _parse_provider_response(self, response: Any, **kwargs) -> ModelResponse:
        if isinstance(response, ModelResponse):
            return response
        return ModelResponse(content=str(response))

    def _parse_provider_response_delta(self, response: Any) -> ModelResponse:
        return self._parse_provider_response(response)
