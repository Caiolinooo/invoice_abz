#!/usr/bin/env python3
"""
Script para criar um template fixo padrão baseado em um template existente da planilha ABZ.
Este template será usado quando não houver templates na planilha ABZ.
"""

from pathlib import Path
import sys
sys.path.append(str(Path('app')))

from openpyxl import load_workbook
import shutil

def create_default_template():
    """Cria um template padrão baseado em um template existente"""
    
    # Encontrar planilha ABZ
    root = Path('.')
    abz_files = list((root/'DADOS').glob('*.xlsx'))
    abz_file = None
    
    for f in abz_files:
        if 'ABZ' in f.name.upper():
            abz_file = f
            break
    
    if not abz_file:
        print("❌ Arquivo ABZ não encontrado em DADOS/")
        return False
    
    print(f"📁 Usando arquivo ABZ: {abz_file}")
    
    # Carregar workbook
    wb = load_workbook(abz_file)
    
    # Encontrar sheets de template
    template_sheets = [s for s in wb.sheetnames if s.lower().endswith('_invoice')]
    
    if not template_sheets:
        print("❌ Nenhum template (_invoice) encontrado na planilha ABZ")
        return False
    
    # Usar o primeiro template encontrado
    template_name = template_sheets[0]
    print(f"📋 Usando template: {template_name}")
    
    # Criar novo workbook apenas com o template
    template_sheet = wb[template_name]
    
    # Criar novo workbook
    from openpyxl import Workbook
    new_wb = Workbook()
    new_ws = new_wb.active
    new_ws.title = "Invoice_Template"
    
    # Copiar todas as células do template
    for row in template_sheet.iter_rows():
        for cell in row:
            new_cell = new_ws.cell(row=cell.row, column=cell.column)
            new_cell.value = cell.value
            
            # Copiar formatação
            if cell.has_style:
                new_cell.font = cell.font.copy()
                new_cell.border = cell.border.copy()
                new_cell.fill = cell.fill.copy()
                new_cell.number_format = cell.number_format
                new_cell.protection = cell.protection.copy()
                new_cell.alignment = cell.alignment.copy()
    
    # Copiar dimensões das colunas
    for col_letter, col_dim in template_sheet.column_dimensions.items():
        new_ws.column_dimensions[col_letter].width = col_dim.width
    
    # Copiar dimensões das linhas
    for row_num, row_dim in template_sheet.row_dimensions.items():
        new_ws.row_dimensions[row_num].height = row_dim.height
    
    # Copiar configurações da página
    new_ws.page_setup = template_sheet.page_setup
    new_ws.page_margins = template_sheet.page_margins
    new_ws.print_options = template_sheet.print_options
    
    # Salvar template padrão
    template_path = Path('app/templates/default_invoice_template.xlsx')
    template_path.parent.mkdir(parents=True, exist_ok=True)
    
    new_wb.save(template_path)
    wb.close()
    new_wb.close()
    
    print(f"✅ Template padrão criado: {template_path}")
    print(f"📊 Baseado no template: {template_name}")
    
    return True

if __name__ == "__main__":
    success = create_default_template()
    if success:
        print("\n🎉 Template padrão criado com sucesso!")
        print("   O sistema agora pode funcionar sem templates na planilha ABZ.")
    else:
        print("\n❌ Falha ao criar template padrão.")
        sys.exit(1)
