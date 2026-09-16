"""
Claude CLI Proxy — sub-app FastAPI que expoe um endpoint OpenAI-compatible
proxando para o Claude Code CLI subprocess (sem API key, usa OAuth do Claude Max).

Permite que Hermes (LiteLLM) e qualquer outro cliente OpenAI-compatible usem
o CLI do Claude transparentemente:

    base_url: http://localhost:8000/llm-proxy/v1
    api_key:  dummy
    model:    claude-sonnet-4-6

Reusa a logica do app.core.claude_code_model.ClaudeCodeModel (subprocess +
retry + credential refresh) — nao reinventa.

Endpoints expostos:
  POST /v1/chat/completions      shape OpenAI (sync, sem streaming nesta versao)
  GET  /v1/models                lista modelos disponiveis
  GET  /healthz                  diagnostico
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ─── Sub-app ──────────────────────────────────────────────────────────────────

app = FastAPI(title="Claude CLI Proxy", version="0.1.0")


# ─── Models OpenAI shape ──────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: Optional[Any] = None  # str | List[Dict] (vision content blocks)
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class ToolFunction(BaseModel):
    name: str
    description: Optional[str] = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ToolDef(BaseModel):
    type: str = "function"
    function: ToolFunction


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    tools: Optional[List[ToolDef]] = None
    tool_choice: Optional[Any] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    # Demais campos sao ignorados (top_p, presence_penalty, etc.)


class ChatCompletionChoice(BaseModel):
    index: int = 0
    message: Dict[str, Any]
    finish_reason: str = "stop"


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Dict[str, int] = Field(
        default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    )


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/healthz")
async def healthz():
    """Diagnostico do proxy + status do CLI Claude."""
    try:
        from app.core.model_factory import _is_cli_available, _HAS_CLAUDE_BINARY
        return {
            "status": "ok",
            "claude_binary_present": _HAS_CLAUDE_BINARY,
            "cli_verified": _is_cli_available(),
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


@app.get("/v1/models")
async def list_models():
    """Lista modelos disponiveis (formato OpenAI)."""
    return {
        "object": "list",
        "data": [
            {"id": m, "object": "model", "owned_by": "anthropic"}
            for m in ("claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5-20251001")
        ],
    }


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint via Claude CLI."""
    if request.stream:
        # Streaming nao implementado nesta versao — Hermes/LiteLLM
        # cai pro non-streaming automaticamente.
        raise HTTPException(
            status_code=400,
            detail="Streaming nao suportado pelo claude_cli_proxy. Use stream=false.",
        )

    # 1. Serializa mensagens + tools no formato que ClaudeCodeModel ja entende.
    prompt = _build_prompt(request)

    # 2. Executa subprocess (reusa toda a logica de retry/recovery)
    try:
        from app.core.claude_code_model import ClaudeCodeModel
        model = ClaudeCodeModel(id=request.model)
        raw_text = model._call_cli(prompt)
    except RuntimeError as e:
        logger.error(f"claude_cli_proxy: CLI failed: {e}")
        raise HTTPException(status_code=502, detail=f"Claude CLI failed: {e}")

    # 3. Detecta tool_call no formato texto (TOOL_CALL: {...})
    tool_call = _parse_tool_call(raw_text) if request.tools else None

    if tool_call:
        # Retorna como OpenAI tool_call response
        message = {
            "role": "assistant",
            "content": "",
            "tool_calls": [{
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "type": "function",
                "function": {
                    "name": tool_call["name"],
                    "arguments": json.dumps(tool_call.get("arguments", {})),
                },
            }],
        }
        finish_reason = "tool_calls"
    else:
        message = {"role": "assistant", "content": raw_text}
        finish_reason = "stop"

    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:16]}",
        created=int(time.time()),
        model=request.model,
        choices=[ChatCompletionChoice(message=message, finish_reason=finish_reason)],
    )


# ─── Helpers ──────────────────────────────────────────────────────────────────

_TOOL_CALL_RE = re.compile(r"^TOOL_CALL:\s*(\{.*\})\s*$", re.MULTILINE)


def _stringify_content(content: Any) -> str:
    """Serializa content que pode ser str ou List[ContentBlock]."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                # Vision blocks: {type: image, source: ...} sao ignorados (CLI nao processa)
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif block.get("type") == "image":
                    parts.append("[imagem]")
                else:
                    parts.append(block.get("text") or block.get("content") or "")
            else:
                parts.append(str(block))
        return "\n".join(p for p in parts if p)
    return str(content)


def _build_tool_protocol(tools: List[ToolDef]) -> str:
    """Mesma logica do ClaudeCodeModel — instrui o modelo a usar TOOL_CALL: {...}."""
    lines = []
    for t in tools:
        fn = t.function
        params = fn.parameters or {}
        props = params.get("properties", {})
        required = params.get("required", [])

        param_lines = []
        for pname, pinfo in props.items():
            req = "(required)" if pname in required else "(optional)"
            ptype = pinfo.get("type", "any")
            pdesc = pinfo.get("description", "")
            param_lines.append(f"    - {pname} ({ptype}) {req}: {pdesc}")
        param_str = "\n".join(param_lines) if param_lines else "    (no parameters)"
        lines.append(f"  - {fn.name}: {fn.description or ''}\n{param_str}")

    return (
        "\nTOOL CALLING PROTOCOL:\n"
        "When you need to use a tool, output EXACTLY this on a single line "
        "(nothing else on that line):\n"
        "TOOL_CALL: {\"name\": \"tool_name\", \"arguments\": {\"arg1\": \"val1\"}}\n"
        "Then stop and wait for the tool result before continuing.\n\n"
        "Available tools:\n" + "\n".join(lines)
    )


def _build_prompt(req: ChatCompletionRequest) -> str:
    """Converte request OpenAI em prompt unico pra `claude -p`."""
    system_parts: List[str] = []
    convo_parts: List[str] = []

    for m in req.messages:
        content = _stringify_content(m.content)
        if m.role == "system":
            if content:
                system_parts.append(content)
        elif m.role == "user":
            if content:
                convo_parts.append(f"Human: {content}")
        elif m.role == "assistant":
            if m.tool_calls:
                # Reflete a tool call que foi feita
                tc_text = json.dumps([{
                    "name": tc["function"]["name"],
                    "arguments": json.loads(tc["function"]["arguments"] or "{}"),
                } for tc in m.tool_calls], ensure_ascii=False)
                convo_parts.append(f"Assistant: [tool calls: {tc_text}]")
            elif content:
                convo_parts.append(f"Assistant: {content}")
        elif m.role == "tool":
            tool_name = m.name or "tool"
            convo_parts.append(f"Tool result ({tool_name}): {content}")

    system_text = "\n\n".join(system_parts).strip()
    if req.tools:
        system_text = (system_text + "\n" + _build_tool_protocol(req.tools)).strip()

    parts: List[str] = []
    if system_text:
        parts.append(f"<system>\n{system_text}\n</system>")
    parts.extend(convo_parts)
    parts.append("Assistant:")
    return "\n\n".join(parts)


def _parse_tool_call(text: str) -> Optional[Dict[str, Any]]:
    """Extrai TOOL_CALL: {...} do output texto."""
    m = _TOOL_CALL_RE.search(text)
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
        if isinstance(data, dict) and "name" in data:
            return data
    except json.JSONDecodeError:
        logger.warning(f"claude_cli_proxy: tool_call JSON invalido: {m.group(1)}")
    return None
