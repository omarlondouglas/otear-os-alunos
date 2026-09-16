#!/usr/bin/env python3
"""
Diagnóstico do problema de agentes não retornando resultados
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("\n=== DIAGNÓSTICO DE AGENTES ===\n")

# 1. Verificar importações
print("1. Verificando importações...")
try:
    from app.agents.agno_agents import orchestrator, reviewer, video_director
    print("   ✅ Agentes importados com sucesso")
    print(f"   - Orchestrator: {orchestrator.name}")
    print(f"   - Membros: {[m.name for m in orchestrator.members]}")
except Exception as e:
    print(f"   ❌ Erro ao importar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. Verificar ferramentas
print("\n2. Verificando ferramentas...")
try:
    from app.agents.agno_tools import generate_carousel_tool, edit_video_tool
    print("   ✅ Ferramentas importadas")
    
    # Verificar se as ferramentas têm os metadados corretos
    print(f"   - generate_carousel_tool.__name__: {generate_carousel_tool.__name__}")
    print(f"   - edit_video_tool.__name__: {edit_video_tool.__name__}")
    
    # Verificar docstrings
    if generate_carousel_tool.__doc__:
        print(f"   - generate_carousel_tool tem docstring: ✅")
    else:
        print(f"   - generate_carousel_tool SEM docstring: ⚠️")
        
    if edit_video_tool.__doc__:
        print(f"   - edit_video_tool tem docstring: ✅")
    else:
        print(f"   - edit_video_tool SEM docstring: ⚠️")
        
except Exception as e:
    print(f"   ❌ Erro ao importar ferramentas: {e}")
    import traceback
    traceback.print_exc()

# 3. Verificar se os agentes têm as ferramentas corretas
print("\n3. Verificando ferramentas dos agentes...")
try:
    print(f"   - ReviewerAgent tools: {[t.__name__ if hasattr(t, '__name__') else str(t) for t in reviewer.tools]}")
    print(f"   - VideoDirectorAgent tools: {[t.__name__ if hasattr(t, '__name__') else str(t) for t in video_director.tools]}")
except Exception as e:
    print(f"   ⚠️ Erro ao listar ferramentas: {e}")

# 4. Teste simples de execução
print("\n4. Testando execução simples...")
try:
    response = orchestrator.run("Olá, como você está?")
    print(f"   ✅ Orchestrator respondeu")
    print(f"   - Tipo de resposta: {type(response)}")
    print(f"   - Tem .content? {hasattr(response, 'content')}")
    if hasattr(response, 'content'):
        print(f"   - Conteúdo (primeiros 100 chars): {response.content[:100]}")
except Exception as e:
    print(f"   ❌ Erro ao executar: {e}")
    import traceback
    traceback.print_exc()

# 5. Teste de delegação para carrossel
print("\n5. Testando delegação para carrossel...")
try:
    prompt = "Crie um carrossel simples com 2 slides: 'Título' e 'Fim'"
    print(f"   Prompt: {prompt}")
    response = orchestrator.run(prompt)
    
    if hasattr(response, 'content'):
        content = response.content
        print(f"   - Resposta (primeiros 300 chars): {content[:300]}")
        
        # Verificar se mencionou o ReviewerAgent
        if "ReviewerAgent" in content or "reviewer" in content.lower():
            print("   ✅ Mencionou ReviewerAgent")
        else:
            print("   ⚠️ NÃO mencionou ReviewerAgent")
            
        # Verificar se tem URLs
        if "http" in content:
            print("   ✅ Resposta contém URLs")
        else:
            print("   ⚠️ Resposta NÃO contém URLs")
            
        # Verificar se mencionou erro
        if "erro" in content.lower() or "error" in content.lower():
            print("   ⚠️ Resposta menciona erro")
            
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

# 6. Teste de delegação para vídeo
print("\n6. Testando delegação para vídeo...")
try:
    prompt = "Edite este vídeo: https://exemplo.com/video.mp4"
    print(f"   Prompt: {prompt}")
    response = orchestrator.run(prompt)
    
    if hasattr(response, 'content'):
        content = response.content
        print(f"   - Resposta (primeiros 300 chars): {content[:300]}")
        
        # Verificar se mencionou o VideoDirectorAgent
        if "VideoDirectorAgent" in content or "video" in content.lower():
            print("   ✅ Mencionou vídeo/VideoDirectorAgent")
        else:
            print("   ⚠️ NÃO mencionou vídeo")
            
        # Verificar se tem URLs
        if "http" in content:
            print("   ✅ Resposta contém URLs")
        else:
            print("   ⚠️ Resposta NÃO contém URLs")
            
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n=== DIAGNÓSTICO CONCLUÍDO ===\n")
