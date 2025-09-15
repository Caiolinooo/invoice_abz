from pathlib import Path
import sys
sys.path.append(str(Path('app')))
from openpyxl import load_workbook

# Check the template for formulas that might cause #REF!
abz_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
wb = load_workbook(abz_path)

# Check Caio's template
ws = wb['Caio_Invoice']

print("Checking for formulas in Caio_Invoice template:")
for row in range(1, 20):
    for col in range(1, 10):
        cell = ws.cell(row=row, column=col)
        if cell.data_type == 'f':  # Formula
            print(f"Formula at ({row},{col}): {cell.value}")
        elif cell.value and str(cell.value).strip():
            if 'invoice' in str(cell.value).lower():
                print(f"Invoice-related at ({row},{col}): {cell.value}")

wb.close()
