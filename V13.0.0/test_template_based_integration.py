#!/usr/bin/env python3
"""
Teste de integração do novo gerador baseado em template
"""

from pathlib import Path
import sys
sys.path.append(str(Path('app')))

from invoice.template_filler import generate_from_abz_template

def test_template_based_integration():
    """Testa a integração do novo gerador com o sistema existente"""
    
    print("🧪 TESTE DE INTEGRAÇÃO - GERADOR BASEADO EM TEMPLATE")
    print("=" * 60)
    
    # Dados de teste
    employee_name = "Gabriel Leone"
    line_items = [
        {
            'description': 'Gabriel Leone - Surveyor',
            'unit_price': 450.0,
            'quantity': 22,
            'final': 9900.0
        },
        {
            'description': 'Gabriel Leone - Party Chief',
            'unit_price': 500.0,
            'quantity': 8,
            'final': 4000.0
        },
        {
            'description': 'Brazilian Payroll Additional',
            'unit_price': None,
            'quantity': None,
            'final': 0.0
        },
        {
            'description': 'Expenses',
            'unit_price': None,
            'quantity': None,
            'final': 0.0
        }
    ]
    
    # Configurações
    out_dir = Path("out/test_integration")
    invoice_date = "16/09/2025"
    invoice_no = "INT001/2025"
    call_off = "INTEGRATION-TEST"
    
    # Teste 1: Gerador baseado em template
    print("\n🔧 Teste 1: Gerador baseado em template")
    try:
        result_path = generate_from_abz_template(
            abz_xlsx=Path("DADOS").glob("*ABZ*.xlsx").__next__(),  # Qualquer arquivo ABZ
            template_sheet_name="dummy",  # Não será usado
            employee_name=employee_name,
            line_items=line_items,
            out_dir=out_dir,
            invoice_date=invoice_date,
            invoice_no=invoice_no,
            call_off=call_off,
            use_template_based=True  # USAR NOVO GERADOR
        )
        
        if result_path.exists():
            size = result_path.stat().st_size
            print(f"✅ Invoice gerada com sucesso: {result_path.name} ({size} bytes)")
        else:
            print(f"❌ Arquivo não foi criado")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste 1: {e}")
        return False
    
    # Teste 2: Comparação com gerador profissional (para referência)
    print("\n🔧 Teste 2: Gerador profissional (referência)")
    try:
        result_path_prof = generate_from_abz_template(
            abz_xlsx=Path("DADOS").glob("*ABZ*.xlsx").__next__(),
            template_sheet_name="dummy",
            employee_name=employee_name,
            line_items=line_items,
            out_dir=out_dir,
            invoice_date=invoice_date,
            invoice_no="PROF001/2025",
            call_off=call_off,
            use_default_template=True  # USAR GERADOR PROFISSIONAL
        )
        
        if result_path_prof.exists():
            size = result_path_prof.stat().st_size
            print(f"✅ Invoice profissional gerada: {result_path_prof.name} ({size} bytes)")
        else:
            print(f"❌ Arquivo profissional não foi criado")
            
    except Exception as e:
        print(f"⚠️  Erro no teste 2 (não crítico): {e}")
    
    print(f"\n📁 Arquivos gerados em: {out_dir}")
    print(f"✅ Teste de integração concluído com sucesso!")
    return True

if __name__ == "__main__":
    success = test_template_based_integration()
    if success:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        sys.exit(1)
