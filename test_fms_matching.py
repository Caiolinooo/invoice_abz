#!/usr/bin/env python3
"""
Test template matching for FMS-style complex names
"""
import sys
sys.path.append('app')

import unicodedata
import re
from api.server import _find_template_for_employee, _norm

def test_fms_matching():
    """Test matching algorithm with FMS-style names"""
    print("🧪 Testando matching para nomes complexos estilo FMS...")
    
    # Simulate FMS invoice sheets based on the image
    fms_invoice_sheets = [
        "Filipi Brandao_Invoice",  # Note: without tilde
        "Gil_Invoice", 
        "Izabela_Invoice",
        "Laucilia_Invoice", 
        "Thiago_Invoice"
    ]
    
    # Test cases from FMS spreadsheet
    test_cases = [
        {
            "employee": "Filipi Brandão Lagedo",  # With tilde
            "expected": "Filipi Brandao_Invoice",  # Without tilde
            "description": "Accented character handling"
        },
        {
            "employee": "Gil Anderson Reiser", 
            "expected": "Gil_Invoice",
            "description": "First name only matching"
        },
        {
            "employee": "Izabela Bonacorsi Freire",
            "expected": "Izabela_Invoice", 
            "description": "First name with complex surname"
        },
        {
            "employee": "Laucilia Victoria Nonat",
            "expected": "Laucilia_Invoice",
            "description": "Compound first name handling"
        },
        {
            "employee": "Thiago Dorce Rodrigues",
            "expected": "Thiago_Invoice",
            "description": "Standard first name matching"
        }
    ]
    
    print(f"📋 Invoice sheets disponíveis:")
    for sheet in fms_invoice_sheets:
        print(f"  - {sheet}")
    
    print(f"\n🎯 Testando matching:")
    
    success_count = 0
    for i, case in enumerate(test_cases, 1):
        employee = case["employee"]
        expected = case["expected"]
        description = case["description"]
        
        print(f"\n  {i}. {employee}")
        print(f"     Descrição: {description}")
        print(f"     Esperado: {expected}")
        
        # Test the matching algorithm
        result = _find_template_for_employee(employee, fms_invoice_sheets)
        
        if result == expected:
            print(f"     ✅ Resultado: {result}")
            success_count += 1
        else:
            print(f"     ❌ Resultado: {result} (esperado: {expected})")
            
            # Debug information
            words = employee.split()
            first_norm = _norm(words[0])
            print(f"     🔍 Debug: primeiro nome '{words[0]}' → normalizado '{first_norm}'")
            
            # Check what matches exist
            matches = [s for s in fms_invoice_sheets if first_norm in _norm(s)]
            print(f"     🔍 Matches encontrados: {matches}")
    
    print(f"\n📊 Resultado final:")
    print(f"  ✅ Sucessos: {success_count}/{len(test_cases)}")
    print(f"  ❌ Falhas: {len(test_cases) - success_count}/{len(test_cases)}")
    
    if success_count == len(test_cases):
        print(f"\n🎉 Todos os casos de teste passaram!")
        return True
    else:
        print(f"\n⚠️  Alguns casos falharam, algoritmo precisa de ajustes")
        return False

def test_normalization():
    """Test the normalization function with accented characters"""
    print(f"\n🔤 Testando normalização de caracteres:")
    
    test_pairs = [
        ("Brandão", "brandao"),
        ("José", "jose"), 
        ("André", "andre"),
        ("Ângela", "angela"),
        ("Filipi Brandão", "filipibrandao"),
        ("Gil Anderson", "gilanderson")
    ]
    
    for original, expected in test_pairs:
        normalized = _norm(original)
        status = "✅" if normalized == expected else "❌"
        print(f"  {status} '{original}' → '{normalized}' (esperado: '{expected}')")

if __name__ == "__main__":
    print("=== Teste de Matching para Planilha FMS ===\n")
    
    # Test normalization first
    test_normalization()
    
    # Test matching algorithm
    success = test_fms_matching()
    
    if success:
        print("\n🚀 Sistema pronto para lidar com planilhas FMS!")
        print("✅ Nomes com acentos (Brandão → Brandao)")
        print("✅ Nomes compostos (Gil Anderson → Gil)")
        print("✅ Sobrenomes complexos (Bonacorsi Freire)")
        print("✅ Funciona para todos os modelos de planilha")
    else:
        print("\n❌ Sistema precisa de mais ajustes para planilhas FMS")
