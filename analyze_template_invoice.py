#!/usr/bin/env python3
"""
Analisar o template de invoice fornecido pelo usuário
"""

import pandas as pd
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import sys

def analyze_template_structure():
    """Analisa a estrutura do template de invoice"""
    template_path = Path("DADOS/Template_Invoice_Geral.xlsx")
    
    if not template_path.exists():
        print(f"❌ Template não encontrado: {template_path}")
        return
    
    print(f"📋 Analisando template: {template_path}")
    print("=" * 60)
    
    # Carregar com openpyxl para análise detalhada
    wb = load_workbook(template_path, data_only=False)
    
    print(f"📊 Planilhas disponíveis: {wb.sheetnames}")
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        print(f"\n🔍 Analisando planilha: {sheet_name}")
        print("-" * 40)
        
        # Dimensões da planilha
        max_row = ws.max_row
        max_col = ws.max_column
        print(f"📐 Dimensões: {max_row} linhas x {max_col} colunas")
        
        # Larguras das colunas
        print("\n📏 Larguras das colunas:")
        for col in range(1, min(max_col + 1, 10)):  # Primeiras 10 colunas
            col_letter = get_column_letter(col)
            width = ws.column_dimensions[col_letter].width
            print(f"  Coluna {col_letter}: {width}")
        
        # Conteúdo das primeiras linhas
        print(f"\n📝 Conteúdo das primeiras 20 linhas:")
        for row in range(1, min(max_row + 1, 21)):
            row_content = []
            for col in range(1, min(max_col + 1, 6)):  # Primeiras 6 colunas
                cell = ws.cell(row=row, column=col)
                value = cell.value
                if value is not None:
                    # Truncar valores muito longos
                    str_value = str(value)
                    if len(str_value) > 30:
                        str_value = str_value[:27] + "..."
                    row_content.append(f"{get_column_letter(col)}{row}: {str_value}")
            
            if row_content:
                print(f"  Linha {row:2d}: {' | '.join(row_content)}")
        
        # Procurar por células mescladas
        print(f"\n🔗 Células mescladas:")
        if ws.merged_cells.ranges:
            for merged_range in ws.merged_cells.ranges:
                print(f"  {merged_range}")
        else:
            print("  Nenhuma célula mesclada encontrada")
        
        # Procurar por fórmulas
        print(f"\n🧮 Fórmulas encontradas:")
        formula_count = 0
        for row in ws.iter_rows():
            for cell in row:
                if cell.data_type == 'f':  # Formula
                    formula_count += 1
                    if formula_count <= 5:  # Mostrar apenas as primeiras 5
                        print(f"  {cell.coordinate}: {cell.value}")
        
        if formula_count == 0:
            print("  Nenhuma fórmula encontrada")
        elif formula_count > 5:
            print(f"  ... e mais {formula_count - 5} fórmulas")
    
    wb.close()
    
    # Também tentar carregar com pandas para ver dados tabulares
    print(f"\n📊 Análise com pandas:")
    print("-" * 40)
    
    try:
        # Tentar ler todas as planilhas
        excel_file = pd.ExcelFile(template_path)
        print(f"Planilhas detectadas pelo pandas: {excel_file.sheet_names}")
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n📋 Dados da planilha '{sheet_name}':")
            df = pd.read_excel(template_path, sheet_name=sheet_name, header=None)
            print(f"  Dimensões: {df.shape}")
            
            # Mostrar primeiras linhas não vazias
            print("  Primeiras linhas com dados:")
            for idx, row in df.head(15).iterrows():
                non_null = row.dropna()
                if not non_null.empty:
                    print(f"    Linha {idx}: {dict(non_null)}")
                    
    except Exception as e:
        print(f"❌ Erro ao ler com pandas: {e}")

if __name__ == "__main__":
    analyze_template_structure()
