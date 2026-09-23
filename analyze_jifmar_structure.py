"""
Analyze ABZ - Jifmar spreadsheet structure to understand the data format
"""
import openpyxl
from pathlib import Path

# Load the Jifmar spreadsheet
jifmar_file = Path(r"dev\DADOS\ABZ - Jifmar - Monthly Rates 1509-3009 New Version.xlsx")

print("=" * 80)
print("📊 ANALYZING ABZ - JIFMAR SPREADSHEET STRUCTURE")
print("=" * 80)

wb = openpyxl.load_workbook(jifmar_file, data_only=True)

print(f"\n📋 Total Sheets: {len(wb.sheetnames)}")
print(f"Sheet Names: {wb.sheetnames}\n")

# Analyze each sheet
for sheet_name in wb.sheetnames[:3]:  # Analyze first 3 sheets
    print("=" * 80)
    print(f"📄 SHEET: {sheet_name}")
    print("=" * 80)
    
    ws = wb[sheet_name]
    
    # Find header row and data structure
    print("\n🔍 First 30 rows:")
    for row_idx in range(1, 31):
        row_data = []
        for col_idx in range(1, 15):
            cell = ws.cell(row=row_idx, column=col_idx)
            if cell.value:
                row_data.append(f"[{col_idx}] {str(cell.value)[:50]}")
        
        if row_data:
            print(f"Row {row_idx:2d}: {' | '.join(row_data)}")
    
    # Try to identify key information
    print("\n🎯 Key Information Detection:")
    
    # Look for client info
    for row_idx in range(1, 20):
        for col_idx in range(1, 10):
            cell_value = ws.cell(row=row_idx, column=col_idx).value
            if cell_value and isinstance(cell_value, str):
                lower_val = cell_value.lower()
                if 'client' in lower_val or 'vessel' in lower_val or 'month' in lower_val:
                    print(f"  - Row {row_idx}, Col {col_idx}: {cell_value}")
    
    # Look for header row (Name, Position, etc.)
    print("\n📊 Potential Header Row:")
    for row_idx in range(1, 20):
        row_values = [ws.cell(row=row_idx, column=c).value for c in range(1, 15)]
        row_str = [str(v).lower() if v else "" for v in row_values]
        
        if any('name' in s for s in row_str) and any('position' in s for s in row_str):
            print(f"  ✅ Header found at Row {row_idx}:")
            for col_idx, val in enumerate(row_values[:12], 1):
                if val:
                    print(f"     Col {col_idx}: {val}")
            
            # Show first few data rows
            print(f"\n  📝 First 3 data rows:")
            for data_row in range(row_idx + 1, row_idx + 4):
                data_values = [ws.cell(row=data_row, column=c).value for c in range(1, 12)]
                if any(v for v in data_values):
                    print(f"     Row {data_row}: {data_values}")
            break
    
    print("\n")

print("=" * 80)
print("🔍 COMPARISON WITH CURRENT ABZ FORMAT")
print("=" * 80)

# Load current ABZ format for comparison
current_abz = Path(r"dev\ABZ - FMS - Maximus Project  -Monthly Charge Rates 09 2025.xlsx")
if current_abz.exists():
    wb_current = openpyxl.load_workbook(current_abz, data_only=True)
    print(f"\n📋 Current ABZ Sheets: {wb_current.sheetnames[:5]}")
    
    # Check for invoice templates
    invoice_sheets = [s for s in wb_current.sheetnames if '_invoice' in s.lower()]
    print(f"📄 Invoice Template Sheets: {len(invoice_sheets)}")
    if invoice_sheets:
        print(f"   Examples: {invoice_sheets[:3]}")

print("\n" + "=" * 80)
print("📝 SUMMARY")
print("=" * 80)
print("""
JIFMAR FORMAT:
- Client: Jifmar Group (not ABZ Group)
- Structure: Each sheet = Vessel/Project (Voe Vanguard, Voe Viking, Faraday, etc.)
- Columns: Name, Position, Day Rate, Days, Overtime Hours, Overtime Cost, Insurance, Social Security
- Simpler structure than current ABZ format
- NO invoice template sheets (need to generate from scratch)

CURRENT ABZ FORMAT:
- Client: ABZ Group (FMS, OMEGA, etc.)
- Structure: Charge Rate sheet + Individual invoice template sheets per employee
- More complex with pre-existing invoice templates

IMPLEMENTATION NEEDS:
1. ✅ Multi-company selector in UI (ABZ Group vs ABZ International)
2. ✅ Separate data storage per company (company_id in database)
3. ✅ Different parsers for different formats
4. ✅ Unified invoice generation (works for both formats)
5. ✅ Combined reporting (aggregate data from both companies)
6. ✅ Separate historical data per company
""")

wb.close()
if current_abz.exists():
    wb_current.close()

