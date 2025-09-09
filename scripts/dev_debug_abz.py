from pathlib import Path
import sys
# allow importing from app/ without requiring package init
sys.path.append(str(Path('app')))
from utils.abz_charge_rate_parser import read_charge_rate_table, aggregate_employee
from utils.excel_abz_template import find_invoice_table_coords
import openpyxl

root = Path('.')
abz_dir = root / 'DADOS'
file = None
for x in abz_dir.glob('*.xlsx'):
    if 'ABZ' in x.name.upper() and 'OMEGA' in x.name.upper():
        file = x
        break
if not file:
    raise SystemExit('ABZ file not found')

print('Using:', file)

df = read_charge_rate_table(file, 'Charge Rate')
print('Parsed columns:', list(df.columns))
print(df.head(12).to_string(index=False))

agg = aggregate_employee(df)
print('\nAggregated sample (first 20):')
print(agg.head(20).to_string(index=False))

wb = openpyxl.load_workbook(file, data_only=True)
sheet_candidates = [s for s in wb.sheetnames if 'invoice' in s.lower() and 'barbara' in s.lower()]
print('\nInvoice sheet candidates:', sheet_candidates)
if sheet_candidates:
    coords = find_invoice_table_coords(file, sheet_candidates[0])
    print('Detected coords:', coords)
else:
    print('No invoice sheet found to scan.')

