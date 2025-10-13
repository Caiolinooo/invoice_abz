#!/usr/bin/env python3
"""
Simple server to test if the system is working
"""
import sys
sys.path.append('app')

from pathlib import Path
import json
import asyncio
from api.server import GenerateRequest, api_generate_pdf

def test_invoice_generation():
    """Test invoice generation directly"""
    print("🧪 Testando geração de invoices...")
    
    session_id = 'c4c3fe2ff1e64cdb8b126c5c80744369'
    
    # Create the request object
    req = GenerateRequest(
        session_id=session_id,
        invoice_date='11/09/2025',
        invoice_no='108',
        call_off='P25-122'
    )
    
    async def run_test():
        try:
            result = await api_generate_pdf(req)
            return result
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # Run the async function
    result = asyncio.run(run_test())
    
    if result:
        files = result.get('files', [])
        warnings = result.get('warnings', [])
        
        print(f"✅ Geração concluída!")
        print(f"📄 Arquivos gerados: {len(files)}")
        print(f"⚠️  Warnings: {len(warnings)}")
        
        if files:
            print("\n📋 Arquivos gerados:")
            for file in files:
                print(f"  - {file['name']}")
        
        if warnings:
            print("\n⚠️  Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        return True
    else:
        print("❌ Falha na geração")
        return False

if __name__ == "__main__":
    print("🚀 Sistema de Geração de Invoices")
    print("=" * 50)
    
    success = test_invoice_generation()
    
    if success:
        print("\n🎉 SISTEMA FUNCIONANDO CORRETAMENTE!")
        print("\n📁 Os arquivos XLSX foram gerados em:")
        print("   out/sessions/c4c3fe2ff1e64cdb8b126c5c80744369/xlsx/")
        print("\n💡 Para usar a interface web, execute:")
        print("   uvicorn app.api.server:app --host 0.0.0.0 --port 8000")
        print("   Depois acesse: http://localhost:8000/ui/")
    else:
        print("\n❌ SISTEMA COM PROBLEMAS!")
