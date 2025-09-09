from pathlib import Path
from openpyxl import load_workbook

root = Path('.')
fn = next(x for x in (root/'DADOS').glob('*.xlsx') if 'AN-FIN' in x.name.upper())
wb = load_workbook(fn, data_only=True)
ws = wb[next(s for s in wb.sheetnames if 'caio' in s.lower())]
print('Sheet:', ws.title)
found = False
for r in range(1, 400):
    txt = ' '.join(str(ws.cell(row=r, column=c).value or '') for c in range(1, 8)).lower()
    if 'brazilian payroll addition' in txt:
        print('Section row:', r, txt)
        for rr in range(r, r+40):
            row_vals = [ws.cell(row=rr, column=c).value for c in range(1, 6)]
            print(rr, row_vals)
        found = True
        break
if not found:
    print('Section not found')

