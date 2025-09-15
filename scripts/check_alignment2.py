from pathlib import Path
import sys
sys.path.append(str(Path('app')))
from openpyxl import load_workbook
from utils.excel_abz_template import find_invoice_table_coords

# Pick the first generated invoice XLSX
xlsx_dir = Path('out/invoices/xlsx')
files = sorted(xlsx_dir.glob('*.xlsx'))
if not files:
    raise SystemExit('No XLSX found in out/invoices/xlsx')
f = files[0]
print('Inspecting:', f)

wb = load_workbook(f)
ws = wb.active
coords = find_invoice_table_coords(Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx'), 'Barbara_Invoice')
print('coords', coords)
row = coords['first_data_row']
uc, qc, fc = coords['unit_col'], coords['qty_col'], coords['final_col']
# scan first 10 rows for non-empty numeric cells and print their alignments
for r in range(row, row+12):
    u = ws.cell(row=r, column=uc)
    q = ws.cell(row=r, column=qc)
    fcell = ws.cell(row=r, column=fc)
    if any(cell.value not in (None, '') for cell in (u,q,fcell)):
        def a(c):
            al = c.alignment
            return (al.horizontal, al.vertical)
        print(r, 'values:', u.value, q.value, fcell.value, 'align:', a(u), a(q), a(fcell))

