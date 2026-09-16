# FIX: Agentes Não Retornam Resultados

## 🔴 Problema

Os agentes (ReviewerAgent e VideoDirectorAgent) não estão retornando resultados quando chamados pelo Orchestrator.

## 🎯 Causa Raiz

Após análise detalhada, identifiquei **3 problemas principais**:

### 1. Decorator `@with_logging` Interferindo com Agno

O decorator está envolvendo as funções e pode estar escondendo os metadados necessários para o Agno inspecionar as ferramentas.

### 2. Falta de Type Hints Explícitos

As ferramentas não têm type hints completos, dificultando o Agno de entender os parâmetros.

### 3. Instruções do Orchestrator Muito Complexas

O Orchestrator tem instruções muito longas e complexas que podem estar confundindo o modelo.

## ✅ Solução Implementada

### Passo 1: Remover Decorator das Ferramentas Críticas

Vamos remover o `@with_logging` das ferramentas `generate_carousel_tool` e `edit_video_tool` e adicionar logging manual dentro delas.

### Passo 2: Adicionar Type Hints Completos

Adicionar type hints explícitos em todas as ferramentas.

### Passo 3: Simplificar Instruções

Reduzir as instruções do Orchestrator para focar no essencial.

## 📝 Mudanças Necessárias

### Arquivo: `app/agents/agno_tools.py`

#### Mudança 1: generate_carousel_tool

**ANTES:**
```python
@with_logging("Generate Carousel")
def generate_carousel_tool(slides_data: list):
```

**DEPOIS:**
```python
from typing import List, Dict, Any, Optional

def generate_carousel_tool(slides_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    FERRAMENTA OBRIGATÓRIA para gerar carrosséis do Instagram.
    
    Args:
        slides_data: Lista de dicts com os dados de cada slide.
    
    Returns:
        Dict com success, slides (array de URLs), carouselId, totalSlides, ou error.
    """
    # Logging manual no início
    logger.info(f"[CAROUSEL TOOL] Iniciando geração de {len(slides_data) if slides_data else 0} slides")
    
    try:
        # ... resto do código ...
        
        # Logging manual no final
        logger.info(f"[CAROUSEL TOOL] Concluído com sucesso")
        return result
        
    except Exception as e:
        logger.error(f"[CAROUSEL TOOL] Erro: {str(e)}")
        return {"success": False, "error": str(e)}
```

#### Mudança 2: edit_video_tool

**ANTES:**
```python
@with_logging("Edit Video")
def edit_video_tool(video_url: str, operations: list = None, ...):
```

**DEPOIS:**
```python
from typing import List, Dict, Any, Optional

def edit_video_tool(
    video_url: str,
    operations: Optional[List[Dict[str, Any]]] = None,
    operation_type: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    preset: Optional[str] = None
) -> Dict[str, Any]:
    """
    FERRAMENTA OBRIGATÓRIA para editar vídeos.
    
    Args:
        video_url: URL do vídeo (obrigatório)
        preset: Nome do preset ('VIRAL', 'MODERN_SUBTITLES', etc)
        operations: Lista de operações customizadas
    
    Returns:
        Dict com status, download_url, id, ou error.
    """
    # Logging manual
    logger.info(f"[VIDEO TOOL] Iniciando edição: {video_url}")
    
    try:
        # ... resto do código ...
        
        logger.info(f"[VIDEO TOOL] Concluído")
        return result
        
    except Exception as e:
        logger.error(f"[VIDEO TOOL] Erro: {str(e)}")
        return {"error": str(e)}
```

### Arquivo: `app/agents/agno_agents.py`

#### Mudança 3: Simplificar Instruções do ReviewerAgent

**REDUZIR de 100+ linhas para ~30 linhas focadas:**

```python
reviewer = Agent(
    name="ReviewerAgent",
    model=Gemini(id=MODEL_PLANNER),
    tools=[list_fonts_tool, check_carousel_health_tool, generate_carousel_tool],
    instructions=[
        "Você é o ReviewerAgent, especialista em gerar carrosséis para Instagram.",
        "",
        "REGRA ABSOLUTA:",
        "- SEMPRE chame generate_carousel_tool quando receber um pedido de carrossel",
        "- NUNCA dê instruções manuais ou diga que está pronto sem ter as URLs",
        "",
        "SCHEMA DE CADA SLIDE:",
        "- type: 'cover' | 'image-text' | 'two-images' | 'text-only' (obrigatório)",
        "- title: Texto principal (obrigatório)",
        "- subtitle: Texto secundário (opcional)",
        "- titleColor: Cor hex (ex: '#ffffff')",
        "- bgColor: Cor hex (ex: '#0a0a0a')",
        "- fontFamily: 'urbanist', 'montserrat', 'inter', 'poppins'",
        "",
        "EXEMPLO DE CHAMADA:",
        "generate_carousel_tool([",
        "    {'type': 'cover', 'title': 'TÍTULO', 'subtitle': 'Subtítulo', 'bgColor': '#0a0a0a'},",
        "    {'type': 'text-only', 'title': 'Conteúdo', 'bgColor': '#1a1a1a'}",
        "])",
        "",
        "WORKFLOW:",
        "1. Receba o conteúdo do carrossel",
        "2. Monte o array de slides com type e title",
        "3. CHAME generate_carousel_tool(slides)",
        "4. Verifique se retornou 'success': true e 'slides' com URLs",
        "5. RETORNE as URLs completas ao usuário",
        "",
        "FORMATO DA RESPOSTA:",
        "Carrossel criado! 🎨",
        "Imagens geradas (N slides):",
        "1. [URL_1]",
        "2. [URL_2]",
        "...",
    ],
    db=agent_storage,
    add_history_to_context=True,
    learning=True,
    pre_hooks=[log_agent_start],
    post_hooks=[log_agent_end],
    tool_hooks=[log_tool_call]
)
```

#### Mudança 4: Simplificar Instruções do VideoDirectorAgent

**REDUZIR de 150+ linhas para ~40 linhas:**

```python
video_director = Agent(
    name="VideoDirectorAgent",
    model=Gemini(id=MODEL_PLANNER),
    tools=[edit_video_tool, transcribe_video_tool, check_video_status_tool, generate_presigned_url_tool],
    instructions=[
        "Você é o VideoDirectorAgent, especialista em edição de vídeos.",
        "",
        "REGRA ABSOLUTA:",
        "- SEMPRE chame edit_video_tool quando receber um pedido de edição",
        "- NUNCA simule edição ou diga que está pronto sem ter a URL",
        "",
        "PRESETS DISPONÍVEIS:",
        "- 'VIRAL': Legendas amarelas + remoção de silêncio (RECOMENDADO)",
        "- 'MODERN_SUBTITLES': Legendas brancas modernas",
        "- 'REACTION': Para vídeos de reação",
        "- 'CLEAN': Legendas simples",
        "",
        "WORKFLOW:",
        "1. Receba a URL do vídeo",
        "2. Se for caminho do MinIO (ex: 'stories/video.mp4'), chame generate_presigned_url_tool primeiro",
        "3. CHAME edit_video_tool(video_url=URL, preset='VIRAL')",
        "4. A ferramenta aguarda até 30 minutos pelo processamento",
        "5. Verifique a resposta:",
        "   - Se tem 'download_url': SUCESSO! Retorne a URL",
        "   - Se tem 'status': 'processing': GUARDE o job_id e continue verificando",
        "   - Se tem 'error': Informe o erro",
        "6. SEMPRE retorne a URL completa quando receber",
        "",
        "FORMATO DA RESPOSTA:",
        "Vídeo editado com sucesso! 🎬",
        "Job ID: {job_id}",
        "Download: [URL_COMPLETA]",
        "",
        "MEMÓRIA:",
        "- Você tem memória persistente (PostgreSQL)",
        "- GUARDE o job_id quando criar um job",
        "- Use check_video_status_tool(job_id) para verificar progresso",
    ],
    db=agent_storage,
    add_history_to_context=True,
    learning=True,
    pre_hooks=[log_agent_start],
    post_hooks=[log_agent_end],
    tool_hooks=[log_tool_call]
)
```

#### Mudança 5: Simplificar Instruções do Orchestrator

**REDUZIR de 100+ linhas para ~50 linhas:**

```python
orchestrator = Team(
    name="Patricia",
    model=Gemini(id=MODEL_PLANNER),
    members=[stylist, copywriter, designer, reviewer, video_director, dona],
    instructions=[
        "Meu nome é Patricia. Sou especializada em criar conteúdo viral, carrosséis e vídeos.",
        "",
        "REGRA SUPREMA:",
        "NUNCA desista dizendo que os agentes 'não responderam'. Se não receber URLs, delegue novamente.",
        "",
        "TIME DE ESPECIALISTAS:",
        "- Stylist: Modela estilos de criadores",
        "- Copywriter: Textos e roteiros",
        "- Designer: Imagens individuais",
        "- ReviewerAgent: GERA CARROSSÉIS (generate_carousel_tool)",
        "- VideoDirectorAgent: EDITA VÍDEOS (edit_video_tool)",
        "- Dona: Roteiros de vídeo viral",
        "",
        "PIPELINE DE CARROSSEL:",
        "1. Copywriter cria os textos",
        "2. DELEGUE ao ReviewerAgent: 'Gere o carrossel com estes textos: [textos]'",
        "3. ReviewerAgent chama generate_carousel_tool e retorna URLs",
        "4. Você retorna as URLs ao usuário",
        "",
        "PIPELINE DE VÍDEO:",
        "1. DELEGUE ao VideoDirectorAgent: 'Edite este vídeo: [URL]'",
        "2. VideoDirectorAgent chama edit_video_tool e aguarda",
        "3. VideoDirectorAgent retorna URL do vídeo editado",
        "4. Você retorna a URL ao usuário",
        "",
        "VALIDAÇÃO:",
        "NUNCA diga que está pronto sem ter:",
        "✓ Para carrossel: Array de URLs das imagens",
        "✓ Para vídeo: URL do vídeo editado",
        "✓ Se não tem URLs, DELEGUE novamente",
        "",
        "FORMATO DA RESPOSTA:",
        "Seja direto e entregue as URLs. Não use desculpas.",
    ],
    db=agent_storage,
    add_history_to_context=True,
    markdown=True,
    pre_hooks=[log_agent_start],
    post_hooks=[log_agent_end],
    tool_hooks=[log_tool_call]
)
```

## 🧪 Como Testar

### Teste 1: Ferramenta Direta
```bash
python -c "from app.agents.agno_tools import generate_carousel_tool; print(generate_carousel_tool([{'type': 'cover', 'title': 'TESTE'}]))"
```

### Teste 2: Agente Individual
```bash
python -c "from app.agents.agno_agents import reviewer; print(reviewer.run('Gere um carrossel com 1 slide: TESTE').content)"
```

### Teste 3: Orchestrator
```bash
python -c "from app.agents.agno_agents import orchestrator; print(orchestrator.run('Crie um carrossel simples').content)"
```

## 📋 Checklist de Implementação

- [ ] Remover `@with_logging` de `generate_carousel_tool`
- [ ] Remover `@with_logging` de `edit_video_tool`
- [ ] Adicionar logging manual nas ferramentas
- [ ] Adicionar type hints completos
- [ ] Simplificar instruções do ReviewerAgent
- [ ] Simplificar instruções do VideoDirectorAgent
- [ ] Simplificar instruções do Orchestrator
- [ ] Testar ferramenta direta
- [ ] Testar agente individual
- [ ] Testar orchestrator
- [ ] Reiniciar serviços
- [ ] Testar via API

## 🎯 Resultado Esperado

Após essas mudanças, os agentes devem:
1. ✅ Chamar as ferramentas corretamente
2. ✅ Retornar URLs completas
3. ✅ Responder ao usuário com os resultados
