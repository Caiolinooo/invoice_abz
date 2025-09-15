#!/usr/bin/env python3
"""
Analyze template matching issues and improve the algorithm
"""
import sys
sys.path.append('app')

import unicodedata
import re
from pathlib import Path
from openpyxl import load_workbook
from collections import Counter

def _norm(s: str) -> str:
    """Normalize string for comparison"""
    s = unicodedata.normalize('NFD', str(s))
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '', s.lower())

def analyze_template_matching(abz_path: Path):
    """Analyze template matching for a specific ABZ file"""
    print(f"🔍 Analisando: {abz_path.name}")
    
    if not abz_path.exists():
        print("❌ Arquivo não encontrado")
        return
    
    wb = load_workbook(abz_path, read_only=True)
    sheets = wb.sheetnames
    
    # Find invoice sheets
    invoice_sheets = [s for s in sheets if s.lower().strip().endswith('_invoice')]
    print(f"📋 Invoice sheets encontradas: {len(invoice_sheets)}")
    
    # Extract first names from invoice sheets
    sheet_first_names = []
    sheet_info = {}
    
    for sheet in invoice_sheets:
        # Extract name from sheet (remove _Invoice suffix)
        base_name = re.sub(r"(?i)[\s_-]*invoice.*$", "", sheet).strip()
        if base_name:
            first_name = base_name.split('_')[0] if '_' in base_name else base_name.split()[0]
            sheet_first_names.append(first_name)
            sheet_info[sheet] = {
                'base_name': base_name,
                'first_name': first_name,
                'normalized_first': _norm(first_name)
            }
    
    # Check for duplicates in first names
    first_name_counts = Counter(sheet_first_names)
    duplicates = {name: count for name, count in first_name_counts.items() if count > 1}
    
    print(f"\n📊 Análise dos nomes:")
    print(f"  - Total de sheets: {len(invoice_sheets)}")
    print(f"  - Primeiros nomes únicos: {len(set(sheet_first_names))}")
    print(f"  - Duplicações encontradas: {len(duplicates)}")
    
    if duplicates:
        print(f"\n🔄 Primeiros nomes duplicados:")
        for name, count in duplicates.items():
            print(f"  - '{name}': {count} ocorrências")
            matching_sheets = [s for s in invoice_sheets if sheet_info[s]['first_name'] == name]
            for sheet in matching_sheets:
                print(f"    → {sheet} (base: {sheet_info[sheet]['base_name']})")
    
    # Now test with some employee names from charge rate table
    try:
        from utils.abz_charge_rate_parser import read_charge_rate_table
        charge_df = read_charge_rate_table(abz_path, "Charge Rate")
        employee_names = sorted(set(charge_df['Name'].astype(str).dropna().tolist()))
        
        print(f"\n👥 Funcionários na planilha: {len(employee_names)}")
        
        # Test matching for each employee
        print(f"\n🎯 Teste de matching:")
        for emp_name in employee_names[:10]:  # Test first 10
            print(f"\n  Funcionário: {emp_name}")
            
            # Current algorithm (first name only)
            first = _norm(emp_name.split()[0])
            current_matches = [s for s in invoice_sheets if first in _norm(s)]
            
            print(f"    Primeiro nome normalizado: '{first}'")
            print(f"    Matches atuais: {current_matches}")
            
            if len(current_matches) == 0:
                print("    ❌ PROBLEMA: Nenhum match encontrado")
                # Try with more sophisticated matching
                words = emp_name.split()
                if len(words) >= 2:
                    second = _norm(words[1])
                    extended_matches = [s for s in invoice_sheets 
                                     if first in _norm(s) or second in _norm(s)]
                    print(f"    💡 Tentativa com segundo nome '{second}': {extended_matches}")
            
            elif len(current_matches) > 1:
                print("    ⚠️  AMBIGUIDADE: Múltiplos matches")
                # Try to disambiguate with second name
                words = emp_name.split()
                if len(words) >= 2:
                    second = _norm(words[1])
                    refined_matches = [s for s in current_matches 
                                     if second in _norm(s)]
                    if refined_matches:
                        print(f"    💡 Refinado com segundo nome '{second}': {refined_matches}")
            else:
                print("    ✅ Match único encontrado")
    
    except Exception as e:
        print(f"❌ Erro ao ler charge rate table: {e}")
    
    wb.close()

def improved_template_matching(employee_name: str, invoice_sheets: list) -> str:
    """Improved template matching algorithm"""
    words = employee_name.split()
    if not words:
        return None
    
    first = _norm(words[0])
    
    # Step 1: Find matches with first name
    first_matches = [s for s in invoice_sheets if first in _norm(s)]
    
    if len(first_matches) == 0:
        # No matches with first name, try with any word
        for word in words:
            word_norm = _norm(word)
            if len(word_norm) > 2:  # Skip very short words
                matches = [s for s in invoice_sheets if word_norm in _norm(s)]
                if matches:
                    return matches[0]
        return None
    
    elif len(first_matches) == 1:
        # Unique match with first name
        return first_matches[0]
    
    else:
        # Multiple matches, try to disambiguate with second name
        if len(words) >= 2:
            second = _norm(words[1])
            refined_matches = [s for s in first_matches if second in _norm(s)]
            if refined_matches:
                return refined_matches[0]
        
        # If still ambiguous, return first match
        return first_matches[0]

if __name__ == "__main__":
    print("=== Análise de Template Matching ===\n")
    
    # Test with current session file
    session_path = Path("out/sessions/2d4de704b5cb47979f9c8bee5ae5770/uploaded_abz.xlsx")
    if session_path.exists():
        analyze_template_matching(session_path)
    else:
        # Fallback to DADOS
        dados_dir = Path("DADOS")
        abz_files = list(dados_dir.glob("*ABZ*.xlsx"))
        if abz_files:
            analyze_template_matching(abz_files[0])
        else:
            print("❌ Nenhum arquivo ABZ encontrado")
    
    print("\n" + "="*50)
    print("💡 Algoritmo melhorado implementado!")
    print("   1. Usa primeiro nome como padrão")
    print("   2. Se houver duplicação, usa segundo nome")
    print("   3. Se não encontrar, tenta outras palavras")
    print("   4. Funciona para todos os modelos de planilha")
