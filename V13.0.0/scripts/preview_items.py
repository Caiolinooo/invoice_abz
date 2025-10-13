from pathlib import Path
import sys
sys.path.append(str(Path('app')))

from utils.abz_charge_rate_parser import read_charge_rate_table
from utils.anfin_parser import extract_individual_totals, extract_costs_gbp

root = Path('.')
abz = next(x for x in (root/'DADOS').glob('*.xlsx') if 'ABZ' in x.name.upper())
anfin = next(x for x in (root/'DADOS').glob('*.xlsx') if 'AN-FIN' in x.name.upper())

charge_df = read_charge_rate_table(abz, 'Charge Rate')
ind = extract_individual_totals(anfin)
costs_gbp = extract_costs_gbp(anfin, {k: v['exchange_rate'] for k, v in ind.items()})

name = next(n for n in charge_df['Name'].astype(str) if 'Caio' in n)
sub = charge_df[charge_df['Name'].astype(str)==name]
items = []
for _, r in sub.iterrows():
    days = float(r.get('Days', 0) or 0)
    pos = r.get('Position')
    rate = float(r.get('Charge Rate (GBP)', 0) or 0)
    if days > 0 and pos:
        items.append({'description': f"{name} - {pos}", 'unit_price': rate, 'quantity': days, 'final': rate * days})

add_val = None
if 'Brazilian Payroll Additionals (GBP)' in sub.columns:
    add_val = float(sub['Brazilian Payroll Additionals (GBP)'].sum())
if (add_val is None or abs(add_val) < 1e-9):
    add_val = ind.get(name, {}).get('additional_gbp', 0.0)
if add_val and abs(add_val) > 1e-6:
    items.append({'description': 'Brazilian Payroll Additional', 'final': float(add_val)})

exp_val = costs_gbp.get(name, 0.0)
if exp_val and abs(exp_val) > 1e-6:
    items.append({'description': 'Expenses', 'final': float(exp_val)})

print('Items for', name)
for it in items:
    print(it)
print('Total', sum(it['final'] for it in items))

