from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from openpyxl import load_workbook


EXPECTED_COLS = [
    'Name', 'Position', 'Charge Rate (GBP)', 'Days',
    'Brazilian Payroll Additionals (GBP)', 'Expenses', 'Monthly Total (GBP)'
]


def _find_header_row(df: pd.DataFrame) -> Optional[int]:
    """Return the row index that looks like the proper header row."""
    for i in range(min(80, len(df))):
        row_vals = [str(x).strip() for x in df.iloc[i].tolist()]
        low = [v.lower() for v in row_vals]
        if 'name' in low and 'position' in low and 'charge rate' in low:
            return i
    return None


def _best_text_col(df: pd.DataFrame) -> Optional[str]:
    """Pick the column that most looks like a names column (strings, many spaces)."""
    best = None
    best_score = -1
    for c in df.columns:
        series = df[c]
        texts = series.dropna().astype(str)
        if texts.empty:
            continue
        score = (texts.apply(lambda s: (' ' in s) and (3 < len(s) < 80)).mean())
        if score > best_score:
            best = c
            best_score = score
    return best


def _read_with_openpyxl(xlsx_path: Path, sheet_name: str) -> pd.DataFrame:
    wb = load_workbook(filename=xlsx_path, data_only=True)
    ws = wb[sheet_name]
    # detect header row
    header_row = None
    for r in range(1, 200):
        vals = [ws.cell(row=r, column=c).value for c in range(1, 16)]
        lower = [str(v).strip().lower() if v is not None else '' for v in vals]
        if all(any(k in cell for cell in lower) for k in ['name', 'position', 'charge rate']):
            header_row = r
            break
    if not header_row:
        raise RuntimeError('Could not detect header row in Charge Rate sheet')

    rows = []
    for r in range(header_row + 1, header_row + 200):
        row = [ws.cell(row=r, column=c).value for c in range(1, 12)]
        if all(v is None for v in row[:3]):
            # stop when empty block reached (after totals)
            break
        rows.append(row)

    # build dataframe with fixed columns indices from observed layout
    df = pd.DataFrame(rows, columns=[
        'Name', 'Position', 'Charge Rate (GBP)', 'Days',
        'Brazilian Payroll Additionals (GBP)', 'Expenses', 'Monthly Total (GBP)',
        'C8', 'C9', 'C10', 'Check'
    ])
    # clean
    df = df.dropna(how='all')
    # keep only logical rows (Name or Position present)
    mask = df['Name'].notna() | df['Position'].notna() | df['Charge Rate (GBP)'].notna()
    df = df.loc[mask]
    # coerce numbers
    for col in ['Charge Rate (GBP)', 'Days', 'Brazilian Payroll Additionals (GBP)', 'Expenses', 'Monthly Total (GBP)']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    # forward-fill names for multi-position entries
    df['Name'] = df['Name'].ffill()
    # keep expected columns
    return df[[c for c in EXPECTED_COLS if c in df.columns]]


def read_charge_rate_table(xlsx_path: Path, sheet_name: str = 'Charge Rate') -> pd.DataFrame:
    # try pandas-first
    try:
        xls = pd.ExcelFile(xlsx_path)
        raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        header_row = _find_header_row(raw)
        if header_row is None:
            header_row = raw.iloc[:60].apply(lambda r: r.notna().sum(), axis=1).idxmax()
        df = pd.read_excel(xls, sheet_name=sheet_name, header=header_row)
        df = df.iloc[:, :14]
        cols = [str(c).strip() for c in df.columns]
        mapping = {}
        for c in cols:
            lc = c.lower()
            if 'name' == lc:
                mapping[c] = 'Name'
            elif 'position' in lc or 'function' in lc:
                mapping[c] = 'Position'
            elif 'charge rate' in lc or 'charge rates' in lc:
                mapping[c] = 'Charge Rate (GBP)'
            elif lc in ('days', 'day', 'qty', 'quantity'):
                mapping[c] = 'Days'
            elif 'brazilian payroll' in lc and 'gbp' in lc:
                mapping[c] = 'Brazilian Payroll Additionals (GBP)'
            elif 'expenses' in lc:
                mapping[c] = 'Expenses'
            elif ('monthly total' in lc) or ('total (gbp)' in lc):
                mapping[c] = 'Monthly Total (GBP)'
            else:
                mapping[c] = c
        df = df.rename(columns=mapping)
        if 'Name' not in df.columns:
            name_col = _best_text_col(df)
            if name_col:
                df = df.rename(columns={name_col: 'Name'})
        df = df.dropna(how='all')
        conds = []
        if 'Name' in df.columns:
            conds.append(df['Name'].notna())
        if 'Position' in df.columns:
            conds.append(df['Position'].notna())
        if 'Charge Rate (GBP)' in df.columns:
            conds.append(df['Charge Rate (GBP)'].notna())
        mask_core = pd.Series([False] * len(df))
        for c in conds:
            mask_core = mask_core | c
        df = df.loc[mask_core]
        for num_col in ['Charge Rate (GBP)', 'Days', 'Brazilian Payroll Additionals (GBP)', 'Expenses', 'Monthly Total (GBP)']:
            if num_col in df.columns:
                df[num_col] = pd.to_numeric(df[num_col], errors='coerce').fillna(0.0)
        if 'Name' in df.columns:
            df['Name'] = df['Name'].ffill()
        keep = [c for c in EXPECTED_COLS if c in df.columns]
        # require at least 3 meaningful columns, otherwise fallback
        if len([c for c in keep if c != 'Name']) >= 2:
            return df[keep]
    except Exception:
        pass
    # fallback to openpyxl direct parsing (handles merged headers)
    return _read_with_openpyxl(xlsx_path, sheet_name)


def aggregate_employee(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-employee structure with individual service lines and totals.
    We keep multiple positions as separate service lines and also compute totals
    for Additional and Expenses.
    """
    if 'Name' not in df.columns:
        return pd.DataFrame(columns=['Name','Type','Description','Unit Price (GBP)','Quantity','Final Price (GBP)'])

    add_map = df.groupby('Name')['Brazilian Payroll Additionals (GBP)'].sum() if 'Brazilian Payroll Additionals (GBP)' in df.columns else {}
    exp_map = df.groupby('Name')['Expenses'].sum() if 'Expenses' in df.columns else {}

    records: List[Dict] = []
    for _, row in df.iterrows():
        name = row.get('Name')
        pos = row.get('Position')
        rate = float(row.get('Charge Rate (GBP)', 0) or 0)
        days = float(row.get('Days', 0) or 0)
        if (days > 0) and pos:
            records.append({
                'Name': name,
                'Type': 'service',
                'Description': f"{name} - {pos}",
                'Unit Price (GBP)': rate,
                'Quantity': days,
                'Final Price (GBP)': rate * days,
            })

    for name, add_val in getattr(add_map, 'items', lambda: [])():
        if add_val and add_val != 0:
            records.append({
                'Name': name,
                'Type': 'additional',
                'Description': 'Brazilian Payroll Additional',
                'Unit Price (GBP)': None,
                'Quantity': None,
                'Final Price (GBP)': float(add_val),
            })
    for name, exp_val in getattr(exp_map, 'items', lambda: [])():
        if exp_val and exp_val != 0:
            records.append({
                'Name': name,
                'Type': 'expenses',
                'Description': 'Expenses',
                'Unit Price (GBP)': None,
                'Quantity': None,
                'Final Price (GBP)': float(exp_val),
            })

    return pd.DataFrame.from_records(records)

