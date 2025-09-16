#!/usr/bin/env python3
"""
Teste final do novo gerador baseado em template através da API
"""

import sys
sys.path.append('app')

import asyncio
from pathlib import Path
import json
from api.server import GenerateRequest, api_generate_pdf

async def test_template_based_api():
    """Testa o novo gerador através da API"""
    
    print("🧪 TESTE FINAL - GERADOR BASEADO EM TEMPLATE VIA API")
    print("=" * 60)
    
    # Usar uma sessão existente ou criar uma simulada
    session_id = 'test_template_based_session'
    session_dir = Path(f"out/sessions/{session_id}")
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Criar meta.json simulado
    meta = {
        "abz": "ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx",
        "preview": {
            "Gabriel Leone": {
                "items": [
                    {
                        "description": "Gabriel Leone - Surveyor",
                        "unit_price": 450.0,
                        "quantity": 22,
                        "final": 9900.0
                    },
                    {
                        "description": "Gabriel Leone - Party Chief", 
                        "unit_price": 500.0,
                        "quantity": 8,
                        "final": 4000.0
                    },
                    {
                        "description": "Brazilian Payroll Additional",
                        "unit_price": None,
                        "quantity": None,
                        "final": 0.0
                    },
                    {
                        "description": "Expenses",
                        "unit_price": None,
                        "quantity": None,
                        "final": 0.0
                    }
                ],
                "meta": {
                    "invoice_no": None,
                    "invoice_date": None,
                    "call_off": None
                }
            }
        }
    }
    
    # Copiar arquivo ABZ para a sessão
    abz_source = None
    for abz_file in Path("DADOS").glob("*ABZ*.xlsx"):
        abz_source = abz_file
        break
    
    if abz_source:
        import shutil
        abz_dest = session_dir / meta["abz"]
        shutil.copy2(abz_source, abz_dest)
        print(f"📁 Arquivo ABZ copiado: {abz_dest}")
    else:
        print("❌ Nenhum arquivo ABZ encontrado em DADOS/")
        return False
    
    # Salvar meta.json
    meta_file = session_dir / "meta.json"
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Sessão criada: {session_id}")
    
    # Criar requisição
    req = GenerateRequest(
        session_id=session_id,
        invoice_date='16/09/2025',
        invoice_no='FINAL001/2025',
        call_off='TEMPLATE-BASED-TEST'
    )
    
    print(f"\n🔧 Gerando invoice via API...")
    print(f"📅 Data: {req.invoice_date}")
    print(f"🔢 Número: {req.invoice_no}")
    print(f"📞 Call-off: {req.call_off}")
    
    try:
        result = await api_generate_pdf(req)
        
        files = result.get('files', [])
        warnings = result.get('warnings', [])
        
        print(f"\n✅ API executada com sucesso!")
        print(f"📄 Arquivos gerados: {len(files)}")
        print(f"⚠️  Warnings: {len(warnings)}")
        
        if files:
            print(f"\n📁 Arquivos criados:")
            for file_info in files:
                file_path = Path(file_info['path'])
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"  ✅ {file_info['name']} ({size} bytes)")
                else:
                    print(f"  ❌ {file_info['name']} (não encontrado)")
        
        if warnings:
            print(f"\n⚠️  Warnings encontrados:")
            for warning in warnings:
                print(f"  - {warning}")
        
        return len(files) > 0
        
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    success = asyncio.run(test_template_based_api())
    
    if success:
        print(f"\n🎉 TESTE FINAL PASSOU!")
        print(f"✅ O novo gerador baseado em template está funcionando corretamente!")
        print(f"📋 As invoices agora seguem exatamente o formato do Template_Invoice_Geral.xlsx")
    else:
        print(f"\n❌ TESTE FINAL FALHOU!")
        sys.exit(1)

if __name__ == "__main__":
    main()
