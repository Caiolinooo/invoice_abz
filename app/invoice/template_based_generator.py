#!/usr/bin/env python3
"""
Gerador de invoices baseado no template Template_Invoice_Geral.xlsx
Este gerador preserva toda a formatação, células mescladas e fórmulas do template original
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.cell.cell import MergedCell
from openpyxl.worksheet.worksheet import Worksheet
from datetime import datetime
import shutil
import copy

class TemplateBasedInvoiceGenerator:
    """Gerador de invoices que usa o template fornecido como base"""
    
    def __init__(self, template_path: Path = None):
        """
        Inicializa o gerador com o caminho do template
        
        Args:
            template_path: Caminho para Template_Invoice_Geral.xlsx
        """
        if template_path is None:
            template_path = Path("DADOS/Template_Invoice_Geral.xlsx")
        
        self.template_path = template_path
        
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template não encontrado: {self.template_path}")
    
    def create_invoice(self, 
                      employee_name: str,
                      line_items: List[Dict],
                      output_path: Path,
                      invoice_date: str = None,
                      invoice_no: str = None,
                      call_off: str = None) -> Path:
        """
        Cria uma invoice baseada no template
        
        Args:
            employee_name: Nome do funcionário
            line_items: Lista de itens de serviço
            output_path: Caminho para salvar o arquivo
            invoice_date: Data da invoice (formato DD/MM/YYYY)
            invoice_no: Número da invoice
            call_off: Call-off number
            
        Returns:
            Path do arquivo criado
        """
        
        print(f"🎨 Criando invoice baseada no template para {employee_name}")

        # Copiar template completamente para preservar tudo
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        # Copiar arquivo template para temporário
        shutil.copy2(self.template_path, temp_path)

        # Carregar cópia do template
        wb = load_workbook(temp_path)
        ws = wb.active

        # Aplicar configurações específicas para uma página
        self._ensure_single_page_layout(ws)

        # Preencher dados da invoice
        self._fill_invoice_metadata(ws, invoice_date, invoice_no, call_off)

        # Preencher tabela de serviços
        self._fill_services_table(ws, line_items, call_off)

        # Formatar seção Corporate Account Details
        self._format_corporate_account_details(ws)

        # Preservar fontes do template original
        self._preserve_template_fonts(ws)
        
        # Garantir que diretório de saída existe
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Salvar arquivo
        wb.save(output_path)
        wb.close()

        # Limpar arquivo temporário
        try:
            temp_path.unlink()
        except:
            pass

        print(f"✅ Invoice criada: {output_path}")
        return output_path
    
    def _fill_invoice_metadata(self, ws, invoice_date: str, invoice_no: str, call_off: str):
        """Preenche metadados da invoice (data, número, etc.)"""
        
        # Data da invoice (C12)
        if invoice_date:
            ws['C12'].value = f"Invoice date: {invoice_date}"
        else:
            ws['C12'].value = f"Invoice date: {datetime.now().strftime('%d/%m/%Y')}"
        
        # Número da invoice (C13)
        if invoice_no:
            ws['C13'].value = f"Invoice No: {invoice_no}"
        else:
            ws['C13'].value = "Invoice No: TBD/2025"

        # Call-off (C14) - adicionar se fornecido
        if call_off:
            ws['C14'].value = f"Call-Off: {call_off}"
            print(f"📞 Call-off adicionado: {call_off}")

        print(f"📝 Metadados preenchidos: Data={invoice_date}, No={invoice_no}, Call-off={call_off}")
    
    def _fill_services_table(self, ws, line_items: List[Dict], call_off: str = None):
        """Preenche a tabela de serviços nas linhas 18-29 (células mescladas em grupos de 3)"""

        if not line_items:
            print("⚠️  Nenhum item de serviço fornecido")
            return

        # O template tem células mescladas em grupos de 3 linhas:
        # Grupo 1: linhas 18-20 (A18:A20, B18:B20, C18:C20, D18:D20)
        # Grupo 2: linhas 21-23 (A21:A23, B21:B23, C21:C23, D21:D23)
        # Grupo 3: linhas 24-26 (A24:A26, B24:B26, C24:C26, D24:D26)
        # Grupo 4: linhas 27-29 (A27:A29, B27:B29, C27:C29, D27:D29)

        merged_groups = [
            18,  # Grupo 1: linhas 18-20
            21,  # Grupo 2: linhas 21-23
            24,  # Grupo 3: linhas 24-26
            27,  # Grupo 4: linhas 27-29
        ]

        max_groups = len(merged_groups)

        print(f"📊 Preenchendo {len(line_items)} itens de serviço em {max_groups} grupos de células mescladas")

        # Primeiro, limpar todas as células da tabela de serviços
        self._clear_services_table(ws, merged_groups)

        for i, item in enumerate(line_items[:max_groups]):  # Limitar a 4 grupos
            # Usar a primeira linha de cada grupo mesclado
            row = merged_groups[i]

            # Extrair dados do item
            description = item.get('description', '')
            unit_price = item.get('unit_price', 0)
            quantity = item.get('quantity', 0)
            final_price = item.get('final', 0)

            # Se final_price não estiver definido, calcular
            if not final_price and unit_price and quantity:
                final_price = float(unit_price) * float(quantity)

            # Adicionar call-off à descrição se fornecido
            if call_off and call_off.strip():
                description_with_calloff = f"{description} - {call_off}"
            else:
                description_with_calloff = description

            # Preencher células mescladas (usar primeira célula do grupo)
            self._set_merged_cell_value(ws, f'A{row}', description_with_calloff)

            # Unit Price (B) - só preencher se tiver valor
            if unit_price and float(unit_price) > 0:
                self._set_merged_cell_value(ws, f'B{row}', float(unit_price))
            else:
                self._set_merged_cell_value(ws, f'B{row}', "N/A")

            # Quantity (C) - só preencher se tiver valor
            if quantity and float(quantity) > 0:
                self._set_merged_cell_value(ws, f'C{row}', float(quantity))
            else:
                self._set_merged_cell_value(ws, f'C{row}', "N/A")

            # Final Price (D)
            if final_price and float(final_price) > 0:
                self._set_merged_cell_value(ws, f'D{row}', float(final_price))
            else:
                self._set_merged_cell_value(ws, f'D{row}', 0.0)

            print(f"  Grupo {i+1} (linha {row}): {description_with_calloff} | {unit_price} | {quantity} | {final_price}")

        if len(line_items) > max_groups:
            print(f"⚠️  Atenção: {len(line_items) - max_groups} itens foram omitidos (máximo {max_groups} grupos)")

        # A fórmula =SUM(D18:D29) já existe em D30, não precisa alterar
        print(f"✅ Tabela de serviços preenchida com {min(len(line_items), max_groups)} itens")

    def _clear_services_table(self, ws, merged_groups):
        """Limpa todas as células da tabela de serviços antes de preencher"""
        try:
            print("🧹 Limpando tabela de serviços...")

            # Limpar todas as células dos grupos de serviços
            for row in merged_groups:
                for col in ['A', 'B', 'C', 'D']:
                    # Limpar célula mesclada usando o método específico
                    self._set_merged_cell_value(ws, f'{col}{row}', None)

            print("✅ Tabela de serviços limpa")

        except Exception as e:
            print(f"⚠️  Erro ao limpar tabela de serviços: {e}")

    def _set_cell_value(self, ws, cell_ref: str, value):
        """Define valor de uma célula, lidando com células mescladas"""
        try:
            cell = ws[cell_ref]
            if isinstance(cell, MergedCell):
                print(f"⚠️  {cell_ref} é uma célula mesclada, pulando...")
                return
            cell.value = value
        except Exception as e:
            print(f"⚠️  Erro ao definir valor em {cell_ref}: {e}")

    def _set_merged_cell_value(self, ws, cell_ref: str, value):
        """Define valor em uma célula mesclada usando unmerge/merge"""
        try:
            # Encontrar o range mesclado que contém esta célula
            merged_range = None
            for range_obj in ws.merged_cells.ranges:
                if cell_ref in range_obj:
                    merged_range = range_obj
                    break

            if merged_range:
                # Desmerge temporariamente
                ws.unmerge_cells(str(merged_range))

                # Define o valor na célula superior esquerda
                top_left = str(merged_range).split(':')[0]
                ws[top_left].value = value

                # Merge novamente
                ws.merge_cells(str(merged_range))

                print(f"✅ Valor definido em célula mesclada {cell_ref} (range: {merged_range})")
            else:
                # Não é célula mesclada, definir normalmente
                ws[cell_ref].value = value

        except Exception as e:
            print(f"⚠️  Erro ao definir valor em célula mesclada {cell_ref}: {e}")

    def _ensure_single_page_layout(self, ws: Worksheet):
        """Garante que o layout caiba em uma única página"""
        try:
            # Configurações de página para forçar uma página
            page_setup = ws.page_setup

            # Orientação retrato
            page_setup.orientation = 'portrait'

            # Tamanho A4
            page_setup.paperSize = 9

            # Forçar ajuste em uma página
            page_setup.fitToPage = True
            page_setup.fitToWidth = 1
            page_setup.fitToHeight = 1

            # Remover escala fixa para permitir ajuste automático
            page_setup.scale = None

            # Área de impressão específica
            ws.print_area = 'A1:D50'

            # Configurações de propriedades da planilha
            if hasattr(ws, 'sheet_properties') and hasattr(ws.sheet_properties, 'pageSetUpPr'):
                ws.sheet_properties.pageSetUpPr.fitToPage = True

            print("✅ Layout configurado para uma página")

        except Exception as e:
            print(f"⚠️  Erro ao configurar layout: {e}")

    def _format_corporate_account_details(self, ws: Worksheet):
        """Formata a seção Corporate Account Details"""
        try:
            from openpyxl.styles import Alignment

            print("🏦 Formatando seção Corporate Account Details")

            # Definir área dos detalhes corporativos (linhas 43-50)
            corporate_rows = range(43, 51)  # 43 a 50
            corporate_cols = ['A', 'B']

            # Aplicar formatação para cada célula
            for row in corporate_rows:
                for col in corporate_cols:
                    cell_ref = f"{col}{row}"
                    cell = ws[cell_ref]

                    if cell.value and str(cell.value).strip():
                        # Centralizar em todas as direções
                        cell.alignment = Alignment(
                            horizontal='center',
                            vertical='center',
                            wrap_text=True  # Permitir quebra de texto
                        )

                        print(f"  ✅ {cell_ref}: '{cell.value}' - centralizado")

            # Ajustar largura das colunas para se adaptar ao texto
            # Coluna A (labels)
            ws.column_dimensions['A'].auto_size = True
            ws.column_dimensions['A'].width = max(20, ws.column_dimensions['A'].width or 20)

            # Coluna B (valores)
            ws.column_dimensions['B'].auto_size = True
            ws.column_dimensions['B'].width = max(25, ws.column_dimensions['B'].width or 25)

            print("  ✅ Larguras das colunas ajustadas automaticamente")

            # Ajustar altura das linhas para acomodar texto centralizado
            for row in corporate_rows:
                ws.row_dimensions[row].height = max(18, ws.row_dimensions[row].height or 18)

            print("  ✅ Alturas das linhas ajustadas")
            print("✅ Formatação Corporate Account Details concluída")

        except Exception as e:
            print(f"⚠️  Erro ao formatar Corporate Account Details: {e}")

    def _preserve_template_fonts(self, ws: Worksheet):
        """Garante que as fontes do template original sejam preservadas"""
        try:
            # Como estamos copiando o template original, as fontes já devem estar preservadas
            # Esta função serve como verificação e correção se necessário

            # Verificar se alguma célula perdeu a fonte original
            # (isso pode acontecer quando definimos novos valores)

            # Células que podem ter perdido formatação ao serem preenchidas
            cells_to_check = [
                ('C12', 'Calibri', 12.0, True),   # Data da invoice
                ('C13', 'Calibri', 12.0, True),   # Número da invoice
                ('C14', 'Calibri', 12.0, False),  # Call-off
            ]

            from openpyxl.styles import Font

            for cell_ref, font_name, font_size, is_bold in cells_to_check:
                cell = ws[cell_ref]
                if cell.value:  # Só aplicar se a célula tiver conteúdo
                    current_font = cell.font

                    # Verificar se precisa corrigir a fonte
                    needs_fix = (
                        current_font.name != font_name or
                        current_font.size != font_size or
                        current_font.bold != is_bold
                    )

                    if needs_fix:
                        cell.font = Font(
                            name=font_name,
                            size=font_size,
                            bold=is_bold
                        )
                        print(f"  🔧 Fonte corrigida em {cell_ref}: {font_name} {font_size}pt {'Bold' if is_bold else 'Normal'}")

            print("✅ Fontes do template preservadas")

        except Exception as e:
            print(f"⚠️  Erro ao preservar fontes: {e}")
    
    def validate_template(self) -> bool:
        """Valida se o template tem a estrutura esperada"""
        
        try:
            wb = load_workbook(self.template_path)
            ws = wb.active
            
            # Verificar elementos chave
            checks = [
                (ws['A7'].value == 'Invoice', "Título 'Invoice' em A7"),
                ('Client:' in str(ws['A12'].value or ''), "Cliente em A12"),
                ('Services' in str(ws['A16'].value or ''), "Cabeçalho 'Services' em A16"),
                ('Unit Price' in str(ws['B16'].value or ''), "Cabeçalho 'Unit Price' em B16"),
                ('=SUM(D18:D29)' in str(ws['D30'].value or ''), "Fórmula de soma em D30"),
            ]
            
            all_valid = True
            for check, description in checks:
                if not check:
                    print(f"❌ Validação falhou: {description}")
                    all_valid = False
                else:
                    print(f"✅ {description}")
            
            wb.close()
            return all_valid
            
        except Exception as e:
            print(f"❌ Erro ao validar template: {e}")
            return False


def create_template_based_invoice(employee_name: str,
                                line_items: List[Dict],
                                output_path: Path,
                                invoice_date: str = None,
                                invoice_no: str = None,
                                call_off: str = None,
                                template_path: Path = None) -> Path:
    """
    Função de conveniência para criar invoice baseada no template
    
    Args:
        employee_name: Nome do funcionário
        line_items: Lista de itens de serviço com keys: description, unit_price, quantity, final
        output_path: Caminho para salvar o arquivo
        invoice_date: Data da invoice (DD/MM/YYYY)
        invoice_no: Número da invoice
        call_off: Call-off number
        template_path: Caminho customizado para o template
        
    Returns:
        Path do arquivo criado
    """
    
    generator = TemplateBasedInvoiceGenerator(template_path)
    
    return generator.create_invoice(
        employee_name=employee_name,
        line_items=line_items,
        output_path=output_path,
        invoice_date=invoice_date,
        invoice_no=invoice_no,
        call_off=call_off
    )


if __name__ == "__main__":
    # Teste básico
    generator = TemplateBasedInvoiceGenerator()
    
    print("🧪 Validando template...")
    if generator.validate_template():
        print("✅ Template válido!")
    else:
        print("❌ Template inválido!")
    
    # Teste de criação
    test_items = [
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
        },
        {
            'description': 'Brazilian Payroll Additional',
            'unit_price': None,
            'quantity': None,
            'final': 0.0
        },
        {
            'description': 'Expenses',
            'unit_price': None,
            'quantity': None,
            'final': 0.0
        }
    ]
    
    output_path = Path("out/test_template_based_invoice.xlsx")
    
    try:
        result = generator.create_invoice(
            employee_name="Gabriel Leone",
            line_items=test_items,
            output_path=output_path,
            invoice_date="15/09/2025",
            invoice_no="001/2025",
            call_off="TEST-001"
        )
        print(f"🎉 Teste concluído: {result}")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
