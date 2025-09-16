#!/usr/bin/env python3
"""
Analisar os problemas identificados: Expenses duplicado, call-off e fonte
"""

from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

def analyze_issues():
    """Analisa os problemas identificados"""
    
    print("🔍 ANÁLISE DOS PROBLEMAS IDENTIFICADOS")
    print("=" * 45)
    
    # Caminhos
    template_path = Path("DADOS/Template_Invoice_Geral.xlsx")
    generated_path = Path("out/test_corporate_formatting/ABZ Group 001-2025 CLIENT 09 2025 Gabriel.xlsx")
    
    if not template_path.exists():
        print(f"❌ Template não encontrado: {template_path}")
        return
    
    if not generated_path.exists():
        print(f"❌ Invoice gerada não encontrada: {generated_path}")
        return
    
    # Carregar arquivos
    print(f"📋 Template: {template_path.name}")
    template_wb = load_workbook(template_path)
    template_ws = template_wb.active
    
    print(f"📄 Invoice gerada: {generated_path.name}")
    generated_wb = load_workbook(generated_path)
    generated_ws = generated_wb.active
    
    # 1. ANALISAR PROBLEMA DOS EXPENSES DUPLICADOS
    print(f"\n🔍 PROBLEMA 1: EXPENSES DUPLICADOS")
    print("-" * 35)
    
    print("Conteúdo da tabela de serviços (linhas 18-29):")
    for row in range(18, 30):
        row_content = []
        for col in ['A', 'B', 'C', 'D']:
            cell_value = generated_ws[f'{col}{row}'].value
            if cell_value:
                row_content.append(f"{col}{row}:'{cell_value}'")
        
        if row_content:
            print(f"  Linha {row}: {' | '.join(row_content)}")
    
    # 2. ANALISAR PROBLEMA DO CALL-OFF
    print(f"\n🔍 PROBLEMA 2: CALL-OFF NÃO APARECE")
    print("-" * 35)
    
    # Procurar onde deveria aparecer o call-off
    print("Procurando por 'call' em todo o template:")
    for row in range(1, template_ws.max_row + 1):
        for col in range(1, template_ws.max_column + 1):
            cell_ref = f"{get_column_letter(col)}{row}"
            cell_value = template_ws[cell_ref].value
            
            if cell_value and isinstance(cell_value, str) and 'call' in cell_value.lower():
                print(f"  Template {cell_ref}: '{cell_value}'")
    
    print("\nProcurando por 'call' na invoice gerada:")
    for row in range(1, generated_ws.max_row + 1):
        for col in range(1, generated_ws.max_column + 1):
            cell_ref = f"{get_column_letter(col)}{row}"
            cell_value = generated_ws[cell_ref].value
            
            if cell_value and isinstance(cell_value, str) and 'call' in cell_value.lower():
                print(f"  Gerado {cell_ref}: '{cell_value}'")
    
    # Verificar linha 14 onde geralmente fica call-off
    print(f"\nVerificando linha 14 (onde geralmente fica call-off):")
    for col in ['A', 'B', 'C', 'D']:
        template_val = template_ws[f'{col}14'].value
        generated_val = generated_ws[f'{col}14'].value
        print(f"  {col}14: Template='{template_val}' | Gerado='{generated_val}'")
    
    # 3. ANALISAR PROBLEMA DA FONTE
    print(f"\n🔍 PROBLEMA 3: FONTE DIFERENTE")
    print("-" * 30)
    
    # Verificar fontes em diferentes seções
    sections = [
        ("Título (A7)", "A7"),
        ("Cliente (A12)", "A12"),
        ("Cabeçalho tabela (A16)", "A16"),
        ("Dados tabela (A18)", "A18"),
        ("Corporate details (A43)", "A43"),
        ("Account Name (A44)", "A44"),
        ("Valor account (B44)", "B44")
    ]
    
    for section_name, cell_ref in sections:
        template_cell = template_ws[cell_ref]
        generated_cell = generated_ws[cell_ref]
        
        template_font = template_cell.font
        generated_font = generated_cell.font
        
        print(f"\n{section_name}:")
        print(f"  Template: {template_font.name}, Tamanho={template_font.size}, Bold={template_font.bold}")
        print(f"  Gerado:   {generated_font.name}, Tamanho={generated_font.size}, Bold={generated_font.bold}")
        
        if template_font.name != generated_font.name or template_font.size != generated_font.size:
            print(f"  ❌ DIFERENÇA DETECTADA!")
        else:
            print(f"  ✅ Fonte correta")
    
    # 4. VERIFICAR ESTRUTURA GERAL
    print(f"\n📊 ESTRUTURA GERAL:")
    print("-" * 20)
    
    print("Metadados principais:")
    metadata_cells = [
        ("A7", "Título"),
        ("A12", "Cliente"),
        ("C12", "Data invoice"),
        ("C13", "Número invoice"),
        ("C14", "Call-off (se houver)")
    ]
    
    for cell_ref, desc in metadata_cells:
        template_val = template_ws[cell_ref].value
        generated_val = generated_ws[cell_ref].value
        print(f"  {desc} ({cell_ref}): '{generated_val}'")
        if template_val != generated_val and 'invoice' not in desc.lower():
            print(f"    (Template tinha: '{template_val}')")
    
    template_wb.close()
    generated_wb.close()
    
    print(f"\n💡 RESUMO DOS PROBLEMAS:")
    print("-" * 25)
    print("1. ❌ Expenses pode estar duplicado na tabela")
    print("2. ❌ Call-off não está aparecendo onde deveria")
    print("3. ❌ Fonte pode ter mudado do template original")

if __name__ == "__main__":
    analyze_issues()
