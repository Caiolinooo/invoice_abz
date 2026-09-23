#!/usr/bin/env python3
"""
Test invoice generation with standardized filenames
"""
import sys
import asyncio
import os
from pathlib import Path

# Change to dev directory and add app to path
os.chdir('dev')
sys.path.append('app')

from api.server import GenerateRequest, api_generate_pdf

async def test_standardized_generation():
    """Test invoice generation with standardized filenames"""
    print("🧪 Testando geração com nomes padronizados...")
    
    # Use the existing FMS session
    session_id = '54e2a1574b774e3f8ef5ff4afa1a3863'
    
    req = GenerateRequest(
        session_id=session_id,
        invoice_date='12/09/2025',
        invoice_no='141',
        call_off='FMS-001'
    )
    
    try:
        result = await api_generate_pdf(req)
        
        files = result.get('files', [])
        warnings = result.get('warnings', [])
        
        print(f"✅ API executada com sucesso!")
        print(f"📄 Arquivos gerados: {len(files)}")
        print(f"⚠️  Warnings: {len(warnings)}")
        
        if files:
            print(f"\n📋 Invoices geradas com nomes padronizados:")
            for file in files:
                file_path = Path(file['xlsx'])
                filename = file_path.name
                print(f"  ✅ {file['name']}")
                print(f"     📁 {filename}")
                
                # Check if filename follows the new pattern
                if filename.startswith("ABZ Group"):
                    print(f"     🎯 Padrão correto!")
                else:
                    print(f"     ⚠️  Padrão antigo")
                print()
        
        if warnings:
            print(f"\n⚠️  Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        return len(files) > 0 and len(warnings) == 0
        
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_generated_files():
    """Check the generated files in the session directory"""
    session_dir = Path("out/sessions/54e2a1574b774e3f8ef5ff4afa1a3863/xlsx")
    
    if not session_dir.exists():
        print(f"📁 Diretório não encontrado: {session_dir}")
        return
    
    print(f"\n📁 Verificando arquivos em: {session_dir}")
    
    xlsx_files = list(session_dir.glob("*.xlsx"))
    
    if not xlsx_files:
        print("  ❌ Nenhum arquivo .xlsx encontrado")
        return
    
    print(f"  📄 {len(xlsx_files)} arquivos encontrados:")
    
    standardized_count = 0
    legacy_count = 0
    
    for file in xlsx_files:
        filename = file.name
        size = file.stat().st_size
        
        if filename.startswith("ABZ Group"):
            print(f"  🎯 {filename} ({size} bytes) - PADRONIZADO")
            standardized_count += 1
        else:
            print(f"  📄 {filename} ({size} bytes) - legado")
            legacy_count += 1
    
    print(f"\n📊 Resumo:")
    print(f"  🎯 Padronizados: {standardized_count}")
    print(f"  📄 Legados: {legacy_count}")
    
    if standardized_count > 0:
        print(f"  ✅ Padronização funcionando!")
    else:
        print(f"  ⚠️  Nenhum arquivo padronizado encontrado")

if __name__ == "__main__":
    print("=== Teste de Geração com Nomes Padronizados ===\n")
    
    # First check existing files
    asyncio.run(check_generated_files())
    
    print("\n" + "="*50)
    print("Gerando novas invoices...")
    
    success = asyncio.run(test_standardized_generation())
    
    if success:
        print(f"\n🎉 SUCESSO! Invoices geradas com nomes padronizados!")
        
        # Check files again
        print("\n" + "="*50)
        print("Verificando arquivos após geração...")
        asyncio.run(check_generated_files())
        
        print(f"\n✅ Padrão implementado:")
        print(f"   ABZ Group {{invoice_no}}-{{year}} {{client}} {{month}} {{year}} {{first_name}}.xlsx")
        print(f"\n📋 Exemplo esperado:")
        print(f"   ABZ Group 141-2025 FMS 09 2025 Filipi.xlsx")
        print(f"   ABZ Group 141-2025 FMS 09 2025 Gil.xlsx")
        
    else:
        print(f"\n❌ Falha na geração com nomes padronizados")
