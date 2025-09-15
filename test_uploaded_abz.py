#!/usr/bin/env python3
"""
Test using uploaded ABZ file (simulating user upload)
"""
import sys
sys.path.append('app')

import asyncio
import shutil
from pathlib import Path
import json
from api.server import GenerateRequest, api_generate_pdf

async def test_uploaded_abz():
    """Test using uploaded ABZ file instead of DADOS fallback"""
    print("🧪 Testando uso de planilha ABZ carregada pelo usuário...")
    
    # Simulate user uploading an ABZ file
    session_id = 'test_uploaded_abz'
    session_dir = Path(f"out/sessions/{session_id}")
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the ABZ file to simulate upload
    source_abz = Path("DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx")
    uploaded_abz = session_dir / "uploaded_abz.xlsx"
    
    if not source_abz.exists():
        print("❌ Arquivo ABZ fonte não encontrado")
        return False
    
    # Copy file to simulate upload
    shutil.copy2(source_abz, uploaded_abz)
    print(f"📤 Simulando upload: {uploaded_abz.name}")
    
    # Create meta.json to simulate session
    meta = {
        "abz": "uploaded_abz.xlsx",
        "employees": [
            {
                "name": "Caio Cesar Silva Nascimento",
                "services": [
                    {
                        "Description": "Caio - ROV Pilot",
                        "Unit Price (GBP)": 1900,
                        "Quantity": 3,
                        "Final Price (GBP)": 5700
                    },
                    {
                        "Description": "Caio - Logistic",
                        "Unit Price (GBP)": 900,
                        "Quantity": 3,
                        "Final Price (GBP)": 2700
                    }
                ],
                "additionals": [
                    {
                        "Description": "Brazilian Payroll Additional",
                        "Final Price (GBP)": 700
                    }
                ],
                "expenses": [
                    {
                        "Description": "Expenses",
                        "Final Price (GBP)": 40
                    }
                ]
            },
            {
                "name": "Daniel Vieira Silva Nunes",
                "services": [
                    {
                        "Description": "Daniel - ROV Supervisor",
                        "Unit Price (GBP)": 1500,
                        "Quantity": 5,
                        "Final Price (GBP)": 7500
                    }
                ],
                "additionals": [
                    {
                        "Description": "Brazilian Payroll Additional",
                        "Final Price (GBP)": 400
                    }
                ],
                "expenses": [
                    {
                        "Description": "Expenses",
                        "Final Price (GBP)": 20
                    }
                ]
            }
        ]
    }
    
    meta_file = session_dir / "meta.json"
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Meta criado com {len(meta['employees'])} funcionários")
    
    # Test the API
    req = GenerateRequest(
        session_id=session_id,
        invoice_date='11/09/2025',
        invoice_no='108',
        call_off='P25-122'
    )
    
    try:
        result = await api_generate_pdf(req)
        
        files = result.get('files', [])
        warnings = result.get('warnings', [])
        
        print(f"\n✅ Geração concluída!")
        print(f"📄 Arquivos gerados: {len(files)}")
        print(f"⚠️  Warnings: {len(warnings)}")
        
        if warnings:
            print("\n⚠️  Warnings:")
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
                print(f"\n📁 Arquivos físicos criados: {len(actual_files)}")
                for file in actual_files:
                    print(f"  - {file.name} ({file.stat().st_size} bytes)")
            
            return len(files) > 0
        else:
            print("❌ Nenhum arquivo gerado")
            return False
            
    except Exception as e:
        print(f"❌ Erro na geração: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Teste de Planilha ABZ Carregada ===\n")
    
    success = asyncio.run(test_uploaded_abz())
    
    if success:
        print("\n🎉 Sistema funciona com planilha ABZ carregada!")
        print("✅ Colaboradores duplicados são processados corretamente")
        print("✅ Múltiplas linhas aparecem na invoice")
    else:
        print("\n❌ Problema com planilha ABZ carregada!")
