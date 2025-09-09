from pathlib import Path
from openpyxl import load_workbook

root = Path('.')
fn = next(x for x in (root/'DADOS').glob('*.xlsx') if 'AN-FIN' in x.name.upper())
wb = load_workbook(fn, data_only=True)
ws = wb[next(s for s in wb.sheetnames if 'caio' in s.lower())]
print('Sheet:', ws.title)
found = False
for r in range(1, 200):
    for c in range(1, 10):
        v = ws.cell(row=r, column=c).value
        if v and 'addition' in str(v).lower():
            print('found at', r, c, ':', v)
            row = [ws.cell(row=r+i, column=3).value for i in range(0, 20)]
            print('col3 next 20 rows:', row)
            found = True
            break
    if found:
        break
if not found:
    print('not found')

