from pathlib import Path
import pandas as pd

abz_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
xl = pd.ExcelFile(abz_path)
print("Available sheets in ABZ file:")
for sheet in xl.sheet_names:
    print(f"  - {sheet}")
