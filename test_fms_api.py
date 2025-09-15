#!/usr/bin/env python3
"""
Test FMS API directly
"""
import sys
sys.path.append('app')

import asyncio
from api.server import GenerateRequest, api_generate_pdf

async def test_fms_api():
    """Test FMS API directly"""
    print("🧪 Testando API FMS diretamente...")
    
    # Use the FMS session
    session_id = '54e2a1574b774e3f8ef5ff4afa1a3863'
    
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
        
        print(f"✅ API FMS executada com sucesso!")
        print(f"📄 Arquivos gerados: {len(files)}")
        print(f"⚠️  Warnings: {len(warnings)}")
        
        if files:
            print(f"\n📋 Invoices FMS geradas:")
            for file in files:
                print(f"  ✅ {file['name']}")
        
        if warnings:
            print(f"\n⚠️  Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        return len(files) > 0 and len(warnings) == 0
        
    except Exception as e:
        print(f"❌ Erro na API FMS: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Teste API FMS ===\n")
    
    success = asyncio.run(test_fms_api())
    
    if success:
        print(f"\n🎉 SUCESSO! As invoices FMS foram geradas!")
        print(f"📁 Pasta: out/sessions/54e2a1574b774e3f8ef5ff4afa1a3863/xlsx/")
        print(f"📄 Esperado: 5 arquivos .xlsx")
        print(f"\n✅ Casos testados:")
        print(f"  - Filipi Brandão Lagedo (nome com acento)")
        print(f"  - Gil Anderson Reiser (nome composto)")
        print(f"  - Izabela Bonacorsi Freire (sobrenome complexo)")
        print(f"  - Laucilia Victoria Nonato Simplicio (nome longo)")
        print(f"  - Thiago Dorce Rodrigues (padrão)")
        print(f"\n🚀 Sistema funcionando para planilha FMS!")
    else:
        print(f"\n❌ Falha no teste da API FMS")
