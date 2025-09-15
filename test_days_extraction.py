#!/usr/bin/env python3
"""
Test the new days extraction functionality
"""
import sys
from pathlib import Path

# Add app to path
sys.path.append('app')

def test_days_extraction():
    """Test extracting days from Invoice sheets"""
    from utils.abz_charge_rate_parser import read_charge_rate_table
    
    abz_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
    
    if not abz_path.exists():
        print(f"ABZ file not found: {abz_path}")
        return False
    
    print('=== TESTE DA NOVA FUNCIONALIDADE DE EXTRAÇÃO DE DIAS ===')
    
    try:
        df = read_charge_rate_table(abz_path, 'Charge Rate')
        
        print(f"✅ Dados extraídos com sucesso! {len(df)} linhas encontradas.")
        print("\nColunas disponíveis:", df.columns.tolist())
        
        print('\n📊 Dados extraídos:')
        for col in ['Name', 'Position', 'Charge Rate (GBP)', 'Days']:
            if col in df.columns:
                print(f"✅ {col}")
            else:
                print(f"❌ {col} - FALTANDO")
        
        if 'Days' in df.columns and 'Name' in df.columns:
            print('\n👥 Resumo dos funcionários e dias:')
            for _, row in df.iterrows():
                name = str(row['Name'])[:30]
                days = float(row['Days']) if row['Days'] else 0
                rate = float(row['Charge Rate (GBP)']) if row['Charge Rate (GBP)'] else 0
                total = days * rate
                print(f'{name:30} | {days:4.0f} dias | £{rate:6.0f} | Total: £{total:8.0f}')
            
            total_days = df['Days'].sum()
            print(f'\n📈 Total de dias trabalhados: {total_days:.0f}')
            
            # Verificar quais funcionários têm dias > 0
            with_days = df[df['Days'] > 0]
            print(f'👷 Funcionários com dias trabalhados: {len(with_days)}/{len(df)}')
            
            return True
        else:
            print("❌ Colunas essenciais não encontradas")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Testando Extração de Dias das Abas Invoice ===\n")
    
    success = test_days_extraction()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
    else:
        print("\n❌ Teste falhou!")
