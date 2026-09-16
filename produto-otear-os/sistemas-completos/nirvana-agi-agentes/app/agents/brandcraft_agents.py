import os
from agno.agent import Agent
from agno.team import Team

# Storage
from app.agents.agno_agents import agent_storage

# Model factory — Claude CLI ou Claude SDK dependendo do env
from app.core.model_factory import get_model

# BrandCraft Tools
from app.agents.agno_tools import (
    extract_design_system_tool,
    create_branded_pdf_tool,
    create_branded_pptx_tool,
    inspect_asset_tool
)

# 1. Extractor Agent
bc_extractor = Agent(
    name="BrandCraftExtractor",
    model=get_model("planner"),
    tools=[extract_design_system_tool],
    instructions=[
        "Você é um especialista em Extração de Design Systems (Prober).",
        "Sua função é receber URLs de marcas e acionar a 'extract_design_system_tool' para descobrir cores primárias, secundárias e tipografias.",
        "Sempre avise qual site foi extraído e registre o JSON gerado nos logs.",
        "Repasse o design token em formato string literal/JSON para o próximo agente encarregado de construir."
    ],
    db=agent_storage,
    add_history_to_context=True,
    markdown=True
)

# 2. Document Renderer Agent
bc_renderer = Agent(
    name="BrandCraftRenderer",
    model=get_model("fast"),
    tools=[create_branded_pdf_tool, create_branded_pptx_tool],
    instructions=[
        "Você é um Engenheiro de Documentos (Forge/Canvas).",
        "Sua função é gerar PDFs (create_branded_pdf_tool) ou PPTXs (create_branded_pptx_tool) institucionais.",
        "Para gerar, você DEVE receber o texto bruto a ser formatado e um Dicionário JSON do esquema de cor (retornado do Extractor).",
        "Após acionar as tools, pegue a URL resultante e informe o sucesso do arquivo gerado.",
        "Não gere textos e não traduza: seu trabalho é estritamente montar o layout."
    ],
    db=agent_storage,
    add_history_to_context=True,
    markdown=True
)

# 3. Quality Inspector Agent
bc_inspector = Agent(
    name="BrandCraftInspector",
    model=get_model("fast"),
    tools=[inspect_asset_tool],
    instructions=[
        "Você é um Inspetor de Qualidade Visual (Gauge).",
        "Sua função é testar e validar o asset gerado (PDF, PPTX) usando a tool 'inspect_asset_tool'.",
        "Retorne o status do QA (PASS/FAIL) e observações sugeridas sobre compliance com marca.",
        "Apenas diga que está completo após informar o relatório de verificação."
    ],
    db=agent_storage,
    add_history_to_context=True,
    markdown=True
)

# BrandCraft Sub-Team
brandcraft_team = Team(
    name="Neumeier",
    model=get_model("planner"),
    members=[bc_extractor, bc_renderer, bc_inspector],
    instructions=[
        "Você é o Neumeier, coordenador do squad de branding e recursos visuais.",
        "Trabalhe apenas em solicitações referentes a Identidade Visual de Marcas, Design Systems, criação de apostilas PDF e elaboração de PPTX profissionais.",
        "Cadeia de Valor Padrão:",
        "1. Extraia o token da marca via bc_extractor (se aplicável/fornecido URL).",
        "2. Encaminhe texto e tokens de marca passados pelo HeadOrchestrator para o bc_renderer compor a apresentação/documento.",
        "3. Acione o bc_inspector para fazer compliance da mídia produzida antes de devolver a URL final."
    ],
    db=agent_storage,
    add_history_to_context=True,
    markdown=True
)
