from pathlib import Path
from typing import List, Dict
from openpyxl import load_workbook

# Import compatible with both package and script usage
try:
    from app.utils.excel_abz_template import find_invoice_table_coords, set_invoice_meta  # type: ignore
except ModuleNotFoundError:
    from utils.excel_abz_template import find_invoice_table_coords, set_invoice_meta  # type: ignore


def generate_from_abz_template(
    abz_xlsx: Path,
    template_sheet_name: str,
    employee_name: str,
    line_items: List[Dict],
    out_dir: Path,
    invoice_date: str = None,
    invoice_no: str = None,
    call_off: str = None,
) -> Path:
    """
    Clone the given template sheet from the ABZ workbook and fill the Services table.
    line_items: list of dicts with keys: description, unit_price, quantity, final
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    wb = load_workbook(abz_xlsx)
    if template_sheet_name not in wb.sheetnames:
        raise ValueError(f"Template sheet {template_sheet_name} not found")
    tpl = wb[template_sheet_name]

    # Duplicate the template inside the same workbook
    ws = wb.copy_worksheet(tpl)
    ws.title = f"{employee_name}_Invoice"

    # Write meta values by scanning for labels in the template
    set_invoice_meta(ws, invoice_no=invoice_no, invoice_date=invoice_date, call_off=call_off)

    # Locate service table coordinates
    coords = find_invoice_table_coords(abz_xlsx, template_sheet_name)
    if not coords:
        # fallback: try again using the copied sheet name (same layout)
        coords = find_invoice_table_coords(abz_xlsx, ws.title) if hasattr(ws, 'title') else {}
    if not coords:
        # if still not found, do nothing (save raw copy)
        out_path = out_dir / f"{employee_name.replace(' ', '_')}_Invoice.xlsx"
        wb.save(out_path)
        return out_path

    header_row = coords['header_row'][0]
    first_row = coords['first_data_row']
    services_col = coords['services_col']
    unit_col = coords['unit_col']
    qty_col = coords['qty_col']
    final_col = coords['final_col']

    # Normalize to exactly 3 fixed rows: Service, Additional, Expenses
    def _partition_items(items):
        service = None
        additional = None
        expenses = None
        for it in items or []:
            d = str(it.get('description') or '').lower()
            if 'brazilian payroll additional' in d:
                additional = it
            elif 'expense' in d:
                expenses = it
            else:
                service = it
        return service or {}, additional or {}, expenses or {}

    srv, addi, exp = _partition_items(line_items)

    # Clear existing data rows (e.g., 10 rows)
    for r in range(first_row, first_row + 20):
        ws.cell(row=r, column=services_col).value = None
        ws.cell(row=r, column=unit_col).value = None
        ws.cell(row=r, column=qty_col).value = None
        ws.cell(row=r, column=final_col).value = None

    # Row 1: Service (can be zero)
    r = first_row
    ws.cell(row=r, column=services_col).value = srv.get('description') or 'Service'
    if srv.get('unit_price') is not None:
        cell = ws.cell(row=r, column=unit_col)
        cell.value = round(float(srv.get('unit_price')), 2)
        cell.number_format = "0.00"
    if srv.get('quantity') is not None:
        # Se preferir 0.00, descomente a linha de number_format
        qcell = ws.cell(row=r, column=qty_col)
        qcell.value = float(srv.get('quantity'))
        # qcell.number_format = "0.00"
    if srv.get('final') is not None:
        fcell = ws.cell(row=r, column=final_col)
        fcell.value = round(float(srv.get('final')), 2)
        fcell.number_format = "£#,##0.00"

    # Row 2: Additional
    r += 1
    ws.cell(row=r, column=services_col).value = 'Brazilian Payroll Additional'
    if addi.get('final') is not None:
        acell = ws.cell(row=r, column=final_col)
        acell.value = round(float(addi.get('final')), 2)
        acell.number_format = "£#,##0.00"

    # Row 3: Expenses
    r += 1
    ws.cell(row=r, column=services_col).value = 'Expenses'
    if exp.get('final') is not None:
        ecell = ws.cell(row=r, column=final_col)
        ecell.value = round(float(exp.get('final')), 2)
        ecell.number_format = "£#,##0.00"

    # Save to a new workbook path (keep other sheets to preserve formulas and named ranges)
    out_path = out_dir / f"{employee_name.replace(' ', '_')}_Invoice.xlsx"
    wb.save(out_path)
    return out_path

