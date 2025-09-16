#!/usr/bin/env python3
"""
Script para criar uma planilha ABZ de teste SEM templates (_invoice sheets).
Isso vai testar se o sistema funciona com o template padrão.
"""

from pathlib import Path
import sys
sys.path.append(str(Path('app')))

import pandas as pd
from openpyxl import load_workbook

def create_test_abz_without_templates():
    """Cria uma planilha ABZ de teste sem templates"""
    
    # Encontrar planilha ABZ original
    root = Path('.')
    abz_files = list((root/'DADOS').glob('*.xlsx'))
    abz_file = None
    
    for f in abz_files:
        if 'ABZ' in f.name.upper():
            abz_file = f
            break
    
    if not abz_file:
        print("❌ Arquivo ABZ não encontrado em DADOS/")
        return False
    
    print(f"📁 Usando arquivo ABZ original: {abz_file}")
    
    # Carregar workbook
    wb = load_workbook(abz_file)
    
    # Remover todas as sheets de template (_invoice)
    template_sheets = [s for s in wb.sheetnames if s.lower().endswith('_invoice')]
    
    print(f"🗑️ Removendo {len(template_sheets)} templates: {template_sheets}")
    
    for sheet_name in template_sheets:
        if sheet_name in wb.sheetnames:
            wb.remove(wb[sheet_name])
            print(f"   ❌ Removido: {sheet_name}")
    
    # Manter apenas as sheets essenciais (Charge Rate, etc.)
    remaining_sheets = wb.sheetnames
    print(f"📋 Sheets restantes: {remaining_sheets}")
    
    # Salvar planilha de teste
    test_path = Path('DADOS/ABZ_TEST_NO_TEMPLATES.xlsx')
    wb.save(test_path)
    wb.close()
    
    print(f"✅ Planilha de teste criada: {test_path}")
    print("   Esta planilha NÃO possui templates (_invoice sheets)")
    print("   O sistema deve usar o template padrão para gerar invoices")
    
    return True

if __name__ == "__main__":
    success = create_test_abz_without_templates()
    if success:
        print("\n🎉 Planilha de teste criada com sucesso!")
        print("   Agora você pode testar o sistema sem templates.")
    else:
        print("\n❌ Falha ao criar planilha de teste.")
        sys.exit(1)
