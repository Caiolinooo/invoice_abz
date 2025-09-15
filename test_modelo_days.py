#!/usr/bin/env python3
"""
Ad-hoc test to validate Days extraction against the root 'MODELO ABZ' file.
"""
import sys
from pathlib import Path

# Add app to path
sys.path.append('app')

def test_modelo_days():
    from utils.abz_charge_rate_parser import read_charge_rate_table

    # Root modelo path (example name present in repo root)
    modelo = Path("MODELO ABZ - OMEGA - Maximus Project  -Monthly Charge Rates xx.2025 (1).xlsx")

    if not modelo.exists():
        print(f"Modelo file not found: {modelo}")
        return False

    print("=== Testando extração de dias no MODELO ABZ da raiz ===")

    try:
        df = read_charge_rate_table(modelo, 'Charge Rate')
        print(f"Linhas carregadas: {len(df)}")
        print("Colunas:", df.columns.tolist())

        if 'Days' not in df.columns or 'Name' not in df.columns:
            print("❌ Colunas essenciais (Days/Name) não encontradas")
            return False

        total_days = float(df['Days'].sum())
        print(f"Total de dias (soma): {total_days}")

        # Mostrar alguns funcionários
        for _, row in df.head(10).iterrows():
            name = str(row.get('Name', ''))
            days = row.get('Days', 0)
            rate = row.get('Charge Rate (GBP)', 0)
            try:
                days_f = float(days or 0)
                rate_f = float(rate or 0)
            except Exception:
                days_f, rate_f = 0.0, 0.0
            print(f" - {name[:30]:30} | Days={days_f} | Rate={rate_f}")

        # Expect at least one non-zero or zero but present value
        has_any_value = any((float(x or 0) >= 0) for x in df['Days'])
        if not has_any_value:
            print("❌ Nenhum valor válido encontrado em Days")
            return False

        print("✅ Extração no MODELO concluída")
        return True

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    ok = test_modelo_days()
    print("OK=", ok)

