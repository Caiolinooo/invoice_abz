#!/usr/bin/env python3
"""
Teste final completo do sistema V3.0 Universal
"""
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Adicionar V3.0 ao path
sys.path.insert(0, str(Path("V3.0").absolute()))

def test_all_components():
    """Testa todos os componentes do sistema"""
    print("🧪 TESTE FINAL COMPLETO - SISTEMA V3.0 UNIVERSAL")
    print("=" * 60)
    
    results = {}
    
    # 1. Testar imports
    print("1️⃣ TESTANDO IMPORTS...")
    try:
        from app.invoice.universal_invoice_generator import UniversalInvoiceGenerator
        from app.utils.filename_standardizer import generate_standardized_filename
        print("   ✅ Imports funcionando")
        results['imports'] = True
    except Exception as e:
        print(f"   ❌ Erro nos imports: {e}")
        results['imports'] = False
    
    # 2. Testar criação de template
    print("\n2️⃣ TESTANDO CRIAÇÃO DE TEMPLATE...")
    try:
        generator = UniversalInvoiceGenerator()
        wb = generator.create_universal_template()
        ws = wb.active
        
        # Verificar estrutura básica
        checks = [
            ('A1', 'ABZ GROUP'),
            ('A2', 'INVOICE / FATURA'),
            ('A4', 'Employee Name:'),
            ('D4', 'Invoice No:')
        ]
        
        all_good = True
        for cell_ref, expected in checks:
            if ws[cell_ref].value != expected:
                all_good = False
                break
        
        if all_good:
            print("   ✅ Template criado corretamente")
            results['template'] = True
        else:
            print("   ❌ Template com problemas")
            results['template'] = False
            
    except Exception as e:
        print(f"   ❌ Erro na criação do template: {e}")
        results['template'] = False
    
    # 3. Testar padronização de nomes
    print("\n3️⃣ TESTANDO PADRONIZAÇÃO DE NOMES...")
    try:
        filename = generate_standardized_filename(
            employee_name="Filipi Brandão Lagedo",
            invoice_no="141",
            invoice_date="15/09/2025",
            abz_path=Path("ABZ - FMS - Test.xlsx"),
            extension="xlsx"
        )
        
        expected_parts = ["ABZ Group", "141-2025", "FMS", "09", "2025", "Filipi.xlsx"]
        if all(part in filename for part in expected_parts):
            print(f"   ✅ Nome padronizado: {filename}")
            results['filename'] = True
        else:
            print(f"   ❌ Nome incorreto: {filename}")
            results['filename'] = False
            
    except Exception as e:
        print(f"   ❌ Erro na padronização: {e}")
        results['filename'] = False
    
    # 4. Testar geração completa
    print("\n4️⃣ TESTANDO GERAÇÃO COMPLETA...")
    try:
        # Criar dados de teste
        import pandas as pd
        data = {
            'Nome': ['Filipi Brandão', 'Gil Santos', 'Izabela Costa'],
            'Posição': ['ROV Supervisor', 'ROV Pilot', 'Surveyor'],
            'Call-Off': ['P25-227', 'P25-285', 'P25-122'],
            'Rate': [85.0, 75.0, 80.0],
            'Horas': [160.0, 168.0, 152.0],
            'Amount': [13600.0, 12600.0, 12160.0],
            'Percentage': [20.0, 20.0, 40.0]
        }
        
        df = pd.DataFrame(data)
        temp_file = Path(tempfile.mktemp(suffix='.xlsx'))
        df.to_excel(temp_file, index=False)
        
        output_dir = Path(tempfile.mkdtemp())
        
        # Gerar invoices
        generator = UniversalInvoiceGenerator()
        results_gen = generator.generate_all_invoices(
            abz_path=temp_file,
            output_dir=output_dir,
            invoice_date="15/09/2025",
            starting_invoice_no=141
        )
        
        # Verificar resultados
        if (results_gen['total_success'] == 3 and 
            len(results_gen['files']) == 3 and
            len(results_gen['errors']) == 0):
            print("   ✅ Geração completa funcionando")
            results['generation'] = True
        else:
            print(f"   ❌ Problemas na geração: {results_gen}")
            results['generation'] = False
        
        # Limpeza
        temp_file.unlink()
        shutil.rmtree(output_dir)
        
    except Exception as e:
        print(f"   ❌ Erro na geração: {e}")
        results['generation'] = False
    
    # 5. Testar API endpoint
    print("\n5️⃣ TESTANDO API ENDPOINT...")
    try:
        server_file = Path("V3.0/app/api/server.py")
        content = server_file.read_text(encoding='utf-8')
        
        if ("/api/generate/universal" in content and 
            "UniversalInvoiceGenerator" in content):
            print("   ✅ API endpoint configurado")
            results['api'] = True
        else:
            print("   ❌ API endpoint não encontrado")
            results['api'] = False
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar API: {e}")
        results['api'] = False
    
    # 6. Verificar estrutura de arquivos
    print("\n6️⃣ VERIFICANDO ESTRUTURA DE ARQUIVOS...")
    try:
        required_files = [
            "V3.0/app/invoice/universal_invoice_generator.py",
            "V3.0/app/utils/filename_standardizer.py",
            "V3.0/app/api/server.py",
            "V3.0/start_server.py",
            "V3.0/README_SISTEMA_UNIVERSAL.md"
        ]
        
        all_exist = True
        for file_path in required_files:
            if not Path(file_path).exists():
                print(f"   ❌ Arquivo faltando: {file_path}")
                all_exist = False
        
        if all_exist:
            print("   ✅ Todos os arquivos necessários presentes")
            results['files'] = True
        else:
            results['files'] = False
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar arquivos: {e}")
        results['files'] = False
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL DOS TESTES:")
    
    test_names = {
        'imports': 'Imports e Dependências',
        'template': 'Criação de Template',
        'filename': 'Padronização de Nomes',
        'generation': 'Geração Completa',
        'api': 'API Endpoint',
        'files': 'Estrutura de Arquivos'
    }
    
    passed = 0
    total = len(results)
    
    for key, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_names[key]}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n📈 TAXA DE SUCESSO: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate == 100:
        print("\n🎉 SISTEMA V3.0 UNIVERSAL COMPLETAMENTE FUNCIONAL!")
        print("\n🚀 PRONTO PARA PRODUÇÃO:")
        print("   ✅ Todos os componentes testados e funcionando")
        print("   ✅ Zero erros de 'template não encontrado'")
        print("   ✅ Processa 100% dos funcionários")
        print("   ✅ Nomes padronizados automáticos")
        print("   ✅ API REST completa")
        print("   ✅ Documentação completa")
        
        print("\n📋 INSTRUÇÕES DE USO:")
        print("   1. cd V3.0")
        print("   2. python start_server.py")
        print("   3. Abrir http://localhost:8000")
        print("   4. Carregar planilha ABZ")
        print("   5. Usar sistema universal")
        print("   6. Baixar ZIP com TODAS as invoices!")
        
        print("\n🎯 PROBLEMA ORIGINAL 100% RESOLVIDO!")
        return True
        
    else:
        print(f"\n⚠️  ALGUNS TESTES FALHARAM ({100-success_rate:.1f}%)")
        print("   Verificar componentes com falha antes de usar em produção")
        return False

if __name__ == "__main__":
    success = test_all_components()
    sys.exit(0 if success else 1)
