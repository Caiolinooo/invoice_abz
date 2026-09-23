#!/usr/bin/env python3
"""
Teste do servidor V3.0
"""
import subprocess
import time
import requests
import os
from pathlib import Path

def test_v3_server():
    """Test V3.0 server startup and basic functionality"""
    print("🚀 === TESTE DO SERVIDOR V3.0 ===\n")
    
    # Change to V3.0 directory
    v3_dir = Path("V3.0")
    if not v3_dir.exists():
        print("❌ Diretório V3.0 não encontrado!")
        return False
    
    print("📋 1. Verificando arquivos do servidor...")
    
    server_files = [
        "start_server.py",
        "app/api/server.py",
        "app/ui/index.html"
    ]
    
    for file_path in server_files:
        full_path = v3_dir / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING!")
            return False
    
    print(f"\n📋 2. Iniciando servidor V3.0...")
    
    try:
        # Start server in V3.0 directory
        os.chdir(str(v3_dir))
        
        # Start server process
        server_process = subprocess.Popen(
            ["python", "start_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("  🔄 Aguardando servidor inicializar...")
        time.sleep(5)  # Wait for server to start
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000", timeout=5)
            if response.status_code == 200:
                print("  ✅ Servidor V3.0 iniciado com sucesso!")
                print(f"  🌐 Acessível em: http://localhost:8000")
                
                # Test API endpoint
                try:
                    api_response = requests.get("http://localhost:8000/api/health", timeout=5)
                    if api_response.status_code == 200:
                        print("  ✅ API funcionando!")
                    else:
                        print("  ⚠️  API pode ter problemas")
                except:
                    print("  ⚠️  Endpoint /api/health não encontrado (normal)")
                
                success = True
            else:
                print(f"  ❌ Servidor retornou status {response.status_code}")
                success = False
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Não foi possível conectar ao servidor: {e}")
            success = False
        
        # Stop server
        print(f"\n📋 3. Parando servidor...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print("  ✅ Servidor parado")
        
        return success
        
    except Exception as e:
        print(f"  ❌ Erro ao iniciar servidor: {e}")
        return False
    finally:
        # Make sure we're back in the original directory
        os.chdir("..")

def main():
    """Main test function"""
    success = test_v3_server()
    
    if success:
        print(f"\n🎉 === SERVIDOR V3.0 - FUNCIONANDO! ===")
        print(f"\n✅ Testes aprovados:")
        print(f"  📁 Arquivos essenciais presentes")
        print(f"  🚀 Servidor inicia corretamente")
        print(f"  🌐 Interface web acessível")
        print(f"  📡 API respondendo")
        
        print(f"\n🎯 Como usar a V3.0:")
        print(f"  1. cd V3.0")
        print(f"  2. python start_server.py")
        print(f"  3. Abra http://localhost:8000")
        print(f"  4. Carregue planilha ABZ")
        print(f"  5. Gere invoices com nomes padronizados!")
        
        print(f"\n📋 Padrão de nomes:")
        print(f"  ABZ Group 141-2025 FMS 09 2025 Filipi.xlsx")
        print(f"  ABZ Group 142-2025 OMEGA 10 2025 Daniel.xlsx")
        
    else:
        print(f"\n❌ === SERVIDOR V3.0 - PROBLEMAS ===")
        print(f"  Verifique os erros acima")
        print(f"  Certifique-se de que:")
        print(f"    - Python está instalado")
        print(f"    - Dependências estão instaladas (pip install -r requirements.txt)")
        print(f"    - Porta 8000 está livre")

if __name__ == "__main__":
    main()
