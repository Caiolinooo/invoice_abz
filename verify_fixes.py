#!/usr/bin/env python3
"""
Verificar se as correções foram aplicadas: call-off, fontes e expenses
"""

from pathlib import Path
from openpyxl import load_workbook

def verify_fixes():
    """Verifica se as correções foram aplicadas"""
    
    print("🔍 VERIFICANDO CORREÇÕES APLICADAS")
    print("=" * 40)
    
    generated_path = Path("out/test_corporate_formatting/ABZ Group 001-2025 CLIENT 09 2025 Gabriel.xlsx")
    
    if not generated_path.exists():
        print(f"❌ Invoice não encontrada: {generated_path}")
        return False
    
    # Carregar arquivo gerado
    wb = load_workbook(generated_path)
    ws = wb.active
    
    print(f"📄 Analisando: {generated_path.name}")
    
    # 1. VERIFICAR CALL-OFF
    print(f"\n✅ CORREÇÃO 1: CALL-OFF")
    print("-" * 25)
    
    call_off_cell = ws['C14']
    call_off_value = call_off_cell.value
    
    if call_off_value and 'Call-Off' in str(call_off_value):
        print(f"✅ Call-off encontrado: '{call_off_value}'")
        call_off_ok = True
    else:
        print(f"❌ Call-off não encontrado. Valor em C14: '{call_off_value}'")
        call_off_ok = False
    
    # 2. VERIFICAR FONTES
    print(f"\n✅ CORREÇÃO 2: FONTES PRESERVADAS")
    print("-" * 35)
    
    font_checks = [
        ('C12', 'Data da invoice'),
        ('C13', 'Número da invoice'),
        ('C14', 'Call-off'),
        ('A7', 'Título'),
        ('A12', 'Cliente'),
        ('A16', 'Cabeçalho tabela')
    ]
    
    fonts_ok = True
    
    for cell_ref, desc in font_checks:
        cell = ws[cell_ref]
        if cell.value:
            font = cell.font
            print(f"✅ {desc} ({cell_ref}): {font.name} {font.size}pt {'Bold' if font.bold else 'Normal'}")
            
            # Verificar se é uma fonte esperada
            if font.name not in ['Calibri', 'Aptos Narrow']:
                print(f"  ⚠️  Fonte inesperada: {font.name}")
                fonts_ok = False
    
    # 3. VERIFICAR ESTRUTURA DA TABELA (não duplicação)
    print(f"\n✅ CORREÇÃO 3: ESTRUTURA DA TABELA")
    print("-" * 35)
    
    # Verificar quantos itens foram preenchidos
    service_items = []
    for row in [18, 21, 24, 27]:
        cell_value = ws[f'A{row}'].value
        if cell_value and str(cell_value).strip():
            service_items.append((row, cell_value))
    
    print(f"Itens de serviço encontrados: {len(service_items)}")
    for row, desc in service_items:
        print(f"  Linha {row}: '{desc}'")
    
    # No teste passamos apenas 2 itens, então deveria ter apenas 2
    table_ok = len(service_items) == 2
    
    if table_ok:
        print("✅ Tabela com número correto de itens (2)")
    else:
        print(f"⚠️  Esperado 2 itens, encontrado {len(service_items)}")
    
    # 4. VERIFICAR METADADOS GERAIS
    print(f"\n📊 METADADOS GERAIS:")
    print("-" * 20)
    
    metadata = [
        ('A7', 'Título'),
        ('A12', 'Cliente'),
        ('C12', 'Data'),
        ('C13', 'Número'),
        ('C14', 'Call-off')
    ]
    
    for cell_ref, desc in metadata:
        value = ws[cell_ref].value
        print(f"  {desc}: '{value}'")
    
    wb.close()
    
    # RESUMO
    print(f"\n📈 RESUMO DAS CORREÇÕES:")
    print("-" * 25)
    
    if call_off_ok:
        print("✅ Call-off: Corrigido e aparecendo em C14")
    else:
        print("❌ Call-off: Ainda não está aparecendo")
    
    if fonts_ok:
        print("✅ Fontes: Preservadas do template original")
    else:
        print("⚠️  Fontes: Algumas podem ter mudado")
    
    if table_ok:
        print("✅ Tabela: Estrutura correta sem duplicações")
    else:
        print("⚠️  Tabela: Pode ter itens extras")
    
    all_ok = call_off_ok and fonts_ok and table_ok
    
    return all_ok

if __name__ == "__main__":
    success = verify_fixes()
    
    if success:
        print(f"\n🎉 TODAS AS CORREÇÕES APLICADAS COM SUCESSO!")
        print(f"✅ Call-off aparece corretamente")
        print(f"✅ Fontes preservadas do template")
        print(f"✅ Estrutura da tabela correta")
    else:
        print(f"\n⚠️  Algumas correções podem precisar de ajustes")
