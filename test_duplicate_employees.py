#!/usr/bin/env python3
"""
Test duplicate employee handling
"""
import sys
sys.path.append('app')

import pandas as pd
from pathlib import Path
from utils.abz_charge_rate_parser import aggregate_employee

def test_duplicate_employees():
    """Test how the system handles duplicate employees with different positions"""
    print("🧪 Testando processamento de colaboradores duplicados...")
    
    # Create test data with duplicate employees
    test_data = {
        'Name': ['Caio', 'Caio', 'Daniel', 'Gabriel', 'Gabriel'],
        'Position': ['ROV Pilot', 'Logistic', 'ROV Supervisor', 'Surveyor', 'ROV Pilot'],
        'Charge Rate (GBP)': [1900, 900, 1500, 1200, 1800],
        'Days': [3, 3, 5, 2, 1],
        'Brazilian Payroll Additionals (GBP)': [500, 200, 400, 300, 150],
        'Expenses': [20, 20, 20, 40, 20]
    }
    
    df = pd.DataFrame(test_data)
    print("📊 Dados de teste:")
    print(df.to_string(index=False))
    
    # Process with aggregate_employee function
    result = aggregate_employee(df)
    
    print(f"\n✅ Resultado do processamento:")
    print(f"📄 Total de linhas processadas: {len(result)}")
    
    if not result.empty:
        print("\n📋 Itens de serviço gerados:")
        for _, row in result.iterrows():
            name = row['Name']
            type_item = row['Type']
            desc = row['Description']
            unit_price = row.get('Unit Price (GBP)', 0)
            quantity = row.get('Quantity', 0)
            final_price = row.get('Final Price (GBP)', 0)
            
            print(f"  {name:15} | {type_item:12} | {desc:35} | £{unit_price:6.0f} x {quantity:3.0f} = £{final_price:8.0f}")
        
        # Check for duplicates
        service_items = result[result['Type'] == 'service']
        employees_with_multiple_services = service_items.groupby('Name').size()
        duplicates = employees_with_multiple_services[employees_with_multiple_services > 1]
        
        if not duplicates.empty:
            print(f"\n🔄 Colaboradores com múltiplos serviços:")
            for name, count in duplicates.items():
                print(f"  - {name}: {count} serviços")
            return True
        else:
            print("\n❌ Nenhum colaborador duplicado foi processado corretamente")
            return False
    else:
        print("❌ Nenhum resultado gerado")
        return False

if __name__ == "__main__":
    print("=== Teste de Colaboradores Duplicados ===\n")
    
    success = test_duplicate_employees()
    
    if success:
        print("\n✅ Sistema processa colaboradores duplicados corretamente!")
    else:
        print("\n❌ Problema no processamento de colaboradores duplicados!")
