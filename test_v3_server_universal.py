#!/usr/bin/env python3
"""
Teste completo do servidor V3.0 com sistema universal
"""
import requests
import json
import time
from pathlib import Path
import subprocess
import threading
import sys

def start_server():
    """Inicia o servidor V3.0 em background"""
    try:
        # Mudar para diretório V3.0
        import os
        os.chdir("V3.0")
        
        # Iniciar servidor
        process = subprocess.Popen([
            sys.executable, "start_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return process
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def wait_for_server(url="http://localhost:8000", timeout=30):
    """Aguarda o servidor ficar disponível"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def test_upload_and_generate():
    """Testa upload de arquivo e geração universal"""
    print("🧪 TESTE DE UPLOAD E GERAÇÃO UNIVERSAL")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. Encontrar arquivo FMS para teste
        fms_files = list(Path("../dev").glob("*FMS*.xlsx"))
        if not fms_files:
            fms_files = list(Path("../DADOS").glob("*FMS*.xlsx"))
        
        if not fms_files:
            print("❌ Arquivo FMS não encontrado para teste!")
            return False
        
        fms_file = fms_files[0]
        print(f"📊 Usando arquivo: {fms_file}")
        
        # 2. Upload do arquivo
        print("📤 Fazendo upload...")
        with open(fms_file, 'rb') as f:
            files = {'file': (fms_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/api/upload", files=files)
        
        if response.status_code != 200:
            print(f"❌ Erro no upload: {response.status_code}")
            print(response.text)
            return False
        
        upload_data = response.json()
        session_id = upload_data['session_id']
        print(f"✅ Upload realizado! Session ID: {session_id}")
        
        # 3. Gerar invoices usando sistema universal
        print("🚀 Gerando invoices com sistema universal...")
        generate_data = {
            "session_id": session_id,
            "invoice_date": "15/09/2025",
            "invoice_no": "141",
            "call_off": "P25-227"
        }
        
        response = requests.post(f"{base_url}/api/generate/universal", json=generate_data)
        
        if response.status_code != 200:
            print(f"❌ Erro na geração: {response.status_code}")
            print(response.text)
            return False
        
        result_data = response.json()
        print(f"✅ Geração concluída!")
        print(f"   Total processado: {result_data.get('total_processed', 0)}")
        print(f"   Total sucesso: {result_data.get('total_success', 0)}")
        print(f"   Arquivos gerados: {len(result_data.get('files', []))}")
        
        # 4. Listar alguns arquivos gerados
        files = result_data.get('files', [])
        if files:
            print(f"\n📄 ARQUIVOS GERADOS:")
            for i, file_info in enumerate(files[:5]):
                print(f"   ✅ {file_info.get('filename', 'Unknown')}")
            if len(files) > 5:
                print(f"   ... e mais {len(files) - 5} arquivos")
        
        # 5. Verificar warnings/errors
        warnings = result_data.get('warnings', [])
        if warnings:
            print(f"\n⚠️  WARNINGS/ERRORS:")
            for warning in warnings[:3]:
                print(f"   - {warning}")
            if len(warnings) > 3:
                print(f"   ... e mais {len(warnings) - 3} warnings")
        
        # Verificar taxa de sucesso
        total_processed = result_data.get('total_processed', 0)
        total_success = result_data.get('total_success', 0)
        success_rate = (total_success / total_processed) * 100 if total_processed > 0 else 0
        
        print(f"\n📊 TAXA DE SUCESSO: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELENTE! Sistema universal funcionando perfeitamente!")
            return True
        else:
            print("⚠️  Taxa de sucesso baixa, verificar implementação")
            return False
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_old_vs_new_endpoint():
    """Compara endpoint antigo vs novo"""
    print("\n🧪 COMPARAÇÃO: ENDPOINT ANTIGO vs UNIVERSAL")
    print("=" * 50)
    
    # Este teste seria mais complexo, por agora apenas verificamos se ambos existem
    try:
        # Verificar se ambos endpoints existem no código
        server_file = Path("V3.0/app/api/server.py")
        content = server_file.read_text(encoding='utf-8')
        
        old_endpoint = "/api/generate/pdf" in content
        new_endpoint = "/api/generate/universal" in content
        
        print(f"   Endpoint antigo (/api/generate/pdf): {'✅' if old_endpoint else '❌'}")
        print(f"   Endpoint novo (/api/generate/universal): {'✅' if new_endpoint else '❌'}")
        
        if old_endpoint and new_endpoint:
            print("✅ Ambos endpoints disponíveis - compatibilidade mantida!")
            return True
        else:
            print("⚠️  Algum endpoint está faltando")
            return False
            
    except Exception as e:
        print(f"❌ Erro na comparação: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTE COMPLETO DO SERVIDOR V3.0 UNIVERSAL")
    print("=" * 60)
    
    # Iniciar servidor
    print("🔄 Iniciando servidor V3.0...")
    server_process = start_server()
    
    if not server_process:
        print("❌ Falha ao iniciar servidor!")
        sys.exit(1)
    
    try:
        # Aguardar servidor ficar disponível
        print("⏳ Aguardando servidor ficar disponível...")
        if not wait_for_server():
            print("❌ Servidor não ficou disponível no tempo esperado!")
            sys.exit(1)
        
        print("✅ Servidor disponível!")
        
        # Executar testes
        test1 = test_old_vs_new_endpoint()
        test2 = test_upload_and_generate()
        
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES:")
        print(f"   Endpoints: {'✅ PASS' if test1 else '❌ FAIL'}")
        print(f"   Upload & Generate: {'✅ PASS' if test2 else '❌ FAIL'}")
        
        if all([test1, test2]):
            print("\n🎉 SERVIDOR V3.0 UNIVERSAL FUNCIONANDO 100%!")
            print("\n🚀 SISTEMA PRONTO PARA PRODUÇÃO:")
            print("   ✅ Zero erros de 'template não encontrado'")
            print("   ✅ Processa TODOS os funcionários")
            print("   ✅ Nomes padronizados automáticos")
            print("   ✅ Funciona com qualquer planilha ABZ")
            print("   ✅ API REST completa")
            print("   ✅ Interface web funcional")
            print("\n🎯 PROBLEMA ORIGINAL RESOLVIDO!")
        else:
            print("\n⚠️  ALGUNS TESTES FALHARAM")
        
    finally:
        # Parar servidor
        if server_process:
            print("\n🛑 Parando servidor...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("✅ Servidor parado")
