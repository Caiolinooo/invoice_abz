from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from openpyxl import load_workbook


EXPECTED_COLS = [
    'Name', 'Position', 'Charge Rate (GBP)', 'Days',
    'Brazilian Payroll Additionals (GBP)', 'Expenses', 'Monthly Total (GBP)',
    'Exchange Rate'  # Nova coluna opcional
]


def _find_header_row(df: pd.DataFrame) -> Optional[int]:
    """Return the row index that looks like the proper header row.
    Be tolerant to variations like 'Charge Rate (GBP)', trailing spaces, etc.
    """
    for i in range(min(80, len(df))):
        row_vals = [str(x).strip() if x is not None else '' for x in df.iloc[i].tolist()]
        low = [v.lower() for v in row_vals]
        has_name = any(('name' in v) for v in low)
        has_position = any(('position' in v) or ('function' in v) for v in low)
        has_charge = any(('charge rate' in v) or ('charge rates' in v) for v in low)
        if has_name and has_position and has_charge:
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
        # Build mapping based on original column names, comparing with trimmed/lower variants
        mapping = {}
        for orig in list(df.columns):
            norm = str(orig).strip()
            lc = norm.lower()
            if lc == 'name':
                mapping[orig] = 'Name'
            elif ('position' in lc) or ('function' in lc):
                mapping[orig] = 'Position'
            elif ('charge rate' in lc) or ('charge rates' in lc):
                mapping[orig] = 'Charge Rate (GBP)'
            elif lc in ('days', 'day', 'qty', 'quantity'):
                mapping[orig] = 'Days'
            elif ('brazilian payroll' in lc) and ('gbp' in lc):
                mapping[orig] = 'Brazilian Payroll Additionals (GBP)'
            elif 'expenses' in lc:
                mapping[orig] = 'Expenses'
            elif ('monthly total' in lc) or ('total (gbp)' in lc):
                mapping[orig] = 'Monthly Total (GBP)'
            else:
                mapping[orig] = str(orig)
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

        # Extract days from Invoice sheets
        df = _extract_days_from_invoice_sheets(df, xlsx_path)



        keep = [c for c in EXPECTED_COLS if c in df.columns]
        # require at least 3 meaningful columns, otherwise fallback
        if len([c for c in keep if c != 'Name']) >= 2:
            return df[keep]
    except Exception:
        pass
    # fallback to openpyxl direct parsing (handles merged headers)
    df = _read_with_openpyxl(xlsx_path, sheet_name)

    # Calculate missing days from Monthly Total / Charge Rate
    if 'Days' in df.columns and 'Monthly Total (GBP)' in df.columns and 'Charge Rate (GBP)' in df.columns:
        calculated_count = 0
        for idx, row in df.iterrows():
            current_days = row.get('Days')
            monthly_total = row.get('Monthly Total (GBP)')
            charge_rate = row.get('Charge Rate (GBP)')
            name = row.get('Name', '')

            # Only calculate if Days is empty/zero and we have the required data
            if (pd.isna(current_days) or current_days is None or current_days == 0 or current_days == '') and \
               monthly_total and charge_rate and float(charge_rate) > 0 and float(monthly_total) > 0:

                calculated_days = float(monthly_total) / float(charge_rate)
                calculated_days = round(calculated_days, 2)

                df.at[idx, 'Days'] = calculated_days
                calculated_count += 1
                print(f"  Calculated days for '{name}': {calculated_days} (Monthly Total: {monthly_total} / Charge Rate: {charge_rate})")

        if calculated_count > 0:
            print(f"Calculated days for {calculated_count} employees using Monthly Total / Charge Rate")

    return df


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


def _extract_days_from_invoice_sheets(df: pd.DataFrame, xlsx_path: Path) -> pd.DataFrame:
    """
    Extract days worked from individual Invoice sheets and update the DataFrame.
    Robust approach:
      - Detect any sheet whose name contains 'invoice' (case-insensitive)
      - Use table header detection (find_invoice_table_coords) to locate the Quantity column
      - Read the first numeric value under the Quantity column (or sum if multiple found in short range)
      - Fallback to historical fixed cell (row=18, col=3) if headers are not detected
    """
    from openpyxl import load_workbook

    if 'Name' not in df.columns:
        return df

    try:
        # Late import to avoid circulars and support script runs
        try:
            from app.utils.excel_abz_template import find_invoice_table_coords  # type: ignore
        except Exception:
            from utils.excel_abz_template import find_invoice_table_coords  # type: ignore
        import re

        wb = load_workbook(xlsx_path, data_only=True)

        # Create a mapping of days by employee name
        days_mapping: Dict[str, float] = {}

        for sheet_name in wb.sheetnames:
            if 'invoice' not in str(sheet_name).lower():
                continue

            # Extract employee base name from sheet name (remove trailing 'invoice')
            employee_base_name = re.sub(r"(?i)[\s_-]*invoice.*$", "", str(sheet_name)).strip()
            if not employee_base_name:
                employee_base_name = str(sheet_name)

            try:
                ws = wb[sheet_name]

                # 1) Try to find table coords and Quantity column
                days_val: Optional[float] = None
                coords = {}
                try:
                    coords = find_invoice_table_coords(xlsx_path, sheet_name) or {}
                except Exception:
                    coords = {}

                def _to_float(v):
                    try:
                        if isinstance(v, (int, float)):
                            return float(v)
                        s = str(v).strip().replace(',', '.')
                        return float(s)
                    except Exception:
                        return None

                if coords and 'qty_col' in coords and 'first_data_row' in coords:
                    qty_col = int(coords['qty_col'])
                    start_row = int(coords.get('first_data_row') or 1)
                    end_row = min(start_row + 60, ws.max_row)
                    # take the first valid numeric under Quantity
                    for r in range(start_row, end_row + 1):
                        v = ws.cell(row=r, column=qty_col).value
                        fv = _to_float(v)
                        if fv is not None:
                            days_val = float(fv)
                            break

                # 2) If not found, search headers inline (Quantity/Qty) and read below
                if days_val is None:
                    header_pos = None
                    for r in range(1, 120):
                        for c in range(1, 21):
                            v = ws.cell(row=r, column=c).value
                            if v is None:
                                continue
                            s = str(v).strip().lower()
                            if s in ("quantity", "qty"):
                                header_pos = (r, c)
                                break
                        if header_pos:
                            break
                    if header_pos:
                        r0, c0 = header_pos
                        for r in range(r0 + 1, r0 + 80):
                            v = ws.cell(row=r, column=c0).value
                            fv = _to_float(v)
                            if fv is not None:
                                days_val = float(fv)
                                break

                # 3) Fallback to historical fixed cell (row=18, col=3)
                if days_val is None:
                    v = ws.cell(row=18, column=3).value
                    fv = _to_float(v)
                    if fv is not None:
                        days_val = float(fv)

                if days_val is not None and days_val >= 0:
                    days_mapping[employee_base_name] = days_val

            except Exception as e:
                print(f"Warning: Could not extract days from {sheet_name}: {e}")
                continue

        wb.close()

        # Update the DataFrame with extracted days using improved matching
        if days_mapping:
            print(f"Found days data for {len(days_mapping)} employees from Invoice sheets")

            # Create a more sophisticated matching system
            for idx, row in df.iterrows():
                full_name = str(row.get('Name', ''))
                matched_days = None
                matched_from = None

                # Try exact matching first
                for sheet_base_name, days_val in days_mapping.items():
                    if sheet_base_name == full_name:
                        matched_days = days_val
                        matched_from = sheet_base_name
                        break

                # Try partial matching with different strategies
                if matched_days is None:
                    for sheet_base_name, days_val in days_mapping.items():
                        # Strategy 1: Check if sheet name is contained in full name
                        if sheet_base_name.lower() in full_name.lower():
                            matched_days = days_val
                            matched_from = sheet_base_name
                            break
                        # Strategy 2: Check if full name starts with sheet name
                        if full_name.lower().startswith(sheet_base_name.lower()):
                            matched_days = days_val
                            matched_from = sheet_base_name
                            break
                        # Strategy 3: First-name exact match (length > 2)
                        sheet_first_name = sheet_base_name.split()[0] if sheet_base_name else ""
                        full_first_name = full_name.split()[0] if full_name else ""
                        if (len(sheet_first_name) > 2 and len(full_first_name) > 2 and
                            sheet_first_name.lower() == full_first_name.lower()):
                            matched_days = days_val
                            matched_from = sheet_base_name
                            break
                        # Strategy 4: Any significant word in common
                        sheet_words = [w for w in sheet_base_name.lower().split() if len(w) > 3]
                        full_words = [w for w in full_name.lower().split() if len(w) > 3]
                        if sheet_words and full_words:
                            common_words = set(sheet_words) & set(full_words)
                            if len(common_words) >= 1:
                                matched_days = days_val
                                matched_from = sheet_base_name
                                break

                # Update the DataFrame - only if current value is empty/zero
                if matched_days is not None:
                    current_days = row.get('Days')
                    # Only update if current value is None, NaN, 0 or empty
                    if pd.isna(current_days) or current_days is None or current_days == 0 or current_days == '':
                        df.at[idx, 'Days'] = matched_days
                        print(f"  Matched '{full_name}' -> '{matched_from}' = {matched_days} days")
                    else:
                        print(f"  Keeping existing days for '{full_name}': {current_days} (not overwriting with {matched_days})")

        return df

    except Exception as e:
        print(f"Warning: Could not extract days from Invoice sheets: {e}")
        return df


