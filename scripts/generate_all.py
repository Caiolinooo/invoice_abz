from pathlib import Path
import sys
sys.path.append(str(Path('app')))

from utils.abz_charge_rate_parser import read_charge_rate_table
from utils.anfin_parser import extract_individual_totals, extract_costs_gbp
from invoice.template_filler import generate_from_abz_template

root = Path('.')
abz = next(x for x in (root/'DADOS').glob('*.xlsx') if 'ABZ' in x.name.upper())
anfin = next(x for x in (root/'DADOS').glob('*.xlsx') if 'AN-FIN' in x.name.upper())

print('Using ABZ:', abz)
print('Using AN-FIN:', anfin)

# Parse base services from ABZ
charge_df = read_charge_rate_table(abz, 'Charge Rate')

# Read AN-FIN additional/exchange rate from individual sheets
ind = extract_individual_totals(anfin)
# Read AN-FIN costs and convert to GBP
costs_gbp = extract_costs_gbp(anfin, {k: v['exchange_rate'] for k, v in ind.items()})

# Normalize ABZ names to list
names = sorted(set(charge_df['Name'].astype(str).dropna().tolist()))
print('Employees:', names)

out_dir = Path('out/invoices/xlsx')

for name in names:
    sub = charge_df[charge_df['Name'].astype(str)==name]

    items = []
    # service lines from ABZ
    for _, r in sub.iterrows():
        days = float(r.get('Days', 0) or 0)
        pos = r.get('Position')
        rate = float(r.get('Charge Rate (GBP)', 0) or 0)
        if days > 0 and pos:
            items.append({
                'description': f"{name} - {pos}",
                'unit_price': rate,
                'quantity': days,
                'final': rate * days,
            })

    # Additional from AN-FIN individual sheet (preferred); fallback ABZ sum
    add_val = None
    if name in ind:
        add_val = ind[name]['additional_gbp']
    else:
        for k, v in ind.items():
            if k.lower().split()[0] == name.lower().split()[0]:
                add_val = v['additional_gbp']
                break
    if add_val is None:
        add_val = float(sub['Brazilian Payroll Additionals (GBP)'].sum()) if 'Brazilian Payroll Additionals (GBP)' in sub.columns else 0.0
    if add_val and abs(add_val) > 1e-6:
        items.append({'description': 'Brazilian Payroll Additional', 'unit_price': None, 'quantity': None, 'final': float(add_val)})

    # Expenses from AN-FIN costs (preferred); fallback ABZ
    exp_val = None
    if name in costs_gbp:
        exp_val = costs_gbp[name]
    else:
        for k, v in costs_gbp.items():
            if k.lower().split()[0] == name.lower().split()[0]:
                exp_val = v
                break
    if exp_val is None:
        exp_val = float(sub['Expenses'].sum()) if 'Expenses' in sub.columns else 0.0
    if exp_val and abs(exp_val) > 1e-6:
        items.append({'description': 'Expenses', 'unit_price': None, 'quantity': None, 'final': float(exp_val)})

    if not items:
        print('Skip', name, '- no items')
        continue

    # pick the employee-specific template: must exist '<FirstName>_Invoice'
    from openpyxl import load_workbook
    wb = load_workbook(abz, read_only=True)
    first = name.split()[0]
    # find sheet that endswith '_Invoice' and contains the first name (case-insensitive)
    tpl_candidates = [s for s in wb.sheetnames if s.lower().endswith('_invoice') and first.lower() in s.lower()]
    wb.close()
    if not tpl_candidates:
        raise SystemExit(f"Sheet for {name} not found in ABZ (expected something like '{first}_Invoice').")
    tpl = tpl_candidates[0]

    out = generate_from_abz_template(
        abz_xlsx=abz,
        template_sheet_name=tpl,
        employee_name=name,
        line_items=items,
        out_dir=out_dir,
    )
    print('Generated:', out)

