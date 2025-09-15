from pathlib import Path
import sys
sys.path.append(str(Path('app')))
from openpyxl import load_workbook
from utils.excel_abz_template import set_invoice_meta

# Load the generated XLSX and check what happened
xlsx_path = Path('out/invoices/xlsx/Caio_Cesar_Silva_Nascimento_Invoice.xlsx')
if not xlsx_path.exists():
    print("XLSX not found!")
    exit(1)

wb = load_workbook(xlsx_path)
ws = wb.active

print("Checking cells around invoice date area:")
for r in range(10, 16):
    for c in range(1, 8):
        cell = ws.cell(row=r, column=c)
        if cell.value is not None:
            print(f"({r},{c}): {repr(cell.value)} (type: {cell.data_type})")

print("\nNow let's test the metadata writing function directly...")

# Load the original template
abz_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
wb_template = load_workbook(abz_path)
ws_template = wb_template['Caio_Invoice']

print("\nOriginal template cells:")
for r in range(10, 16):
    for c in range(1, 8):
        cell = ws_template.cell(row=r, column=c)
        if cell.value is not None:
            print(f"({r},{c}): {repr(cell.value)} (type: {cell.data_type})")

# Test metadata writing
print("\nTesting metadata writing...")
set_invoice_meta(ws_template,
                 invoice_date="10/09/2025",
                 invoice_no="xx/0000001/2025",
                 call_off="P25-122")

print("\nAfter metadata writing:")
for r in range(10, 16):
    for c in range(1, 8):
        cell = ws_template.cell(row=r, column=c)
        if cell.value is not None:
            print(f"({r},{c}): {repr(cell.value)} (type: {cell.data_type})")

wb.close()
wb_template.close()
