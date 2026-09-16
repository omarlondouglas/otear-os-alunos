#!/usr/bin/env python3
"""
Script para corrigir erros de sintaxe no agno_tools.py
"""

import os
import shutil

def backup_file():
    """Faz backup do arquivo original"""
    original = "app/agents/agno_tools.py"
    backup = "app/agents/agno_tools.py.backup"
    
    if os.path.exists(original):
        shutil.copy2(original, backup)
        print(f"✅ Backup criado: {backup}")
        return True
    return False

def check_syntax():
    """Verifica se há erros de sintaxe"""
    try:
        with open("app/agents/agno_tools.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Tentar compilar o código
        compile(content, "app/agents/agno_tools.py", "exec")
        print("✅ Sintaxe está correta!")
        return True
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.msg}")
        print(f"   Texto: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def fix_file():
    """Corrige o arquivo removendo texto corrompido"""
    print("🔧 Corrigindo arquivo...")
    
    # Usar o arquivo de backup do agi-videos-temp que sabemos que funciona
    source_file = "agi-videos-temp/app/agents/agno_tools.py"
    target_file = "app/agents/agno_tools.py"
    
    if os.path.exists(source_file):
        print(f"📁 Copiando arquivo limpo de: {source_file}")
        shutil.copy2(source_file, target_file)
        print("✅ Arquivo copiado!")
        return True
    else:
        print(f"❌ Arquivo fonte não encontrado: {source_file}")
        return False

def test_import():
    """Testa se consegue importar o módulo"""
    try:
        import sys
        if "app.agents.agno_tools" in sys.modules:
            del sys.modules["app.agents.agno_tools"]
        
        from app.agents.agno_tools import generate_carousel_tool
        print("✅ Importação funcionando!")
        return True
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def main():
    print("🚨 CORREÇÃO DE ERRO DE SINTAXE")
    print("=" * 50)
    
    # 1. Fazer backup
    if backup_file():
        print("Backup criado com sucesso")
    
    # 2. Verificar sintaxe atual
    print("\n🔍 Verificando sintaxe atual...")
    if check_syntax():
        print("Arquivo já está correto!")
        return
    
    # 3. Corrigir arquivo
    print("\n🔧 Corrigindo arquivo...")
    if fix_file():
        print("Arquivo corrigido!")
    else:
        print("Falha ao corrigir arquivo")
        return
    
    # 4. Verificar sintaxe após correção
    print("\n🔍 Verificando sintaxe após correção...")
    if check_syntax():
        print("✅ Sintaxe corrigida com sucesso!")
    else:
        print("❌ Ainda há erros de sintaxe")
        return
    
    # 5. Testar importação
    print("\n🧪 Testando importação...")
    if test_import():
        print("✅ Módulo funcionando perfeitamente!")
    else:
        print("❌ Ainda há problemas na importação")
    
    print("\n🎉 CORREÇÃO CONCLUÍDA!")
    print("Agora você pode reiniciar os serviços:")
    print("  docker-compose restart")

if __name__ == "__main__":
    main()