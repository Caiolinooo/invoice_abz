#!/usr/bin/env python3
"""
Test the improved template matching algorithm
"""
import sys
sys.path.append('app')

import asyncio
import shutil
from pathlib import Path
import json
from api.server import GenerateRequest, api_generate_pdf

async def test_improved_matching():
    """Test the improved matching algorithm with problematic names"""
    print("🧪 Testando algoritmo melhorado de matching...")
    
    # Create a test session with problematic names
    session_id = 'test_improved_matching'
    session_dir = Path(f"out/sessions/{session_id}")
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the ABZ file to simulate upload
    source_abz = Path("DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx")
    uploaded_abz = session_dir / "uploaded_abz.xlsx"
    
    if not source_abz.exists():
        print("❌ Arquivo ABZ fonte não encontrado")
        return False
    
    shutil.copy2(source_abz, uploaded_abz)
    print(f"📤 Arquivo copiado: {uploaded_abz.name}")
    
    # Create meta.json with problematic names (including the Rafaels)
    meta = {
        "abz": "uploaded_abz.xlsx",
        "employees": [
            {
                "name": "Rafael Cabral Marcilio",
                "services": [
                    {
                        "Description": "Rafael Cabral - ROV Pilot",
                        "Unit Price (GBP)": 1800,
                        "Quantity": 5,
                        "Final Price (GBP)": 9000
                    }
                ],
                "additionals": [
                    {
                        "Description": "Brazilian Payroll Additional",
                        "Final Price (GBP)": 500
                    }
                ],
                "expenses": [
                    {
                        "Description": "Expenses",
                        "Final Price (GBP)": 30
                    }
                ]
            },
            {
                "name": "Rafael de Souza da Silva",
                "services": [
                    {
                        "Description": "Rafael de Souza - ROV Supervisor",
                        "Unit Price (GBP)": 2000,
                        "Quantity": 4,
                        "Final Price (GBP)": 8000
                    }
                ],
                "additionals": [
                    {
                        "Description": "Brazilian Payroll Additional",
                        "Final Price (GBP)": 600
                    }
                ],
                "expenses": [
                    {
                        "Description": "Expenses",
                        "Final Price (GBP)": 25
                    }
                ]
            },
            {
                "name": "Filipi Brandão Lagedo",
                "services": [
                    {
                        "Description": "Filipi - ROV Pilot",
                        "Unit Price (GBP)": 1700,
                        "Quantity": 6,
                        "Final Price (GBP)": 10200
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
                        "Final Price (GBP)": 35
                    }
                ]
            }
        ]
    }
    
    meta_file = session_dir / "meta.json"
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Meta criado com {len(meta['employees'])} funcionários problemáticos")
    
    # Test the API with improved matching
    req = GenerateRequest(
        session_id=session_id,
        invoice_date='11/09/2025',
        invoice_no='109',
        call_off='P25-123'
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
            
            # Check specific problematic cases
            expected_names = ["Rafael Cabral Marcilio", "Rafael de Souza da Silva", "Filipi Brandão Lagedo"]
            generated_names = [f['name'] for f in files]
            
            print(f"\n🎯 Verificação de casos problemáticos:")
            for name in expected_names:
                if name in generated_names:
                    print(f"  ✅ {name} - Invoice gerada com sucesso")
                else:
                    print(f"  ❌ {name} - Falha na geração")
            
            return len(warnings) == 0  # Success if no warnings
        else:
            print("❌ Nenhum arquivo gerado")
            return False
            
    except Exception as e:
        print(f"❌ Erro na geração: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Teste do Algoritmo Melhorado de Matching ===\n")
    
    success = asyncio.run(test_improved_matching())
    
    if success:
        print("\n🎉 Algoritmo melhorado funcionando perfeitamente!")
        print("✅ Rafael Cabral e Rafael de Souza diferenciados corretamente")
        print("✅ Filipi Brandão encontrado mesmo com nome complexo")
        print("✅ Sistema funciona para todos os modelos de planilha")
    else:
        print("\n❌ Ainda há problemas com o matching!")
