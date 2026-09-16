#!/usr/bin/env python3
"""
Diagnóstico rápido dos problemas reportados
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_carousel_service():
    """Testa se o serviço de carrossel está funcionando"""
    print("🔍 Testando serviço de carrossel...")
    
    carousel_url = os.getenv("CAROUSEL_API_URL", "")
    carousel_key = os.getenv("CAROUSEL_API_KEY", "")
    
    if not carousel_url:
        print("❌ CAROUSEL_API_URL não configurada no .env")
        return False
    
    try:
        # Testar health check
        health_url = f"{carousel_url}/api/health"
        print(f"   Testando: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Serviço de carrossel está online")
            return True
        else:
            print(f"❌ Serviço retornou status {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print("❌ Timeout ao conectar - serviço pode estar fora do ar")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - serviço não está acessível")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_video_service():
    """Testa se o serviço de vídeo está funcionando"""
    print("\n🔍 Testando serviço de vídeo...")
    
    video_url = os.getenv("VIDEO_EDITOR_API_URL", "")
    video_key = os.getenv("VIDEO_EDITOR_API_KEY", "")
    
    if not video_url:
        print("❌ VIDEO_EDITOR_API_URL não configurada no .env")
        return False
    
    try:
        # Testar health check
        health_url = f"{video_url}/api/health"
        print(f"   Testando: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Serviço de vídeo está online")
            return True
        else:
            print(f"❌ Serviço retornou status {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print("❌ Timeout ao conectar - serviço pode estar fora do ar")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - serviço não está acessível")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_simple_carousel_generation():
    """Testa geração simples de carrossel"""
    print("\n🔍 Testando geração de carrossel...")
    
    carousel_url = os.getenv("CAROUSEL_API_URL", "")
    carousel_key = os.getenv("CAROUSEL_API_KEY", "")
    
    if not carousel_url:
        print("❌ Não é possível testar - URL não configurada")
        return False
    
    try:
        url = f"{carousel_url}/api/generate-multi"
        
        # Dados de teste simples
        test_data = {
            "slides": [
                {
                    "type": "cover",
                    "title": "TESTE",
                    "subtitle": "Carrossel de Teste",
                    "bgColor": "#0a0a0a",
                    "titleColor": "#ffffff"
                },
                {
                    "type": "text-only",
                    "title": "Slide 2 - Teste",
                    "bgColor": "#1a1a1a",
                    "titleColor": "#ffffff"
                }
            ]
        }
        
        headers = {"Content-Type": "application/json"}
        if carousel_key:
            headers["X-API-Key"] = carousel_key
        
        print(f"   Enviando para: {url}")
        print(f"   Slides: {len(test_data['slides'])}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                slides = result.get("slides", [])
                print(f"✅ Carrossel gerado com sucesso! {len(slides)} imagens")
                for i, slide in enumerate(slides, 1):
                    print(f"   Slide {i}: {slide.get('url', 'URL não encontrada')}")
                return True
            else:
                print(f"❌ API retornou erro: {result.get('error', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"   Resposta: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na geração: {e}")
        return False

def test_debug_render():
    """Testa o novo endpoint de diagnóstico do Playwright"""
    print("\n🔍 Testando renderização interna (Playwright)...")
    
    carousel_url = os.getenv("CAROUSEL_API_URL", "")
    if not carousel_url:
        return False
        
    try:
        url = f"{carousel_url}/api/debug-render"
        print(f"   Testando: {url}")
        response = requests.get(url, timeout=45)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Playwright funcionando! Tempo: {result.get('time')}")
                return True
            else:
                print(f"❌ Playwright falhou: {result.get('error')}")
                return False
        return False
    except Exception as e:
        print(f"❌ Erro ao testar render: {e}")
        return False

def main():
    print("🚨 DIAGNÓSTICO RÁPIDO - PROBLEMAS REPORTADOS")
    print("=" * 60)
    print("Verificando por que carrossel e vídeo não estão funcionando...")
    print("=" * 60)
    
    tests = [
        ("Importação dos Agentes", test_agent_import),
        ("Serviço de Carrossel", test_carousel_service),
        ("Renderização Playwright", test_debug_render),
        ("Serviço de Vídeo", test_video_service),
        ("Geração de Carrossel", test_simple_carousel_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 Erro inesperado: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ OK" if success else "❌ FALHA"
        print(f"{status} {test_name}")
    
    failed_tests = [name for name, success in results if not success]
    
    if not failed_tests:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("O problema pode estar na lógica dos agentes ou na interface.")
    else:
        print(f"\n🚨 PROBLEMAS ENCONTRADOS:")
        for test in failed_tests:
            print(f"   • {test}")
        
        print(f"\n🔧 PRÓXIMOS PASSOS:")
        if "Serviço de Carrossel" in failed_tests:
            print("   1. Verificar se o serviço de carrossel está rodando")
            print("   2. Verificar URL e API key do carrossel no .env")
        if "Serviço de Vídeo" in failed_tests:
            print("   3. Verificar se o serviço de vídeo está rodando")
            print("   4. Verificar URL e API key do vídeo no .env")
        if "Importação dos Agentes" in failed_tests:
            print("   5. Verificar dependências Python (agno, etc.)")
        if "Geração de Carrossel" in failed_tests:
            print("   6. Verificar logs do serviço de carrossel")

if __name__ == "__main__":
    main()