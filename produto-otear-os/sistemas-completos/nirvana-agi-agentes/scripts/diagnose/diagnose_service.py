#!/usr/bin/env python3
"""
Diagnóstico rápido do serviço - Identifica por que está retornando 502
"""

import subprocess
import sys
import json

def run_command(cmd, description):
    """Executa um comando e retorna o resultado"""
    print(f"\n🔍 {description}")
    print(f"Comando: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Exit Code: {result.returncode}")
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT - Comando demorou mais de 30 segundos")
        return False, "", "Timeout"
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False, "", str(e)

def diagnose_docker_compose():
    """Diagnostica problemas do docker-compose"""
    print("🐳 DIAGNÓSTICO DOCKER-COMPOSE")
    print("=" * 60)
    
    # 1. Verificar se docker-compose existe
    success, stdout, stderr = run_command("docker-compose --version", "Verificando docker-compose")
    if not success:
        print("❌ Docker-compose não encontrado!")
        return False
    
    # 2. Verificar status dos serviços
    success, stdout, stderr = run_command("docker-compose ps", "Status dos serviços")
    if "gateway" not in stdout:
        print("❌ Serviço 'gateway' não encontrado!")
        return False
    
    # 3. Verificar logs do gateway
    success, stdout, stderr = run_command("docker-compose logs gateway --tail=20", "Logs recentes do gateway")
    
    # 4. Verificar se o container está rodando
    success, stdout, stderr = run_command("docker-compose ps gateway", "Status específico do gateway")
    
    return True

def diagnose_service_health():
    """Diagnostica a saúde do serviço"""
    print("\n🏥 DIAGNÓSTICO DE SAÚDE DO SERVIÇO")
    print("=" * 60)
    
    # 1. Testar endpoint local (se possível)
    success, stdout, stderr = run_command(
        "docker-compose exec -T gateway curl -s http://localhost:8000/api/health || echo 'FAILED'", 
        "Teste local do endpoint /api/health"
    )
    
    # 2. Verificar processo Python
    success, stdout, stderr = run_command(
        "docker-compose exec -T gateway ps aux | grep python || echo 'NO_PYTHON_PROCESS'", 
        "Verificando processo Python"
    )
    
    # 3. Verificar portas abertas
    success, stdout, stderr = run_command(
        "docker-compose exec -T gateway netstat -tlnp | grep 8000 || echo 'PORT_NOT_LISTENING'", 
        "Verificando porta 8000"
    )

def diagnose_python_imports():
    """Diagnostica problemas de importação Python"""
    print("\n🐍 DIAGNÓSTICO PYTHON")
    print("=" * 60)
    
    # 1. Testar importação básica
    success, stdout, stderr = run_command(
        "docker-compose exec -T gateway python -c \"import fastapi; print('FastAPI OK')\" || echo 'IMPORT_FAILED'", 
        "Testando importação FastAPI"
    )
    
    # 2. Testar importação dos agentes
    success, stdout, stderr = run_command(
        "docker-compose exec -T gateway python -c \"from app.agents.agno_agents import orchestrator; print('Agents OK')\" || echo 'AGENTS_FAILED'", 
        "Testando importação dos agentes"
    )
    
    # 3. Verificar variáveis de ambiente
    success, stdout, stderr = run_command(
        "docker-compose exec -T gateway env | grep -E 'PORT|DATABASE_URL|GOOGLE_API_KEY' || echo 'ENV_MISSING'", 
        "Verificando variáveis de ambiente"
    )

def diagnose_external_access():
    """Diagnostica acesso externo"""
    print("\n🌐 DIAGNÓSTICO ACESSO EXTERNO")
    print("=" * 60)
    
    # 1. Testar URL externa
    success, stdout, stderr = run_command(
        "curl -s -I https://otear-agentes-otear.qc7qit.easypanel.host/api/health || echo 'EXTERNAL_FAILED'", 
        "Testando acesso externo"
    )

def provide_solutions():
    """Fornece soluções baseadas no diagnóstico"""
    print("\n🔧 SOLUÇÕES RECOMENDADAS")
    print("=" * 60)
    
    print("\n1. REINICIAR SERVIÇOS:")
    print("   docker-compose down")
    print("   docker-compose up -d")
    
    print("\n2. RECONSTRUIR IMAGENS:")
    print("   docker-compose build --no-cache gateway")
    print("   docker-compose up -d gateway")
    
    print("\n3. VERIFICAR LOGS EM TEMPO REAL:")
    print("   docker-compose logs -f gateway")
    
    print("\n4. ENTRAR NO CONTAINER PARA DEBUG:")
    print("   docker-compose exec gateway bash")
    print("   # Dentro do container:")
    print("   python api_gateway.py")
    
    print("\n5. TESTAR IMPORTAÇÕES MANUALMENTE:")
    print("   docker-compose exec gateway python -c \"from app.agents.agno_agents import orchestrator\"")
    
    print("\n6. VERIFICAR ARQUIVO DE CONFIGURAÇÃO:")
    print("   docker-compose exec gateway cat .env")

def main():
    print("🚨 DIAGNÓSTICO COMPLETO DO SERVIÇO")
    print("Identificando por que o serviço está retornando 502...")
    print("=" * 60)
    
    try:
        # Executar diagnósticos
        diagnose_docker_compose()
        diagnose_service_health()
        diagnose_python_imports()
        diagnose_external_access()
        
        # Fornecer soluções
        provide_solutions()
        
        print("\n" + "=" * 60)
        print("📋 RESUMO")
        print("=" * 60)
        print("\nO diagnóstico foi executado. Verifique os resultados acima.")
        print("Se o serviço não estiver rodando, execute as soluções recomendadas.")
        print("\n🎯 PRÓXIMO PASSO: Reinicie os serviços e verifique os logs!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Diagnóstico interrompido pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro durante diagnóstico: {e}")

if __name__ == "__main__":
    main()