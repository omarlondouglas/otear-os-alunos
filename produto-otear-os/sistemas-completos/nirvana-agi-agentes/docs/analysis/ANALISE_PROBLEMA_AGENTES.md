# Análise do Problema: Agentes Não Retornam Resultados

## 🔍 Problema Identificado

Os agentes (ReviewerAgent e VideoDirectorAgent) não estão retornando resultados quando chamados pelo Orchestrator (Patricia).

## 🎯 Causas Raiz Identificadas

### 1. **Problema com o Decorator `@with_logging`**

O decorator `@with_logging` em `agno_tools.py` está usando `functools.wraps`, mas pode estar causando problemas com a biblioteca Agno ao tentar inspecionar as ferramentas.

**Localização:** `app/agents/agno_tools.py` linhas 30-45

```python
def with_logging(tool_name: str):
    """Decorator that logs tool execution while preserving function metadata."""
    def decorator(func):
        @functools.wraps(func)  # CRITICAL: preserves __name__, __doc__, __annotations__
        def wrapper(*args, **kwargs):
            log_tool_sync(tool_name, "Iniciando execução...", "system")
            try:
                result = func(*args, **kwargs)
                log_tool_sync(tool_name, "Concluído com sucesso.", "system")
                return result
            except Exception as e:
                log_tool_sync(tool_name, f"Erro: {str(e)}", "system")
                raise e
        return wrapper
    return decorator
```

**Problema:** Mesmo com `functools.wraps`, o decorator pode estar interferindo com a forma como o Agno detecta os parâmetros das funções.

### 2. **Falta de Type Hints Explícitos**

As ferramentas não têm type hints explícitos nos parâmetros, o que pode dificultar a biblioteca Agno de entender como chamar as funções.

**Exemplo em `generate_carousel_tool`:**
```python
def generate_carousel_tool(slides_data: list):  # ❌ list genérico
```

**Deveria ser:**
```python
from typing import List, Dict, Any

def generate_carousel_tool(slides_data: List[Dict[str, Any]]):  # ✅ tipo específico
```

### 3. **Possível Problema com Delegação no Agno Team**

O Orchestrator (Team) pode não estar delegando corretamente para os membros. As instruções dizem para "DELEGAR", mas não há evidência de que o Agno Team está realmente fazendo isso.

**Instruções do Orchestrator:**
```python
"3. DELEGUE ao ReviewerAgent: 'Gere o carrossel agora usando os textos que o Copywriter criou: [textos]'"
```

**Problema:** O Agno Team pode não ter uma ferramenta explícita de delegação, ou pode estar tentando fazer tudo sozinho sem chamar os membros.

### 4. **Timeout Muito Longo nas Ferramentas**

As ferramentas de vídeo e carrossel têm timeouts muito longos (300s para carrossel, 120s para vídeo inicial), o que pode estar causando timeouts no nível do Agno.

## 🔧 Soluções Propostas

### Solução 1: Remover o Decorator de Logging (Temporariamente)

Remover o `@with_logging` das ferramentas críticas para testar se é isso que está causando o problema.

### Solução 2: Adicionar Type Hints Completos

Adicionar type hints explícitos em todas as ferramentas para ajudar o Agno a entender os parâmetros.

### Solução 3: Simplificar as Instruções do Orchestrator

Remover a complexidade das instruções e focar em fazer o Orchestrator chamar as ferramentas diretamente, sem depender de delegação complexa.

### Solução 4: Adicionar Logging Detalhado

Adicionar prints/logs para ver exatamente o que está acontecendo quando o Orchestrator tenta usar os agentes.

### Solução 5: Testar Agentes Individualmente

Criar testes que chamam os agentes diretamente (sem passar pelo Orchestrator) para ver se eles funcionam isoladamente.

## 📋 Plano de Ação

1. ✅ **Criar script de diagnóstico** (diagnose_agents.py)
2. ⏳ **Remover decorator de logging das ferramentas críticas**
3. ⏳ **Adicionar type hints completos**
4. ⏳ **Simplificar instruções do Orchestrator**
5. ⏳ **Testar agentes individualmente**
6. ⏳ **Adicionar logging detalhado no Orchestrator**

## 🧪 Testes Necessários

### Teste 1: Agente Individual
```python
from app.agents.agno_agents import reviewer

slides = [
    {"type": "cover", "title": "TESTE", "bgColor": "#0a0a0a"}
]

response = reviewer.run(f"Gere um carrossel com estes slides: {slides}")
print(response.content)
```

### Teste 2: Ferramenta Direta
```python
from app.agents.agno_tools import generate_carousel_tool

slides = [
    {"type": "cover", "title": "TESTE", "bgColor": "#0a0a0a"}
]

result = generate_carousel_tool(slides)
print(result)
```

### Teste 3: Orchestrator com Logging
```python
from app.agents.agno_agents import orchestrator

# Adicionar logging antes
import logging
logging.basicConfig(level=logging.DEBUG)

response = orchestrator.run("Crie um carrossel simples com 2 slides")
print(response.content)
```

## 🎯 Próximos Passos

1. Executar o script de diagnóstico
2. Implementar as correções uma por uma
3. Testar após cada correção
4. Documentar o que funcionou
