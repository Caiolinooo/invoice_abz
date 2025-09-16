#!/usr/bin/env python3

from openpyxl import load_workbook
from pathlib import Path

def analyze_exact_template():
    """Analisa o template original para extrair dimensões e formatação exatas"""
    
    # Carregar planilha original com templates
    abz_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
    
    if not abz_path.exists():
        print("❌ Planilha original não encontrada")
        return
    
    wb = load_workbook(abz_path)
    
    # Encontrar primeiro template
    template_sheets = [s for s in wb.sheetnames if s.lower().endswith('_invoice')]
    if not template_sheets:
        print('❌ Nenhum template encontrado')
        wb.close()
        return
    
    template_name = template_sheets[0]
    ws = wb[template_name]
    
    print(f'=== ANÁLISE EXATA DO TEMPLATE: {template_name} ===')
    print()
    
    # 1. DIMENSÕES DAS COLUNAS
    print('📏 DIMENSÕES DAS COLUNAS:')
    for col in ['A', 'B', 'C', 'D', 'E']:
        width = ws.column_dimensions[col].width
        print(f'  Coluna {col}: {width}')
    
    print()
    
    # 2. DIMENSÕES DAS LINHAS
    print('📏 DIMENSÕES DAS LINHAS (primeiras 40):')
    for row in range(1, 41):
        height = ws.row_dimensions[row].height
        if height:
            print(f'  Linha {row}: {height}')
    
    print()
    
    # 3. ANÁLISE DETALHADA DE CÉLULAS IMPORTANTES
    print('🎨 FORMATAÇÃO DETALHADA:')
    
    important_cells = [
        ('A3', 'Logo ABZ'),
        ('A5', 'Título Invoice'),
        ('A8', 'Cliente'),
        ('D8', 'Data Invoice'),
        ('A9', 'Endereço Cliente'),
        ('D9', 'Número Invoice'),
        ('A12', 'Cabeçalho Services'),
        ('B12', 'Cabeçalho Unit Price'),
        ('C12', 'Cabeçalho Quantity'),
        ('D12', 'Cabeçalho Final Price'),
        ('A28', 'Corporate Account'),
    ]
    
    for cell_ref, description in important_cells:
        cell = ws[cell_ref]
        print(f'\n{description} ({cell_ref}):')
        print(f'  Valor: "{cell.value}"')
        print(f'  Font: {cell.font.name}, Size: {cell.font.size}')
        print(f'  Bold: {cell.font.bold}')
        print(f'  Italic: {cell.font.italic}')
        print(f'  Underline: {cell.font.underline}')
        print(f'  Color: {cell.font.color.rgb if cell.font.color and hasattr(cell.font.color, "rgb") else "Default"}')
        print(f'  Fill: {cell.fill.start_color.rgb if cell.fill.start_color and hasattr(cell.fill.start_color, "rgb") else "None"}')
        print(f'  Alignment: H={cell.alignment.horizontal}, V={cell.alignment.vertical}')
        print(f'  Border Top: {cell.border.top.style if cell.border.top.style else "None"}')
        print(f'  Border Bottom: {cell.border.bottom.style if cell.border.bottom.style else "None"}')
        print(f'  Border Left: {cell.border.left.style if cell.border.left.style else "None"}')
        print(f'  Border Right: {cell.border.right.style if cell.border.right.style else "None"}')
    
    print()
    
    # 4. ANÁLISE DE MERGED CELLS
    print('🔗 CÉLULAS MESCLADAS:')
    for merged_range in ws.merged_cells.ranges:
        print(f'  {merged_range}')
    
    print()
    
    # 5. ESTRUTURA COMPLETA DA TABELA
    print('📋 ESTRUTURA COMPLETA (linhas 1-40):')
    for row in range(1, 41):
        row_content = []
        for col in range(1, 6):
            cell = ws.cell(row=row, column=col)
            if cell.value:
                col_letter = chr(64 + col)
                row_content.append(f'{col_letter}{row}: "{str(cell.value)[:30]}"')
        
        if row_content:
            print(f'  {" | ".join(row_content)}')
    
    wb.close()
    print('\n✅ ANÁLISE COMPLETA FINALIZADA!')

if __name__ == "__main__":
    analyze_exact_template()
