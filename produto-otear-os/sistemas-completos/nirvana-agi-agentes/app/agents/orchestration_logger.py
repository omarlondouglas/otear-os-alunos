"""
Orchestration Logger - Captures agent lifecycle events for real-time visualization.

Uses Redis to store events that are displayed in the frontend logs panel.
"""

import redis
import json
from datetime import datetime
import os
from agno.utils.log import logger

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def get_redis():
    """Get Redis client for orchestration logs."""
    try:
        return redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        return None


def get_entity_name(agent=None, team=None, **kwargs):
    """
    Extract the name from agent or team parameter.
    Agno passes 'agent' for Agent hooks and 'team' for Team hooks.
    """
    if agent is not None:
        name = getattr(agent, 'name', None)
        if name:
            return name
            
    if team is not None:
        name = getattr(team, 'name', None)
        if name:
            return name
            
    # Fallback: Agno sometimes passes the Agent instance inside kwargs under different names
    for key, value in kwargs.items():
        if hasattr(value, 'name'):
            name = getattr(value, 'name', None)
            if name and isinstance(name, str):
                return name
        
        # Sometimes it's passed directly as a string (e.g., agent_name)
        if key == 'agent_name' and isinstance(value, str):
            return value

    return "Jobs"  # Default to orchestrator name


def log_orchestration_event(agent: str, event_type: str, message: str, metadata: dict = None):
    """
    Log an orchestration event to Redis.
    
    Args:
        agent: Name of the agent
        event_type: One of 'delegation', 'tool_call', 'decision', 'agent', 'system'
        message: Human-readable message
        metadata: Optional additional data
    """
    try:
        client = get_redis()
        if not client:
            logger.debug(f"[OrchLog] Redis not available: {message}")
            return
        
        entry = {
            "id": f"orch-{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "message": message,
            "type": event_type,
            "metadata": metadata or {}
        }
        client.lpush("agent_logs", json.dumps(entry))
        client.ltrim("agent_logs", 0, 999)
        logger.debug(f"[OrchLog] {event_type}: {message}")
    except Exception as e:
        logger.error(f"[OrchLog] Failed to log: {e}")


def log_agent_start(agent=None, team=None, **kwargs):
    """Pre-hook: Called when an agent/team starts processing."""
    entity_name = get_entity_name(agent=agent, team=team, **kwargs)
    
    # Try to extract the incoming task or message
    incoming_task = ""
    if "message" in kwargs and kwargs["message"]:
        incoming_task = str(kwargs["message"])
    elif "task" in kwargs and kwargs["task"]:
        incoming_task = str(kwargs["task"])
        
    log_message = f"🎯 {entity_name} começou a processar"
    if incoming_task:
        # Include exactly what the agent received
        log_message += f"\nRecebeu: {incoming_task}"
        
    log_orchestration_event(
        agent=entity_name,
        event_type="delegation",
        message=log_message,
        metadata={"event": "start", "task": incoming_task}
    )


def log_agent_end(agent=None, team=None, response=None, **kwargs):
    """Post-hook: Called when an agent/team finishes processing."""
    entity_name = get_entity_name(agent=agent, team=team, **kwargs)
    
    # Extract FULL response content
    full_content = ""
    if response:
        if hasattr(response, 'content'):
            full_content = str(response.content)
        elif isinstance(response, str):
            full_content = response
    
    log_orchestration_event(
        agent=entity_name,
        event_type="decision",
        message=f"✅ {entity_name} concluiu:\n{full_content}" if full_content else f"✅ {entity_name} concluiu",
        metadata={"event": "end"}
    )


def log_tool_call(function_name=None, function_call=None, arguments=None, agent=None, team=None, **kwargs):
    """Tool hook: Called when a tool is invoked.
    
    IMPORTANT: In Agno, tool_hooks INTERCEPT the tool call.
    The hook MUST call function_call(**arguments) and return the result,
    otherwise the tool will not execute and will return None.
    """
    
    # Em hooks de ferramentas do Agno, as vezes o agent vem só em kwargs
    if 'agent' in kwargs and kwargs['agent'] is not None and agent is None:
        agent = kwargs['agent']
        
    entity_name = get_entity_name(agent=agent, team=team, **kwargs)
    
    # Format full arguments
    args_full = ""
    if arguments:
        try:
            if isinstance(arguments, dict):
                args_full = json.dumps(arguments, ensure_ascii=False, indent=2)
            else:
                args_full = str(arguments)
        except:
            args_full = str(arguments)

    # SPECIAL HANDLING: Delegation
    if function_name == "delegate_task_to_member":
        target = "Membro"
        if isinstance(arguments, dict):
            target = arguments.get("agent_name") or arguments.get("name") or target
        
        message = f"➡️ Delegou tarefa para: {target}\nCom argumentos:\n{args_full}"
        event_type = "delegation"
    else:
        message = f"🔧 Chamou tool: {function_name}\nCom argumentos:\n{args_full}"
        event_type = "tool_call"

    log_orchestration_event(
        agent=entity_name,
        event_type=event_type,
        message=message,
        metadata={"tool": function_name, "args_full": args_full}
    )

    # CRITICAL: Execute the actual tool function and return its result
    # Without this, Agno tool_hooks will cause all tools to return None
    if function_call is not None and arguments is not None:
        try:
            result = function_call(**arguments)
            
            # FIX: Se Agno instanciar a ferramenta como assíncrona, a execução inicial
            # retorna uma corotina. Precisamos avaliá-la de forma segura se possível,
            # sem quebrar o uvloop (comum no FastAPI e incompatível com nest_asyncio).
            import inspect
            if inspect.iscoroutine(result):
                import asyncio
                import threading
                
                try:
                    loop = asyncio.get_running_loop()
                    is_running = loop.is_running()
                except RuntimeError:
                    is_running = False
                    
                if is_running:
                    # Executa a corotina em uma nova thread com um novo event loop sincronizado
                    thread_result = []
                    thread_error = []
                    
                    def run_in_thread():
                        try:
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            res = new_loop.run_until_complete(result)
                            thread_result.append(res)
                        except Exception as thread_exc:
                            thread_error.append(thread_exc)
                        finally:
                            new_loop.close()
                            
                    t = threading.Thread(target=run_in_thread)
                    t.start()
                    t.join()
                    
                    if thread_error:
                        raise thread_error[0]
                    result = thread_result[0]
                else:
                    result = asyncio.run(result)

            log_orchestration_event(
                agent=entity_name,
                event_type="tool_call",
                message=f"✅ Tool {function_name} concluída com sucesso",
                metadata={"tool": function_name}
            )
            return result
        except Exception as e:
            log_orchestration_event(
                agent=entity_name,
                event_type="tool_call",
                message=f"❌ Tool {function_name} falhou: {str(e)}",
                metadata={"tool": function_name, "error": str(e)}
            )
            raise
    elif function_call is not None:
        return function_call()
    
    return None


def log_delegation(from_agent: str, to_agent: str, task: str = ""):
    """Log when one agent delegates to another."""
    log_orchestration_event(
        agent=from_agent,
        event_type="delegation",
        message=f"➡️ {from_agent} delegou para {to_agent}" + (f": {task}" if task else ""),
        metadata={"from": from_agent, "to": to_agent, "task": task}
    )

