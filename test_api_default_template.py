#!/usr/bin/env python3

import requests
import json
from pathlib import Path

def test_api_with_default_template():
    """Testa a API com planilha sem templates"""
    
    base = 'http://127.0.0.1:8001'
    
    # Upload planilha sem templates
    file_path = Path('DADOS/ABZ_TEST_NO_TEMPLATES.xlsx')
    if not file_path.exists():
        print('ERROR: Arquivo de teste não encontrado')
        return False
    
    print(f'Enviando planilha: {file_path}')
    
    with open(file_path, 'rb') as f:
        files = {'abz': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        r = requests.post(f'{base}/api/import', files=files)
    
    if r.status_code != 200:
        print(f'ERROR no upload: {r.status_code}')
        print(r.text[:200])
        return False
    
    data = r.json()
    session_id = data['session_id']
    print(f'OK Upload, session: {session_id}')
    print(f'Funcionários encontrados: {len(data.get("employees", []))}')
    
    # Testar geração com template padrão
    gen_req = {
        'session_id': session_id,
        'invoice_date': '15/09/2025',
        'invoice_no': '1',
        'call_off': '',  # Vazio para testar
        'overrides': {}
    }
    
    print('Gerando invoices com template padrão...')
    r2 = requests.post(f'{base}/api/generate/pdf', json=gen_req)
    
    if r2.status_code != 200:
        print(f'ERROR na geração: {r2.status_code}')
        print(r2.text[:500])
        return False
    
    result = r2.json()
    print(f'OK Geração!')
    print(f'Invoices geradas: {len(result.get("invoices", []))}')
    print(f'Warnings: {len(result.get("warnings", []))}')
    
    if result.get('warnings'):
        print('Warnings:')
        for w in result['warnings'][:5]:  # Mostrar apenas 5 primeiros
            print(f'  - {w}')
    
    if result.get('invoices'):
        print('Invoices geradas:')
        for inv in result['invoices'][:3]:  # Mostrar apenas 3 primeiras
            print(f'  - {inv.get("employee_name", "Unknown")}: {inv.get("url_xlsx", "No URL")}')
    
    return True

if __name__ == "__main__":
    success = test_api_with_default_template()
    if success:
        print("\nSUCCESS: API funciona com template padrão!")
        print("O sistema agora é independente de templates na planilha ABZ.")
    else:
        print("\nERROR: Teste da API falhou.")
        exit(1)
