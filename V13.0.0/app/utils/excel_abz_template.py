from pathlib import Path
from typing import Optional, Tuple, Dict
from openpyxl import load_workbook


def find_invoice_table_coords(xlsx_path: Path, sheet_name: str) -> Dict[str, Tuple[int, int]]:
    """
    Heurística: localizar cabeçalhos 'Services', 'Unit Price', 'Quantity', 'Final Price'
    e retornar as coordenadas (row, col) da primeira célula de dados logo abaixo dos cabeçalhos.
    Retorna dict com:
      - header_row
      - services_col, unit_col, qty_col, final_col
      - first_data_row
    """
    wb = load_workbook(filename=xlsx_path, data_only=True)
    ws = wb[sheet_name]

    target_headers = {
        'services': ['services'],
        'unit': ['unit price', 'unit'],
        'qty': ['quantity', 'qty'],
        'final': ['final price', 'final price (gbp)', 'amount']
    }

    header_row = None
    header_positions: Dict[str, Tuple[int, int]] = {}

    # varrer primeiras 100 linhas e 20 colunas
    for r in range(1, 120):
        row_vals = [ws.cell(row=r, column=c).value for c in range(1, 21)]
        lower = [str(v).strip().lower() if v is not None else '' for v in row_vals]
        # tentar detectar todos os cabeçalhos na mesma linha
        found = {}
        for c, val in enumerate(lower, start=1):
            for key, opts in target_headers.items():
                if key in found:
                    continue
                if any(opt == val for opt in opts):
                    found[key] = (r, c)
        if len(found) >= 3 and ('final' in found):
            header_row = r
            header_positions = found
            break

    if not header_row:
        return {}

    out = {
        'header_row': (header_row, 1),
        'services_col': header_positions.get('services', (header_row, 1))[1],
        'unit_col': header_positions.get('unit', (header_row, 2))[1],
        'qty_col': header_positions.get('qty', (header_row, 3))[1],
        'final_col': header_positions.get('final', (header_row, 4))[1],
        'first_data_row': header_row + 1,
    }
    return out




def get_invoice_meta(xlsx_path: Path, sheet_name: str) -> Dict[str, Optional[str]]:
    """
    Scan the template sheet for labels like 'Invoice No', 'Invoice Date', 'Call Off' / 'Call-Off'
    and return adjacent text values as strings. Best-effort heuristics.
    """
    from typing import Optional
    wb = load_workbook(filename=xlsx_path, data_only=True)
    ws = wb[sheet_name]

    labels = {
        'invoice_no': ['invoice no', 'invoice number', 'invoice #'],
        'invoice_date': ['invoice date', 'date'],
        'call_off': ['call off', 'call-off', 'calloff'],
    }

    def find_value_for(keys) -> Optional[str]:
        keys = [k.lower() for k in keys]
        # search grid
        for r in range(1, 120):
            for c in range(1, 21):
                v = ws.cell(row=r, column=c).value
                if v is None:
                    continue
                s = str(v).strip().lower()
                if any(k in s for k in keys):
                    # value to the right
                    for dc in range(1, 6):
                        val = ws.cell(row=r, column=c+dc).value
                        if val not in (None, ''):
                            return str(val)
                    # or below
                    for dr in range(1, 4):
                        val = ws.cell(row=r+dr, column=c+1).value
                        if val not in (None, ''):
                            return str(val)
        return None

    meta = {
        'invoice_no': find_value_for(labels['invoice_no']),
        'invoice_date': find_value_for(labels['invoice_date']),
        'call_off': find_value_for(labels['call_off']),
    }
    return meta



def set_invoice_meta(ws, invoice_no=None, invoice_date=None, call_off=None):
    """Write meta (Invoice No/Date/Call-Off) into the template in a predictable way.

    Behavior:
    - Always write into the cell immediately to the right of the label (c+1),
      overwriting any placeholder (e.g., '01') that might exist there.
    - Clear a couple of cells to the right to remove leftover placeholders and
      avoid duplicated values (e.g., '01 10/09/2025').
    - For invoice_date, normalize common formats (yyyy-mm-dd -> dd/mm/yyyy).
    """
    import re

    def _norm_date(val: str) -> str:
        if not val:
            return ''
        s = str(val).strip()
        # yyyy-mm-dd -> dd/mm/yyyy
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
        if m:
            y, mo, d = m.groups()
            return f"{d}/{mo}/{y}"
        # Try to extract first dd/mm/yyyy sequence if present
        m = re.search(r"(\d{2})[/-](\d{2})[/-](\d{4})", s)
        if m:
            d, mo, y = m.groups()
            return f"{d}/{mo}/{y}"
        return s

    labels = []
    if invoice_no is not None:
        labels.append(('invoice_no', ['invoice no', 'invoice number', 'invoice #'], str(invoice_no).strip()))
    if invoice_date is not None:
        labels.append(('invoice_date', ['invoice date', 'date'], _norm_date(invoice_date)))
    if call_off is not None:
        co_str = str(call_off).strip()
        if co_str and co_str.lower() not in ('none', 'null', 'n/a', 'nan', '-', ''):
            labels.append(('call_off', ['call off', 'call-off', 'calloff'], co_str))
        else:
            # Clear call_off field in template when empty
            labels.append(('call_off', ['call off', 'call-off', 'calloff'], ''))

    for key, keys, value in labels:
        kset = [k.lower() for k in keys]
        written = False
        for r in range(1, 120):
            for c in range(1, 30):
                cell = ws.cell(row=r, column=c)
                v = cell.value
                if v is None:
                    continue

                # Handle formulas that reference other sheets (common issue in templates)
                if cell.data_type == 'f' and key == 'invoice_date':
                    # If it's a formula referencing another sheet for invoice date, replace it
                    if '!' in str(v) and 'invoice' in str(v).lower():
                        # Replace the formula with the actual invoice date value
                        clean_value = (str(value).strip() if value is not None else '')
                        ws.cell(row=r, column=c).value = f"invoice date:{clean_value}"
                        written = True
                        break

                s = str(v).strip().lower()
                if any(k in s for k in kset):
                    # Normalize label and write values per spec
                    try:
                        # Clean base label (remove placeholders like 'xx/' or numbers after ':')
                        base_lbl = s.split(':')[0] + ':' if ':' in s else s
                        # Prepare cleaned value
                        clean_value = (str(value).strip() if value is not None else '')
                        if key == 'invoice_no':
                            import re as _re_val
                            # Remove prefixes like 'xx/' (any number of x) from user/template input
                            clean_value = _re_val.sub(r'^\s*x{1,5}\s*/\s*', '', clean_value, flags=_re_val.I)
                        if key == 'invoice_date':
                            # Write in the SAME cell with no space after ':'
                            ws.cell(row=r, column=c).value = f"{base_lbl}{clean_value}"
                            # Clear cells to the right to avoid duplicates
                            for dc in (1, 2, 3):
                                ws.cell(row=r, column=c+dc).value = None
                        else:
                            # Keep only the clean label in label cell (removes 'xx/' etc.)
                            ws.cell(row=r, column=c).value = base_lbl
                            # Clear placeholders to the right and write the value in c+1
                            for dc in (1, 2, 3):
                                ws.cell(row=r, column=c+dc).value = None
                            tgt = ws.cell(row=r, column=c+1)
                            tgt.value = clean_value
                        written = True
                    except Exception:
                        written = False
                    if not written:
                        # fallback: try below-right
                        for dr in range(1, 4):
                            tgt = ws.cell(row=r+dr, column=c+1)
                            if tgt.value in (None, ''):
                                tgt.value = value
                                written = True
                                break
                if written:
                    break
            if written:
                break
