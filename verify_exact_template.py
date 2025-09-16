#!/usr/bin/env python3

from openpyxl import load_workbook
from pathlib import Path

def verify_exact_template():
    """Verifica se a invoice está exatamente como o template original"""
    
    file_path = Path('out/test_professional/ABZ_Professional_Gabriel.xlsx')
    
    if not file_path.exists():
        print("❌ Invoice não encontrada")
        return False
    
    wb = load_workbook(file_path)
    ws = wb.active

    print('=== VERIFICAÇÃO DETALHADA DO TEMPLATE EXATO ===')
    print()

    # Verificar estrutura completa
    print('📋 ESTRUTURA COMPLETA DA INVOICE:')
    for row in range(1, 40):
        row_content = []
        for col in range(1, 6):
            cell = ws.cell(row=row, column=col)
            if cell.value:
                col_letter = chr(64 + col)  # A=65, B=66, etc.
                row_content.append(f'{col_letter}{row}: {str(cell.value)[:50]}')
        
        if row_content:
            print(f'  {" | ".join(row_content)}')

    print()
    print('🎨 VERIFICAÇÃO DE FORMATAÇÃO:')
    
    # Verificar logo
    logo_cell = ws['A3']
    print(f'Logo "abz group":')
    print(f'  Valor: {logo_cell.value}')
    print(f'  Font: {logo_cell.font.name}, Size: {logo_cell.font.size}')
    print(f'  Bold: {logo_cell.font.bold}')
    print(f'  Color: {logo_cell.font.color.rgb if logo_cell.font.color else "Default"}')
    
    # Verificar título
    title_cell = ws['A5']
    print(f'Título "Invoice":')
    print(f'  Valor: {title_cell.value}')
    print(f'  Font: {title_cell.font.name}, Size: {title_cell.font.size}')
    print(f'  Bold: {title_cell.font.bold}')
    print(f'  Underline: {title_cell.font.underline}')
    
    # Verificar bordas da tabela
    services_cell = ws['A12']
    print(f'Cabeçalho da tabela:')
    print(f'  Valor: {services_cell.value}')
    print(f'  Border: {bool(services_cell.border.top.style)}')
    
    # Verificar se Corporate Account details existe
    corp_cell = ws['A28']
    print(f'Corporate Account details:')
    print(f'  Valor: {corp_cell.value}')
    print(f'  Existe: {"✅" if corp_cell.value else "❌"}')
    
    # Verificar dados da conta
    if corp_cell.value:
        print('  Dados da conta:')
        for row in range(29, 36):
            label_cell = ws.cell(row=row, column=1)
            value_cell = ws.cell(row=row, column=2)
            if label_cell.value:
                print(f'    {label_cell.value}: {value_cell.value}')

    wb.close()
    
    print()
    print('✅ VERIFICAÇÃO COMPLETA!')
    print(f'📄 Tamanho do arquivo: {file_path.stat().st_size} bytes')
    
    return True

if __name__ == "__main__":
    verify_exact_template()
