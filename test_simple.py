#!/usr/bin/env python3
import sys
sys.path.append('app')

try:
    from utils.abz_charge_rate_parser import read_charge_rate_table
    from pathlib import Path
    
    abz_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
    
    print("Iniciando teste...")
    df = read_charge_rate_table(abz_path, 'Charge Rate')
    print(f"Dados carregados: {len(df)} linhas")
    
    if 'Days' in df.columns:
        print("Coluna Days encontrada!")
        print(f"Soma total de dias: {df['Days'].sum()}")
    else:
        print("Coluna Days não encontrada!")
        
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
