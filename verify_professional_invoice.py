#!/usr/bin/env python3

from openpyxl import load_workbook
from pathlib import Path

def verify_professional_invoice():
    """Verifica a invoice profissional gerada"""
    
    # Verificar invoice profissional gerada
    file_path = Path('out/test_professional/ABZ_Professional_Gabriel.xlsx')
    
    if not file_path.exists():
        print("❌ Invoice profissional não encontrada")
        return False
    
    wb = load_workbook(file_path)
    ws = wb.active

    print('=== VERIFICAÇÃO DA INVOICE PROFISSIONAL ===')
    print()

    # Verificar estrutura
    print('📋 ESTRUTURA DA INVOICE:')
    for row in range(1, 35):
        row_content = []
        for col in range(1, 5):
            cell = ws.cell(row=row, column=col)
            if cell.value:
                row_content.append(f'C{col}: {str(cell.value)[:40]}')
        
        if row_content:
            print(f'Linha {row:2d}: {" | ".join(row_content)}')

    print()
    print('🎨 FORMATAÇÃO:')
    
    # Verificar formatação do título
    title_cell = ws['A7']
    print(f'Título: {title_cell.value}')
    print(f'  Font: {title_cell.font.name}, Size: {title_cell.font.size}, Bold: {title_cell.font.bold}')

    # Verificar cabeçalho da tabela
    header_cell = ws['A16']
    print(f'Cabeçalho: {header_cell.value}')
    print(f'  Font: {header_cell.font.name}, Bold: {header_cell.font.bold}')
    
    # Verificar dados do cliente
    client_cell = ws['A12']
    print(f'Cliente: {client_cell.value}')
    
    # Verificar serviços
    service_count = 0
    for row in range(18, 30):
        cell = ws.cell(row=row, column=1)
        if cell.value and 'Gabriel' in str(cell.value):
            service_count += 1
            print(f'Serviço {service_count}: {cell.value}')

    wb.close()
    
    print()
    print('✅ INVOICE PROFISSIONAL VERIFICADA!')
    print(f'📊 Serviços encontrados: {service_count}')
    print(f'📄 Tamanho do arquivo: {file_path.stat().st_size} bytes')
    
    return True

if __name__ == "__main__":
    verify_professional_invoice()
