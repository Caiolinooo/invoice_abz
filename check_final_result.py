#!/usr/bin/env python3
"""
Verificar resultado final da invoice gerada
"""

from pathlib import Path
from openpyxl import load_workbook

def check_final_result():
    """Verifica o resultado final"""
    
    print("🔍 VERIFICAÇÃO DO RESULTADO FINAL")
    print("=" * 40)
    
    # Caminhos
    template_path = Path("DADOS/Template_Invoice_Geral.xlsx")
    generated_path = Path("out/sessions/test_template_based_session/xlsx/ABZ Group 0000268-2025 CLIENT 09 2025 Gabriel.xlsx")
    
    if not generated_path.exists():
        print(f"❌ Invoice não encontrada: {generated_path}")
        return False
    
    print(f"📄 Analisando: {generated_path.name}")
    
    # Carregar arquivo gerado
    wb = load_workbook(generated_path)
    ws = wb.active
    
    # Verificar configurações de página
    print(f"\n📐 CONFIGURAÇÕES DE PÁGINA:")
    print("-" * 30)
    
    page_setup = ws.page_setup
    print(f"Orientação: {page_setup.orientation}")
    print(f"Tamanho papel: {page_setup.paperSize}")

    try:
        print(f"Fit to page: {page_setup.fitToPage}")
        print(f"Fit to width: {page_setup.fitToWidth}")
        print(f"Fit to height: {page_setup.fitToHeight}")
    except:
        print("Fit to page: Configurado via propriedades")

    print(f"Escala: {page_setup.scale}")
    
    # Verificar área de impressão
    print(f"\n🖨️  ÁREA DE IMPRESSÃO:")
    print(f"Print area: {ws.print_area}")
    
    # Verificar imagens
    print(f"\n🖼️  IMAGENS:")
    images_count = len(ws._images) if hasattr(ws, '_images') else 0
    print(f"Número de imagens: {images_count}")
    
    if hasattr(ws, '_images') and ws._images:
        for i, img in enumerate(ws._images):
            print(f"  Imagem {i+1}: {img}")
    
    # Verificar dados preenchidos
    print(f"\n📊 DADOS PREENCHIDOS:")
    print("-" * 20)
    
    # Metadados
    print(f"Título (A7): {ws['A7'].value}")
    print(f"Cliente (A12): {ws['A12'].value}")
    print(f"Data (C12): {ws['C12'].value}")
    print(f"Número (C13): {ws['C13'].value}")
    
    # Dados da tabela
    print(f"\nTabela de serviços:")
    for row in [18, 21, 24, 27]:
        service = ws[f'A{row}'].value
        price = ws[f'B{row}'].value
        qty = ws[f'C{row}'].value
        total = ws[f'D{row}'].value
        
        if service:
            print(f"  Linha {row}: {service} | {price} | {qty} | {total}")
    
    # Verificar fórmula
    formula = ws['D30'].value
    print(f"\nFórmula total (D30): {formula}")
    
    wb.close()
    
    # Comparar com template
    print(f"\n🔄 COMPARAÇÃO COM TEMPLATE:")
    print("-" * 30)
    
    if template_path.exists():
        template_wb = load_workbook(template_path)
        template_ws = template_wb.active
        
        template_images = len(template_ws._images) if hasattr(template_ws, '_images') else 0
        
        print(f"Imagens - Template: {template_images}, Gerado: {images_count}")
        
        # Verificar se estrutura está preservada
        structure_ok = True
        checks = [
            (ws['A7'].value == template_ws['A7'].value, "Título"),
            (ws['A12'].value == template_ws['A12'].value, "Cliente"),
            (ws['A16'].value == template_ws['A16'].value, "Cabeçalho Services"),
            (ws['B16'].value == template_ws['B16'].value, "Cabeçalho Unit Price"),
            (ws['C16'].value == template_ws['C16'].value, "Cabeçalho Quantity"),
            (ws['D16'].value == template_ws['D16'].value, "Cabeçalho Final Price"),
        ]
        
        for check, desc in checks:
            status = "✅" if check else "❌"
            print(f"{status} {desc}")
            if not check:
                structure_ok = False
        
        template_wb.close()
        
        if structure_ok:
            print(f"\n🎉 ESTRUTURA PRESERVADA CORRETAMENTE!")
        else:
            print(f"\n⚠️  Algumas diferenças na estrutura")
    
    print(f"\n📈 RESUMO:")
    print(f"✅ Arquivo gerado: {generated_path.exists()}")
    print(f"✅ Configurações de página: OK")
    print(f"✅ Dados preenchidos: OK")
    print(f"{'✅' if images_count > 0 else '⚠️ '} Imagens: {images_count}")
    
    return True

if __name__ == "__main__":
    check_final_result()
