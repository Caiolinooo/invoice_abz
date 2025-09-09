from pathlib import Path
import openpyxl

f = next(x for x in Path('DADOS').glob('*.xlsx') if 'ABZ' in x.name.upper())
print('File:', f)
wb = openpyxl.load_workbook(f, data_only=True)
ws = wb['Charge Rate']

header_keywords = ['name','position','charge rate','days','brazilian payroll additionals','monthly total','expenses']
found_row=None
for r in range(1,200):
    values=[ws.cell(row=r,column=c).value for c in range(1,16)]
    lower=[str(v).strip().lower() if v is not None else '' for v in values]
    if any(k in ' '.join(lower) for k in header_keywords):
        print('row',r, lower)
    if all(any(k in cell for cell in lower) for k in ['name','position','charge rate']):
        found_row=r
        break
print('found_row:',found_row)

if found_row:
    for r in range(found_row-1, found_row+8):
        print(r, [ws.cell(row=r,column=c).value for c in range(1,12)])

start = found_row+1 if found_row else None
if start:
    for r in range(start, start+20):
        row=[ws.cell(row=r,column=c).value for c in range(1,13)]
        print('data', r, row)

