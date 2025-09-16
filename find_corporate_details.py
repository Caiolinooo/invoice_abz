#!/usr/bin/env python3
"""
Encontrar a seção Corporate Account Details no template
"""

from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

def find_corporate_details():
    """Encontra onde estão os Corporate Account Details"""
    
    print("🔍 PROCURANDO CORPORATE ACCOUNT DETAILS")
    print("=" * 45)
    
    template_path = Path("DADOS/Template_Invoice_Geral.xlsx")
    
    if not template_path.exists():
        print(f"❌ Template não encontrado: {template_path}")
        return
    
    # Carregar template
    wb = load_workbook(template_path)
    ws = wb.active
    
    print(f"📋 Analisando template: {template_path.name}")
    print(f"📊 Dimensões: {ws.max_row} linhas x {ws.max_column} colunas")
    
    # Procurar por texto relacionado a "corporate", "account", "details", "bank"
    keywords = ['corporate', 'account', 'details', 'bank', 'sort', 'iban', 'swift', 'address']
    
    found_cells = []
    
    print(f"\n🔎 PROCURANDO POR PALAVRAS-CHAVE:")
    print("-" * 35)
    
    for row in range(1, ws.max_row + 1):
        for col in range(1, ws.max_column + 1):
            cell_ref = f"{get_column_letter(col)}{row}"
            cell = ws[cell_ref]
            
            if cell.value and isinstance(cell.value, str):
                cell_text = cell.value.lower()
                
                for keyword in keywords:
                    if keyword in cell_text:
                        found_cells.append((cell_ref, cell.value, keyword))
                        print(f"✅ {cell_ref}: '{cell.value}' (contém '{keyword}')")
                        break
    
    if not found_cells:
        print("⚠️  Nenhuma palavra-chave encontrada. Vamos ver o conteúdo das últimas linhas:")
        
        # Mostrar últimas 20 linhas
        print(f"\n📄 ÚLTIMAS 20 LINHAS DO TEMPLATE:")
        print("-" * 35)
        
        start_row = max(1, ws.max_row - 19)
        for row in range(start_row, ws.max_row + 1):
            row_content = []
            for col in range(1, ws.max_column + 1):
                cell_ref = f"{get_column_letter(col)}{row}"
                cell_value = ws[cell_ref].value
                if cell_value:
                    row_content.append(f"{cell_ref}:'{cell_value}'")
            
            if row_content:
                print(f"Linha {row}: {' | '.join(row_content)}")
    
    # Verificar área específica onde geralmente ficam detalhes bancários (linhas 40-50)
    print(f"\n🏦 ÁREA PROVÁVEL DOS DETALHES BANCÁRIOS (linhas 40-50):")
    print("-" * 55)
    
    for row in range(40, min(51, ws.max_row + 1)):
        row_content = []
        for col in range(1, ws.max_column + 1):
            cell_ref = f"{get_column_letter(col)}{row}"
            cell_value = ws[cell_ref].value
            if cell_value and str(cell_value).strip():
                row_content.append(f"{cell_ref}:'{cell_value}'")
        
        if row_content:
            print(f"Linha {row}: {' | '.join(row_content)}")
    
    # Verificar formatação das células nessa área
    print(f"\n🎨 FORMATAÇÃO DAS CÉLULAS (linhas 43-50):")
    print("-" * 40)
    
    for row in range(43, min(51, ws.max_row + 1)):
        for col in range(1, ws.max_column + 1):
            cell_ref = f"{get_column_letter(col)}{row}"
            cell = ws[cell_ref]
            
            if cell.value and str(cell.value).strip():
                # Verificar alinhamento
                alignment = cell.alignment
                font = cell.font
                
                h_align = alignment.horizontal if alignment.horizontal else 'general'
                v_align = alignment.vertical if alignment.vertical else 'bottom'
                
                print(f"{cell_ref}: '{cell.value}'")
                print(f"  Alinhamento: H={h_align}, V={v_align}")
                print(f"  Fonte: {font.name}, Tamanho={font.size}")
                print()
    
    wb.close()

if __name__ == "__main__":
    find_corporate_details()
