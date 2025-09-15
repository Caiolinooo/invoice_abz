from openpyxl import load_workbook
from pathlib import Path

abz = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
wb = load_workbook(abz, read_only=True)

print('Verificando abas que terminam com _Invoice:')
for sheet in wb.sheetnames:
    lower_sheet = sheet.lower()
    ends_with_invoice = lower_sheet.endswith('_invoice')
    print(f'  {sheet} -> lower: "{lower_sheet}" -> ends with _invoice: {ends_with_invoice}')

print()
print('Abas que terminam com _Invoice:')
invoice_sheets = [s for s in wb.sheetnames if s.lower().endswith('_invoice')]
for sheet in invoice_sheets:
    print(f'  - {sheet}')

wb.close()
