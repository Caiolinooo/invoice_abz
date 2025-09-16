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
        
        # Configurar largura das colunas EXATAMENTE como no template original
        ws.column_dimensions['A'].width = 69.7109375    # Services
        ws.column_dimensions['B'].width = 16.140625     # Unit Price
        ws.column_dimensions['C'].width = 13.28515625   # Quantity
        ws.column_dimensions['D'].width = 19.85546875   # Final Price
        ws.column_dimensions['E'].width = 13.0          # Extra

        # Criar layout exato do template
        self._create_exact_template_layout(ws, employee_name, line_items, invoice_date, invoice_no, call_off)
        
        # Salvar arquivo
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(output_path)
        wb.close()
        
        return output_path

    def _create_exact_template_layout(self, ws, employee_name: str, line_items: List[Dict],
                                    invoice_date: str, invoice_no: str, call_off: str):
        """Cria layout EXATAMENTE idêntico ao template original com dimensões precisas"""

        # Configurar alturas das linhas EXATAMENTE como no template
        ws.row_dimensions[7].height = 36.0      # Título Invoice
        ws.row_dimensions[8].height = 23.25     # Cliente/Data
        ws.row_dimensions[9].height = 23.25     # Endereço/Número
        ws.row_dimensions[10].height = 23.25    # Cidade
        ws.row_dimensions[12].height = 15.75    # Cabeçalho tabela
        ws.row_dimensions[13].height = 15.75    # Linha tabela
        ws.row_dimensions[16].height = 15.75    # Services
        ws.row_dimensions[17].height = 16.5     # (GBP)
        ws.row_dimensions[18].height = 15.0     # Primeira linha serviço

        # 1. Logo ABZ GROUP (como imagem no template original - simular com texto azul)
        # Posição aproximada onde está a imagem no template
        ws['A1'].value = "abz group"
        ws['A1'].font = Font(name="Calibri", size=20, bold=True, color="4472C4")
        ws['A1'].alignment = self.ALIGN_LEFT

        # 2. Título Invoice (linha 7 - posição exata do template)
        ws['A7'].value = "Invoice"
        ws['A7'].font = Font(name="Calibri", size=18, bold=True, underline="single")
        ws['A7'].alignment = Alignment(horizontal='center', vertical='center')

        # 3. Informações do cliente (posições exatas do template)
        # Linha 12: Cliente e Data da Invoice
        ws['A12'].value = "Client: Omega Subsea Ltd"
        ws['A12'].font = Font(name="Calibri", size=12, bold=True)
        ws['A12'].alignment = Alignment(vertical='center')

        ws['C12'].value = f"Invoice date: {invoice_date or '15/09/2025'}"
        ws['C12'].font = Font(name="Calibri", size=11)

        # Linha 13: Endereço e Número da Invoice
        ws['A13'].value = "Client Address: 30 Abercrombie Court Prospect Road,"
        ws['A13'].font = Font(name="Calibri", size=11)

        ws['C13'].value = f"Invoice no: {invoice_no or '0000200/2025'}"
        ws['C13'].font = Font(name="Calibri", size=11)

        # Linha 14: Cidade
        ws['A14'].value = "Westhill, AB32 6FE. UK"
        ws['A14'].font = Font(name="Calibri", size=11)

        # 4. Tabela de serviços (posições exatas do template)
        self._create_exact_services_table(ws, employee_name, line_items, call_off)

        # 5. Seção Notes to invoice above (linha 40 como no template)
        ws['A40'].value = "Notes to invoice above"
        ws['A40'].font = Font(name="Calibri", size=11, bold=True)

        # Linha vazia para notas (linha 41)
        ws.merge_cells('A41:D41')
        ws['A41'].border = self.BORDER_ALL

        # 6. Corporate Account details (linha 43)
        self._create_exact_corporate_account_details(ws)

    def _create_exact_services_table(self, ws, employee_name: str, line_items: List[Dict], call_off: str):
        """Cria tabela de serviços nas posições EXATAS do template original"""

        # Cabeçalho da tabela (linha 16 como no template)
        ws['A16'].value = "Services"
        ws['A16'].font = Font(name="Calibri", size=11, bold=True)
        ws['A16'].border = self.BORDER_ALL
        ws['A16'].alignment = self.ALIGN_CENTER

        ws['B16'].value = "Unit Price"
        ws['B16'].font = Font(name="Calibri", size=11, bold=True)
        ws['B16'].border = self.BORDER_ALL
        ws['B16'].alignment = self.ALIGN_CENTER

        ws['C16'].value = "Quantity"
        ws['C16'].font = Font(name="Calibri", size=11, bold=True)
        ws['C16'].border = self.BORDER_ALL
        ws['C16'].alignment = self.ALIGN_CENTER

        ws['D16'].value = "Final Price"
        ws['D16'].font = Font(name="Calibri", size=11, bold=True)
        ws['D16'].border = self.BORDER_ALL
        ws['D16'].alignment = self.ALIGN_CENTER

        # Linha 17: (GBP) como no template
        ws['D17'].value = "(GBP)"
        ws['D17'].font = Font(name="Calibri", size=11)
        ws['D17'].alignment = self.ALIGN_CENTER

        # Linhas de serviços (começando na linha 18 como no template)
        current_row = 18

        # Adicionar serviços do funcionário
        for item in line_items:
            description = item.get('description', '')
            # Adicionar call-off na descrição se fornecido (como no template)
            if call_off:
                description = f"{description} - call off - {call_off}"

            # Usar merged cells como no template original
            ws.merge_cells(f'A{current_row}:A{current_row+2}')
            ws[f'A{current_row}'].value = description
            ws[f'A{current_row}'].font = Font(name="Calibri", size=11)
            ws[f'A{current_row}'].border = self.BORDER_ALL
            ws[f'A{current_row}'].alignment = Alignment(vertical='center')

            # Unit Price, Quantity, Final Price (merged cells como no template)
            ws.merge_cells(f'B{current_row}:B{current_row+2}')
            ws[f'B{current_row}'].border = self.BORDER_ALL

            ws.merge_cells(f'C{current_row}:C{current_row+2}')
            ws[f'C{current_row}'].border = self.BORDER_ALL

            ws.merge_cells(f'D{current_row}:D{current_row+2}')
            ws[f'D{current_row}'].border = self.BORDER_ALL

            current_row += 3  # Pular 3 linhas como no template

        # Brazilian Payroll Additional (linha 24 como no template)
        ws.merge_cells('A24:A26')
        ws['A24'].value = "Brazilian Payroll Additional"
        ws['A24'].font = Font(name="Calibri", size=11)
        ws['A24'].border = self.BORDER_ALL
        ws['A24'].alignment = Alignment(vertical='center')

        ws.merge_cells('B24:B26')
        ws['B24'].value = "N/A"
        ws['B24'].font = Font(name="Calibri", size=11)
        ws['B24'].border = self.BORDER_ALL
        ws['B24'].alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells('C24:C26')
        ws['C24'].value = "N/A"
        ws['C24'].font = Font(name="Calibri", size=11)
        ws['C24'].border = self.BORDER_ALL
        ws['C24'].alignment = Alignment(horizontal='center', vertical='center')

        # Calcular total dos serviços
        total_amount = sum(item.get('final', 0) for item in line_items)

        ws.merge_cells('D24:D26')
        ws['D24'].value = f"£{total_amount:.2f}"
        ws['D24'].font = Font(name="Calibri", size=11)
        ws['D24'].border = self.BORDER_ALL
        ws['D24'].alignment = Alignment(horizontal='right', vertical='center')

        # Expenses (linha 27 como no template)
        ws.merge_cells('A27:A29')
        ws['A27'].value = "Expenses"
        ws['A27'].font = Font(name="Calibri", size=11)
        ws['A27'].border = self.BORDER_ALL
        ws['A27'].alignment = Alignment(vertical='center')

        ws.merge_cells('B27:B29')
        ws['B27'].value = "N/A"
        ws['B27'].font = Font(name="Calibri", size=11)
        ws['B27'].border = self.BORDER_ALL
        ws['B27'].alignment = Alignment(horizontal='center', vertical='center')

        ws.merge_cells('C27:C29')
        ws['C27'].value = "N/A"
        ws['C27'].font = Font(name="Calibri", size=11)
        ws['C27'].border = self.BORDER_ALL
        ws['C27'].alignment = Alignment(horizontal='center', vertical='center')

        # Expenses vazio como no template
        ws.merge_cells('D27:D29')
        ws['D27'].border = self.BORDER_ALL

        # Total amount payable (linha 30 como no template)
        ws.merge_cells('A30:C32')
        ws['A30'].value = "Total amount payable"
        ws['A30'].font = Font(name="Calibri", size=11, bold=True)
        ws['A30'].border = self.BORDER_ALL
        ws['A30'].alignment = Alignment(vertical='center')

        ws.merge_cells('D30:D32')
        ws['D30'].value = f"£{total_amount:.2f}"
        ws['D30'].font = Font(name="Calibri", size=11, bold=True)
        ws['D30'].border = self.BORDER_ALL
        ws['D30'].alignment = Alignment(horizontal='right', vertical='center')

    def _create_exact_corporate_account_details(self, ws):
        """Cria seção Corporate Account details nas posições exatas do template"""

        # Cabeçalho (linha 43 como no template)
        ws.merge_cells('A43:D43')
        ws['A43'].value = "Corporate Account details"
        ws['A43'].font = Font(name="Calibri", size=11, bold=True)
        ws['A43'].border = self.BORDER_ALL
        ws['A43'].alignment = Alignment(horizontal='center', vertical='center')

        # Dados da conta (linhas 44-50 como no template)
        account_data = [
            ("Account Name", "ABZ Group SAS"),
            ("Account Number", "92997116"),
            ("Sort Code", "23 01 62"),
            ("Bank Name", "35 Money Club"),
            ("Bank Address", "35 Frognal St, London, E1 6GL"),
            ("Currency", "GBP"),
            ("Mandatory payment reference", "GB880802269")
        ]

        for i, (label, value) in enumerate(account_data, 44):
            # Label na coluna A
            ws.cell(row=i, column=1).value = label
            ws.cell(row=i, column=1).font = Font(name="Calibri", size=11)
            ws.cell(row=i, column=1).border = self.BORDER_ALL
            ws.cell(row=i, column=1).alignment = Alignment(vertical='center')

            # Value nas colunas B-D (merged como no template)
            ws.merge_cells(f'B{i}:D{i}')
            ws.cell(row=i, column=2).value = value
            ws.cell(row=i, column=2).font = Font(name="Calibri", size=11)
            ws.cell(row=i, column=2).border = self.BORDER_ALL
            ws.cell(row=i, column=2).alignment = Alignment(vertical='center')

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
