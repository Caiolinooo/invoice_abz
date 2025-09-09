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
    """Best-effort write of meta values by scanning labels in the given worksheet.
    Looks for label cells (Invoice No/Date/Call Off) and writes the provided value
    to the cell on the right (or just below-right) when found.
    """
    labels = []
    if invoice_no is not None:
        labels.append(('invoice_no', ['invoice no', 'invoice number', 'invoice #'], invoice_no))
    if invoice_date is not None:
        labels.append(('invoice_date', ['invoice date', 'date'], invoice_date))
    if call_off is not None:
        labels.append(('call_off', ['call off', 'call-off', 'calloff'], call_off))

    for key, keys, value in labels:
        kset = [k.lower() for k in keys]
        written = False
        for r in range(1, 120):
            for c in range(1, 30):
                v = ws.cell(row=r, column=c).value
                if v is None:
                    continue
                s = str(v).strip().lower()
                if any(k in s for k in kset):
                    # try to write to the right
                    for dc in range(1, 6):
                        tgt = ws.cell(row=r, column=c+dc)
                        if tgt.value in (None, ''):
                            tgt.value = value
                            written = True
                            break
                    if not written:
                        # try below to the right
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
