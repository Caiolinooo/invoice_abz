from pathlib import Path
import sys
sys.path.append(str(Path('app')))
from utils.abz_charge_rate_parser import read_charge_rate_table

root = Path('.')
abz = next(x for x in (root/'DADOS').glob('*.xlsx') if 'ABZ' in x.name.upper())
df = read_charge_rate_table(abz, 'Charge Rate')
print(df.columns.tolist())
rows = df[df['Name'].astype(str).str.contains('Caio', case=False, na=False)]
print(rows[['Name','Brazilian Payroll Additionals (GBP)','Expenses','Days','Charge Rate (GBP)','Position']].to_string(index=False))

