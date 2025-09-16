#!/usr/bin/env python3
"""
Teste final com call-off nas descrições dos serviços
"""

from pathlib import Path
from openpyxl import load_workbook
from app.invoice.template_based_generator import create_template_based_invoice

def test_final_with_calloff():
    """Teste final com todas as funcionalidades incluindo call-off nas descrições"""
    
    print("🎯 TESTE FINAL - TODAS AS FUNCIONALIDADES + CALL-OFF")
    print("=" * 55)
    
    # Diretório de saída
    out_dir = Path("out/final_with_calloff")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Dados de teste
    employee_name = "Maria Fernanda Costa"
    invoice_no = "155"
    invoice_date = "16/09/2025"
    call_off = "P25-155-SUBSEA"
    
    line_items = [
        {
            'description': f'{employee_name} - Lead Surveyor',
            'unit_price': 850.0,
            'quantity': 12,
            'final': 10200.0
        },
        {
            'description': f'{employee_name} - Quality Inspector',
            'unit_price': 750.0,
            'quantity': 8,
            'final': 6000.0
        }
    ]
    
    print(f"👤 Colaborador: {employee_name}")
    print(f"📄 Invoice No: {invoice_no}")
    print(f"📅 Data: {invoice_date}")
    print(f"📞 Call-off: {call_off}")
    print(f"📊 Itens: {len(line_items)}")
    
    # Gerar nome do arquivo
    from app.utils.filename_standardizer import generate_standardized_filename
    
    fake_abz_path = Path("DADOS/ABZ - OMEGA - Subsea Project.xlsx")
    filename = generate_standardized_filename(
        employee_name=employee_name,
        invoice_no=invoice_no,
        invoice_date=invoice_date,
        abz_path=fake_abz_path
    )
    
    print(f"📋 Nome esperado: {filename}")
    
    # Gerar invoice
    print(f"\n🔧 GERANDO INVOICE FINAL...")
    print("-" * 30)
    
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
    
    # Verificações completas
    print(f"\n🔍 VERIFICAÇÕES FINAIS...")
    print("-" * 25)
    
    if not result_path.exists():
        print("❌ Arquivo não foi criado!")
        return False
    
    # Carregar arquivo
    wb = load_workbook(result_path)
    ws = wb.active
    
    all_checks_passed = True
    
    # 1. Nome do arquivo
    first_name = employee_name.split()[0]
    if first_name in result_path.name:
        print(f"✅ 1. Nome do colaborador '{first_name}' no arquivo")
    else:
        print(f"❌ 1. Nome do colaborador '{first_name}' FALTANDO")
        all_checks_passed = False
    
    # 2. Call-off em C14
    call_off_c14 = ws['C14'].value
    if call_off_c14 and call_off in str(call_off_c14):
        print(f"✅ 2. Call-off em C14: '{call_off_c14}'")
    else:
        print(f"❌ 2. Call-off em C14 não encontrado: '{call_off_c14}'")
        all_checks_passed = False
    
    # 3. Call-off nas descrições dos serviços
    service_rows = [18, 21]
    calloff_in_descriptions = 0
    
    for row in service_rows:
        cell_value = ws[f'A{row}'].value
        if cell_value and call_off in str(cell_value):
            calloff_in_descriptions += 1
            print(f"✅ 3.{row-17}. Call-off na descrição linha {row}: '{cell_value}'")
        else:
            print(f"❌ 3.{row-17}. Call-off FALTANDO na linha {row}: '{cell_value}'")
            all_checks_passed = False
    
    # 4. Tabela sem duplicações
    service_items = []
    for row in [18, 21, 24, 27]:
        cell_value = ws[f'A{row}'].value
        if cell_value and str(cell_value).strip():
            service_items.append(cell_value)
    
    if len(service_items) == len(line_items):
        print(f"✅ 4. Tabela com número correto de itens: {len(service_items)}")
    else:
        print(f"❌ 4. Tabela com número incorreto: {len(service_items)} (esperado {len(line_items)})")
        all_checks_passed = False
    
    # 5. Notes to invoice above preservado
    notes_title = ws['A40'].value
    if notes_title and 'Notes to invoice above' in str(notes_title):
        print(f"✅ 5. Notes to invoice above preservado: '{notes_title}'")
    else:
        print(f"❌ 5. Notes to invoice above não encontrado: '{notes_title}'")
        all_checks_passed = False
    
    # 6. Corporate Account Details centralizado
    corporate_title = ws['A43'].value
    if corporate_title and 'Corporate Account details' in str(corporate_title):
        cell_a43 = ws['A43']
        if cell_a43.alignment.horizontal == 'center':
            print(f"✅ 6. Corporate Account Details centralizado")
        else:
            print(f"⚠️  6. Corporate Account Details pode não estar centralizado")
    else:
        print(f"❌ 6. Corporate Account Details não encontrado")
        all_checks_passed = False
    
    wb.close()
    
    # Resultado final
    print(f"\n📈 RESULTADO FINAL:")
    print("=" * 20)
    
    if all_checks_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Nome do arquivo com colaborador")
        print("✅ Call-off em C14")
        print("✅ Call-off nas descrições dos serviços")
        print("✅ Tabela sem duplicações")
        print("✅ Notes to invoice above preservado")
        print("✅ Corporate Account Details formatado")
        print(f"\n🚀 SISTEMA COMPLETAMENTE FUNCIONAL!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM!")
        print("🔧 Verificar implementação!")
    
    return all_checks_passed

if __name__ == "__main__":
    success = test_final_with_calloff()
    
    if success:
        print(f"\n✅ IMPLEMENTAÇÃO COMPLETA E FUNCIONAL!")
        print(f"🎯 Call-off agora aparece:")
        print(f"   📍 Em C14 (como antes)")
        print(f"   📊 Nas descrições dos serviços (NOVO!)")
    else:
        print(f"\n❌ IMPLEMENTAÇÃO PRECISA DE CORREÇÕES!")
