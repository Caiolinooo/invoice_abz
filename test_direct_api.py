#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path('app')))

import json
import uuid
from utils.abz_charge_rate_parser import read_charge_rate_table
from invoice.template_filler import generate_from_abz_template

def test_direct_generation():
    """Teste direto da geração sem API"""
    
    # Usar planilha sem templates
    test_abz = Path('DADOS/ABZ_TEST_NO_TEMPLATES.xlsx')
    
    if not test_abz.exists():
        print("ERROR: Planilha de teste não encontrada")
        return False
    
    print(f"Usando planilha: {test_abz}")
    
    # Ler dados da planilha
    try:
        df = read_charge_rate_table(test_abz, 'Charge Rate')
        print(f"Dados carregados: {len(df)} linhas")
    except Exception as e:
        print(f"ERROR ao ler planilha: {e}")
        return False
    
    if df.empty:
        print("ERROR: Nenhum dado encontrado")
        return False
    
    # Usar a mesma lógica do servidor
    sys.path.append('app/api')
    from server import _build_preview_single_file

    preview = _build_preview_single_file(test_abz)
    print(f"Preview gerado: {len(preview)} funcionários")

    # Encontrar funcionário com dados
    selected_name = None
    selected_data = None

    for name, data in preview.items():
        items = data.get('items', [])
        if items:
            selected_name = name
            selected_data = data
            break

    if not selected_name:
        print("ERROR: Nenhum funcionário com dados encontrado")
        print("Funcionários disponíveis:")
        for name, data in preview.items():
            items = data.get('items', [])
            print(f"  - {name}: {len(items)} items")
        return False

    print(f"Processando: {selected_name}")
    print(f"Dados do funcionário:")
    print(f"  - Items: {len(selected_data.get('items', []))}")
    print(f"  - Meta: {selected_data.get('meta', {})}")
    
    # Gerar invoice com template padrão
    try:
        items = selected_data.get('items', [])
        if not items:
            print("ERROR: Nenhum item para gerar")
            return False

        print("Gerando invoice com template padrão...")
        print(f"Items a processar: {items}")

        out_path = generate_from_abz_template(
            abz_xlsx=test_abz,
            template_sheet_name="dummy",  # Não será usado
            employee_name=selected_name,
            line_items=items,
            out_dir=Path('out/test_direct'),
            invoice_date='15/09/2025',
            invoice_no='DIRECT001/2025',
            call_off='DIRECT-TEST',
            use_default_template=True,  # USAR TEMPLATE PADRÃO
        )
        
        print(f"Invoice gerada: {out_path}")
        
        if out_path.exists():
            print(f"Arquivo criado: {out_path.stat().st_size} bytes")
            return True
        else:
            print("ERROR: Arquivo não foi criado")
            return False
            
    except Exception as e:
        print(f"ERROR na geração: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_generation()
    if success:
        print("\nSUCCESS: Geração direta funciona!")
        print("O problema pode estar na API, não na lógica de geração.")
    else:
        print("\nERROR: Geração direta falhou.")
        sys.exit(1)
