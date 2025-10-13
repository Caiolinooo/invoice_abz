from pathlib import Path
from app.utils.abz_charge_rate_parser import read_charge_rate_table

abz = Path(r'out\sessions\c6edd65f89e94d528fb703903ff33cab\ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')

df = read_charge_rate_table(abz, 'Charge Rate')
print('Columns:', list(df.columns))
print('Rows:', len(df))
print('Has Additional col:', 'Brazilian Payroll Additionals (GBP)' in df.columns)
print('Has Expenses col:', 'Expenses' in df.columns)
if 'Brazilian Payroll Additionals (GBP)' in df.columns:
    print('Additional sum:', float(df['Brazilian Payroll Additionals (GBP)'].fillna(0).sum()))
if 'Expenses' in df.columns:
    print('Expenses sum:', float(df['Expenses'].fillna(0).sum()))
print(df.head(5).to_string())

