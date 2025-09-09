from pathlib import Path
from openpyxl import load_workbook

root = Path('.')
fn = next(x for x in (root/'DADOS').glob('*.xlsx') if 'AN-FIN' in x.name.upper())
wb = load_workbook(fn, data_only=True)
sh = next(s for s in wb.sheetnames if 'caio' in s.lower())
ws = wb[sh]
print('Sheet:', sh)

for r in range(1, 40):
    row = [ws.cell(row=r, column=c).value for c in range(1, 8)]
    if any(v is not None for v in row):
        print(r, row)

# print number_format for row 16 if exists
for r in range(10, 20):
    cells = []
    for c in range(1, 8):
        cell = ws.cell(row=r, column=c)
        cells.append((cell.value, cell.number_format))
    print('FMT', r, cells)

