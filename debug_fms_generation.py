#!/usr/bin/env python3
"""
Debug FMS invoice generation
"""
import sys
sys.path.append('app')

import asyncio
from pathlib import Path
import json
from api.server import GenerateRequest, api_generate_pdf

async def debug_fms_generation():
    """Debug the FMS invoice generation issue"""
    print("🔍 Debugando geração de invoices FMS...")
    
    # Use the session ID from the screenshot
    session_id = '54e2a1574b774e3f8ef5ff4afa1a3863'
    session_dir = Path(f"out/sessions/{session_id}")
    
    print(f"📁 Verificando sessão: {session_id}")
    
    if not session_dir.exists():
        print("❌ Diretório da sessão não existe")
        return False
    
    # Check session files
    meta_file = session_dir / "meta.json"
    if not meta_file.exists():
        print("❌ Arquivo meta.json não encontrado")
        return False
    
    # Read meta.json
    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    print(f"📋 Meta.json carregado:")
    print(f"  - ABZ file: {meta.get('abz', 'N/A')}")
    print(f"  - Employees: {len(meta.get('employees', []))}")
    
    # Check if ABZ file exists
    abz_file = session_dir / meta.get('abz', '')
    if not abz_file.exists():
        print(f"❌ Arquivo ABZ não encontrado: {abz_file}")
        return False
    
    print(f"✅ Arquivo ABZ encontrado: {abz_file.name}")
    
    # Check invoice templates in the ABZ file
    from openpyxl import load_workbook
    try:
        wb = load_workbook(abz_file, read_only=True)
        sheets = wb.sheetnames
        invoice_sheets = [s for s in sheets if s.lower().strip().endswith('_invoice')]
        
        print(f"📊 Sheets na planilha: {len(sheets)}")
        print(f"📄 Invoice templates: {len(invoice_sheets)}")
        
        if invoice_sheets:
            print("  Templates encontrados:")
            for sheet in invoice_sheets:
                print(f"    - {sheet}")
        else:
            print("  ❌ Nenhum template de invoice encontrado!")
        
        wb.close()
        
    except Exception as e:
        print(f"❌ Erro ao ler planilha ABZ: {e}")
        return False
    
    # Test the API call
    print(f"\n🧪 Testando geração de invoices...")
    
    req = GenerateRequest(
        session_id=session_id,
        invoice_date='12/09/2025',
        invoice_no='121',
        call_off='FMS-001'
    )
    
    try:
        result = await api_generate_pdf(req)
        
        files = result.get('files', [])
        warnings = result.get('warnings', [])
        
        print(f"\n✅ API executada!")
        print(f"📄 Arquivos gerados: {len(files)}")
        print(f"⚠️  Warnings: {len(warnings)}")
        
        if warnings:
            print("\n⚠️  Warnings encontrados:")
            for warning in warnings:
                print(f"  - {warning}")
        
        if files:
            print("\n📋 Arquivos gerados:")
            for file in files:
                print(f"  - {file['name']}")
            
            # Check if files actually exist
            xlsx_dir = session_dir / "xlsx"
            if xlsx_dir.exists():
                actual_files = list(xlsx_dir.glob("*.xlsx"))
                print(f"\n📁 Arquivos físicos: {len(actual_files)}")
                for file in actual_files:
                    print(f"  - {file.name} ({file.stat().st_size} bytes)")
            else:
                print("\n❌ Diretório xlsx não foi criado")
            
            return len(files) > 0 and len(warnings) == 0
        else:
            print("❌ Nenhum arquivo foi gerado")
            return False
            
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Debug da Geração FMS ===\n")
    
    success = asyncio.run(debug_fms_generation())
    
    if success:
        print("\n🎉 Geração funcionando corretamente!")
    else:
        print("\n❌ Problema identificado na geração!")
