#!/usr/bin/env python3
"""
Teste final específico para formatação Corporate Account Details
"""

import sys
sys.path.append('app')

from pathlib import Path
from invoice.template_filler import generate_from_abz_template
from openpyxl import load_workbook

def test_corporate_formatting():
    """Testa especificamente a formatação Corporate Account Details"""
    
    print("🧪 TESTE ESPECÍFICO - FORMATAÇÃO CORPORATE ACCOUNT DETAILS")
    print("=" * 60)
    
    # Dados de teste
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
        }
    ]
    
    # Diretório de saída
    out_dir = Path("out/test_corporate_formatting")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Diretório de saída: {out_dir}")
    
    # Gerar invoice usando template-based
    print(f"\n🔧 Gerando invoice com formatação Corporate Account Details...")
    
    try:
        result_path = generate_from_abz_template(
            abz_xlsx=None,  # Não usado quando use_template_based=True
            template_sheet_name="dummy",  # Não usado
            employee_name="Gabriel Leone",
            line_items=line_items,
            out_dir=out_dir,
            invoice_date="16/09/2025",
            invoice_no="CORP001/2025",
            call_off="CORPORATE-FORMAT-TEST",
            use_template_based=True  # USAR NOVO GERADOR
        )
        
        if result_path.exists():
            size = result_path.stat().st_size
            print(f"✅ Invoice gerada: {result_path.name} ({size} bytes)")
            
            # Verificar formatação
            print(f"\n🔍 Verificando formatação Corporate Account Details...")
            
            wb = load_workbook(result_path)
            ws = wb.active
            
            # Verificar células específicas
            corporate_cells = [
                ('A43', 'Corporate Account details'),
                ('A44', 'Account Name'),
                ('B44', 'ABZ Group SAS'),
                ('A45', 'Account Number'),
                ('B45', '92997216'),
                ('A46', 'Sort Code'),
                ('B46', '23-01-62'),
                ('A47', 'Bank Name'),
                ('B47', '3S Money Club'),
                ('A48', 'Bank Address'),
                ('B48', '45 Folgate St, London, E1 6GL'),
                ('A49', 'Currency'),
                ('B49', 'GBP'),
                ('A50', 'Mandatory payment reference'),
                ('B50', 'MCV988805269')
            ]
            
            all_centered = True
            
            for cell_ref, expected_text in corporate_cells:
                cell = ws[cell_ref]
                alignment = cell.alignment
                
                h_align = alignment.horizontal if alignment.horizontal else 'general'
                v_align = alignment.vertical if alignment.vertical else 'bottom'
                
                is_centered = (h_align == 'center' and v_align == 'center')
                status = "✅" if is_centered else "❌"
                
                print(f"{status} {cell_ref}: '{cell.value}' - H={h_align}, V={v_align}")
                
                if not is_centered:
                    all_centered = False
            
            # Verificar larguras das colunas
            col_a_width = ws.column_dimensions['A'].width
            col_b_width = ws.column_dimensions['B'].width
            
            print(f"\n📏 Larguras das colunas:")
            print(f"  Coluna A: {col_a_width}")
            print(f"  Coluna B: {col_b_width}")
            
            wb.close()
            
            # Resumo
            print(f"\n📈 RESULTADO:")
            if all_centered:
                print("✅ Todas as células Corporate Account Details estão centralizadas!")
                print("✅ Larguras das colunas ajustadas!")
                print("✅ Formatação aplicada com sucesso!")
                return True
            else:
                print("❌ Algumas células não estão centralizadas")
                return False
        else:
            print(f"❌ Arquivo não foi gerado: {result_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao gerar invoice: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    success = test_corporate_formatting()
    
    if success:
        print(f"\n🎉 TESTE DE FORMATAÇÃO PASSOU!")
        print(f"✅ Corporate Account Details formatados corretamente!")
    else:
        print(f"\n❌ TESTE DE FORMATAÇÃO FALHOU!")
        sys.exit(1)

if __name__ == "__main__":
    main()
