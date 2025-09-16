#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path('app')))

print("=== TESTE TEMPLATE PADRÃO ===")

# Test 1: Template exists
template_path = Path('app/templates/default_invoice_template.xlsx')
print(f"Template exists: {template_path.exists()}")

# Test 2: ABZ test file exists  
abz_path = Path('DADOS/ABZ_TEST_NO_TEMPLATES.xlsx')
print(f"ABZ test file exists: {abz_path.exists()}")

# Test 3: Import template_filler
try:
    from invoice.template_filler import generate_from_abz_template
    print("OK template_filler imported successfully")
except Exception as e:
    print(f"ERROR template_filler import error: {e}")
    sys.exit(1)

# Test 4: Import abz parser
try:
    from utils.abz_charge_rate_parser import read_charge_rate_table
    print("OK abz_charge_rate_parser imported successfully")
except Exception as e:
    print(f"ERROR abz_charge_rate_parser import error: {e}")
    sys.exit(1)

print("=== ALL IMPORTS OK ===")

# Test 5: Read ABZ data
try:
    df = read_charge_rate_table(abz_path, 'Charge Rate')
    print(f"OK ABZ data loaded: {len(df)} rows")
    
    if not df.empty:
        first_row = df.iloc[0]
        name = str(first_row.get('Name', 'Unknown'))
        print(f"First employee: {name}")
    else:
        print("ERROR No data in ABZ file")
        sys.exit(1)
        
except Exception as e:
    print(f"ERROR reading ABZ: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=== ABZ READ OK ===")

# Test 6: Generate with default template
try:
    items = [{
        'description': f"{name} - Test Position",
        'unit_price': 100.0,
        'quantity': 1.0,
        'final': 100.0,
    }]
    
    out_path = generate_from_abz_template(
        abz_xlsx=abz_path,
        template_sheet_name="dummy",
        employee_name=name,
        line_items=items,
        out_dir=Path('out/test_simple'),
        invoice_date='15/09/2025',
        invoice_no='TEST001/2025',
        call_off='TEST-CALL-OFF',
        use_default_template=True,
    )
    
    print(f"OK Invoice generated: {out_path}")
    print(f"File exists: {out_path.exists()}")

    if out_path.exists():
        print(f"File size: {out_path.stat().st_size} bytes")
        print("SUCCESS: Default template works!")
    else:
        print("ERROR File was not created")
        
except Exception as e:
    print(f"ERROR generating invoice: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=== TEST COMPLETE ===")
