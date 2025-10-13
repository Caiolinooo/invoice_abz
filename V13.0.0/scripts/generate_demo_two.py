from pathlib import Path
import sys
sys.path.append(str(Path('app')))

from utils.abz_charge_rate_parser import read_charge_rate_table
from invoice.template_filler import generate_from_abz_template

root = Path('.')
abz = next(x for x in (root/'DADOS').glob('*.xlsx') if 'ABZ' in x.name.upper())
df = read_charge_rate_table(abz, 'Charge Rate')

names = [
    'B\u00e1rbara Chapeta Mattoso Franco',
    'Daniel Vieira Silva Nunes',
]

for name in names:
    sub = df[df['Name'].astype(str)==name]
    items=[]
    for _, r in sub.iterrows():
        days = float(r.get('Days', 0) or 0)
        if days>0:
            items.append({
                'description': f"{name} - {r.get('Position')}",
                'unit_price': float(r.get('Charge Rate (GBP)',0) or 0),
                'quantity': days,
                'final': float(r.get('Charge Rate (GBP)',0) or 0)*days,
            })
    add_val = float(sub['Brazilian Payroll Additionals (GBP)'].sum()) if 'Brazilian Payroll Additionals (GBP)' in sub.columns else 0.0
    if add_val:
        items.append({'description':'Brazilian Payroll Additional', 'unit_price': None, 'quantity': None, 'final': add_val})
    exp_val = float(sub['Expenses'].sum()) if 'Expenses' in sub.columns else 0.0
    if exp_val:
        items.append({'description':'Expenses', 'unit_price': None, 'quantity': None, 'final': exp_val})

    out = generate_from_abz_template(
        abz_xlsx=abz,
        template_sheet_name='Barbara_Invoice',
        employee_name=name,
        line_items=items,
        out_dir=Path('out/invoices/xlsx')
    )
    print('Generated:', out)

