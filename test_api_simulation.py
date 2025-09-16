#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path('app')))

import json
import uuid
from api.server import _build_preview_single_file, _find_template_for_employee
from invoice.template_filler import generate_from_abz_template
from openpyxl import load_workbook

def simulate_api_generation():
    """Simula exatamente o que a API faz"""
    
    # Usar planilha sem templates
    test_abz = Path('DADOS/ABZ_TEST_NO_TEMPLATES.xlsx')
    
    if not test_abz.exists():
        print("ERROR: Planilha de teste não encontrada")
        return False
    
    print(f"=== SIMULAÇÃO DA API ===")
    print(f"Usando planilha: {test_abz}")
    
    # 1. Build preview (como na API)
    try:
        preview = _build_preview_single_file(test_abz)
        print(f"✅ Preview gerado: {len(preview)} funcionários")
    except Exception as e:
        print(f"❌ Erro no preview: {e}")
        return False
    
    # 2. Verificar templates na planilha (como na API)
    try:
        wb = load_workbook(test_abz, read_only=True)
        sheets = wb.sheetnames
        invoice_sheets = [s for s in sheets if s.lower().strip().endswith('_invoice')]
        wb.close()
        print(f"📋 Invoice sheets encontradas: {invoice_sheets}")
    except Exception as e:
        print(f"❌ Erro ao verificar templates: {e}")
        return False
    
    # 3. Simular geração para cada funcionário
    print(f"\n=== SIMULANDO GERAÇÃO ===")
    
    generated_count = 0
    total = len(preview)
    
    for i, (name, pdata) in enumerate(preview.items(), 1):
        print(f"\n🔄 Processando {i}/{total}: {name}")
        
        # Verificar se há items
        items = list(pdata.get("items") or [])
        print(f"📊 Items: {len(items)}")
        
        if not items:
            print(f"⚠️ Pulando {name} - sem items")
            continue
        
        # Encontrar template (como na API)
        tpl = _find_template_for_employee(name, invoice_sheets)
        use_default_template = False
        
        if not tpl:
            use_default_template = True
            tpl = "default_template"
            print(f"🔧 Usando template padrão para {name}")
        else:
            print(f"📋 Usando template ABZ: {tpl} para {name}")
        
        # Simular metadados
        m = dict(pdata.get("meta") or {})
        m["invoice_date"] = "15/09/2025"
        m["invoice_no"] = f"{i:03d}/2025"
        m["call_off"] = None
        
        # Gerar invoice
        try:
            print(f"🔧 Gerando invoice para {name}...")
            
            out_path = generate_from_abz_template(
                abz_xlsx=test_abz,
                template_sheet_name=tpl,
                employee_name=name,
                line_items=items,
                out_dir=Path('out/test_api_sim'),
                invoice_date=m.get("invoice_date"),
                invoice_no=m.get("invoice_no"),
                call_off=m.get("call_off"),
                use_default_template=use_default_template,
            )
            
            if out_path.exists():
                print(f"✅ Invoice gerada: {out_path.name} ({out_path.stat().st_size} bytes)")
                generated_count += 1
            else:
                print(f"❌ Arquivo não foi criado para {name}")
                
        except Exception as e:
            print(f"❌ Erro ao gerar invoice para {name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== RESULTADO ===")
    print(f"Total de funcionários: {total}")
    print(f"Invoices geradas: {generated_count}")
    
    return generated_count > 0

if __name__ == "__main__":
    success = simulate_api_generation()
    if success:
        print("\n🎉 SIMULAÇÃO PASSOU!")
        print("O template padrão funciona corretamente.")
        print("O problema deve estar em outro lugar da API.")
    else:
        print("\n❌ SIMULAÇÃO FALHOU.")
        sys.exit(1)
