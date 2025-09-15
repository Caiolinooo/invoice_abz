#!/usr/bin/env python3
"""
Test ABZ file detection and processing
"""
import sys
sys.path.append('app')

from pathlib import Path
from openpyxl import load_workbook

def test_abz_detection():
    """Test detection of different ABZ files"""
    print("🔍 Testando detecção de arquivos ABZ...")
    
    dados_dir = Path("DADOS")
    if not dados_dir.exists():
        print("❌ Diretório DADOS não encontrado")
        return False
    
    # List all files in DADOS
    all_files = list(dados_dir.glob("*.xlsx"))
    abz_files = list(dados_dir.glob("*ABZ*.xlsx"))
    
    print(f"📁 Arquivos no diretório DADOS:")
    for file in all_files:
        print(f"  - {file.name}")
    
    print(f"\n📊 Arquivos ABZ encontrados: {len(abz_files)}")
    for abz_file in abz_files:
        print(f"  - {abz_file.name}")
        
        # Test if we can open and read basic info
        try:
            wb = load_workbook(abz_file, read_only=True)
            sheets = wb.sheetnames
            invoice_sheets = [s for s in sheets if s.lower().strip().endswith('_invoice')]
            
            print(f"    📋 Total sheets: {len(sheets)}")
            print(f"    📄 Invoice sheets: {len(invoice_sheets)}")
            
            if invoice_sheets:
                print(f"    🎯 Invoice templates found:")
                for sheet in invoice_sheets[:5]:  # Show first 5
                    print(f"      - {sheet}")
                if len(invoice_sheets) > 5:
                    print(f"      ... and {len(invoice_sheets) - 5} more")
            else:
                print(f"    ❌ No invoice templates found")
            
            wb.close()
            
        except Exception as e:
            print(f"    ❌ Error reading file: {e}")
    
    return len(abz_files) > 0

def test_abz_matching():
    """Test ABZ file matching logic"""
    print("\n🎯 Testando lógica de matching de arquivos ABZ...")
    
    # Simulate different uploaded file names
    test_cases = [
        "ABZ - OMEGA - Maximus Project.xlsx",
        "ABZ - FMS - Project.xlsx", 
        "ABZ - OMEGA - Different Project.xlsx",
        "Some other file.xlsx"
    ]
    
    dados_dir = Path("DADOS")
    abz_files = list(dados_dir.glob("*ABZ*.xlsx"))
    
    for uploaded_name in test_cases:
        print(f"\n📤 Arquivo carregado simulado: {uploaded_name}")
        uploaded_abz_name = uploaded_name.lower()
        matching_abz = None
        
        # Look for similar ABZ files (same project/type)
        for abz_file in abz_files:
            abz_name = abz_file.name.lower()
            # Check if they share common keywords (like project names)
            keywords = ['omega', 'maximus', 'fms', 'project']
            shared_keywords = [keyword for keyword in keywords 
                             if keyword in abz_name and keyword in uploaded_abz_name]
            
            if shared_keywords:
                matching_abz = abz_file
                print(f"  ✅ Match encontrado: {abz_file.name}")
                print(f"  🔗 Palavras-chave compartilhadas: {shared_keywords}")
                break
        
        if not matching_abz:
            fallback = abz_files[0] if abz_files else None
            print(f"  ⚠️  Nenhum match específico, usando fallback: {fallback.name if fallback else 'None'}")

if __name__ == "__main__":
    print("=== Teste de Detecção de Arquivos ABZ ===\n")
    
    success = test_abz_detection()
    
    if success:
        test_abz_matching()
        print("\n✅ Teste de detecção concluído!")
    else:
        print("\n❌ Falha na detecção de arquivos ABZ!")
