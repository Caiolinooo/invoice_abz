from pathlib import Path
from openpyxl import load_workbook

# Check where "invoice date" text is in the template
abz_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
wb = load_workbook(abz_path)
ws = wb['Barbara_Invoice']

print("Looking for 'invoice date' text in Barbara_Invoice template:")
for r in range(1, 30):
    for c in range(1, 15):
        cell = ws.cell(row=r, column=c)
        if cell.value and 'invoice date' in str(cell.value).lower():
            print(f"Found at ({r},{c}): {repr(cell.value)}")

print("\nLooking for any cell containing 'date':")
for r in range(1, 30):
    for c in range(1, 15):
        cell = ws.cell(row=r, column=c)
        if cell.value and 'date' in str(cell.value).lower():
            print(f"Found at ({r},{c}): {repr(cell.value)}")

wb.close()
