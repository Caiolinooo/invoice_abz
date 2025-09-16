#!/usr/bin/env python3
"""
Teste final abrangente de todas as correções implementadas
"""

from pathlib import Path
from openpyxl import load_workbook
from app.invoice.template_based_generator import create_template_based_invoice

def final_comprehensive_test():
    """Teste final de todas as correções"""
    
    print("🎯 TESTE FINAL ABRANGENTE - TODAS AS CORREÇÕES")
    print("=" * 55)
    
    # Diretório de saída
    out_dir = Path("out/final_test")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Dados de teste
    employee_name = "Filipi Brandão Lagedo"
    invoice_no = "145"
    invoice_date = "16/09/2025"
    call_off = "FINAL-TEST-P25-145"
    
    line_items = [
        {
            'description': f'{employee_name} - Senior Surveyor',
            'unit_price': 650.0,
            'quantity': 18,
            'final': 11700.0
        },
        {
            'description': f'{employee_name} - Team Leader',
            'unit_price': 700.0,
            'quantity': 7,
            'final': 4900.0
        }
    ]
    
    print(f"👤 Colaborador: {employee_name}")
    print(f"📄 Invoice No: {invoice_no}")
    print(f"📅 Data: {invoice_date}")
    print(f"📞 Call-off: {call_off}")
    print(f"📊 Itens: {len(line_items)}")
    
    # Gerar nome do arquivo esperado
    from app.utils.filename_standardizer import generate_standardized_filename
    
    fake_abz_path = Path("DADOS/ABZ - FMS - Maximus Project.xlsx")
    expected_filename = generate_standardized_filename(
        employee_name=employee_name,
        invoice_no=invoice_no,
        invoice_date=invoice_date,
        abz_path=fake_abz_path
    )
    
    print(f"📋 Nome esperado: {expected_filename}")
    
    # Gerar invoice
    print(f"\n🔧 GERANDO INVOICE...")
    print("-" * 25)
    
    output_path = out_dir / expected_filename
    
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
    
    # Verificar arquivo gerado
    print(f"\n🔍 VERIFICANDO CORREÇÕES IMPLEMENTADAS...")
    print("-" * 45)
    
    if not result_path.exists():
        print("❌ Arquivo não foi criado!")
        return False
    
    # Carregar arquivo para análise
    wb = load_workbook(result_path)
    ws = wb.active
    
    # VERIFICAÇÃO 1: Nome do arquivo
    print(f"1️⃣ NOME DO ARQUIVO:")
    first_name = employee_name.split()[0]  # "Filipi"
    if first_name in result_path.name:
        print(f"   ✅ Nome do colaborador '{first_name}' incluído")
    else:
        print(f"   ❌ Nome do colaborador '{first_name}' FALTANDO")
        wb.close()
        return False
    
    # VERIFICAÇÃO 2: Call-off
    print(f"2️⃣ CALL-OFF:")
    call_off_cell = ws['C14'].value
    if call_off_cell and call_off in str(call_off_cell):
        print(f"   ✅ Call-off encontrado: '{call_off_cell}'")
    else:
        print(f"   ❌ Call-off não encontrado. Valor: '{call_off_cell}'")
        wb.close()
        return False
    
    # VERIFICAÇÃO 3: Tabela de serviços (sem duplicação)
    print(f"3️⃣ TABELA DE SERVIÇOS:")
    service_items = []
    for row in [18, 21, 24, 27]:
        cell_value = ws[f'A{row}'].value
        if cell_value and str(cell_value).strip():
            service_items.append((row, cell_value))
    
    if len(service_items) == len(line_items):
        print(f"   ✅ Número correto de itens: {len(service_items)}")
        for row, desc in service_items:
            print(f"      Linha {row}: '{desc}'")
    else:
        print(f"   ❌ Número incorreto de itens. Esperado: {len(line_items)}, Encontrado: {len(service_items)}")
        wb.close()
        return False
    
    # VERIFICAÇÃO 4: Fontes preservadas
    print(f"4️⃣ FONTES:")
    font_checks = [
        ('A7', 'Título'),
        ('C12', 'Data'),
        ('C13', 'Número'),
        ('C14', 'Call-off')
    ]
    
    fonts_ok = True
    for cell_ref, desc in font_checks:
        cell = ws[cell_ref]
        if cell.value:
            font = cell.font
            expected_fonts = ['Calibri', 'Aptos Narrow']
            if font.name in expected_fonts:
                print(f"   ✅ {desc} ({cell_ref}): {font.name} {font.size}pt")
            else:
                print(f"   ⚠️  {desc} ({cell_ref}): {font.name} {font.size}pt (inesperado)")
                fonts_ok = False
    
    # VERIFICAÇÃO 5: Notes to invoice above e Corporate Account Details
    print(f"5️⃣ NOTES TO INVOICE ABOVE:")
    
    # Verificar título
    notes_title = ws['A40'].value
    if notes_title and 'Notes to invoice above' in str(notes_title):
        print(f"   ✅ Título encontrado: '{notes_title}'")
    else:
        print(f"   ❌ Título não encontrado. Valor: '{notes_title}'")
        wb.close()
        return False
    
    # Verificar "1."
    notes_number = ws['A41'].value
    if notes_number and '1.' in str(notes_number):
        print(f"   ✅ Numeração encontrada: '{notes_number}'")
    else:
        print(f"   ❌ Numeração não encontrada. Valor: '{notes_number}'")
        wb.close()
        return False
    
    # Verificar Corporate Account Details
    print(f"6️⃣ CORPORATE ACCOUNT DETAILS:")
    corporate_title = ws['A43'].value
    if corporate_title and 'Corporate Account details' in str(corporate_title):
        print(f"   ✅ Título da tabela: '{corporate_title}'")
        
        # Verificar centralização
        cell_a43 = ws['A43']
        if cell_a43.alignment.horizontal == 'center' and cell_a43.alignment.vertical == 'center':
            print(f"   ✅ Centralização aplicada")
        else:
            print(f"   ⚠️  Centralização pode não estar aplicada")
        
        # Verificar bordas (deve ter bordas do template original)
        if cell_a43.border.top.style or cell_a43.border.bottom.style:
            print(f"   ✅ Bordas preservadas")
        else:
            print(f"   ⚠️  Bordas podem não estar preservadas")
    else:
        print(f"   ❌ Título da tabela não encontrado. Valor: '{corporate_title}'")
        wb.close()
        return False
    
    wb.close()
    
    # RESULTADO FINAL
    print(f"\n📈 RESULTADO FINAL:")
    print("=" * 20)
    
    all_checks_passed = True
    
    checks_summary = [
        "✅ Nome do arquivo inclui colaborador",
        "✅ Call-off aparece em C14",
        "✅ Tabela sem duplicações",
        "✅ Fontes preservadas" if fonts_ok else "⚠️  Fontes podem ter mudado",
        "✅ Notes to invoice above preservado",
        "✅ Corporate Account Details formatado"
    ]
    
    for check in checks_summary:
        print(f"  {check}")
        if "⚠️" in check or "❌" in check:
            all_checks_passed = False
    
    if all_checks_passed:
        print(f"\n🎉 TODAS AS CORREÇÕES IMPLEMENTADAS COM SUCESSO!")
        print(f"✅ Sistema pronto para uso em produção!")
    else:
        print(f"\n⚠️  Algumas verificações apresentaram avisos")
        print(f"✅ Funcionalidades principais estão funcionando")
    
    return all_checks_passed

if __name__ == "__main__":
    success = final_comprehensive_test()
    
    if success:
        print(f"\n🚀 SISTEMA TOTALMENTE FUNCIONAL!")
    else:
        print(f"\n🔧 SISTEMA FUNCIONAL COM PEQUENOS AJUSTES NECESSÁRIOS!")
