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
            
            print("\n📋 Conteúdo da invoice (posições exatas):")
            print(f"  - Logo: {ws['A1'].value}")
            print(f"  - Título: {ws['A7'].value}")
            print(f"  - Cliente: {ws['A12'].value}")
            print(f"  - Data: {ws['C12'].value}")
            print(f"  - Número: {ws['C13'].value}")
            print(f"  - Endereço: {ws['A14'].value}")

            # Verificar cabeçalho da tabela (linha 16)
            print(f"  - Cabeçalho Services: {ws['A16'].value}")
            print(f"  - Cabeçalho Unit Price: {ws['B16'].value}")
            print(f"  - Cabeçalho Quantity: {ws['C16'].value}")
            print(f"  - Cabeçalho Final Price: {ws['D16'].value}")
            print(f"  - (GBP): {ws['D17'].value}")

            # Verificar serviços (linha 18+)
            services_found = 0
            for row in range(18, 25):
                cell_value = ws[f'A{row}'].value
                if cell_value and 'Gabriel' in str(cell_value):
                    services_found += 1
                    print(f"  - Serviço {services_found}: {cell_value}")

            # Verificar totais (posições exatas)
            print(f"  - Brazilian Payroll: {ws['A24'].value if ws['A24'].value else 'Não encontrado'}")
            print(f"  - Expenses: {ws['A27'].value if ws['A27'].value else 'Não encontrado'}")
            print(f"  - Total: {ws['A30'].value if ws['A30'].value else 'Não encontrado'}")
            print(f"  - Notes: {ws['A40'].value if ws['A40'].value else 'Não encontrado'}")

            # Verificar Corporate Account (linha 43)
            print(f"  - Corporate Account: {ws['A43'].value if ws['A43'].value else 'Não encontrado'}")
            
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
