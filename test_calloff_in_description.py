#!/usr/bin/env python3
"""
Testar se o call-off está sendo adicionado na descrição dos serviços
"""

from pathlib import Path
from openpyxl import load_workbook
from app.invoice.template_based_generator import create_template_based_invoice

def test_calloff_in_description():
    """Testa se o call-off aparece na descrição dos serviços"""
    
    print("🧪 TESTE - CALL-OFF NA DESCRIÇÃO DOS SERVIÇOS")
    print("=" * 50)
    
    # Diretório de saída
    out_dir = Path("out/test_calloff_description")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Dados de teste
    employee_name = "João Silva Santos"
    invoice_no = "150"
    invoice_date = "16/09/2025"
    call_off = "P25-150-OFFSHORE"
    
    line_items = [
        {
            'description': f'{employee_name} - Senior Surveyor',
            'unit_price': 750.0,
            'quantity': 15,
            'final': 11250.0
        },
        {
            'description': f'{employee_name} - Project Coordinator',
            'unit_price': 800.0,
            'quantity': 10,
            'final': 8000.0
        }
    ]
    
    print(f"👤 Colaborador: {employee_name}")
    print(f"📄 Invoice No: {invoice_no}")
    print(f"📅 Data: {invoice_date}")
    print(f"📞 Call-off: {call_off}")
    print(f"📊 Itens: {len(line_items)}")
    
    # Gerar nome do arquivo
    from app.utils.filename_standardizer import generate_standardized_filename
    
    fake_abz_path = Path("DADOS/ABZ - MAXIMUS - Test Project.xlsx")
    filename = generate_standardized_filename(
        employee_name=employee_name,
        invoice_no=invoice_no,
        invoice_date=invoice_date,
        abz_path=fake_abz_path
    )
    
    print(f"📋 Nome do arquivo: {filename}")
    
    # Gerar invoice
    print(f"\n🔧 GERANDO INVOICE COM CALL-OFF NA DESCRIÇÃO...")
    print("-" * 50)
    
    output_path = out_dir / filename
    
    try:
        result_path = create_template_based_invoice(
            employee_name=employee_name,
            line_items=line_items,
            output_path=output_path,
            invoice_date=invoice_date,
            invoice_no=invoice_no,
            call_off=call_off
        )
        
        print(f"✅ Invoice criada: {result_path.name}")
        
    except Exception as e:
        print(f"❌ Erro ao criar invoice: {e}")
        return False
    
    # Verificar se o call-off foi adicionado nas descrições
    print(f"\n🔍 VERIFICANDO CALL-OFF NAS DESCRIÇÕES...")
    print("-" * 45)
    
    if not result_path.exists():
        print("❌ Arquivo não foi criado!")
        return False
    
    # Carregar arquivo para análise
    wb = load_workbook(result_path)
    ws = wb.active
    
    # Verificar descrições nas linhas da tabela de serviços
    service_rows = [18, 21, 24, 27]  # Linhas dos grupos de serviços
    
    descriptions_found = []
    calloff_found_count = 0
    
    for i, row in enumerate(service_rows):
        cell_value = ws[f'A{row}'].value
        if cell_value and str(cell_value).strip():
            descriptions_found.append((row, cell_value))
            
            # Verificar se o call-off está na descrição
            if call_off in str(cell_value):
                calloff_found_count += 1
                print(f"✅ Linha {row}: '{cell_value}'")
                print(f"   📞 Call-off '{call_off}' encontrado!")
            else:
                print(f"❌ Linha {row}: '{cell_value}'")
                print(f"   📞 Call-off '{call_off}' NÃO encontrado!")
    
    # Verificar também se o call-off ainda aparece em C14
    print(f"\n🔍 VERIFICANDO CALL-OFF EM C14...")
    print("-" * 35)
    
    call_off_c14 = ws['C14'].value
    if call_off_c14 and call_off in str(call_off_c14):
        print(f"✅ Call-off em C14: '{call_off_c14}'")
        c14_ok = True
    else:
        print(f"❌ Call-off em C14 não encontrado: '{call_off_c14}'")
        c14_ok = False
    
    wb.close()
    
    # Resultado
    print(f"\n📈 RESULTADO:")
    print("-" * 15)
    
    print(f"📊 Descrições encontradas: {len(descriptions_found)}")
    print(f"📞 Call-off encontrado em descrições: {calloff_found_count}/{len(line_items)}")
    print(f"📍 Call-off em C14: {'✅' if c14_ok else '❌'}")
    
    # Verificar se o call-off aparece em todas as descrições esperadas
    expected_descriptions = len(line_items)
    success = (calloff_found_count == expected_descriptions) and c14_ok
    
    if success:
        print(f"\n🎉 TESTE PASSOU!")
        print(f"✅ Call-off '{call_off}' adicionado em todas as descrições!")
        print(f"✅ Call-off também mantido em C14!")
    else:
        print(f"\n⚠️  TESTE PARCIALMENTE PASSOU!")
        if calloff_found_count < expected_descriptions:
            print(f"❌ Call-off faltando em {expected_descriptions - calloff_found_count} descrição(ões)")
        if not c14_ok:
            print(f"❌ Call-off não encontrado em C14")
    
    return success

if __name__ == "__main__":
    success = test_calloff_in_description()
    
    if success:
        print(f"\n🚀 CALL-OFF IMPLEMENTADO CORRETAMENTE!")
        print(f"✅ Aparece nas descrições dos serviços")
        print(f"✅ Mantido também em C14")
    else:
        print(f"\n🔧 IMPLEMENTAÇÃO PRECISA DE AJUSTES!")
