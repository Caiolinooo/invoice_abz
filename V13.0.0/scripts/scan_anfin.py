from pathlib import Path
import openpyxl

anfin = Path('DADOS')
f = next(x for x in anfin.glob('*.xlsx') if 'AN-FIN' in x.name.upper())
print('File:', f)
wb = openpyxl.load_workbook(f, data_only=True)
print('Sheets:', wb.sheetnames)

# preview first sheet
sh = wb.sheetnames[0]
ws = wb[sh]
print('\nPreview of', sh)
for r in range(1, 18):
    row=[ws.cell(row=r,column=c).value for c in range(1, 16)]
    if any(v is not None for v in row):
        print(r, row)

pay_sheet = next((s for s in wb.sheetnames if 'payroll' in s.lower()), None)
cost_sheet = next((s for s in wb.sheetnames if 'cost' in s.lower()), None)
print('Detected pay_sheet:', pay_sheet, 'cost_sheet:', cost_sheet)

if cost_sheet:
    ws2 = wb[cost_sheet]
    print('\nHeaders scan for', cost_sheet)
    for r in range(1, 25):
        vals=[ws2.cell(row=r,column=c).value for c in range(1, 22)]
        if any(v is not None for v in vals):
            print(r, vals[:20])

name_sheets=[s for s in wb.sheetnames if any(k in s.lower() for k in ['barb','daniel','caio','fabricio','gabriel','kaue','otavio','rafael','rodrigo','semaias','vinicius'])]
print('\nIndividual sheets:', name_sheets)

b_sheet = next((s for s in wb.sheetnames if 'barb' in s.lower()), None)
if b_sheet:
    ws3 = wb[b_sheet]
    print('\nScan Barbara sheet:', b_sheet)
    for r in range(1, 120):
        vals=[ws3.cell(row=r,column=c).value for c in range(1, 18)]
        lower=[str(v).strip().lower() if v is not None else '' for v in vals]
        if any('total in gbp' in v for v in lower) or any('exchange rate' in v for v in lower):
            print(r, vals[:14])
    # numeric right of TOTAL in GBP
    for r in range(1, 120):
        vals=[ws3.cell(row=r,column=c).value for c in range(1, 18)]
        lower=[str(v).strip().lower() if v is not None else '' for v in vals]
        if any('total in gbp' in v for v in lower):
            idx = next(i for i,v in enumerate(lower) if 'total in gbp' in v)
            for c in range(idx+1, idx+6):
                val = ws3.cell(row=r, column=c+1).value
                if isinstance(val,(int,float)):
                    print('TOTAL_GBP value @', r, c+1, '=', val)
                    raise SystemExit
    print('TOTAL in GBP not found by simple scan')

