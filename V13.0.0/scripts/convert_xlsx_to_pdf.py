from pathlib import Path
import sys
sys.path.append(str(Path('app')))

from utils.libreoffice_export import ensure_libreoffice, xlsx_to_pdf


def main():
    xlsx_dir = Path('out/invoices/xlsx')
    pdf_dir = Path('out/invoices/pdf')
    pdf_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(xlsx_dir.glob('*.xlsx'))
    if not files:
        print('No XLSX files to convert in', xlsx_dir)
        return

    soffice = ensure_libreoffice(auto_install=True, progress_cb=lambda m: print('[LibreOffice]', m))
    if not soffice:
        print('ERROR: LibreOffice not available after attempted install.')
        sys.exit(1)

    ok = 0
    for f in files:
        out_pdf = pdf_dir / (f.stem + '.pdf')
        try:
            print('Converting:', f.name, '->', out_pdf.name)
            xlsx_to_pdf(f, out_pdf, soffice_path=soffice)
            ok += 1
        except Exception as e:
            print('Failed to convert', f.name, '->', e)
    print('Converted PDFs:', ok, 'of', len(files))

    # Create a single zip with all PDFs
    import zipfile
    zip_path = pdf_dir / 'all_pdfs.zip'
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(pdf_dir.glob('*.pdf')):
            zf.write(p, arcname=p.name)
    print('ZIP created at', zip_path)


if __name__ == '__main__':
    main()

