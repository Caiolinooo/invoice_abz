from pathlib import Path
import pandas as pd

p = Path('MODELO ABZ - OMEGA - Maximus Project  -Monthly Charge Rates xx.2025 (1).xlsx')
raw = pd.read_excel(p, sheet_name='Charge Rate', header=None)

for i in range(20):
    row = [raw.iloc[i, j] if j < raw.shape[1] else None for j in range(12)]
    if any(x is not None for x in row):
        def s(x):
            try:
                import math
                if x is None: return None
                if isinstance(x, float) and pd.isna(x): return None
                return str(x)
            except Exception:
                return str(x)
        print(i, [s(x) for x in row])

header_row = None
for i in range(min(80, len(raw))):
    row_vals = [str(x).strip() for x in raw.iloc[i].tolist()]
    low = [v.lower() for v in row_vals]
    if 'name' in low and 'position' in low and 'charge rate' in low:
        header_row = i
        break
print('DETECTED HEADER ROW:', header_row)

if header_row is not None:
    df = pd.read_excel(p, sheet_name='Charge Rate', header=header_row)
    print('COLUMNS:', [str(c) for c in df.columns])

