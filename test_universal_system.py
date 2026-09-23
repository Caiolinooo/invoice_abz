#!/usr/bin/env python3
"""
Teste do sistema universal de geração de invoices
"""
import sys
import os
from pathlib import Path
import pandas as pd
import tempfile
import shutil

# Adicionar V3.0 ao path
sys.path.insert(0, str(Path("V3.0").absolute()))

from app.invoice.universal_invoice_generator import UniversalInvoiceGenerator

def create_test_abz_file():
    """Cria uma planilha ABZ de teste com dados de funcionários"""
    data = {
        'Nome': [
            'Filipi Brandão Lagedo',
            'Gil Santos Silva', 
            'Izabela Costa Ferreira',
            'Laucilia Maria Santos',
            'Thiago Oliveira Lima',
            'Daniel Rodrigues',
            'Barbara Silva Costa'
        ],
        'Posição': [
            'ROV Supervisor',
            'ROV Sr Pilot',
            'Surveyor',
            'ROV Pilot',
            'ROV Technician',
            'Survey Supervisor',
            'ROV Pilot'
        ],
        'Call-Off': [
            'P25-227',
            'P25-285',
            'P25-122',
            'P25-156',
            'P25-189',
            'P25-201',
            'P25-234'
        ],
        'Rate': [85.0, 75.0, 80.0, 70.0, 65.0, 90.0, 70.0],
        'Horas': [160.0, 168.0, 152.0, 176.0, 144.0, 160.0, 168.0],
        'Amount': [13600.0, 12600.0, 12160.0, 12320.0, 9360.0, 14400.0, 11760.0],
        'Percentage': [20.0, 20.0, 40.0, 20.0, 20.0, 40.0, 20.0]
    }
    
    df = pd.DataFrame(data)
    
    # Salvar em arquivo temporário
    temp_file = Path(tempfile.mktemp(suffix='.xlsx'))
    df.to_excel(temp_file, index=False, sheet_name='Dados')
    
    return temp_file

def test_universal_generator():
    """Testa o gerador universal"""
    print("🧪 TESTE DO SISTEMA UNIVERSAL DE INVOICES")
    print("=" * 50)
    
    # Criar planilha de teste
    print("📊 Criando planilha ABZ de teste...")
    abz_file = create_test_abz_file()
    print(f"✅ Planilha criada: {abz_file}")
    
    # Criar diretório de output temporário
    output_dir = Path(tempfile.mkdtemp())
    print(f"📁 Diretório de output: {output_dir}")
    
    try:
        # Inicializar gerador
        generator = UniversalInvoiceGenerator()
        
        # Gerar invoices
        print("\n🚀 Gerando invoices universais...")
        results = generator.generate_all_invoices(
            abz_path=abz_file,
            output_dir=output_dir,
            invoice_date="15/09/2025",
            starting_invoice_no=141
        )
        
        # Mostrar resultados
        print(f"\n📈 RESULTADOS:")
        print(f"   Total processado: {results['total_processed']}")
        print(f"   Total sucesso: {results['total_success']}")
        print(f"   Arquivos gerados: {len(results['files'])}")
        print(f"   Warnings: {len(results['warnings'])}")
        print(f"   Errors: {len(results['errors'])}")
        
        # Listar arquivos gerados
        if results['files']:
            print(f"\n📄 ARQUIVOS GERADOS:")
            for file_info in results['files']:
                filename = Path(file_info['xlsx']).name
                print(f"   ✅ {filename}")
        
        # Mostrar warnings/errors
        if results['warnings']:
            print(f"\n⚠️  WARNINGS:")
            for warning in results['warnings']:
                print(f"   - {warning}")
                
        if results['errors']:
            print(f"\n❌ ERRORS:")
            for error in results['errors']:
                print(f"   - {error}")
        
        # Verificar se todos os funcionários foram processados
        expected_employees = 7
        if results['total_success'] == expected_employees:
            print(f"\n🎉 SUCESSO TOTAL! Todos os {expected_employees} funcionários foram processados!")
            return True
        else:
            print(f"\n⚠️  ATENÇÃO: Esperado {expected_employees}, processado {results['total_success']}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Limpeza
        try:
            abz_file.unlink()
            shutil.rmtree(output_dir)
            print(f"\n🧹 Arquivos temporários removidos")
        except Exception as e:
            print(f"⚠️  Erro na limpeza: {e}")

def test_template_creation():
    """Testa a criação do template universal"""
    print("\n🧪 TESTE DE CRIAÇÃO DE TEMPLATE")
    print("=" * 40)
    
    try:
        generator = UniversalInvoiceGenerator()
        
        # Criar template
        wb = generator.create_universal_template()
        
        # Verificar estrutura
        ws = wb.active
        
        # Verificar células importantes
        checks = [
            ('A1', 'ABZ GROUP'),
            ('A2', 'INVOICE / FATURA'),
            ('A4', 'Employee Name:'),
            ('D4', 'Invoice No:'),
            ('A8', 'Description')  # Header da tabela
        ]
        
        all_good = True
        for cell_ref, expected in checks:
            actual = ws[cell_ref].value
            if actual == expected:
                print(f"   ✅ {cell_ref}: '{actual}'")
            else:
                print(f"   ❌ {cell_ref}: esperado '{expected}', encontrado '{actual}'")
                all_good = False
        
        if all_good:
            print("🎉 Template criado com sucesso!")
            return True
        else:
            print("⚠️  Template tem problemas")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar template: {e}")
        return False

def test_employee_data_extraction():
    """Testa a extração de dados de funcionários"""
    print("\n🧪 TESTE DE EXTRAÇÃO DE DADOS")
    print("=" * 40)
    
    try:
        # Criar dados de teste
        abz_file = create_test_abz_file()
        df = pd.read_excel(abz_file)
        
        generator = UniversalInvoiceGenerator()
        
        # Testar extração para primeiro funcionário
        employee_data = generator.extract_employee_data(df, 0)
        
        print(f"   Nome: {employee_data['name']}")
        print(f"   Posição: {employee_data['position']}")
        print(f"   Call-Off: {employee_data['call_off']}")
        print(f"   Rate: ${employee_data['rate']:.2f}")
        print(f"   Horas: {employee_data['hours']}")
        print(f"   Total: ${employee_data['total']:.2f}")
        
        # Verificar se dados estão corretos
        expected_name = 'Filipi Brandão Lagedo'
        if employee_data['name'] == expected_name:
            print("✅ Extração de dados funcionando!")
            abz_file.unlink()
            return True
        else:
            print(f"❌ Nome esperado: '{expected_name}', encontrado: '{employee_data['name']}'")
            abz_file.unlink()
            return False
            
    except Exception as e:
        print(f"❌ Erro na extração: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DO SISTEMA UNIVERSAL")
    print("=" * 60)
    
    # Executar testes
    test1 = test_template_creation()
    test2 = test_employee_data_extraction()
    test3 = test_universal_generator()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    print(f"   Template Creation: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   Data Extraction: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"   Universal Generator: {'✅ PASS' if test3 else '❌ FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema universal está funcionando!")
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. Testar com planilha real FMS")
        print("   2. Verificar interface web")
        print("   3. Testar endpoint /api/generate/universal")
        print("   4. Confirmar que TODOS os funcionários são processados")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM. Verificar implementação.")
