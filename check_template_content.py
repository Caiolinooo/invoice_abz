#!/usr/bin/env python3
"""
Verificar se o template original já tem conteúdo nas células da tabela
"""

from pathlib import Path
from openpyxl import load_workbook

def check_template_content():
    """Verifica o conteúdo original do template"""
    
    print("🔍 VERIFICANDO CONTEÚDO ORIGINAL DO TEMPLATE")
    print("=" * 50)
    
    template_path = Path("DADOS/Template_Invoice_Geral.xlsx")
    
    if not template_path.exists():
        print(f"❌ Template não encontrado: {template_path}")
        return
    
    # Carregar template
    wb = load_workbook(template_path)
    ws = wb.active
    
    print(f"📋 Template: {template_path.name}")
    
    # Verificar conteúdo da área da tabela de serviços
    print(f"\n📊 CONTEÚDO ORIGINAL DA TABELA DE SERVIÇOS:")
    print("-" * 45)
    
    # Verificar linhas 18-29 (área da tabela)
    for row in range(18, 30):
        row_content = []
        for col in ['A', 'B', 'C', 'D']:
            cell_value = ws[f'{col}{row}'].value
            if cell_value and str(cell_value).strip():
                row_content.append(f"{col}{row}:'{cell_value}'")
        
        if row_content:
            print(f"  Linha {row}: {' | '.join(row_content)}")
        else:
            print(f"  Linha {row}: (vazia)")
    
    # Verificar especificamente as linhas dos grupos
    print(f"\n🎯 GRUPOS DE CÉLULAS MESCLADAS:")
    print("-" * 30)
    
    groups = [
        (18, "Grupo 1 (18-20)"),
        (21, "Grupo 2 (21-23)"),
        (24, "Grupo 3 (24-26)"),
        (27, "Grupo 4 (27-29)")
    ]
    
    for row, desc in groups:
        values = []
        for col in ['A', 'B', 'C', 'D']:
            cell_value = ws[f'{col}{row}'].value
            values.append(f"{col}:'{cell_value}'" if cell_value else f"{col}:None")
        
        print(f"  {desc}: {' | '.join(values)}")
    
    wb.close()

if __name__ == "__main__":
    check_template_content()
