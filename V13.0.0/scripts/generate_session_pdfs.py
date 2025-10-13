from __future__ import annotations
from pathlib import Path
import json, uuid, zipfile
import sys
sys.path.append(str(Path('app')))

try:
    from app.api.server import _norm  # type: ignore
    from app.api.server import _build_preview  # type: ignore
    from app.invoice.template_filler import generate_from_abz_template  # type: ignore
    from app.utils.libreoffice_export import ensure_libreoffice, xlsx_to_pdf  # type: ignore
except ModuleNotFoundError:
    from api.server import _norm  # type: ignore
    from api.server import _build_preview  # type: ignore
    from invoice.template_filler import generate_from_abz_template  # type: ignore
    from utils.libreoffice_export import ensure_libreoffice, xlsx_to_pdf  # type: ignore
from openpyxl import load_workbook
try:
    from app.invoice.pdf_rl import generate_pdf_invoice  # type: ignore
except ModuleNotFoundError:
    from invoice.pdf_rl import generate_pdf_invoice  # type: ignore


def main():
    root = Path('.')
    abz = next(x for x in (root/'DADOS').glob('*.xlsx') if 'ABZ' in x.name.upper())
    anfin = next(x for x in (root/'DADOS').glob('*.xlsx') if 'AN-FIN' in x.name.upper())

    sid = uuid.uuid4().hex
    sdir = Path('out')/ 'sessions' / sid
    (sdir/'xlsx').mkdir(parents=True, exist_ok=True)
    (sdir/'pdf').mkdir(parents=True, exist_ok=True)

    print('Session:', sid)
    print('ABZ:', abz)
    print('AN-FIN:', anfin)

    preview = _build_preview(abz, anfin)
    # Save meta for future reference
    (sdir / 'meta.json').write_text(json.dumps({'abz': str(abz), 'anfin': str(anfin), 'preview': preview}, ensure_ascii=False, indent=2), encoding='utf-8')

    wb = load_workbook(abz, read_only=True)
    sheets = wb.sheetnames
    invoice_sheets = [s for s in sheets if s.lower().endswith('_invoice')]

    soffice = ensure_libreoffice(auto_install=True, progress_cb=lambda m: print('[LibreOffice]', m))

    # Persistent invoice sequence for CLI generation (aligns with API behavior)
    seq_file = Path('out') / 'invoice_seq.json'
    try:
        seq = json.loads(seq_file.read_text(encoding='utf-8')) if seq_file.exists() else {"last": 0}
        last_used = int(seq.get('last', 0) or 0)
    except Exception:
        last_used = 0
    next_no = last_used + 1

    i = 0
    for name, pdata in preview.items():
        i += 1
        print(f'[{i}/{len(preview)}] Generating for', name)
        first = _norm(name.split()[0])
        tpl_candidates = [s for s in invoice_sheets if first in _norm(s)]
        items = list(pdata.get('items') or [])
        m = dict(pdata.get('meta') or {})

        if not tpl_candidates:
            print('  WARN: template not found for', name, '-> using fallback PDF')
            # fallback: direct ReportLab PDF
            pdf_path = (sdir/'pdf') / (name.replace(' ', '_') + '_Invoice.pdf')
            inv_no = str(next_no); next_no += 1
            generate_pdf_invoice(
                out_path=pdf_path,
                employee_name=name,
                items=items,
                invoice_no=inv_no,
                invoice_date=m.get('invoice_date'),
                call_off=m.get('call_off'),
                company_name='ABZ Group',
                client_name='Client',
            )
        else:
            tpl = tpl_candidates[0]
            inv_no = str(next_no); next_no += 1
            xlsx_path = generate_from_abz_template(
                abz_xlsx=abz,
                template_sheet_name=tpl,
                employee_name=name,
                line_items=items,
                out_dir=(sdir/'xlsx'),
                invoice_date=m.get('invoice_date'),
                invoice_no=inv_no,
                call_off=m.get('call_off'),
            )
            pdf_path = (sdir/'pdf') / (xlsx_path.stem + '.pdf')
            if soffice:
                xlsx_to_pdf(xlsx_path, pdf_path, soffice_path=soffice)
            else:
                print('  WARN: LibreOffice not available; skipping PDF for', name)

    wb.close()

    # Zip PDFs
    zip_path = sdir / 'session_{}_pdf.zip'.format(sid)
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted((sdir/'pdf').glob('*.pdf')):
            zf.write(p, arcname=p.name)
    print('ZIP created at', zip_path)
    # persist last used sequence (write back the last number assigned)
    try:
        seq_file.parent.mkdir(parents=True, exist_ok=True)
        seq_file.write_text(json.dumps({"last": next_no-1}, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
        pass



if __name__ == '__main__':
    main()

