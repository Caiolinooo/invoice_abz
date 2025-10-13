#!/usr/bin/env python3
"""
Script para criar uma nova sessão com a planilha correta
"""

import requests
import json
from pathlib import Path

def create_correct_session():
    """Cria uma nova sessão com a planilha correta"""
    
    correct_abz_path = "DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx"
    
    print("🔧 CRIANDO NOVA SESSÃO COM PLANILHA CORRETA")
    print("=" * 80)
    print(f"📄 Arquivo: {correct_abz_path}")
    
    if not Path(correct_abz_path).exists():
        print(f"❌ Arquivo não encontrado: {correct_abz_path}")
        return
    
    try:
        # Fazer upload da planilha correta
        url = "http://127.0.0.1:8000/api/import"
        
        with open(correct_abz_path, 'rb') as f:
            files = {'abz': (Path(correct_abz_path).name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print(f"🌐 Fazendo upload para: {url}")
            response = requests.post(url, files=files)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            employees = data.get("employees", [])
            
            print(f"✅ Nova sessão criada: {session_id}")
            print(f"👥 Funcionários encontrados ({len(employees)}):")
            for emp in employees:
                print(f"   - {emp}")
            
            # Testar preview da nova sessão
            print(f"\n🔍 TESTANDO PREVIEW DA NOVA SESSÃO:")
            preview_url = f"http://127.0.0.1:8000/api/preview?session_id={session_id}"
            preview_response = requests.get(preview_url)
            
            if preview_response.status_code == 200:
                preview_data = preview_response.json()
                preview = preview_data.get("preview", {})
                
                print(f"✅ Preview carregado com {len(preview)} funcionários")
                
                # Mostrar alguns exemplos
                for name, employee_data in list(preview.items())[:5]:
                    print(f"\n👤 {name}")
                    items = employee_data.get("items", [])
                    for item in items:
                        desc = item.get("description", "")
                        unit_price = item.get("unit_price")
                        quantity = item.get("quantity")
                        final = item.get("final", 0)
                        
                        if unit_price is not None and quantity is not None:
                            print(f"   🔧 {desc}")
                            print(f"      Unit: £{unit_price}, Qty: {quantity}, Final: £{final}")
                        else:
                            print(f"   ➕ {desc}: £{final}")
                
                print(f"\n🎯 NOVA SESSÃO CRIADA COM SUCESSO!")
                print(f"🌐 URL para acessar: http://127.0.0.1:8000/ui/?session={session_id}")
                
            else:
                print(f"❌ Erro ao carregar preview: {preview_response.status_code}")
                
        else:
            print(f"❌ Erro no upload: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    create_correct_session()
