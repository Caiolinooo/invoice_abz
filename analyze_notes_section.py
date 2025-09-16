#!/usr/bin/env python3
"""
Analisar a seção "Notes to invoice above" no template atual
"""

from pathlib import Path
from openpyxl import load_workbook

def analyze_notes_section():
    """Analisa a seção Notes to invoice above no template"""
    
    print("🔍 ANALISANDO SEÇÃO 'NOTES TO INVOICE ABOVE'")
    print("=" * 50)
    
    template_path = Path("DADOS/Template_Invoice_Geral.xlsx")
    
    if not template_path.exists():
        print(f"❌ Template não encontrado: {template_path}")
        return
    
    # Carregar template
    wb = load_workbook(template_path)
    ws = wb.active
    
    print(f"📋 Template: {template_path.name}")
    
    # Procurar por "Notes to invoice above" ou similar
    print(f"\n🔍 PROCURANDO SEÇÃO 'NOTES TO INVOICE ABOVE':")
    print("-" * 45)
    
    found_notes = False
    notes_row = None
    
    # Verificar todas as células para encontrar "Notes"
    for row in range(1, 60):  # Verificar até linha 60
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            cell_value = ws[f'{col}{row}'].value
            if cell_value and 'notes' in str(cell_value).lower():
                print(f"  📍 Encontrado em {col}{row}: '{cell_value}'")
                found_notes = True
                notes_row = row
    
    if not found_notes:
        print("  ❌ Seção 'Notes to invoice above' não encontrada")
        print("  🔍 Verificando área após linha 30 (após tabela de serviços):")
        
        # Verificar área após a tabela de serviços
        for row in range(32, 55):
            row_content = []
            for col in ['A', 'B', 'C', 'D']:
                cell_value = ws[f'{col}{row}'].value
                if cell_value and str(cell_value).strip():
                    row_content.append(f"{col}{row}:'{cell_value}'")
            
            if row_content:
                print(f"    Linha {row}: {' | '.join(row_content)}")
    
    # Verificar especificamente a área onde deveria estar a seção Corporate Account Details
    print(f"\n🏦 ÁREA CORPORATE ACCOUNT DETAILS (linhas 40-55):")
    print("-" * 50)
    
    for row in range(40, 56):
        row_content = []
        for col in ['A', 'B', 'C', 'D']:
            cell_value = ws[f'{col}{row}'].value
            if cell_value and str(cell_value).strip():
                row_content.append(f"{col}{row}:'{cell_value}'")
        
        if row_content:
            print(f"  Linha {row}: {' | '.join(row_content)}")
    
    # Verificar se há alguma formatação especial na área
    print(f"\n🎨 FORMATAÇÃO DA ÁREA (linhas 40-50):")
    print("-" * 35)
    
    for row in range(40, 51):
        for col in ['A', 'B']:
            cell = ws[f'{col}{row}']
            if cell.value:
                font = cell.font
                border = cell.border
                alignment = cell.alignment
                
                print(f"  {col}{row}: '{cell.value}'")
                print(f"    Fonte: {font.name} {font.size}pt {'Bold' if font.bold else 'Normal'}")
                print(f"    Alinhamento: H={alignment.horizontal}, V={alignment.vertical}")
                if border.top.style or border.bottom.style or border.left.style or border.right.style:
                    print(f"    Bordas: T={border.top.style}, B={border.bottom.style}, L={border.left.style}, R={border.right.style}")
    
    wb.close()

if __name__ == "__main__":
    analyze_notes_section()
