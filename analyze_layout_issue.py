#!/usr/bin/env python3
"""
Analisar problema de layout - comparar template original com invoice gerada
"""

from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

def analyze_layout_issue():
    """Analisa diferenças de layout entre template e invoice gerada"""
    
    print("🔍 ANÁLISE DO PROBLEMA DE LAYOUT")
    print("=" * 50)
    
    # Caminhos
    template_path = Path("DADOS/Template_Invoice_Geral.xlsx")
    generated_path = Path("out/test_integration/ABZ Group 001-2025 CLIENT 09 2025 Gabriel.xlsx")
    
    if not template_path.exists():
        print(f"❌ Template não encontrado: {template_path}")
        return
    
    if not generated_path.exists():
        print(f"❌ Invoice gerada não encontrada: {generated_path}")
        return
    
    # Carregar arquivos
    print(f"📋 Carregando template: {template_path.name}")
    template_wb = load_workbook(template_path)
    template_ws = template_wb.active
    
    print(f"📄 Carregando invoice gerada: {generated_path.name}")
    generated_wb = load_workbook(generated_path)
    generated_ws = generated_wb.active
    
    # Comparar configurações de página
    print(f"\n📐 CONFIGURAÇÕES DE PÁGINA:")
    print("-" * 30)
    
    # Page setup
    template_page = template_ws.page_setup
    generated_page = generated_ws.page_setup
    
    print(f"Template - Orientação: {template_page.orientation}")
    print(f"Gerado   - Orientação: {generated_page.orientation}")
    
    print(f"Template - Tamanho papel: {template_page.paperSize}")
    print(f"Gerado   - Tamanho papel: {generated_page.paperSize}")
    
    print(f"Template - Escala: {template_page.scale}")
    print(f"Gerado   - Escala: {generated_page.scale}")
    
    print(f"Template - Fit to page: {template_page.fitToPage}")
    print(f"Gerado   - Fit to page: {generated_page.fitToPage}")
    
    print(f"Template - Fit to width: {template_page.fitToWidth}")
    print(f"Gerado   - Fit to width: {generated_page.fitToWidth}")
    
    print(f"Template - Fit to height: {template_page.fitToHeight}")
    print(f"Gerado   - Fit to height: {generated_page.fitToHeight}")
    
    # Print area
    print(f"\n🖨️  ÁREA DE IMPRESSÃO:")
    print("-" * 20)
    
    template_print_area = template_ws.print_area
    generated_print_area = generated_ws.print_area
    
    print(f"Template - Print area: {template_print_area}")
    print(f"Gerado   - Print area: {generated_print_area}")
    
    # Page breaks
    print(f"\n📄 QUEBRAS DE PÁGINA:")
    print("-" * 20)
    
    template_row_breaks = list(template_ws.row_breaks)
    generated_row_breaks = list(generated_ws.row_breaks)
    
    template_col_breaks = list(template_ws.col_breaks)
    generated_col_breaks = list(generated_ws.col_breaks)
    
    print(f"Template - Row breaks: {template_row_breaks}")
    print(f"Gerado   - Row breaks: {generated_row_breaks}")
    
    print(f"Template - Col breaks: {template_col_breaks}")
    print(f"Gerado   - Col breaks: {generated_col_breaks}")
    
    # Margens
    print(f"\n📏 MARGENS:")
    print("-" * 10)
    
    template_margins = template_ws.page_margins
    generated_margins = generated_ws.page_margins
    
    margins = ['left', 'right', 'top', 'bottom', 'header', 'footer']
    for margin in margins:
        template_val = getattr(template_margins, margin, 'N/A')
        generated_val = getattr(generated_margins, margin, 'N/A')
        print(f"{margin.capitalize():8} - Template: {template_val}, Gerado: {generated_val}")
    
    # Dimensões da planilha
    print(f"\n📊 DIMENSÕES DA PLANILHA:")
    print("-" * 25)
    
    print(f"Template - Max row: {template_ws.max_row}, Max col: {template_ws.max_column}")
    print(f"Gerado   - Max row: {generated_ws.max_row}, Max col: {generated_ws.max_column}")
    
    # Verificar conteúdo linha por linha
    print(f"\n📝 COMPARAÇÃO DE CONTEÚDO (primeiras 50 linhas):")
    print("-" * 50)
    
    differences = []
    for row in range(1, min(51, max(template_ws.max_row, generated_ws.max_row) + 1)):
        template_row = []
        generated_row = []
        
        for col in range(1, 5):  # Colunas A-D
            col_letter = get_column_letter(col)
            
            template_cell = template_ws[f'{col_letter}{row}']
            generated_cell = generated_ws[f'{col_letter}{row}']
            
            template_val = template_cell.value
            generated_val = generated_cell.value
            
            if template_val != generated_val:
                differences.append((f'{col_letter}{row}', template_val, generated_val))
    
    if differences:
        print(f"⚠️  Encontradas {len(differences)} diferenças:")
        for cell_ref, template_val, generated_val in differences[:10]:  # Mostrar apenas primeiras 10
            print(f"  {cell_ref}: Template='{template_val}' vs Gerado='{generated_val}'")
        if len(differences) > 10:
            print(f"  ... e mais {len(differences) - 10} diferenças")
    else:
        print("✅ Conteúdo idêntico nas primeiras 50 linhas")
    
    # Verificar se há imagens/shapes
    print(f"\n🖼️  IMAGENS E SHAPES:")
    print("-" * 18)
    
    template_images = len(template_ws._images) if hasattr(template_ws, '_images') else 0
    generated_images = len(generated_ws._images) if hasattr(generated_ws, '_images') else 0
    
    print(f"Template - Imagens: {template_images}")
    print(f"Gerado   - Imagens: {generated_images}")
    
    template_wb.close()
    generated_wb.close()
    
    print(f"\n💡 POSSÍVEIS CAUSAS DO PROBLEMA:")
    print("-" * 35)
    print("1. Configurações de página não copiadas do template")
    print("2. Área de impressão não definida corretamente")
    print("3. Quebras de página automáticas inseridas")
    print("4. Margens diferentes")
    print("5. Imagem do logo não copiada")

if __name__ == "__main__":
    analyze_layout_issue()
