#!/usr/bin/env python3
"""
Test filename standardization
"""
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append('dev/app')

from utils.filename_standardizer import generate_standardized_filename

def test_filename_standardization():
    """Test the filename standardization with real examples"""
    print("🧪 Testing filename standardization...")
    
    test_cases = [
        {
            "name": "FMS Case - Filipi",
            "employee_name": "Filipi Brandão Lagedo",
            "invoice_no": "141",
            "invoice_date": "12/09/2025",
            "abz_path": Path("ABZ - FMS - Maximus Project  -Monthly Charge Rates 09 2025.xlsx"),
            "expected_pattern": "ABZ Group 141-2025 FMS 09 2025 Filipi.xlsx"
        },
        {
            "name": "FMS Case - Gil",
            "employee_name": "Gil Anderson Reiser",
            "invoice_no": "142",
            "invoice_date": "12/09/2025",
            "abz_path": Path("ABZ - FMS - Maximus Project  -Monthly Charge Rates 09 2025.xlsx"),
            "expected_pattern": "ABZ Group 142-2025 FMS 09 2025 Gil.xlsx"
        },
        {
            "name": "OMEGA Case",
            "employee_name": "Daniel Vieira Silva Nunes",
            "invoice_no": "108",
            "invoice_date": "11/09/2025",
            "abz_path": Path("MODELO ABZ - OMEGA - Maximus Project  -Monthly Charge Rates xx.2025 (1).xlsx"),
            "expected_pattern": "ABZ Group 108-2025 OMEGA 09 2025 Daniel.xlsx"
        },
        {
            "name": "Edge Case - Long Name",
            "employee_name": "Laucilia Victoria Nonato Simplicio",
            "invoice_no": "143",
            "invoice_date": "15/04/2025",
            "abz_path": Path("ABZ - FMS - Project.xlsx"),
            "expected_pattern": "ABZ Group 143-2025 FMS 04 2025 Laucilia.xlsx"
        },
        {
            "name": "Edge Case - No Invoice Number",
            "employee_name": "Thiago Dorce Rodrigues",
            "invoice_no": None,
            "invoice_date": "01/01/2025",
            "abz_path": Path("ABZ - FMS - Project.xlsx"),
            "expected_pattern": "ABZ Group 001-2025 FMS 01 2025 Thiago.xlsx"
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        try:
            result = generate_standardized_filename(
                employee_name=case["employee_name"],
                invoice_no=case["invoice_no"],
                invoice_date=case["invoice_date"],
                abz_path=case["abz_path"],
                extension="xlsx"
            )
            
            passed = result == case["expected_pattern"]
            status = "✅" if passed else "❌"
            
            print(f"  {i}. {status} {case['name']}")
            print(f"     Result:   {result}")
            if not passed:
                print(f"     Expected: {case['expected_pattern']}")
                all_passed = False
            print()
            
        except Exception as e:
            print(f"  {i}. ❌ {case['name']} - ERROR: {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("=== Teste de Padronização de Nomes ===\n")
    
    success = test_filename_standardization()
    
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n✅ Padrão implementado:")
        print("   ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}.xlsx")
        print("\n📋 Exemplos:")
        print("   - ABZ Group 141-2025 FMS 09 2025 Filipi.xlsx")
        print("   - ABZ Group 142-2025 FMS 09 2025 Gil.xlsx")
        print("   - ABZ Group 108-2025 OMEGA 09 2025 Daniel.xlsx")
        print("\n🚀 Sistema pronto para gerar invoices com nomes padronizados!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("   Verifique os erros acima e corrija a implementação.")
