#!/usr/bin/env python3

from openpyxl import load_workbook
from pathlib import Path

def analyze_original_template():
    """Analisa o template original para entender o layout"""
    
    # Carregar planilha original com templates
    abz_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
    
    if not abz_path.exists():
        print("Planilha original não encontrada")
        return
    
    wb = load_workbook(abz_path)
    
    # Encontrar primeiro template
    template_sheets = [s for s in wb.sheetnames if s.lower().endswith('_invoice')]
    if not template_sheets:
        print('Nenhum template encontrado')
        wb.close()
        return
    
    template_name = template_sheets[0]
    ws = wb[template_name]
    
    print(f'=== ANÁLISE DO TEMPLATE: {template_name} ===')
    print()
    
    # Examinar primeiras 30 linhas
    for r in range(1, 31):
        row_data = []
        for c in range(1, 8):
            cell = ws.cell(row=r, column=c)
            value = str(cell.value) if cell.value is not None else ''
            if value.strip():
                row_data.append(f'C{c}: {value[:30]}')
        
        if row_data:
            print(f'Linha {r:2d}: {" | ".join(row_data)}')
    
    print()
    print("=== FORMATAÇÃO DAS CÉLULAS ===")
    
    # Examinar formatação de células importantes
    for r in range(1, 20):
        for c in range(1, 6):
            cell = ws.cell(row=r, column=c)
            if cell.value:
                print(f'Célula {cell.coordinate}:')
                print(f'  Valor: {cell.value}')
                print(f'  Font: {cell.font.name}, Size: {cell.font.size}, Bold: {cell.font.bold}')
                print(f'  Fill: {cell.fill.start_color.rgb if cell.fill.start_color else "None"}')
                print(f'  Border: {bool(cell.border.top.style)}')
                print()
                break
        if r > 10:  # Limitar output
            break
    
    wb.close()

if __name__ == "__main__":
    analyze_original_template()
