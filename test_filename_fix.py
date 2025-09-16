#!/usr/bin/env python3
"""
Testar se o nome do arquivo está correto com o nome do colaborador
"""

from pathlib import Path
from app.invoice.template_based_generator import create_template_based_invoice

def test_filename_with_employee_name():
    """Testa se o nome do arquivo inclui o nome do colaborador"""
    
    print("🧪 TESTE - NOME DO ARQUIVO COM COLABORADOR")
    print("=" * 45)
    
    # Diretório de saída
    out_dir = Path("out/test_filename")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Dados de teste
    employee_name = "Gabriel Leone Silva"
    invoice_no = "142"
    invoice_date = "16/09/2025"
    call_off = "FILENAME-TEST-001"
    
    line_items = [
        {
            'description': f'{employee_name} - Senior Surveyor',
            'unit_price': 550.0,
            'quantity': 20,
            'final': 11000.0
        },
        {
            'description': f'{employee_name} - Project Manager',
            'unit_price': 600.0,
            'quantity': 5,
            'final': 3000.0
        }
    ]
    
    print(f"👤 Colaborador: {employee_name}")
    print(f"📄 Invoice No: {invoice_no}")
    print(f"📅 Data: {invoice_date}")
    print(f"📞 Call-off: {call_off}")
    
    # Gerar invoice
    print(f"\n🔧 Gerando invoice...")
    
    # Simular um arquivo ABZ para teste
    fake_abz_path = Path("DADOS/ABZ - OMEGA - Test Project.xlsx")
    
    # O nome do arquivo deveria ser gerado pela função generate_standardized_filename
    # que agora recebe o abz_path
    expected_filename_pattern = f"ABZ Group {invoice_no}-2025 OMEGA 09 2025 Gabriel.xlsx"
    
    print(f"📋 Nome esperado: {expected_filename_pattern}")
    
    # Como não temos um arquivo ABZ real, vamos testar diretamente a função
    from app.utils.filename_standardizer import generate_standardized_filename
    
    generated_filename = generate_standardized_filename(
        employee_name=employee_name,
        invoice_no=invoice_no,
        invoice_date=invoice_date,
        abz_path=fake_abz_path
    )
    
    print(f"📋 Nome gerado: {generated_filename}")
    
    # Verificar se o nome contém o primeiro nome do colaborador
    first_name = employee_name.split()[0]  # "Gabriel"
    
    if first_name in generated_filename:
        print(f"✅ Nome do colaborador '{first_name}' encontrado no arquivo!")
    else:
        print(f"❌ Nome do colaborador '{first_name}' NÃO encontrado no arquivo!")
    
    # Verificar outros componentes
    checks = [
        (invoice_no, "Número da invoice"),
        ("2025", "Ano"),
        ("OMEGA", "Cliente"),
        ("09", "Mês"),
        (first_name, "Nome do colaborador")
    ]
    
    print(f"\n🔍 VERIFICAÇÕES:")
    print("-" * 20)
    
    all_ok = True
    for component, desc in checks:
        if component in generated_filename:
            print(f"✅ {desc}: '{component}' - OK")
        else:
            print(f"❌ {desc}: '{component}' - FALTANDO")
            all_ok = False
    
    # Testar criação real do arquivo
    print(f"\n🔧 TESTANDO CRIAÇÃO REAL DO ARQUIVO:")
    print("-" * 40)
    
    output_path = out_dir / generated_filename
    
    try:
        result_path = create_template_based_invoice(
            employee_name=employee_name,
            line_items=line_items,
            output_path=output_path,
            invoice_date=invoice_date,
            invoice_no=invoice_no,
            call_off=call_off
        )
        
        if result_path.exists():
            print(f"✅ Arquivo criado: {result_path.name}")
            print(f"📊 Tamanho: {result_path.stat().st_size} bytes")
            
            # Verificar se o nome do arquivo real contém o nome do colaborador
            if first_name in result_path.name:
                print(f"✅ Nome do colaborador '{first_name}' confirmado no arquivo real!")
            else:
                print(f"❌ Nome do colaborador '{first_name}' NÃO encontrado no arquivo real!")
                all_ok = False
        else:
            print(f"❌ Arquivo não foi criado!")
            all_ok = False
            
    except Exception as e:
        print(f"❌ Erro ao criar arquivo: {e}")
        all_ok = False
    
    # Resultado final
    print(f"\n📈 RESULTADO FINAL:")
    print("-" * 20)
    
    if all_ok:
        print("🎉 TESTE PASSOU! Nome do arquivo inclui o nome do colaborador!")
    else:
        print("⚠️  TESTE FALHOU! Nome do arquivo pode estar incorreto!")
    
    return all_ok

if __name__ == "__main__":
    success = test_filename_with_employee_name()
    
    if success:
        print(f"\n✅ CORREÇÃO DO NOME DO ARQUIVO FUNCIONANDO!")
    else:
        print(f"\n❌ CORREÇÃO DO NOME DO ARQUIVO PRECISA DE AJUSTES!")
