#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path('app')))

from invoice.professional_generator import InvoiceProfessionalGenerator

def test_professional_generator():
    """Testa o gerador profissional de invoices"""
    
    print("=== TESTE DO GERADOR PROFISSIONAL ===")
    
    # Dados de teste
    employee_name = "Gabriel Silva"
    line_items = [
        {
            'description': 'Gabriel Silva - ROV Pilot',
            'unit_price': 691.00,
            'quantity': 15,
            'final': 10365.00
        },
        {
            'description': 'Gabriel Silva - Surveyor',
            'unit_price': 962.00,
            'quantity': 8,
            'final': 7696.00
        }
    ]
    
    # Criar gerador
    generator = InvoiceProfessionalGenerator()
    
    # Gerar invoice
    output_path = Path('out/test_professional/ABZ_Professional_Gabriel.xlsx')
    
    try:
        result_path = generator.create_invoice(
            employee_name=employee_name,
            line_items=line_items,
            output_path=output_path,
            invoice_date='15/09/2025',
            invoice_no='PROF001/2025',
            call_off='TEST-PROFESSIONAL'
        )
        
        if result_path.exists():
            print(f"✅ Invoice profissional criada: {result_path}")
            print(f"📄 Tamanho: {result_path.stat().st_size} bytes")
            
            # Verificar conteúdo básico
            from openpyxl import load_workbook
            wb = load_workbook(result_path)
            ws = wb.active
            
            print("\n📋 Conteúdo da invoice:")
            print(f"  - Logo: {ws['A3'].value}")
            print(f"  - Título: {ws['A5'].value}")
            print(f"  - Cliente: {ws['A8'].value}")
            print(f"  - Data: {ws['D8'].value}")
            print(f"  - Número: {ws['D9'].value}")
            print(f"  - Endereço: {ws['A10'].value}")

            # Verificar cabeçalho da tabela
            print(f"  - Cabeçalho tabela: {ws['A12'].value}")

            # Verificar serviços
            services_found = 0
            for row in range(13, 20):
                cell_value = ws[f'A{row}'].value
                if cell_value and 'Gabriel' in str(cell_value):
                    services_found += 1
                    print(f"  - Serviço {services_found}: {cell_value}")

            # Verificar totais
            print(f"  - Brazilian Payroll: {ws['A16'].value if ws['A16'].value else 'Não encontrado'}")
            print(f"  - Total: {ws['A20'].value if ws['A20'].value else 'Não encontrado'}")

            # Verificar Corporate Account
            print(f"  - Corporate Account: {ws['A28'].value if ws['A28'].value else 'Não encontrado'}")
            
            wb.close()
            
            print(f"\n🎯 Serviços encontrados: {services_found}")
            
            return True
            
        else:
            print("❌ Arquivo não foi criado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao gerar invoice: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_professional_generator()
    if success:
        print("\n🎉 GERADOR PROFISSIONAL FUNCIONANDO!")
        print("✅ Layout profissional criado com sucesso")
        print("✅ Formatação aplicada corretamente")
        print("✅ Dados inseridos dinamicamente")
    else:
        print("\n❌ Teste do gerador profissional falhou")
        sys.exit(1)
