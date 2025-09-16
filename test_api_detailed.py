#!/usr/bin/env python3

import requests
import json
from pathlib import Path

def test_api_detailed():
    """Teste detalhado da API"""
    
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
        print(r.text[:500])
        return False
    
    data = r.json()
    session_id = data['session_id']
    print(f'OK Upload, session: {session_id}')
    print(f'Funcionários encontrados: {len(data.get("employees", []))}')
    
    # Listar funcionários
    if data.get('employees'):
        print('Funcionários:')
        for emp in data['employees'][:5]:
            print(f'  - {emp}')
    
    # Verificar preview
    print('\nVerificando preview...')
    r_preview = requests.get(f'{base}/api/preview/{session_id}')
    if r_preview.status_code == 200:
        preview_data = r_preview.json()
        print(f'Preview OK: {len(preview_data.get("employees", []))} funcionários')
        
        # Mostrar primeiro funcionário
        if preview_data.get('employees'):
            first_emp = preview_data['employees'][0]
            print(f'Primeiro funcionário: {first_emp.get("name", "Unknown")}')
            print(f'  - Linhas de serviço: {len(first_emp.get("line_items", []))}')
    else:
        print(f'ERROR no preview: {r_preview.status_code}')
        print(r_preview.text[:200])
    
    # Testar geração
    gen_req = {
        'session_id': session_id,
        'invoice_date': '15/09/2025',
        'invoice_no': '1',
        'call_off': '',
        'overrides': {}
    }
    
    print('\nGerando invoices...')
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
        for w in result['warnings'][:5]:
            print(f'  - {w}')
    
    if result.get('invoices'):
        print('Invoices geradas:')
        for inv in result['invoices'][:3]:
            print(f'  - {inv.get("employee_name", "Unknown")}: {inv.get("url_xlsx", "No URL")}')
        return True
    else:
        print('NENHUMA INVOICE GERADA!')
        
        # Verificar se há dados na sessão
        session_dir = Path(f'out/sessions/{session_id}')
        if session_dir.exists():
            print(f'Diretório da sessão existe: {session_dir}')
            print(f'Conteúdo: {list(session_dir.iterdir())}')
        else:
            print(f'Diretório da sessão não existe: {session_dir}')
        
        return False

if __name__ == "__main__":
    success = test_api_detailed()
    if success:
        print("\nSUCCESS: API funciona com template padrão!")
    else:
        print("\nERROR: Teste da API falhou.")
        exit(1)
