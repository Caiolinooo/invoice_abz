#!/usr/bin/env python3
"""
Validar se as invoices geradas seguem o template original
"""

from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

def validate_template_compliance():
    """Valida se a invoice gerada segue o template original"""
    
    print("🔍 VALIDAÇÃO DE CONFORMIDADE COM TEMPLATE")
    print("=" * 50)
    
    # Caminhos
    template_path = Path("DADOS/Template_Invoice_Geral.xlsx")
    generated_path = Path("out/sessions/test_template_based_session/xlsx/ABZ Group 0000256-2025 CLIENT 09 2025 Gabriel.xlsx")
    
    if not template_path.exists():
        print(f"❌ Template não encontrado: {template_path}")
        return False
    
    if not generated_path.exists():
        print(f"❌ Invoice gerada não encontrada: {generated_path}")
        return False
    
    print(f"📋 Template original: {template_path.name}")
    print(f"📄 Invoice gerada: {generated_path.name}")
    
    # Carregar ambos os arquivos
    template_wb = load_workbook(template_path)
    template_ws = template_wb.active
    
    generated_wb = load_workbook(generated_path)
    generated_ws = generated_wb.active
    
    # Validações estruturais
    validations = []
    
    # 1. Verificar título "Invoice"
    template_title = template_ws['A7'].value
    generated_title = generated_ws['A7'].value
    validations.append(("Título 'Invoice'", template_title == generated_title, f"Template: {template_title}, Gerado: {generated_title}"))
    
    # 2. Verificar cliente
    template_client = template_ws['A12'].value
    generated_client = generated_ws['A12'].value
    validations.append(("Cliente", template_client == generated_client, f"Template: {template_client}, Gerado: {generated_client}"))
    
    # 3. Verificar cabeçalhos da tabela
    headers = [
        ('A16', 'Services'),
        ('B16', 'Unit Price'),
        ('C16', 'Quantity'),
        ('D16', 'Final Price')
    ]
    
    for cell_ref, expected in headers:
        template_val = template_ws[cell_ref].value
        generated_val = generated_ws[cell_ref].value
        validations.append((f"Cabeçalho {cell_ref}", template_val == generated_val, f"Template: {template_val}, Gerado: {generated_val}"))
    
    # 4. Verificar se dados foram preenchidos
    data_filled = []
    for row in [18, 21, 24, 27]:  # Primeiras linhas de cada grupo
        for col in ['A', 'B', 'C', 'D']:
            cell_ref = f"{col}{row}"
            value = generated_ws[cell_ref].value
            if value is not None and str(value).strip():
                data_filled.append(cell_ref)
    
    validations.append(("Dados preenchidos", len(data_filled) > 0, f"Células com dados: {len(data_filled)}"))
    
    # 5. Verificar fórmula de soma
    template_formula = template_ws['D30'].value
    generated_formula = generated_ws['D30'].value
    validations.append(("Fórmula de soma", template_formula == generated_formula, f"Template: {template_formula}, Gerado: {generated_formula}"))
    
    # 6. Verificar células mescladas
    template_merged = len(list(template_ws.merged_cells.ranges))
    generated_merged = len(list(generated_ws.merged_cells.ranges))
    validations.append(("Células mescladas", template_merged == generated_merged, f"Template: {template_merged}, Gerado: {generated_merged}"))
    
    # 7. Verificar larguras das colunas
    column_widths = []
    for col in ['A', 'B', 'C', 'D']:
        template_width = template_ws.column_dimensions[col].width
        generated_width = generated_ws.column_dimensions[col].width
        width_match = abs(template_width - generated_width) < 0.1  # Tolerância pequena
        column_widths.append((f"Largura coluna {col}", width_match, f"Template: {template_width}, Gerado: {generated_width}"))
    
    validations.extend(column_widths)
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS DA VALIDAÇÃO:")
    print("-" * 50)
    
    passed = 0
    total = len(validations)
    
    for test_name, passed_test, details in validations:
        status = "✅" if passed_test else "❌"
        print(f"{status} {test_name}")
        if not passed_test:
            print(f"    {details}")
        else:
            passed += 1
    
    # Verificar dados específicos preenchidos
    print(f"\n📋 DADOS PREENCHIDOS:")
    print("-" * 30)
    
    for row in [18, 21, 24, 27]:
        row_data = []
        for col in ['A', 'B', 'C', 'D']:
            cell_ref = f"{col}{row}"
            value = generated_ws[cell_ref].value
            if value is not None:
                row_data.append(f"{cell_ref}:{value}")
        
        if row_data:
            print(f"Linha {row}: {' | '.join(row_data)}")
    
    # Resumo final
    print(f"\n📈 RESUMO:")
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"❌ Testes falharam: {total - passed}/{total}")
    
    success_rate = (passed / total) * 100
    print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
    
    template_wb.close()
    generated_wb.close()
    
    return success_rate >= 80  # 80% de conformidade mínima

if __name__ == "__main__":
    success = validate_template_compliance()
    
    if success:
        print(f"\n🎉 VALIDAÇÃO PASSOU!")
        print(f"✅ A invoice gerada está em conformidade com o template!")
    else:
        print(f"\n❌ VALIDAÇÃO FALHOU!")
        print(f"⚠️  A invoice gerada não está totalmente conforme o template!")
