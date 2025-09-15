from pathlib import Path
import openpyxl

f = Path('out/invoices/xlsx/Bárbara_Chapeta_Mattoso_Franco_Invoice.xlsx')
wb = openpyxl.load_workbook(f, data_only=True)
ws = wb.active

labels = ['invoice no', 'invoice number', 'invoice #', 'invoice date', 'date', 'call off', 'call-off']
res = []
for r in range(1, 120):
    for c in range(1, 30):
        v = ws.cell(row=r, column=c).value
        if v is None:
            continue
        s = str(v).strip()
        sl = s.lower()
        if any(k in sl for k in labels):
            # show this cell and right 3 cells
            neigh = [ws.cell(row=r, column=c+i).value for i in range(0, 5)]
            res.append(((r,c), neigh))

if not res:
    print('No label matches found; dumping a 30x10 preview:')
    for r in range(1, 31):
        row_vals = [ws.cell(row=r, column=c).value for c in range(1, 11)]
        print(r, row_vals)
else:
    for (r,c), neigh in res:
        print(f'@({r},{c}) ->', neigh)

