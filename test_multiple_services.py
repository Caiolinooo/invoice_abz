#!/usr/bin/env python3
"""
Test multiple services for the same employee in invoice
"""
import sys
sys.path.append('app')

from pathlib import Path
from invoice.template_filler import generate_from_abz_template

def test_multiple_services_invoice():
    """Test generating invoice with multiple services for same employee"""
    print("🧪 Testando invoice com múltiplos serviços...")
    
    # Use the ABZ file
    abz_path = Path("DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx")
    
    if not abz_path.exists():
        print("❌ Arquivo ABZ não encontrado")
        return False
    
    # Test data: Caio with multiple positions
    employee_name = "Caio Cesar Silva Nascimento"
    
    # Multiple line items for the same employee (like duplicate positions)
    line_items = [
        {
            "description": "Caio - ROV Pilot Tech 1",
            "unit_price": 1900.0,
            "quantity": 3.0,
            "final": 5700.0
        },
        {
            "description": "Caio - Logistic Support",
            "unit_price": 900.0,
            "quantity": 3.0,
            "final": 2700.0
        },
        {
            "description": "Brazilian Payroll Additional",
            "unit_price": None,
            "quantity": None,
            "final": 700.0
        },
        {
            "description": "Expenses",
            "unit_price": None,
            "quantity": None,
            "final": 40.0
        }
    ]
    
    print(f"👤 Funcionário: {employee_name}")
    print(f"📋 Itens de serviço:")
    for i, item in enumerate(line_items, 1):
        desc = item['description']
        unit_price = item.get('unit_price', 'N/A')
        quantity = item.get('quantity', 'N/A')
        final = item.get('final', 0)
        print(f"  {i}. {desc}")
        print(f"     Unit: £{unit_price} x {quantity} = £{final}")
    
    # Create output directory
    out_dir = Path("test_output")
    out_dir.mkdir(exist_ok=True)
    
    try:
        # Generate invoice
        xlsx_path = generate_from_abz_template(
            abz_xlsx=abz_path,
            template_sheet_name="Caio_Invoice",
            employee_name=employee_name,
            line_items=line_items,
            out_dir=out_dir,
            invoice_date="11/09/2025",
            invoice_no="0000108/2025",
            call_off="P25-122",
        )
        
        print(f"\n✅ Invoice gerada com sucesso!")
        print(f"📄 Arquivo: {xlsx_path}")
        
        # Verify the file exists
        if xlsx_path.exists():
            print(f"📊 Tamanho do arquivo: {xlsx_path.stat().st_size} bytes")
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
    print("=== Teste de Invoice com Múltiplos Serviços ===\n")
    
    success = test_multiple_services_invoice()
    
    if success:
        print("\n🎉 Invoice com múltiplos serviços gerada com sucesso!")
        print("📝 A invoice deve mostrar:")
        print("   - Caio - ROV Pilot Tech 1: £1900 x 3 = £5700")
        print("   - Caio - Logistic Support: £900 x 3 = £2700")
        print("   - Brazilian Payroll Additional: £700")
        print("   - Expenses: £40")
        print("   - Total: £9140")
    else:
        print("\n❌ Falha no teste de múltiplos serviços!")
