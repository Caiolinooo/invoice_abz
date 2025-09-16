#!/usr/bin/env python3

from openpyxl import load_workbook
from pathlib import Path

def verify_exact_layout():
    """Verifica se a invoice gerada tem layout exato"""
    
    # Verificar invoice gerada
    invoice_path = Path('out/test_direct/ABZ Group 001-2025 CLIENT 09 2025 Daniel.xlsx')
    
    if not invoice_path.exists():
        print("❌ Invoice não encontrada")
        return
    
    wb = load_workbook(invoice_path)
    ws = wb.active
    
    print('=== VERIFICAÇÃO DO LAYOUT EXATO ===')
    print()
    
    # 1. DIMENSÕES DAS COLUNAS
    print('📏 DIMENSÕES DAS COLUNAS:')
    expected_widths = {
        'A': 69.7109375,
        'B': 16.140625,
        'C': 13.28515625,
        'D': 19.85546875,
        'E': 13.0
    }
    
    for col, expected in expected_widths.items():
        actual = ws.column_dimensions[col].width
        status = "✅" if abs(actual - expected) < 0.1 else "❌"
        print(f'  {status} Coluna {col}: {actual} (esperado: {expected})')
    
    print()
    
    # 2. VERIFICAR POSIÇÕES ESPECÍFICAS
    print('🎯 POSIÇÕES ESPECÍFICAS:')
    
    checks = [
        ('A1', 'abz group', 'Logo'),
        ('A7', 'Invoice', 'Título'),
        ('A12', 'Client: Omega Subsea Ltd', 'Cliente'),
        ('C12', 'Invoice date:', 'Data'),
        ('C13', 'Invoice no:', 'Número'),
        ('A14', 'Westhill, AB32 6FE. UK', 'Endereço'),
        ('A16', 'Services', 'Cabeçalho Services'),
        ('B16', 'Unit Price', 'Cabeçalho Unit Price'),
        ('C16', 'Quantity', 'Cabeçalho Quantity'),
        ('D16', 'Final Price', 'Cabeçalho Final Price'),
        ('D17', '(GBP)', 'Moeda'),
        ('A24', 'Brazilian Payroll Additional', 'Brazilian Payroll'),
        ('A27', 'Expenses', 'Expenses'),
        ('A30', 'Total amount payable', 'Total'),
        ('A40', 'Notes to invoice above', 'Notes'),
        ('A43', 'Corporate Account details', 'Corporate Account'),
    ]
    
    for cell_ref, expected_text, description in checks:
        actual_value = ws[cell_ref].value
        if actual_value and expected_text in str(actual_value):
            print(f'  ✅ {description} ({cell_ref}): {actual_value}')
        else:
            print(f'  ❌ {description} ({cell_ref}): {actual_value} (esperado: {expected_text})')
    
    print()
    
    # 3. VERIFICAR FORMATAÇÃO
    print('🎨 FORMATAÇÃO:')
    
    # Logo
    logo_cell = ws['A1']
    print(f'  Logo - Font: {logo_cell.font.name}, Size: {logo_cell.font.size}, Bold: {logo_cell.font.bold}')
    print(f'  Logo - Color: {logo_cell.font.color}')
    
    # Título
    title_cell = ws['A7']
    print(f'  Título - Font: {title_cell.font.name}, Size: {title_cell.font.size}, Bold: {title_cell.font.bold}')
    print(f'  Título - Underline: {title_cell.font.underline}')
    
    print()
    
    # 4. VERIFICAR MERGED CELLS
    print('🔗 CÉLULAS MESCLADAS:')
    merged_count = len(ws.merged_cells.ranges)
    print(f'  Total de células mescladas: {merged_count}')
    
    for merged_range in list(ws.merged_cells.ranges)[:10]:  # Mostrar primeiras 10
        print(f'  - {merged_range}')
    
    print()
    
    # 5. VERIFICAR DADOS DINÂMICOS
    print('📊 DADOS DINÂMICOS:')
    
    # Procurar serviços do Daniel
    services_found = []
    for row in range(18, 25):
        cell_value = ws[f'A{row}'].value
        if cell_value and 'Daniel' in str(cell_value):
            services_found.append(cell_value)
    
    print(f'  Serviços encontrados: {len(services_found)}')
    for i, service in enumerate(services_found, 1):
        print(f'    {i}. {service}')
    
    # Verificar valores monetários
    total_cell = ws['D30']
    print(f'  Total amount payable: {total_cell.value}')
    
    wb.close()
    print('\n✅ VERIFICAÇÃO COMPLETA!')

if __name__ == "__main__":
    verify_exact_layout()
