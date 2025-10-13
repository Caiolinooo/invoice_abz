from pathlib import Path
import sys
sys.path.append(str(Path('app')))

from invoice.pdf_export import export_sheet_to_pdf_with_excel

xlsx_dir = Path('out/invoices/xlsx')
pdf_dir = Path('out/invoices/pdf')
pdf_dir.mkdir(parents=True, exist_ok=True)

files = sorted(xlsx_dir.glob('*.xlsx'))
if not files:
    print('No XLSX files found in', xlsx_dir)
    raise SystemExit(0)

ok = 0
fail = 0
for f in files:
    # each generated workbook contains only one invoice sheet; export active sheet
    out_pdf = pdf_dir / (f.stem + '.pdf')
    res = export_sheet_to_pdf_with_excel(f, None, out_pdf)
    if res is None:
        print('\nERROR: Could not export to PDF. Microsoft Excel automation (pywin32) not available.')
        print('Please install:  pip install pywin32  and ensure Excel is installed on this machine.')
        raise SystemExit(1)
    else:
        print('Exported:', res)
        ok += 1

print(f'PDF export complete. {ok} files.')

