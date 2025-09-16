#!/usr/bin/env python3
"""
Analisar células mescladas no template para entender onde podemos preencher dados
"""

from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

def analyze_merged_cells():
    """Analisa células mescladas no template"""
    
    template_path = Path("DADOS/Template_Invoice_Geral.xlsx")
    
    print("🔍 ANÁLISE DE CÉLULAS MESCLADAS")
    print("=" * 50)
    
    wb = load_workbook(template_path)
    ws = wb.active
    
    print(f"📋 Planilha: {ws.title}")
    print(f"📐 Dimensões: {ws.max_row} linhas x {ws.max_column} colunas")
    
    # Listar todas as células mescladas
    print(f"\n🔗 CÉLULAS MESCLADAS:")
    merged_ranges = list(ws.merged_cells.ranges)
    
    for i, merged_range in enumerate(merged_ranges, 1):
        print(f"{i:2d}. {merged_range}")
        
        # Verificar se afeta a área de dados (linhas 18-29)
        start_row = merged_range.min_row
        end_row = merged_range.max_row
        
        if 18 <= start_row <= 29 or 18 <= end_row <= 29:
            print(f"    ⚠️  AFETA ÁREA DE DADOS (linhas 18-29)")
    
    # Verificar especificamente as linhas 18-29
    print(f"\n📊 ANÁLISE DA ÁREA DE DADOS (linhas 18-29):")
    
    for row in range(18, 30):
        row_info = []
        for col in range(1, 5):  # Colunas A-D
            cell_ref = f"{get_column_letter(col)}{row}"
            cell = ws[cell_ref]
            
            # Verificar se é célula mesclada
            is_merged = False
            merged_range_info = None
            
            for merged_range in merged_ranges:
                if cell.coordinate in merged_range:
                    is_merged = True
                    merged_range_info = str(merged_range)
                    break
            
            if is_merged:
                row_info.append(f"{cell_ref}:MERGED({merged_range_info})")
            else:
                value = cell.value
                if value is not None:
                    row_info.append(f"{cell_ref}:{value}")
                else:
                    row_info.append(f"{cell_ref}:LIVRE")
        
        print(f"Linha {row}: {' | '.join(row_info)}")
    
    # Identificar linhas completamente livres
    print(f"\n✅ LINHAS DISPONÍVEIS PARA DADOS:")
    
    free_rows = []
    for row in range(18, 30):
        is_free = True
        for col in range(1, 5):  # Colunas A-D
            cell_ref = f"{get_column_letter(col)}{row}"
            
            # Verificar se está em alguma célula mesclada
            for merged_range in merged_ranges:
                if cell_ref in merged_range:
                    is_free = False
                    break
        
        if is_free:
            free_rows.append(row)
    
    print(f"Linhas livres: {free_rows}")
    print(f"Total de linhas disponíveis: {len(free_rows)}")
    
    wb.close()

if __name__ == "__main__":
    analyze_merged_cells()
