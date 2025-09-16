from pathlib import Path
from typing import List, Dict
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.styles.borders import Border, Side
from openpyxl.worksheet.page import PageMargins

# Import compatible with both package and script usage
try:
    from app.utils.excel_abz_template import find_invoice_table_coords, set_invoice_meta  # type: ignore
    from app.utils.filename_standardizer import generate_standardized_filename  # type: ignore
    from app.invoice.professional_generator import InvoiceProfessionalGenerator  # type: ignore
except ModuleNotFoundError:
    from utils.excel_abz_template import find_invoice_table_coords, set_invoice_meta  # type: ignore
    from utils.filename_standardizer import generate_standardized_filename  # type: ignore
    from invoice.professional_generator import InvoiceProfessionalGenerator  # type: ignore


def generate_from_abz_template(
    abz_xlsx: Path,
    template_sheet_name: str,
    employee_name: str,
    line_items: List[Dict],
    out_dir: Path,
    invoice_date: str = None,
    invoice_no: str = None,
    call_off: str = None,
    use_default_template: bool = False,
) -> Path:
    """
    Clone the given template sheet from the ABZ workbook and fill the Services table.
    line_items: list of dicts with keys: description, unit_price, quantity, final
    use_default_template: if True, use built-in default template instead of ABZ template
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    if use_default_template:
        # Use professional generator instead of template
        print(f"🎨 Using professional invoice generator for {employee_name}")

        # Generate filename
        filename = generate_standardized_filename(
            employee_name=employee_name,
            invoice_no=invoice_no,
            invoice_date=invoice_date
        )
        output_path = out_dir / filename

        # Create professional invoice
        generator = InvoiceProfessionalGenerator()
        result_path = generator.create_invoice(
            employee_name=employee_name,
            line_items=line_items,
            output_path=output_path,
            invoice_date=invoice_date,
            invoice_no=invoice_no,
            call_off=call_off
        )

        print(f"✅ Professional invoice created: {result_path}")
        return result_path
    else:
        # Use template from ABZ workbook (original behavior)
        wb = load_workbook(abz_xlsx)
        if template_sheet_name not in wb.sheetnames:
            raise ValueError(f"Template sheet {template_sheet_name} not found")
        tpl = wb[template_sheet_name]

    # Use the template sheet directly to preserve images/shapes/header-footer
    ws = tpl
    try:
        ws.title = f"{employee_name}_Invoice"[:31]  # Excel sheet name max 31 chars
    except Exception:
        pass

    # Write meta values by scanning for labels in the template
    set_invoice_meta(ws, invoice_no=invoice_no, invoice_date=invoice_date, call_off=call_off)

    # Locate service table coordinates
    if use_default_template:
        # For default template, try to find any _invoice sheet in ABZ for coordinate detection
        abz_wb = load_workbook(abz_xlsx)
        invoice_sheets = [s for s in abz_wb.sheetnames if s.lower().endswith('_invoice')]
        if invoice_sheets:
            coords = find_invoice_table_coords(abz_xlsx, invoice_sheets[0])
        else:
            # No template sheets in ABZ - use hardcoded coordinates for standard ABZ layout
            coords = {
                'header_row': (9, 1),    # Header at row 9
                'services_col': 1,       # Column A
                'unit_col': 2,           # Column B
                'qty_col': 3,            # Column C
                'final_col': 4,          # Column D
                'first_data_row': 10     # Row 10 (typical start)
            }
            print(f"🔧 No template sheets in ABZ, using default coordinates: {coords}")
        abz_wb.close()
    else:
        # Original behavior for ABZ templates
        coords = find_invoice_table_coords(abz_xlsx, template_sheet_name)
        if not coords:
            # fallback: try again using the copied sheet name (same layout)
            coords = find_invoice_table_coords(abz_xlsx, ws.title) if hasattr(ws, 'title') else {}

    if not coords:
        # if still not found, do nothing (save raw copy)
        filename = generate_standardized_filename(
            employee_name=employee_name,
            invoice_no=invoice_no,
            invoice_date=invoice_date,
            abz_path=abz_xlsx,
            extension="xlsx"
        )
        out_path = out_dir / filename
        wb.save(out_path)
        return out_path

    header_row = coords['header_row'][0]
    first_row = coords['first_data_row']
    services_col = coords['services_col']
    unit_col = coords['unit_col']
    qty_col = coords['qty_col']
    final_col = coords['final_col']

    # Center the header titles to match the visual spec (including merged headers)
    try:
        for cidx in range(services_col, final_col + 1):
            cell = ws.cell(row=header_row, column=cidx)
            cell.alignment = Alignment(horizontal='center', vertical='center')
        # Ensure merged header cells are centered by setting the anchor (top-left) cell
        try:
            for mr in getattr(ws, 'merged_cells', []).ranges:
                if mr.min_row <= header_row <= mr.max_row and not (mr.max_col < services_col or mr.min_col > final_col):
                    anchor = ws.cell(row=mr.min_row, column=mr.min_col)
                    anchor.alignment = Alignment(horizontal='center', vertical='center')
        except Exception:
            pass
    except Exception:
        pass

    # Prepare list of rows to write exactly as received (support multiple services)
    items_to_write = list(line_items or [])

    # Preserve merged cells defined by the template to keep layout/spacing exact.
    # We no longer unmerge inside the table; when writing values, we always target
    # simple (non-merged) numeric columns, which in the template are individual cells.
    # This avoids introducing extra grid lines and spacing issues in the exported PDF.

    # Clear only numeric columns in data rows (preserve descriptions/layout from template)
    for r in range(first_row, first_row + 25):
        # Preserve original alignment/row heights from the template (do not force wrap)
        # sc = ws.cell(row=r, column=services_col)
        # leave as-is to keep spacing identical to the template
        for c in (unit_col, qty_col, final_col):
            try:
                cell = ws.cell(row=r, column=c)
                cell.value = None
                # alignment rules: Unit = right, Qty = center, Final = center
                # Center all numeric columns per spec (Final, Qty, Unit)
                cell.alignment = Alignment(horizontal='center', vertical='center', shrinkToFit=True)
            except Exception:
                pass
        # hard-clear any stray values to the right of Final Price (avoid vazamento)
        try:
            for c in range(final_col + 1, final_col + 21):
                ws.cell(row=r, column=c).value = None
        except Exception:
            pass

    # Map items into existing description rows
    def _lower(v):
        try:
            return str(v or '').strip().lower()
        except Exception:
            return ''

    service_items = [it for it in items_to_write if ('additional' not in _lower(it.get('description')) and 'expense' not in _lower(it.get('description')))]
    add_item = next((it for it in items_to_write if 'additional' in _lower(it.get('description'))), None)
    exp_item = next((it for it in items_to_write if 'expense' in _lower(it.get('description'))), None)

    sidx = 0
    total_sum = 0.0
    last_row_written = first_row
    total_row_idx = None
    for r in range(first_row, first_row + 25):
        desc_cell = ws.cell(row=r, column=services_col)
        d = _lower(desc_cell.value)
        if not d:
            # stop at first fully empty row in the table block
            continue
        if 'total amount payable' in d:
            last_row_written = r
            total_row_idx = r
            break
        if 'additional' in d:
            if add_item and add_item.get('final') is not None:
                f = ws.cell(row=r, column=final_col)
                fv = round(float(add_item['final']), 2)
                f.value = fv
                f.number_format = "£#,##0.00"
                f.alignment = Alignment(horizontal='center', vertical='center', shrinkToFit=True)
                total_sum += float(fv)
            # mark unit/qty as N/A (centered)
            u_cell = ws.cell(row=r, column=unit_col)
            q_cell = ws.cell(row=r, column=qty_col)
            u_cell.value = 'N/A'
            q_cell.value = 'N/A'
            u_cell.alignment = Alignment(horizontal='center', vertical='center', shrinkToFit=True)
            q_cell.alignment = Alignment(horizontal='center', vertical='center', shrinkToFit=True)
            last_row_written = max(last_row_written, r)
            continue
        if 'expense' in d:
            if exp_item and exp_item.get('final') is not None:
                f = ws.cell(row=r, column=final_col)
                fv = round(float(exp_item['final']), 2)
                f.value = fv
                f.number_format = "£#,##0.00"
                f.alignment = Alignment(horizontal='center', vertical='center', shrinkToFit=True)
                total_sum += float(fv)
            # N/A centered as well
            u_cell = ws.cell(row=r, column=unit_col)
            q_cell = ws.cell(row=r, column=qty_col)
            u_cell.value = 'N/A'
            q_cell.value = 'N/A'
            u_cell.alignment = Alignment(horizontal='center', vertical='center', shrinkToFit=True)
            q_cell.alignment = Alignment(horizontal='center', vertical='center', shrinkToFit=True)
            last_row_written = max(last_row_written, r)
            continue
        # service-line (anything else)
        if sidx < len(service_items):
            it = service_items[sidx]
            sidx += 1
            # Override the description in the template with our clean description
            if it.get('description'):
                desc_cell.value = it['description']
            if it.get('unit_price') is not None:
                u = ws.cell(row=r, column=unit_col)
                u.value = round(float(it['unit_price']), 2)
                u.number_format = "£#,##0.00"
                u.alignment = Alignment(horizontal='center', vertical='center', shrinkToFit=True)
            if it.get('quantity') is not None:
                q = ws.cell(row=r, column=qty_col)
                try:
                    q.value = float(it['quantity'])
                except Exception:
                    q.value = it['quantity']
                q.alignment = Alignment(horizontal='center', vertical='center', shrinkToFit=True)
            if it.get('final') is not None:
                f = ws.cell(row=r, column=final_col)
                fv = round(float(it['final']), 2)
                f.value = fv
                f.number_format = "£#,##0.00"
                f.alignment = Alignment(horizontal='center', vertical='center', shrinkToFit=True)
                total_sum += float(fv)
            last_row_written = max(last_row_written, r)
        else:
            # if no data for this row, leave as is (template keeps text like second role)
            pass

    # Write total amount payable explicitly (do not rely on template formulas)
    if total_row_idx:
        tf = ws.cell(row=total_row_idx, column=final_col)
        tf.value = round(total_sum, 2)
        tf.number_format = "£#,##0.00"
        tf.alignment = Alignment(horizontal='center', vertical='center', shrinkToFit=True)

    # Keep original borders from the template. Do not force new horizontal lines,
    # to avoid extra inner rules that caused visual artifacts in the PDF.

    # Keep only the generated invoice sheet to avoid exporting the whole workbook to PDF
    try:
        for sh_name in list(wb.sheetnames):
            if sh_name != ws.title:
                wb.remove(wb[sh_name])
        # ensure our invoice sheet is active
        try:
            wb.active = wb.sheetnames.index(ws.title)
        except Exception:
            pass
    except Exception:
        # If anything goes wrong, proceed without pruning (worst case: larger PDF)
        pass

    # Define print area: prefer template's own print area; only set if missing
    try:
        from openpyxl.utils import get_column_letter
        existing = getattr(ws, 'print_area', None)
        if existing:
            pr = str(existing)
        else:
            # Detect the content bounds to avoid capturing stray cells on the right
            left_col = 1
            # Find the rightmost non-empty cell (scan a safe window)
            rightmost = 1
            try:
                max_scan_row = min(ws.max_row, int(first_row) + 240)
                max_scan_col = max(int(final_col) + 6, 40)
                for r in range(1, max_scan_row + 1):
                    for c in range(1, max_scan_col + 1):
                        if ws.cell(row=r, column=c).value not in (None, ""):
                            if c > rightmost:
                                rightmost = c
            except Exception:
                rightmost = max(int(final_col), 20)
            right_col = rightmost
            top_row = 1
            bottom_row = min(max(ws.max_row, int(first_row) + 100), int(first_row) + 240)
            pr = f"{get_column_letter(left_col)}{top_row}:{get_column_letter(right_col)}{bottom_row}"
        try:
            ws.print_area = pr
        except Exception:
            ws.print_area = pr
        # Page setup for an A4, centered output that fills the page nicely
        try:
            ws.page_setup.orientation = 'portrait'
            # A4 paper size code in Excel is 9
            ws.page_setup.paperSize = 9
            ws.page_setup.fitToPage = True
            ws.page_setup.fitToWidth = 1
            # Let height flow naturally (0 = automatic in Excel)
            ws.page_setup.fitToHeight = 0
        except Exception:
            pass
        try:
            ws.print_options.horizontalCentered = True
        except Exception:
            pass
        try:
            ws.print_options.verticalCentered = False
        except Exception:
            pass
        try:
            ws.page_margins = PageMargins(left=0.5, right=0.5, top=0.6, bottom=0.6, header=0.3, footer=0.3)
        except Exception:
            pass
    except Exception:
        pass

    # Save to a new workbook path containing only this invoice sheet
    # Use standardized filename format: "ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}.xlsx"
    filename = generate_standardized_filename(
        employee_name=employee_name,
        invoice_no=invoice_no,
        invoice_date=invoice_date,
        abz_path=abz_xlsx,
        extension="xlsx"
    )
    out_path = out_dir / filename
    wb.save(out_path)
    return out_path

