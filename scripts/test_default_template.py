#!/usr/bin/env python3
"""
Script para testar o template padrão diretamente.
"""

from pathlib import Path
import sys
sys.path.append(str(Path('app')))

from utils.abz_charge_rate_parser import read_charge_rate_table
from invoice.template_filler import generate_from_abz_template

def test_default_template():
    """Testa a geração com template padrão"""
    
    # Usar planilha sem templates
    test_abz = Path('DADOS/ABZ_TEST_NO_TEMPLATES.xlsx')
    
    if not test_abz.exists():
        print("❌ Planilha de teste não encontrada")
        return False
    
    print(f"📁 Usando planilha: {test_abz}")
    
    # Ler dados da planilha
    try:
        df = read_charge_rate_table(test_abz, 'Charge Rate')
        print(f"📊 Dados carregados: {len(df)} linhas")
    except Exception as e:
        print(f"❌ Erro ao ler planilha: {e}")
        return False
    
    # Pegar primeiro funcionário
    if df.empty:
        print("❌ Nenhum dado encontrado")
        return False
    
    first_employee = df.iloc[0]
    name = str(first_employee.get('Name', 'Test Employee'))
    
    print(f"👤 Testando com funcionário: {name}")
    
    # Criar items de teste
    items = [{
        'description': f"{name} - {first_employee.get('Position', 'Test Position')}",
        'unit_price': float(first_employee.get('Charge Rate (GBP)', 100) or 100),
        'quantity': float(first_employee.get('Days', 1) or 1),
        'final': float(first_employee.get('Charge Rate (GBP)', 100) or 100) * float(first_employee.get('Days', 1) or 1),
    }]
    
    print(f"📋 Items: {items}")
    
    # Testar geração com template padrão
    try:
        print("🔧 Testando com template padrão...")
        
        out_path = generate_from_abz_template(
            abz_xlsx=test_abz,
            template_sheet_name="dummy",  # Não será usado
            employee_name=name,
            line_items=items,
            out_dir=Path('out/test_default'),
            invoice_date='15/09/2025',
            invoice_no='TEST001/2025',
            call_off='TEST-CALL-OFF',
            use_default_template=True,  # USAR TEMPLATE PADRÃO
        )
        
        print(f"✅ Invoice gerada: {out_path}")
        
        if out_path.exists():
            print(f"📄 Arquivo criado: {out_path.stat().st_size} bytes")
            return True
        else:
            print("❌ Arquivo não foi criado")
            return False
            
    except Exception as e:
        print(f"❌ Erro na geração: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_default_template()
    if success:
        print("\n🎉 Teste do template padrão passou!")
        print("   O sistema funciona sem templates na planilha ABZ.")
    else:
        print("\n❌ Teste falhou.")
        sys.exit(1)
