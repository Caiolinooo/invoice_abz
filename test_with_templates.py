#!/usr/bin/env python3

import requests
import json
from pathlib import Path

def test_with_templates():
    """Teste com planilha que TEM templates (compatibilidade)"""
    
    base = 'http://127.0.0.1:8001'
    
    # Upload planilha COM templates
    file_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
    if not file_path.exists():
        print('ERROR: Arquivo original não encontrado')
        return False
    
    print(f'=== TESTE COM TEMPLATES ORIGINAIS ===')
    print(f'Enviando planilha: {file_path}')
    
    with open(file_path, 'rb') as f:
        files = {'abz': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        r = requests.post(f'{base}/api/import', files=files)
    
    if r.status_code != 200:
        print(f'ERROR no upload: {r.status_code}')
        print(r.text[:500])
        return False
    
    data = r.json()
    session_id = data['session_id']
    print(f'✅ Upload OK, session: {session_id}')
    print(f'📊 Funcionários encontrados: {len(data.get("employees", []))}')
    
    # Testar geração
    gen_req = {
        'session_id': session_id,
        'invoice_date': '15/09/2025',
        'invoice_no': '200',
        'call_off': 'TESTE-TEMPLATES',
        'overrides': {}
    }
    
    print('\n📋 Gerando invoices com templates ABZ...')
    r2 = requests.post(f'{base}/api/generate/pdf', json=gen_req)
    
    if r2.status_code != 200:
        print(f'ERROR na geração: {r2.status_code}')
        print(r2.text[:500])
        return False
    
    result = r2.json()
    print(f'✅ Geração concluída!')
    print(f'📄 Invoices geradas: {len(result.get("invoices", []))}')
    print(f'⚠️ Warnings: {len(result.get("warnings", []))}')
    
    if result.get('invoices'):
        print('\n📋 Invoices geradas:')
        for inv in result['invoices'][:3]:  # Mostrar apenas 3
            name = inv.get("employee_name", "Unknown")
            xlsx_url = inv.get("url_xlsx", "No URL")
            print(f'  - {name}: {xlsx_url}')
        
        return True
    else:
        print('\n❌ NENHUMA INVOICE GERADA!')
        return False

if __name__ == "__main__":
    success = test_with_templates()
    if success:
        print("\n✅ COMPATIBILIDADE MANTIDA!")
        print("Sistema ainda funciona com templates ABZ originais.")
    else:
        print("\n❌ Problema de compatibilidade.")
        exit(1)
