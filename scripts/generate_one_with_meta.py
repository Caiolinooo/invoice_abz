from pathlib import Path
import sys
sys.path.append(str(Path('app')))

from utils.abz_charge_rate_parser import read_charge_rate_table
from invoice.template_filler import generate_from_abz_template

root = Path('.')
abz = next(x for x in (root/'DADOS').glob('*.xlsx') if 'ABZ' in x.name.upper())
print('ABZ file:', abz)

df = read_charge_rate_table(abz, 'Charge Rate')
print('Got rows:', len(df))

name = 'Bárbara Chapeta Mattoso Franco'
sub = df[df['Name'].astype(str)==name]

# build line items with service lines + additional
items = []

# Add service lines first (to test Unit Price and Quantity alignment)
for _, r in sub.iterrows():
    days = float(r.get('Days', 0) or 0)
    pos = r.get('Position')
    rate = float(r.get('Charge Rate (GBP)', 0) or 0)
    if pos:  # Add even if days=0 to test alignment
        items.append({
            'description': f"{name} - {pos} - Call Off - P25-122 - July 2025",
            'unit_price': rate,
            'quantity': days,
            'final': rate * days,
        })

# Add additional
add_val = float(sub['Brazilian Payroll Additionals (GBP)'].sum()) if 'Brazilian Payroll Additionals (GBP)' in sub.columns else 0.0
if add_val:
    items.append({'description':'Brazilian Payroll Additional', 'unit_price': None, 'quantity': None, 'final': add_val})

# Add expenses (empty for this person but will show N/A)
items.append({'description':'Expenses', 'unit_price': None, 'quantity': None, 'final': 0.0})

print('Items:', items)

out = generate_from_abz_template(
    abz_xlsx=abz,
    template_sheet_name='Barbara_Invoice',
    employee_name=name,
    line_items=items,
    out_dir=Path('out/invoices/xlsx'),
    invoice_date='10/09/2025',
    invoice_no='xx/0000001/2025',
    call_off='770',
)
print('Saved to:', out)

