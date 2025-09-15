from pathlib import Path
import sys
sys.path.append('app')
import pandas as pd
from utils.abz_charge_rate_parser import _find_header_row

p = Path('MODELO ABZ - OMEGA - Maximus Project  -Monthly Charge Rates xx.2025 (1).xlsx')
raw = pd.read_excel(p, sheet_name='Charge Rate', header=None)
hr = _find_header_row(raw)
print('header_row=', hr)
if hr is None:
    hr = raw.iloc[:60].apply(lambda r: r.notna().sum(), axis=1).idxmax()
    print('fallback header_row=', hr)

df = pd.read_excel(p, sheet_name='Charge Rate', header=hr)
df = df.iloc[:, :14]
cols = [str(c).strip() for c in df.columns]
print('cols(raw)=', cols)

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

print('mapping=', mapping)
print('mapped cols=', [mapping[c] for c in cols])

