import sys
sys.path.append('app')

from pathlib import Path
from openpyxl import load_workbook
from invoice.template_filler import generate_from_abz_template

# Test direct invoice generation
dados_dir = Path("DADOS")
abz_files = list(dados_dir.glob("*ABZ*.xlsx"))
if not abz_files:
    print("Planilha ABZ original com templates não encontrada em DADOS/")
    exit(1)

abz = abz_files[0]
print(f"Using ABZ file: {abz}")

wb = load_workbook(abz, read_only=True)
sheets = wb.sheetnames
invoice_sheets = [s for s in sheets if s.lower().strip().endswith('_invoice')]

print(f"Available invoice sheets: {invoice_sheets}")

# Test generating one invoice
employee_name = "Caio Cesar Silva Nascimento"
line_items = [
    {
        "description": "Caio Cesar - ROV Pilot Tech 1",
        "unit_price": 634.0,
        "quantity": 1.0,
        "final": 634.0
    },
    {
        "description": "Brazilian Payroll Additional",
        "final": 679.6
    },
    {
        "description": "Expenses",
        "final": 20.0
    }
]

# Find template for Caio
import unicodedata, re

def _norm(s: str) -> str:
    s = unicodedata.normalize('NFD', str(s))
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '', s.lower())

first = _norm(employee_name.split()[0])
tpl_candidates = [s for s in invoice_sheets if first in _norm(s)]

print(f"Employee: {employee_name}")
print(f"First normalized: '{first}'")
print(f"Template candidates: {tpl_candidates}")

if tpl_candidates:
    template_sheet = tpl_candidates[0]
    print(f"Using template: {template_sheet}")
    
    out_dir = Path("test_output")
    out_dir.mkdir(exist_ok=True)
    
    try:
        xlsx_path = generate_from_abz_template(
            abz_xlsx=abz,
            template_sheet_name=template_sheet,
            employee_name=employee_name,
            line_items=line_items,
            out_dir=out_dir,
            invoice_date="11/09/2025",
            invoice_no="0000108/2025",
            call_off="P25-122",
        )
        print(f"Generated invoice: {xlsx_path}")
    except Exception as e:
        print(f"Error generating invoice: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No template found!")

wb.close()
