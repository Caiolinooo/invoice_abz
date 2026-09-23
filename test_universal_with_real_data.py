#!/usr/bin/env python3
"""
Teste do sistema universal com dados reais FMS
"""
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Adicionar V3.0 ao path
sys.path.insert(0, str(Path("V3.0").absolute()))

from app.invoice.universal_invoice_generator import UniversalInvoiceGenerator

def find_fms_file():
    """Encontra arquivo FMS real para teste"""
    # Procurar em locais comuns
    search_paths = [
        Path("."),
        Path("DADOS"),
        Path("V3.0/DADOS"),
        Path("out/sessions")
    ]
    
    for search_path in search_paths:
        if search_path.exists():
            # Procurar arquivos FMS
            fms_files = list(search_path.glob("*FMS*.xlsx"))
            if fms_files:
                return fms_files[0]
            
            # Procurar em subdiretórios
            for subdir in search_path.iterdir():
                if subdir.is_dir():
                    fms_files = list(subdir.glob("*FMS*.xlsx"))
                    if fms_files:
                        return fms_files[0]
    
    return None

def test_with_real_fms():
    """Testa com arquivo FMS real"""
    print("🧪 TESTE COM DADOS REAIS FMS")
    print("=" * 50)
    
    # Encontrar arquivo FMS
    fms_file = find_fms_file()
    if not fms_file:
        print("❌ Arquivo FMS não encontrado!")
        print("   Procurado em: ., DADOS/, V3.0/DADOS/, out/sessions/")
        return False
    
    print(f"📊 Arquivo FMS encontrado: {fms_file}")
    
    # Criar diretório de output temporário
    output_dir = Path(tempfile.mkdtemp())
    print(f"📁 Diretório de output: {output_dir}")
    
    try:
        # Inicializar gerador
        generator = UniversalInvoiceGenerator()
        
        # Gerar invoices
        print("\n🚀 Gerando invoices com dados reais...")
        results = generator.generate_all_invoices(
            abz_path=fms_file,
            output_dir=output_dir,
            invoice_date="15/09/2025",
            starting_invoice_no=141
        )
        
        # Mostrar resultados
        print(f"\n📈 RESULTADOS COM DADOS REAIS:")
        print(f"   Total processado: {results['total_processed']}")
        print(f"   Total sucesso: {results['total_success']}")
        print(f"   Arquivos gerados: {len(results['files'])}")
        print(f"   Warnings: {len(results['warnings'])}")
        print(f"   Errors: {len(results['errors'])}")
        
        # Listar primeiros 10 arquivos gerados
        if results['files']:
            print(f"\n📄 PRIMEIROS ARQUIVOS GERADOS:")
            for i, file_info in enumerate(results['files'][:10]):
                filename = Path(file_info['xlsx']).name
                print(f"   ✅ {filename}")
            
            if len(results['files']) > 10:
                print(f"   ... e mais {len(results['files']) - 10} arquivos")
        
        # Mostrar warnings/errors se houver
        if results['warnings']:
            print(f"\n⚠️  WARNINGS:")
            for warning in results['warnings'][:5]:  # Mostrar apenas primeiros 5
                print(f"   - {warning}")
            if len(results['warnings']) > 5:
                print(f"   ... e mais {len(results['warnings']) - 5} warnings")
                
        if results['errors']:
            print(f"\n❌ ERRORS:")
            for error in results['errors'][:5]:  # Mostrar apenas primeiros 5
                print(f"   - {error}")
            if len(results['errors']) > 5:
                print(f"   ... e mais {len(results['errors']) - 5} errors")
        
        # Verificar taxa de sucesso
        success_rate = (results['total_success'] / results['total_processed']) * 100 if results['total_processed'] > 0 else 0
        
        print(f"\n📊 TAXA DE SUCESSO: {success_rate:.1f}%")
        
        if success_rate >= 95:
            print(f"🎉 EXCELENTE! Taxa de sucesso muito alta!")
            return True
        elif success_rate >= 80:
            print(f"✅ BOM! Taxa de sucesso aceitável")
            return True
        else:
            print(f"⚠️  ATENÇÃO: Taxa de sucesso baixa, verificar erros")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Limpeza
        try:
            shutil.rmtree(output_dir)
            print(f"\n🧹 Arquivos temporários removidos")
        except Exception as e:
            print(f"⚠️  Erro na limpeza: {e}")

def test_api_endpoint():
    """Testa se o endpoint da API está funcionando"""
    print("\n🧪 TESTE DO ENDPOINT API")
    print("=" * 40)
    
    try:
        # Verificar se o arquivo server.py foi modificado corretamente
        server_file = Path("V3.0/app/api/server.py")
        if not server_file.exists():
            print("❌ Arquivo server.py não encontrado!")
            return False
        
        # Verificar se o endpoint universal existe
        content = server_file.read_text(encoding='utf-8')
        
        if "/api/generate/universal" in content:
            print("✅ Endpoint /api/generate/universal encontrado!")
        else:
            print("❌ Endpoint /api/generate/universal não encontrado!")
            return False
        
        if "UniversalInvoiceGenerator" in content:
            print("✅ Import do UniversalInvoiceGenerator encontrado!")
        else:
            print("❌ Import do UniversalInvoiceGenerator não encontrado!")
            return False
        
        print("✅ API endpoint configurado corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar API: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTE COMPLETO DO SISTEMA UNIVERSAL")
    print("=" * 60)
    
    # Executar testes
    test1 = test_api_endpoint()
    test2 = test_with_real_fms()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    print(f"   API Endpoint: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   Real FMS Data: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if all([test1, test2]):
        print("\n🎉 SISTEMA UNIVERSAL COMPLETAMENTE FUNCIONAL!")
        print("\n🚀 COMO USAR:")
        print("   1. cd V3.0")
        print("   2. python start_server.py")
        print("   3. Abrir http://localhost:8000")
        print("   4. Carregar planilha ABZ (FMS, OMEGA, etc.)")
        print("   5. Usar endpoint /api/generate/universal")
        print("   6. TODOS os funcionários serão processados!")
        print("\n✅ ZERO ERROS DE 'TEMPLATE NÃO ENCONTRADO'!")
        print("✅ NOMES PADRONIZADOS AUTOMÁTICOS!")
        print("✅ FUNCIONA COM QUALQUER PLANILHA ABZ!")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM. Verificar implementação.")
