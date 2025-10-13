"""
Invoice Generator for ABZ International (Jifmar Format)
Generates invoices from scratch without templates
"""
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill


def generate_jifmar_invoice(
    employee_data: Dict[str, Any],
    invoice_no: str,
    invoice_date: str,
    output_path: Path,
    company_name: str = "ABZ International Ltd"
) -> Path:
    """
    Generate invoice for ABZ International (Jifmar format)
    Creates invoice from scratch without templates
    
    Args:
        employee_data: Dictionary with employee information
            Required fields:
            - name: str
            - position: str
            - vessel: str
            - client: str
            - period: str
            - day_rate: float
            - days: int
            - overtime_hours: int (optional)
            - overtime_cost: float (optional)
            - insurance_cost: float (optional)
            - social_security: float (optional)
            - expenses: float (optional)
            - additional_total: float (optional)
            - monthly_salary: float (optional)
            - monthly_charge: float
        invoice_no: Invoice number
        invoice_date: Invoice date string
        output_path: Path to save the invoice
        company_name: Company name for header
    
    Returns:
        Path to generated invoice file
    """
    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Invoice"
    
    # Set column widths
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 15
    
    # Define styles
    header_font = Font(name='Arial', size=14, bold=True)
    title_font = Font(name='Arial', size=12, bold=True)
    normal_font = Font(name='Arial', size=10)
    bold_font = Font(name='Arial', size=10, bold=True)
    
    center_align = Alignment(horizontal='center', vertical='center')
    left_align = Alignment(horizontal='left', vertical='center')
    right_align = Alignment(horizontal='right', vertical='center')
    
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    header_fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')
    
    # Row counter
    row = 1
    
    # Company Header
    ws[f'A{row}'] = company_name
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].alignment = center_align
    ws.merge_cells(f'A{row}:C{row}')
    row += 1
    
    ws[f'A{row}'] = "INVOICE"
    ws[f'A{row}'].font = title_font
    ws[f'A{row}'].alignment = center_align
    ws.merge_cells(f'A{row}:C{row}')
    row += 2
    
    # Invoice Details
    ws[f'A{row}'] = "Invoice No:"
    ws[f'A{row}'].font = bold_font
    ws[f'B{row}'] = invoice_no
    ws[f'B{row}'].font = normal_font
    row += 1
    
    ws[f'A{row}'] = "Invoice Date:"
    ws[f'A{row}'].font = bold_font
    ws[f'B{row}'] = invoice_date
    ws[f'B{row}'].font = normal_font
    row += 1
    
    ws[f'A{row}'] = "Period:"
    ws[f'A{row}'].font = bold_font
    ws[f'B{row}'] = employee_data.get('period', 'N/A')
    ws[f'B{row}'].font = normal_font
    row += 2
    
    # Client Information
    ws[f'A{row}'] = "CLIENT INFORMATION"
    ws[f'A{row}'].font = title_font
    ws[f'A{row}'].fill = header_fill
    ws.merge_cells(f'A{row}:C{row}')
    row += 1
    
    ws[f'A{row}'] = "Client:"
    ws[f'A{row}'].font = bold_font
    ws[f'B{row}'] = employee_data.get('client', 'N/A')
    ws[f'B{row}'].font = normal_font
    row += 1
    
    ws[f'A{row}'] = "Vessel:"
    ws[f'A{row}'].font = bold_font
    ws[f'B{row}'] = employee_data.get('vessel', 'N/A')
    ws[f'B{row}'].font = normal_font
    row += 2
    
    # Employee Information
    ws[f'A{row}'] = "EMPLOYEE INFORMATION"
    ws[f'A{row}'].font = title_font
    ws[f'A{row}'].fill = header_fill
    ws.merge_cells(f'A{row}:C{row}')
    row += 1
    
    ws[f'A{row}'] = "Name:"
    ws[f'A{row}'].font = bold_font
    ws[f'B{row}'] = employee_data.get('name', 'N/A')
    ws[f'B{row}'].font = normal_font
    row += 1
    
    ws[f'A{row}'] = "Position:"
    ws[f'A{row}'].font = bold_font
    ws[f'B{row}'] = employee_data.get('position', 'N/A')
    ws[f'B{row}'].font = normal_font
    row += 2
    
    # Financial Details
    ws[f'A{row}'] = "FINANCIAL DETAILS"
    ws[f'A{row}'].font = title_font
    ws[f'A{row}'].fill = header_fill
    ws.merge_cells(f'A{row}:C{row}')
    row += 1
    
    # Table header
    ws[f'A{row}'] = "Description"
    ws[f'A{row}'].font = bold_font
    ws[f'A{row}'].border = thin_border
    ws[f'A{row}'].fill = header_fill
    
    ws[f'B{row}'] = "Details"
    ws[f'B{row}'].font = bold_font
    ws[f'B{row}'].border = thin_border
    ws[f'B{row}'].fill = header_fill
    
    ws[f'C{row}'] = "Amount (GBP)"
    ws[f'C{row}'].font = bold_font
    ws[f'C{row}'].border = thin_border
    ws[f'C{row}'].fill = header_fill
    ws[f'C{row}'].alignment = right_align
    row += 1
    
    # Day Rate
    day_rate = employee_data.get('day_rate', 0)
    days = employee_data.get('days', 0)
    day_rate_total = day_rate * days
    
    ws[f'A{row}'] = "Day Rate"
    ws[f'A{row}'].border = thin_border
    ws[f'B{row}'] = f"£{day_rate:.2f} x {days} days"
    ws[f'B{row}'].border = thin_border
    ws[f'C{row}'] = f"£{day_rate_total:,.2f}"
    ws[f'C{row}'].border = thin_border
    ws[f'C{row}'].alignment = right_align
    row += 1
    
    # Overtime (if applicable)
    overtime_hours = employee_data.get('overtime_hours', 0)
    overtime_cost = employee_data.get('overtime_cost', 0)
    if overtime_hours > 0 or overtime_cost > 0:
        ws[f'A{row}'] = "Overtime"
        ws[f'A{row}'].border = thin_border
        ws[f'B{row}'] = f"{overtime_hours} hours"
        ws[f'B{row}'].border = thin_border
        ws[f'C{row}'] = f"£{overtime_cost:,.2f}"
        ws[f'C{row}'].border = thin_border
        ws[f'C{row}'].alignment = right_align
        row += 1
    
    # Insurance
    insurance_cost = employee_data.get('insurance_cost', 0)
    if insurance_cost > 0:
        ws[f'A{row}'] = "Insurance"
        ws[f'A{row}'].border = thin_border
        ws[f'B{row}'] = ""
        ws[f'B{row}'].border = thin_border
        ws[f'C{row}'] = f"£{insurance_cost:,.2f}"
        ws[f'C{row}'].border = thin_border
        ws[f'C{row}'].alignment = right_align
        row += 1
    
    # Social Security
    social_security = employee_data.get('social_security', 0)
    if social_security > 0:
        ws[f'A{row}'] = "Social Security"
        ws[f'A{row}'].border = thin_border
        ws[f'B{row}'] = ""
        ws[f'B{row}'].border = thin_border
        ws[f'C{row}'] = f"£{social_security:,.2f}"
        ws[f'C{row}'].border = thin_border
        ws[f'C{row}'].alignment = right_align
        row += 1
    
    # Expenses
    expenses = employee_data.get('expenses', 0)
    if expenses > 0:
        ws[f'A{row}'] = "Expenses"
        ws[f'A{row}'].border = thin_border
        ws[f'B{row}'] = ""
        ws[f'B{row}'].border = thin_border
        ws[f'C{row}'] = f"£{expenses:,.2f}"
        ws[f'C{row}'].border = thin_border
        ws[f'C{row}'].alignment = right_align
        row += 1
    
    # Additional
    additional_total = employee_data.get('additional_total', 0)
    if additional_total > 0:
        ws[f'A{row}'] = "Additional"
        ws[f'A{row}'].border = thin_border
        ws[f'B{row}'] = ""
        ws[f'B{row}'].border = thin_border
        ws[f'C{row}'] = f"£{additional_total:,.2f}"
        ws[f'C{row}'].border = thin_border
        ws[f'C{row}'].alignment = right_align
        row += 1
    
    # Total
    row += 1
    total_amount = employee_data.get('monthly_charge', 0)
    
    ws[f'A{row}'] = "TOTAL"
    ws[f'A{row}'].font = Font(name='Arial', size=12, bold=True)
    ws[f'A{row}'].border = thin_border
    ws[f'A{row}'].fill = header_fill
    ws.merge_cells(f'A{row}:B{row}')
    
    ws[f'C{row}'] = f"£{total_amount:,.2f}"
    ws[f'C{row}'].font = Font(name='Arial', size=12, bold=True)
    ws[f'C{row}'].border = thin_border
    ws[f'C{row}'].fill = header_fill
    ws[f'C{row}'].alignment = right_align
    
    # Footer
    row += 3
    ws[f'A{row}'] = "Thank you for your business!"
    ws[f'A{row}'].font = Font(name='Arial', size=10, italic=True)
    ws[f'A{row}'].alignment = center_align
    ws.merge_cells(f'A{row}:C{row}')
    
    # Save workbook
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    
    return output_path


if __name__ == "__main__":
    # Test the generator
    print("🧪 Testing Jifmar Invoice Generator...")
    
    test_employee = {
        "name": "Mihails Ivanovs",
        "position": "Deckhand",
        "vessel": "Voe Vanguard",
        "client": "Jifmar Group",
        "period": "15th - 30th September 2025",
        "day_rate": 230.0,
        "days": 16,
        "overtime_hours": 10,
        "overtime_cost": 345.0,
        "insurance_cost": 150.0,
        "social_security": 200.0,
        "expenses": 100.0,
        "additional_total": 50.0,
        "monthly_salary": 3680.0,
        "monthly_charge": 4525.0
    }
    
    output = Path("out/test_jifmar_invoice.xlsx")
    
    result = generate_jifmar_invoice(
        employee_data=test_employee,
        invoice_no="142",
        invoice_date="13/10/2025",
        output_path=output
    )
    
    print(f"✅ Invoice generated: {result}")
    print(f"   Employee: {test_employee['name']}")
    print(f"   Vessel: {test_employee['vessel']}")
    print(f"   Total: £{test_employee['monthly_charge']:,.2f}")

