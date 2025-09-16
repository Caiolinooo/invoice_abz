#!/usr/bin/env python3
"""
Análise detalhada do template de invoice para entender a estrutura exata
"""

import pandas as pd
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
import sys

def detailed_template_analysis():
    """Análise detalhada do template"""
    template_path = Path("DADOS/Template_Invoice_Geral.xlsx")
    
    if not template_path.exists():
        print(f"❌ Template não encontrado: {template_path}")
        return
    
    print(f"🔍 ANÁLISE DETALHADA DO TEMPLATE")
    print("=" * 60)
    
    wb = load_workbook(template_path, data_only=False)
    ws = wb.active
    
    print(f"📋 Planilha ativa: {ws.title}")
    print(f"📐 Dimensões: {ws.max_row} linhas x {ws.max_column} colunas")
    
    # Mapear todo o conteúdo
    print(f"\n📝 MAPEAMENTO COMPLETO DO CONTEÚDO:")
    print("-" * 60)
    
    content_map = {}
    for row in range(1, ws.max_row + 1):
        for col in range(1, ws.max_column + 1):
            cell = ws.cell(row=row, column=col)
            if cell.value is not None:
                coord = f"{get_column_letter(col)}{row}"
                content_map[coord] = {
                    'value': cell.value,
                    'data_type': cell.data_type,
                    'coordinate': coord,
                    'row': row,
                    'col': col
                }
    
    # Organizar por linha
    for row in range(1, ws.max_row + 1):
        row_cells = []
        for col in range(1, ws.max_column + 1):
            coord = f"{get_column_letter(col)}{row}"
            if coord in content_map:
                cell_info = content_map[coord]
                value_str = str(cell_info['value'])
                if len(value_str) > 40:
                    value_str = value_str[:37] + "..."
                row_cells.append(f"{coord}: {value_str}")
        
        if row_cells:
            print(f"Linha {row:2d}: {' | '.join(row_cells)}")
    
    # Identificar seções importantes
    print(f"\n🎯 IDENTIFICAÇÃO DE SEÇÕES:")
    print("-" * 60)
    
    # Procurar por cabeçalho da empresa
    company_section = []
    for coord, info in content_map.items():
        value = str(info['value']).lower()
        if any(keyword in value for keyword in ['abz', 'group', 'company']):
            company_section.append((coord, info['value']))
    
    if company_section:
        print("🏢 Seção da empresa:")
        for coord, value in company_section:
            print(f"  {coord}: {value}")
    
    # Procurar por título "Invoice"
    invoice_title = []
    for coord, info in content_map.items():
        value = str(info['value']).lower()
        if 'invoice' in value and len(value.strip()) < 20:
            invoice_title.append((coord, info['value']))
    
    if invoice_title:
        print("\n📄 Título da Invoice:")
        for coord, value in invoice_title:
            print(f"  {coord}: {value}")
    
    # Procurar por informações do cliente
    client_section = []
    for coord, info in content_map.items():
        value = str(info['value']).lower()
        if any(keyword in value for keyword in ['client', 'omega', 'address']):
            client_section.append((coord, info['value']))
    
    if client_section:
        print("\n👤 Seção do cliente:")
        for coord, value in client_section:
            print(f"  {coord}: {value}")
    
    # Procurar por cabeçalho da tabela de serviços
    services_header = []
    for coord, info in content_map.items():
        value = str(info['value']).lower()
        if any(keyword in value for keyword in ['services', 'unit price', 'quantity', 'final price']):
            services_header.append((coord, info['value']))
    
    if services_header:
        print("\n📊 Cabeçalho da tabela de serviços:")
        for coord, value in services_header:
            print(f"  {coord}: {value}")
    
    # Procurar por fórmulas
    print(f"\n🧮 FÓRMULAS ENCONTRADAS:")
    print("-" * 60)
    
    formulas = []
    for row in ws.iter_rows():
        for cell in row:
            if cell.data_type == 'f':
                formulas.append((cell.coordinate, cell.value))
    
    if formulas:
        for coord, formula in formulas:
            print(f"  {coord}: {formula}")
    else:
        print("  Nenhuma fórmula encontrada")
    
    # Analisar células mescladas em detalhes
    print(f"\n🔗 CÉLULAS MESCLADAS DETALHADAS:")
    print("-" * 60)
    
    if ws.merged_cells.ranges:
        for merged_range in ws.merged_cells.ranges:
            # Pegar o valor da célula superior esquerda
            top_left_coord = str(merged_range).split(':')[0]
            cell_value = ws[top_left_coord].value
            print(f"  {merged_range} -> Valor: {cell_value}")
    else:
        print("  Nenhuma célula mesclada")
    
    # Identificar área de dados da tabela
    print(f"\n📋 ÁREA DA TABELA DE SERVIÇOS:")
    print("-" * 60)
    
    # Procurar linhas que podem conter dados de serviços
    service_rows = []
    for row in range(15, 35):  # Área provável da tabela
        row_data = []
        has_data = False
        for col in range(1, 5):  # Colunas A-D
            cell = ws.cell(row=row, column=col)
            if cell.value is not None:
                has_data = True
                row_data.append(f"{get_column_letter(col)}: {cell.value}")
        
        if has_data:
            service_rows.append((row, row_data))
    
    for row_num, data in service_rows:
        print(f"  Linha {row_num}: {' | '.join(data)}")
    
    wb.close()
    
    print(f"\n✅ Análise concluída!")

if __name__ == "__main__":
    detailed_template_analysis()
