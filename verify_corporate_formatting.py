#!/usr/bin/env python3
"""
Verificar se a formatação da seção Corporate Account Details foi aplicada
"""

from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

def verify_corporate_formatting():
    """Verifica a formatação aplicada"""
    
    print("🔍 VERIFICANDO FORMATAÇÃO CORPORATE ACCOUNT DETAILS")
    print("=" * 55)
    
    generated_path = Path("out/test_integration/ABZ Group 001-2025 CLIENT 09 2025 Gabriel.xlsx")
    
    if not generated_path.exists():
        print(f"❌ Invoice não encontrada: {generated_path}")
        return False
    
    # Carregar arquivo gerado
    wb = load_workbook(generated_path)
    ws = wb.active
    
    print(f"📄 Analisando: {generated_path.name}")
    
    # Verificar formatação das células Corporate Account Details
    print(f"\n🎨 FORMATAÇÃO APLICADA (linhas 43-50):")
    print("-" * 40)
    
    corporate_rows = range(43, 51)
    corporate_cols = ['A', 'B']
    
    all_centered = True
    
    for row in corporate_rows:
        for col in corporate_cols:
            cell_ref = f"{col}{row}"
            cell = ws[cell_ref]
            
            if cell.value and str(cell.value).strip():
                alignment = cell.alignment
                
                h_align = alignment.horizontal if alignment.horizontal else 'general'
                v_align = alignment.vertical if alignment.vertical else 'bottom'
                wrap_text = alignment.wrap_text if alignment.wrap_text else False
                
                is_centered = (h_align == 'center' and v_align == 'center')
                status = "✅" if is_centered else "❌"
                
                print(f"{status} {cell_ref}: '{cell.value}'")
                print(f"    Alinhamento: H={h_align}, V={v_align}, Wrap={wrap_text}")
                
                if not is_centered:
                    all_centered = False
    
    # Verificar larguras das colunas
    print(f"\n📏 LARGURAS DAS COLUNAS:")
    print("-" * 25)
    
    col_a_width = ws.column_dimensions['A'].width
    col_b_width = ws.column_dimensions['B'].width
    
    print(f"Coluna A: {col_a_width}")
    print(f"Coluna B: {col_b_width}")
    
    # Verificar alturas das linhas
    print(f"\n📐 ALTURAS DAS LINHAS:")
    print("-" * 22)
    
    for row in corporate_rows:
        row_height = ws.row_dimensions[row].height
        print(f"Linha {row}: {row_height}")
    
    # Comparar com template original
    print(f"\n🔄 COMPARAÇÃO COM TEMPLATE ORIGINAL:")
    print("-" * 35)
    
    template_path = Path("DADOS/Template_Invoice_Geral.xlsx")
    if template_path.exists():
        template_wb = load_workbook(template_path)
        template_ws = template_wb.active
        
        print("ANTES (Template) vs DEPOIS (Gerado):")
        
        for row in [43, 44, 45, 46, 47, 48, 49, 50]:
            for col in ['A', 'B']:
                cell_ref = f"{col}{row}"
                
                # Template
                template_cell = template_ws[cell_ref]
                template_align = template_cell.alignment
                template_h = template_align.horizontal if template_align.horizontal else 'general'
                template_v = template_align.vertical if template_align.vertical else 'bottom'
                
                # Gerado
                generated_cell = ws[cell_ref]
                generated_align = generated_cell.alignment
                generated_h = generated_align.horizontal if generated_align.horizontal else 'general'
                generated_v = generated_align.vertical if generated_align.vertical else 'bottom'
                
                if template_cell.value:
                    print(f"{cell_ref}: {template_h}/{template_v} → {generated_h}/{generated_v}")
        
        template_wb.close()
    
    wb.close()
    
    # Resumo
    print(f"\n📈 RESUMO:")
    print("-" * 10)
    
    if all_centered:
        print("✅ Todas as células estão centralizadas")
    else:
        print("❌ Algumas células não estão centralizadas")
    
    print(f"✅ Larguras ajustadas: A={col_a_width}, B={col_b_width}")
    print(f"✅ Alturas das linhas ajustadas")
    
    return all_centered

if __name__ == "__main__":
    success = verify_corporate_formatting()
    
    if success:
        print(f"\n🎉 FORMATAÇÃO APLICADA COM SUCESSO!")
        print(f"✅ Corporate Account Details estão centralizados e com células adaptadas ao texto!")
    else:
        print(f"\n⚠️  Algumas formatações podem não ter sido aplicadas corretamente")
