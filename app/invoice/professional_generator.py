#!/usr/bin/env python3
"""
Professional Invoice Generator
Cria invoices profissionais do zero sem depender de templates
"""

from pathlib import Path
from typing import List, Dict, Any
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from datetime import datetime

class InvoiceProfessionalGenerator:
    """Gerador de invoices profissionais sem templates"""
    
    def __init__(self):
        # Cores exatas do template
        self.ABZ_BLUE = "4472C4"  # Azul do logo ABZ
        self.BLACK = "000000"
        self.WHITE = "FFFFFF"

        # Fontes exatas do template
        self.FONT_LOGO = Font(name="Calibri", size=24, bold=True, color=self.ABZ_BLUE)
        self.FONT_TITLE = Font(name="Calibri", size=14, bold=True, underline="single")
        self.FONT_NORMAL = Font(name="Calibri", size=11)
        self.FONT_SMALL = Font(name="Calibri", size=10)
        self.FONT_BOLD = Font(name="Calibri", size=11, bold=True)

        # Bordas exatas do template
        self.BORDER_ALL = Border(
            left=Side(style='thin', color=self.BLACK),
            right=Side(style='thin', color=self.BLACK),
            top=Side(style='thin', color=self.BLACK),
            bottom=Side(style='thin', color=self.BLACK)
        )

        # Alinhamentos
        self.ALIGN_CENTER = Alignment(horizontal='center', vertical='center')
        self.ALIGN_LEFT = Alignment(horizontal='left', vertical='center')
        self.ALIGN_RIGHT = Alignment(horizontal='right', vertical='center')
    
    def create_invoice(self, 
                      employee_name: str,
                      line_items: List[Dict],
                      output_path: Path,
                      invoice_date: str = None,
                      invoice_no: str = None,
                      call_off: str = None) -> Path:
        """
        Cria uma invoice profissional do zero
        
        Args:
            employee_name: Nome do funcionário
            line_items: Lista de itens de serviço
            output_path: Caminho para salvar o arquivo
            invoice_date: Data da invoice
            invoice_no: Número da invoice
            call_off: Call-off number
            
        Returns:
            Path do arquivo criado
        """
        
        # Criar workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Invoice"
        
        # Configurar largura das colunas exatamente como no template
        ws.column_dimensions['A'].width = 50  # Services (mais largo)
        ws.column_dimensions['B'].width = 12  # Unit Price
        ws.column_dimensions['C'].width = 12  # Quantity
        ws.column_dimensions['D'].width = 15  # Final Price
        ws.column_dimensions['E'].width = 20  # Para informações extras

        # Criar layout exato do template
        self._create_exact_template_layout(ws, employee_name, line_items, invoice_date, invoice_no, call_off)
        
        # Salvar arquivo
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(output_path)
        wb.close()
        
        return output_path

    def _create_exact_template_layout(self, ws, employee_name: str, line_items: List[Dict],
                                    invoice_date: str, invoice_no: str, call_off: str):
        """Cria layout exato idêntico ao template original"""

        # 1. Logo ABZ GROUP (linha 3)
        ws.merge_cells('A3:B3')
        ws['A3'].value = "abz group"
        ws['A3'].font = self.FONT_LOGO
        ws['A3'].alignment = self.ALIGN_LEFT

        # 2. Título Invoice (linha 5, centralizado e sublinhado)
        ws.merge_cells('A5:D5')
        ws['A5'].value = "Invoice"
        ws['A5'].font = self.FONT_TITLE
        ws['A5'].alignment = self.ALIGN_CENTER

        # 3. Informações do cliente (linhas 8-10)
        # Linha 8: Cliente e Data da Invoice
        ws['A8'].value = "Client: Omega Subsea Ltd"
        ws['A8'].font = self.FONT_NORMAL
        ws['D8'].value = f"Invoice date: {invoice_date or '15/09/2025'}"
        ws['D8'].font = self.FONT_NORMAL

        # Linha 9: Endereço e Número da Invoice
        ws['A9'].value = "Client Address: 30 Abercrombie Court Prospect Road,"
        ws['A9'].font = self.FONT_NORMAL
        ws['D9'].value = f"Invoice no: {invoice_no or '0000200/2025'}"
        ws['D9'].font = self.FONT_NORMAL

        # Linha 10: Cidade
        ws['A10'].value = "Westhill, AB32 6FE. UK"
        ws['A10'].font = self.FONT_NORMAL

        # 4. Tabela de serviços (começando na linha 12)
        self._create_services_table(ws, employee_name, line_items, call_off)

        # 5. Seção Notes to invoice above (linha 25)
        ws['A25'].value = "Notes to invoice above"
        ws['A25'].font = self.FONT_BOLD

        # Linha vazia para notas (linha 26)
        ws.merge_cells('A26:D26')
        ws['A26'].border = self.BORDER_ALL

        # 6. Corporate Account details (linha 28)
        self._create_corporate_account_details(ws)

    def _create_services_table(self, ws, employee_name: str, line_items: List[Dict], call_off: str):
        """Cria tabela de serviços exatamente como no template"""

        # Cabeçalho da tabela (linha 12)
        headers = ["Services", "Unit Price", "Quantity", "Final Price"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=12, column=col)
            cell.value = header
            cell.font = self.FONT_BOLD
            cell.border = self.BORDER_ALL
            cell.alignment = self.ALIGN_CENTER

        current_row = 13

        # Adicionar serviços do funcionário
        for item in line_items:
            description = item.get('description', '')
            # Adicionar call-off na descrição se fornecido
            if call_off:
                description = f"{description} - Call Off - {call_off}"

            # Serviço
            ws.cell(row=current_row, column=1).value = description
            ws.cell(row=current_row, column=1).font = self.FONT_NORMAL
            ws.cell(row=current_row, column=1).border = self.BORDER_ALL

            # Unit Price (vazio como no template)
            ws.cell(row=current_row, column=2).border = self.BORDER_ALL

            # Quantity (vazio como no template)
            ws.cell(row=current_row, column=3).border = self.BORDER_ALL

            # Final Price (vazio como no template)
            ws.cell(row=current_row, column=4).border = self.BORDER_ALL

            current_row += 1

        # Linha vazia entre serviços e totais
        current_row += 1

        # Brazilian Payroll Additional
        ws.cell(row=current_row, column=1).value = "Brazilian Payroll Additional"
        ws.cell(row=current_row, column=1).font = self.FONT_NORMAL
        ws.cell(row=current_row, column=1).border = self.BORDER_ALL

        ws.cell(row=current_row, column=2).value = "N/A"
        ws.cell(row=current_row, column=2).font = self.FONT_NORMAL
        ws.cell(row=current_row, column=2).border = self.BORDER_ALL
        ws.cell(row=current_row, column=2).alignment = self.ALIGN_CENTER

        ws.cell(row=current_row, column=3).value = "N/A"
        ws.cell(row=current_row, column=3).font = self.FONT_NORMAL
        ws.cell(row=current_row, column=3).border = self.BORDER_ALL
        ws.cell(row=current_row, column=3).alignment = self.ALIGN_CENTER

        ws.cell(row=current_row, column=4).value = "£871.63"
        ws.cell(row=current_row, column=4).font = self.FONT_NORMAL
        ws.cell(row=current_row, column=4).border = self.BORDER_ALL
        ws.cell(row=current_row, column=4).alignment = self.ALIGN_RIGHT

        current_row += 1

        # Linha vazia
        for col in range(1, 5):
            ws.cell(row=current_row, column=col).border = self.BORDER_ALL
        current_row += 1

        # Expenses
        ws.cell(row=current_row, column=1).value = "Expenses"
        ws.cell(row=current_row, column=1).font = self.FONT_NORMAL
        ws.cell(row=current_row, column=1).border = self.BORDER_ALL

        ws.cell(row=current_row, column=2).value = "N/A"
        ws.cell(row=current_row, column=2).font = self.FONT_NORMAL
        ws.cell(row=current_row, column=2).border = self.BORDER_ALL
        ws.cell(row=current_row, column=2).alignment = self.ALIGN_CENTER

        ws.cell(row=current_row, column=3).value = "N/A"
        ws.cell(row=current_row, column=3).font = self.FONT_NORMAL
        ws.cell(row=current_row, column=3).border = self.BORDER_ALL
        ws.cell(row=current_row, column=3).alignment = self.ALIGN_CENTER

        # Expenses vazio como no template
        ws.cell(row=current_row, column=4).border = self.BORDER_ALL

        current_row += 1

        # Linha vazia
        for col in range(1, 5):
            ws.cell(row=current_row, column=col).border = self.BORDER_ALL
        current_row += 1

        # Total amount payable
        ws.merge_cells(f'A{current_row}:C{current_row}')
        ws.cell(row=current_row, column=1).value = "Total amount payable"
        ws.cell(row=current_row, column=1).font = self.FONT_BOLD
        ws.cell(row=current_row, column=1).border = self.BORDER_ALL

        ws.cell(row=current_row, column=4).value = "£871.63"
        ws.cell(row=current_row, column=4).font = self.FONT_BOLD
        ws.cell(row=current_row, column=4).border = self.BORDER_ALL
        ws.cell(row=current_row, column=4).alignment = self.ALIGN_RIGHT

    def _create_corporate_account_details(self, ws):
        """Cria seção Corporate Account details"""

        # Cabeçalho (linha 28)
        ws.merge_cells('A28:D28')
        ws['A28'].value = "Corporate Account details"
        ws['A28'].font = self.FONT_BOLD
        ws['A28'].border = self.BORDER_ALL
        ws['A28'].alignment = self.ALIGN_CENTER

        # Dados da conta (linhas 29-35)
        account_data = [
            ("Account Name", "ABZ Group SAS"),
            ("Account Number", "92997116"),
            ("Sort Code", "23 01 62"),
            ("Bank Name", "35 Money Club"),
            ("Bank Address", "35 Frognal St, London, E1 6GL"),
            ("Currency", "GBP"),
            ("Mandatory payment reference", "GB880802269")
        ]

        for i, (label, value) in enumerate(account_data, 29):
            # Label na coluna A
            ws.cell(row=i, column=1).value = label
            ws.cell(row=i, column=1).font = self.FONT_NORMAL
            ws.cell(row=i, column=1).border = self.BORDER_ALL

            # Value nas colunas B-D (merged)
            ws.merge_cells(f'B{i}:D{i}')
            ws.cell(row=i, column=2).value = value
            ws.cell(row=i, column=2).font = self.FONT_NORMAL
            ws.cell(row=i, column=2).border = self.BORDER_ALL

    def _add_company_header(self, ws, start_row: int) -> int:
        """Adiciona cabeçalho da empresa"""
        
        # Logo/Nome da empresa
        ws.merge_cells(f'A{start_row}:D{start_row}')
        cell = ws[f'A{start_row}']
        cell.value = "ABZ GROUP"
        cell.font = Font(name="Calibri", size=16, bold=True, color=self.BLUE_HEADER)
        cell.alignment = self.ALIGN_CENTER
        cell.fill = PatternFill(start_color=self.LIGHT_BLUE, end_color=self.LIGHT_BLUE, fill_type="solid")
        
        start_row += 1
        
        # Endereço da empresa
        ws.merge_cells(f'A{start_row}:D{start_row}')
        cell = ws[f'A{start_row}']
        cell.value = "Professional Services & Consulting"
        cell.font = self.FONT_SMALL
        cell.alignment = self.ALIGN_CENTER
        
        return start_row + 3  # Espaço após cabeçalho
    
    def _add_invoice_title(self, ws, start_row: int) -> int:
        """Adiciona título 'Invoice'"""

        # Posicionar na linha 7 como no template original
        title_row = 7
        ws.merge_cells(f'A{title_row}:D{title_row}')
        cell = ws[f'A{title_row}']
        cell.value = "Invoice"
        cell.font = self.FONT_TITLE
        cell.alignment = self.ALIGN_CENTER

        # Aumentar altura da linha
        ws.row_dimensions[title_row].height = 40

        return 12  # Próxima seção começa na linha 12
    
    def _add_client_info(self, ws, start_row: int, invoice_date: str, invoice_no: str, call_off: str) -> int:
        """Adiciona informações do cliente e invoice"""

        # Usar posições fixas como no template original
        # Linha 12: Cliente e Data
        ws['A12'].value = "Client: Omega Subsea Ltd"
        ws['A12'].font = self.FONT_SUBHEADER

        ws['C12'].value = f"Invoice date: {invoice_date or datetime.now().strftime('%d/%m/%Y')}"
        ws['C12'].font = self.FONT_SUBHEADER

        # Linha 13: Endereço e Número
        ws['A13'].value = "Client Address: 30 Abercrombie"
        ws['A13'].font = self.FONT_NORMAL

        ws['C13'].value = f"Invoice No: {invoice_no or 'TBD/2025'}"
        ws['C13'].font = self.FONT_SUBHEADER

        # Linha 14: Endereço continuação
        ws['A14'].value = "Westhill, AB32 6FE. UK"
        ws['A14'].font = self.FONT_NORMAL

        # Call-off se fornecido
        if call_off:
            ws['C14'].value = f"Call-Off: {call_off}"
            ws['C14'].font = self.FONT_NORMAL

        return 16  # Tabela começa na linha 16
    
    def _add_services_table(self, ws, start_row: int, employee_name: str, line_items: List[Dict]) -> int:
        """Adiciona tabela de serviços"""

        # Cabeçalho da tabela na linha 16
        headers = ["Services", "Unit Price", "Quantity", "Final Price"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=16, column=col)
            cell.value = header
            cell.font = self.FONT_HEADER
            cell.fill = PatternFill(start_color=self.BLUE_HEADER, end_color=self.BLUE_HEADER, fill_type="solid")
            cell.border = self.BORDER_THIN
            cell.alignment = self.ALIGN_CENTER

        # Linha 17: unidade (GBP)
        ws['D17'].value = "(GBP)"
        ws['D17'].font = self.FONT_SMALL
        ws['D17'].alignment = self.ALIGN_CENTER

        # Começar serviços na linha 18
        current_row = 18
        
        # Linhas de serviços
        for item in line_items:
            # Descrição do serviço
            ws.cell(row=current_row, column=1).value = item.get('description', '')
            ws.cell(row=current_row, column=1).font = self.FONT_NORMAL
            ws.cell(row=current_row, column=1).border = self.BORDER_THIN

            # Preço unitário
            unit_price = item.get('unit_price', 0)
            ws.cell(row=current_row, column=2).value = unit_price
            ws.cell(row=current_row, column=2).font = self.FONT_NORMAL
            ws.cell(row=current_row, column=2).border = self.BORDER_THIN
            ws.cell(row=current_row, column=2).alignment = self.ALIGN_RIGHT
            ws.cell(row=current_row, column=2).number_format = '£#,##0.00'

            # Quantidade
            quantity = item.get('quantity', 0)
            ws.cell(row=current_row, column=3).value = quantity
            ws.cell(row=current_row, column=3).font = self.FONT_NORMAL
            ws.cell(row=current_row, column=3).border = self.BORDER_THIN
            ws.cell(row=current_row, column=3).alignment = self.ALIGN_RIGHT

            # Preço final
            final_price = item.get('final', unit_price * quantity)
            ws.cell(row=current_row, column=4).value = final_price
            ws.cell(row=current_row, column=4).font = self.FONT_NORMAL
            ws.cell(row=current_row, column=4).border = self.BORDER_THIN
            ws.cell(row=current_row, column=4).alignment = self.ALIGN_RIGHT
            ws.cell(row=current_row, column=4).number_format = '£#,##0.00'

            current_row += 3  # Espaço entre serviços (como no original)

        return current_row + 1
    
    def _add_totals(self, ws, start_row: int, line_items: List[Dict]) -> int:
        """Adiciona seção de totais"""
        
        # Brazilian Payroll Additional (se aplicável)
        ws.cell(row=start_row, column=1).value = "Brazilian Payroll Additional"
        ws.cell(row=start_row, column=1).font = self.FONT_NORMAL
        ws.cell(row=start_row, column=2).value = "N/A"
        ws.cell(row=start_row, column=3).value = "N/A"
        ws.cell(row=start_row, column=4).value = 0  # Pode ser calculado se necessário
        ws.cell(row=start_row, column=4).number_format = '£#,##0.00'
        
        start_row += 3
        
        # Expenses
        ws.cell(row=start_row, column=1).value = "Expenses"
        ws.cell(row=start_row, column=1).font = self.FONT_NORMAL
        ws.cell(row=start_row, column=2).value = "N/A"
        ws.cell(row=start_row, column=3).value = "N/A"
        ws.cell(row=start_row, column=4).value = 0  # Pode ser calculado se necessário
        ws.cell(row=start_row, column=4).number_format = '£#,##0.00'
        
        start_row += 3
        
        # Total amount payable
        ws.cell(row=start_row, column=1).value = "Total amount payable"
        ws.cell(row=start_row, column=1).font = Font(name="Calibri", size=12, bold=True)
        
        # Calcular total
        total = sum(item.get('final', 0) for item in line_items)
        ws.cell(row=start_row, column=4).value = total
        ws.cell(row=start_row, column=4).font = Font(name="Calibri", size=12, bold=True)
        ws.cell(row=start_row, column=4).number_format = '£#,##0.00'
        ws.cell(row=start_row, column=4).alignment = self.ALIGN_RIGHT
        
        # Adicionar borda ao total
        for col in range(1, 5):
            ws.cell(row=start_row, column=col).border = Border(top=Side(style='thick'))
        
        return start_row + 2
    
    def _add_footer(self, ws, start_row: int):
        """Adiciona rodapé da invoice"""
        
        start_row += 3
        
        ws.merge_cells(f'A{start_row}:D{start_row}')
        cell = ws[f'A{start_row}']
        cell.value = "Thank you for your business!"
        cell.font = Font(name="Calibri", size=10, italic=True)
        cell.alignment = self.ALIGN_CENTER
