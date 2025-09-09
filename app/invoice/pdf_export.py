from pathlib import Path
from typing import Optional


def export_sheet_to_pdf_with_excel(xlsx_path: Path, sheet_name: Optional[str], out_pdf: Path) -> Optional[Path]:
    """
    Export a specific sheet (or the active/only sheet if sheet_name is None) of an XLSX to PDF
    using local Microsoft Excel via COM automation. Returns out_pdf on success, None if
    Excel/pywin32 is not available.
    """
    try:
        import win32com.client  # type: ignore
    except Exception:
        return None

    xlsx_path = Path(xlsx_path).absolute()
    out_pdf = Path(out_pdf).absolute()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    try:
        wb = excel.Workbooks.Open(str(xlsx_path))
        try:
            if sheet_name:
                # Select the sheet by name (case-insensitive)
                try:
                    ws = wb.Sheets(sheet_name)
                except Exception:
                    for sh in wb.Sheets:
                        if str(sh.Name).lower() == sheet_name.lower():
                            ws = sh
                            break
                    else:
                        raise
                ws.Select()
                ws.ExportAsFixedFormat(0, str(out_pdf))  # 0 = xlTypePDF
            else:
                # Export active sheet (or all)
                wb.ActiveSheet.ExportAsFixedFormat(0, str(out_pdf))
        finally:
            wb.Close(SaveChanges=False)
    finally:
        excel.Quit()
    return out_pdf

