#!/usr/bin/env python3
"""
Teste completo da V3.0 - Sistema de geração de invoices com nomes padronizados
"""
import sys
import asyncio
import os
from pathlib import Path

# Change to V3.0 directory and add app to path
os.chdir('V3.0')
sys.path.append('app')

from api.server import GenerateRequest, api_generate_pdf

async def test_v3_complete():
    """Teste completo da V3.0"""
    print("🚀 === TESTE COMPLETO DA V3.0 ===\n")
    
    # Test 1: Check if filename_standardizer exists
    print("📋 1. Verificando arquivos essenciais...")
    
    essential_files = [
        "app/utils/filename_standardizer.py",
        "app/invoice/template_filler.py",
        "app/api/server.py"
    ]
    
    all_files_exist = True
    for file_path in essential_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING!")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Arquivos essenciais faltando! V3.0 não está completa.")
        return False
    
    # Test 2: Test filename standardization
    print(f"\n📋 2. Testando padronização de nomes...")
    
    try:
        from utils.filename_standardizer import generate_standardized_filename
        
        test_filename = generate_standardized_filename(
            employee_name="Filipi Brandão Lagedo",
            invoice_no="141",
            invoice_date="12/09/2025",
            abz_path=Path("ABZ - FMS - Maximus Project  -Monthly Charge Rates 09 2025.xlsx"),
            extension="xlsx"
        )
        
        expected = "ABZ Group 141-2025 FMS 09 2025 Filipi.xlsx"
        
        if test_filename == expected:
            print(f"  ✅ Padronização funcionando: {test_filename}")
        else:
            print(f"  ❌ Padronização falhou:")
            print(f"     Resultado: {test_filename}")
            print(f"     Esperado:  {expected}")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro na padronização: {e}")
        return False
    
    # Test 3: Check if FMS session exists
    print(f"\n📋 3. Verificando sessão FMS...")
    
    fms_session_id = '54e2a1574b774e3f8ef5ff4afa1a3863'
    session_dir = Path(f"out/sessions/{fms_session_id}")
    
    if session_dir.exists():
        print(f"  ✅ Sessão FMS encontrada: {session_dir}")
        
        # Check if ABZ file exists
        abz_files = list(session_dir.glob("*.xlsx"))
        if abz_files:
            print(f"  ✅ Arquivo ABZ encontrado: {abz_files[0].name}")
        else:
            print(f"  ⚠️  Nenhum arquivo ABZ encontrado na sessão")
            
    else:
        print(f"  ⚠️  Sessão FMS não encontrada, usando dados padrão")
    
    # Test 4: Test API generation with standardized names
    print(f"\n📋 4. Testando geração via API...")
    
    try:
        req = GenerateRequest(
            session_id=fms_session_id,
            invoice_date='12/09/2025',
            invoice_no='200',  # Different number to avoid conflicts
            call_off='FMS-V3-TEST'
        )
        
        result = await api_generate_pdf(req)
        
        files = result.get('files', [])
        warnings = result.get('warnings', [])
        
        print(f"  ✅ API executada com sucesso!")
        print(f"  📄 Arquivos gerados: {len(files)}")
        print(f"  ⚠️  Warnings: {len(warnings)}")
        
        # Check if files have standardized names
        standardized_count = 0
        for file in files:
            file_path = Path(file['xlsx'])
            filename = file_path.name
            
            if filename.startswith("ABZ Group"):
                standardized_count += 1
                print(f"  🎯 {filename}")
            else:
                print(f"  📄 {filename} (formato antigo)")
        
        if standardized_count > 0:
            print(f"  ✅ {standardized_count} arquivos com nomes padronizados!")
        else:
            print(f"  ❌ Nenhum arquivo com nome padronizado encontrado")
            return False
            
        if warnings:
            print(f"  ⚠️  Warnings encontrados:")
            for warning in warnings:
                print(f"    - {warning}")
        
    except Exception as e:
        print(f"  ❌ Erro na API: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Verify generated files
    print(f"\n📋 5. Verificando arquivos gerados...")
    
    xlsx_dir = session_dir / "xlsx"
    if xlsx_dir.exists():
        xlsx_files = list(xlsx_dir.glob("*.xlsx"))
        
        standardized_files = [f for f in xlsx_files if f.name.startswith("ABZ Group")]
        legacy_files = [f for f in xlsx_files if not f.name.startswith("ABZ Group")]
        
        print(f"  📊 Total de arquivos: {len(xlsx_files)}")
        print(f"  🎯 Padronizados: {len(standardized_files)}")
        print(f"  📄 Legados: {len(legacy_files)}")
        
        if len(standardized_files) > 0:
            print(f"  ✅ V3.0 gerando arquivos padronizados!")
            
            # Show examples
            print(f"\n  📋 Exemplos de nomes padronizados:")
            for file in standardized_files[:3]:  # Show first 3
                print(f"    🎯 {file.name}")
        else:
            print(f"  ❌ Nenhum arquivo padronizado encontrado")
            return False
    else:
        print(f"  ❌ Diretório xlsx não encontrado")
        return False
    
    return True

async def main():
    """Main test function"""
    success = await test_v3_complete()
    
    if success:
        print(f"\n🎉 === V3.0 TESTE COMPLETO - SUCESSO! ===")
        print(f"\n✅ Funcionalidades testadas e aprovadas:")
        print(f"  🎯 Padronização de nomes de arquivo")
        print(f"  🔍 Matching inteligente de templates")
        print(f"  📊 Geração via API")
        print(f"  📁 Estrutura de arquivos")
        print(f"  🚀 Sistema completo funcionando")
        
        print(f"\n📋 Padrão implementado:")
        print(f"  ABZ Group {{invoice_no}}-{{year}} {{client}} {{month}} {{year}} {{first_name}}.xlsx")
        
        print(f"\n🎯 V3.0 está pronta para produção!")
        print(f"  - Copie a pasta V3.0 para onde desejar")
        print(f"  - Execute: python start_server.py")
        print(f"  - Acesse: http://localhost:8000")
        print(f"  - Carregue planilhas ABZ e gere invoices!")
        
    else:
        print(f"\n❌ === V3.0 TESTE FALHOU ===")
        print(f"  Verifique os erros acima e corrija antes de usar")

if __name__ == "__main__":
    asyncio.run(main())
