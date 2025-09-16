#!/usr/bin/env python3

import requests
import json
from pathlib import Path
import time

def test_final_api():
    """Teste final da API com template padrão"""
    
    base = 'http://127.0.0.1:8001'
    
    # Upload planilha sem templates
    file_path = Path('DADOS/ABZ_TEST_NO_TEMPLATES.xlsx')
    if not file_path.exists():
        print('ERROR: Arquivo de teste não encontrado')
        return False
    
    print(f'=== TESTE FINAL DA API ===')
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
        'invoice_no': '100',
        'call_off': 'TESTE-FINAL',
        'overrides': {}
    }
    
    print('\n🔧 Gerando invoices com template padrão...')
    r2 = requests.post(f'{base}/api/generate/pdf', json=gen_req)
    
    if r2.status_code != 200:
        print(f'ERROR na geração: {r2.status_code}')
        print(r2.text[:500])
        return False
    
    result = r2.json()
    print(f'✅ Geração concluída!')
    print(f'📄 Invoices geradas: {len(result.get("invoices", []))}')
    print(f'⚠️ Warnings: {len(result.get("warnings", []))}')
    
    if result.get('warnings'):
        print('\nWarnings:')
        for w in result['warnings'][:3]:
            print(f'  - {w}')
    
    if result.get('invoices'):
        print('\n📋 Invoices geradas:')
        for inv in result['invoices']:
            name = inv.get("employee_name", "Unknown")
            xlsx_url = inv.get("url_xlsx", "No URL")
            pdf_url = inv.get("url_pdf", "No PDF")
            print(f'  - {name}:')
            print(f'    XLSX: {xlsx_url}')
            print(f'    PDF:  {pdf_url}')
        
        # Verificar se arquivos existem
        print('\n🔍 Verificando arquivos gerados:')
        session_dir = Path(f'out/sessions/{session_id}')
        xlsx_dir = session_dir / 'xlsx'
        pdf_dir = session_dir / 'pdf'
        
        if xlsx_dir.exists():
            xlsx_files = list(xlsx_dir.glob('*.xlsx'))
            print(f'  📄 XLSX: {len(xlsx_files)} arquivos')
            for f in xlsx_files[:3]:
                print(f'    - {f.name} ({f.stat().st_size} bytes)')
        
        if pdf_dir.exists():
            pdf_files = list(pdf_dir.glob('*.pdf'))
            print(f'  📄 PDF: {len(pdf_files)} arquivos')
            for f in pdf_files[:3]:
                print(f'    - {f.name} ({f.stat().st_size} bytes)')
        
        return len(result.get('invoices', [])) > 0
    else:
        print('\n❌ NENHUMA INVOICE GERADA!')
        return False

if __name__ == "__main__":
    success = test_final_api()
    if success:
        print("\n🎉 SUCESSO TOTAL!")
        print("✅ Sistema funciona sem templates na planilha ABZ")
        print("✅ Template padrão implementado com sucesso")
        print("✅ API independente de templates funcionando")
        print("\n🚀 PROBLEMA RESOLVIDO!")
    else:
        print("\n❌ Teste final falhou.")
        exit(1)
