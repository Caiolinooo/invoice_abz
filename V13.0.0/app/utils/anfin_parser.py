from pathlib import Path
from typing import Dict, Tuple, Optional
from openpyxl import load_workbook
import pandas as pd


def _scan_row_for_label(ws, label_substr: str, max_rows: int = 150, max_cols: int = 25) -> Optional[Tuple[int, int]]:
    label_substr = label_substr.lower()
    for r in range(1, max_rows + 1):
        for c in range(1, max_cols + 1):
            v = ws.cell(row=r, column=c).value
            if v is None:
                continue
            if label_substr in str(v).strip().lower():
                return r, c
    return None


def _row_numeric(ws, row: int, max_cols: int = 25, prefer_currency: Optional[str] = None) -> Optional[float]:
    """Return a numeric in the row, preferring cells whose number_format contains prefer_currency
    (e.g., '£' or 'R$'). If none matches, returns the rightmost numeric in the row.
    """
    last_num = None
    last_num_col = None
    for c in range(1, max_cols + 1):
        cell = ws.cell(row=row, column=c)
        val = cell.value
        if isinstance(val, (int, float)):
            fmt = str(getattr(cell, 'number_format', '') or '')
            if prefer_currency and prefer_currency in fmt:
                return float(val)
            last_num = float(val)
            last_num_col = c
    return last_num


def _brl_to_gbp(total_brl: float, rate: float) -> Optional[float]:
    """
    Convert BRL to GBP given an exchange rate that may be expressed as either:
    - GBP per BRL (e.g., 0.1363)  => GBP = BRL * rate
    - BRL per GBP (e.g., 7.27)    => GBP = BRL / rate
    Use a threshold to infer direction.
    """
    if rate is None:
        return None
    if rate <= 0:
        return None
    if rate >= 2.5:  # very likely BRL per GBP
        return float(total_brl) / float(rate)
    else:  # likely GBP per BRL
        return float(total_brl) * float(rate)


def extract_individual_totals(anfin_path: Path) -> Dict[str, Dict[str, float]]:
    """
    For each individual sheet (Barbara, Daniel, ...), find:
      - Exchange Rate (could be BRL/GBP or GBP/BRL)
      - TOTAL in GBP for Brazilian Payroll Additionals
    Returns dict[name] = { 'exchange_rate': rate_detected, 'additional_gbp': total_gbp }
    """
    wb = load_workbook(anfin_path, data_only=True)
    results: Dict[str, Dict[str, float]] = {}
    for sn in wb.sheetnames:
        low = sn.lower()
        if low in ('info for becky', 'payroll', 'costs', ' check2'):
            continue
        ws = wb[sn]
        name = sn

        # Locate label rows
        pos_total_gbp = _scan_row_for_label(ws, 'total in gbp')
        pos_rate = _scan_row_for_label(ws, 'exchange rate')
        pos_total_brl = (
            _scan_row_for_label(ws, 'total in brl')
            or _scan_row_for_label(ws, 'total r$')
            or _scan_row_for_label(ws, 'total rs')
            or _scan_row_for_label(ws, 'total brl')
        )

        # Read values
        t_gbp = None
        if pos_total_gbp:
            t_gbp = _row_numeric(ws, pos_total_gbp[0], prefer_currency='£') or _row_numeric(ws, pos_total_gbp[0])

        rate = None
        if pos_rate:
            # first try right-adjacent cells, then same row
            r, c = pos_rate
            for dc in range(1, 8):
                val = ws.cell(row=r, column=c + dc).value
                if isinstance(val, (int, float)):
                    rate = float(val)
                    break
            if rate is None:
                rate = _row_numeric(ws, r)

        t_brl = None
        if pos_total_brl:
            t_brl = _row_numeric(ws, pos_total_brl[0], prefer_currency='R$') or _row_numeric(ws, pos_total_brl[0])

        # Compute GBP from BRL+rate when needed or when confusion is likely
        if (t_gbp is None or (t_gbp is not None and t_gbp < 2.0)) and (t_brl is not None and rate is not None):
            t_gbp_calc = _brl_to_gbp(t_brl, rate)
            if t_gbp_calc is not None:
                t_gbp = t_gbp_calc

        # Fallbacks
        if rate is None:
            rate = 0.1363  # fallback typical GBP/BRL
        if t_gbp is None:
            t_gbp = 0.0

        results[name] = {
            'exchange_rate': float(rate),
            'additional_gbp': float(t_gbp),
        }

    return results


def extract_costs_gbp(anfin_path: Path, exchange_rates: Dict[str, float]) -> Dict[str, float]:
    """
    Parse the Costs sheet and sum cost columns per employee. Values there appear in BRL;
    convert to GBP using the individual's exchange rate direction (BRL/GBP vs GBP/BRL) inferred above.
    """
    wb = load_workbook(anfin_path, data_only=True)
    if 'Costs' not in wb.sheetnames:
        return {}
    ws = wb['Costs']

    # find header row (row that contains 'Flights' and 'Training')
    header_row = None
    flights_col = None
    training_col = None
    name_col = None

    for r in range(1, 40):
        vals = [ws.cell(row=r, column=c).value for c in range(1, 30)]
        lower = [str(v).strip().lower() if v is not None else '' for v in vals]
        if any('flights' in v for v in lower) and any('training' in v for v in lower):
            header_row = r
            for c, v in enumerate(lower, start=1):
                if 'name' == v:
                    name_col = c
                if 'flights' in v and flights_col is None:
                    flights_col = c
                if 'training' in v:
                    training_col = c
            break

    if header_row is None or name_col is None or flights_col is None or training_col is None:
        return {}

    results: Dict[str, float] = {}
    r = header_row + 1
    while True:
        values = [ws.cell(row=r, column=c).value for c in range(1, training_col + 1)]
        if all(v is None for v in values):
            break
        name = ws.cell(row=r, column=name_col).value
        if name:
            total_brl = 0.0
            for c in range(flights_col, training_col + 1):
                val = ws.cell(row=r, column=c).value
                if isinstance(val, (int, float)):
                    total_brl += float(val)
            rate = exchange_rates.get(str(name))
            if rate is None:
                rate = next((v for k, v in exchange_rates.items() if str(k).lower().startswith(str(name).lower()[:5])), 0.1363)
            gbp = _brl_to_gbp(total_brl, float(rate)) if total_brl else 0.0
            results[str(name)] = float(gbp or 0.0)
        r += 1
        if r - header_row > 200:
            break

    return results

