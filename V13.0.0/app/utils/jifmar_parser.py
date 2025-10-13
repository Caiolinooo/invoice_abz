"""
Parser for ABZ International (Jifmar Group) spreadsheet format

Structure:
- Each sheet represents a Vessel/Project
- Row 4: Client, Vessel, Month/Year info
- Row 7: Headers (Name, Position, Day Rate, Days, etc.)
- Row 8+: Employee data
"""
import openpyxl
from typing import List, Dict, Optional
from pathlib import Path
import re


def parse_jifmar_spreadsheet(file_path: str) -> List[Dict]:
    """
    Parse ABZ International (Jifmar) spreadsheet format
    
    Args:
        file_path: Path to the Jifmar Excel file
    
    Returns:
        List of employee dictionaries with structure:
        {
            'name': str,
            'position': str,
            'vessel': str,  # Sheet name (Voe Vanguard, Voe Viking, etc.)
            'client': str,  # Jifmar Group
            'period': str,  # e.g., "15th - 30th September 2025"
            'day_rate': float,
            'days': int,
            'overtime_hours': float,
            'overtime_cost': float,
            'insurance_cost': float,
            'social_security': float,
            'expenses': float,
            'additional_total': float,
            'monthly_salary': float,
            'monthly_charge': float
        }
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    all_employees = []
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Extract metadata from row 4
        client = _extract_value(ws, 4, 1, "Client:")
        vessel = _extract_value(ws, 4, 2, "Vessel:")
        period = _extract_value(ws, 4, 5, "Month / Year:")
        
        # If no vessel found, use sheet name
        if not vessel:
            vessel = sheet_name
        
        # Find header row (should be row 7, but search to be safe)
        header_row = _find_header_row(ws)
        if not header_row:
            print(f"⚠️  Warning: No header row found in sheet '{sheet_name}', skipping...")
            continue
        
        # Map column indices
        col_map = _map_columns(ws, header_row)
        if not col_map.get('name'):
            print(f"⚠️  Warning: 'Name' column not found in sheet '{sheet_name}', skipping...")
            continue
        
        # Parse employee data (starts after header row)
        data_row = header_row + 1
        while True:
            name = ws.cell(row=data_row, column=col_map.get('name', 1)).value
            
            # Stop if we hit an empty name cell
            if not name or str(name).strip() == "":
                break
            
            # Extract employee data
            employee = {
                'name': str(name).strip(),
                'position': _get_cell_value(ws, data_row, col_map.get('position')),
                'vessel': vessel,
                'client': client or "Jifmar Group",
                'period': period or "",
                'day_rate': _get_float_value(ws, data_row, col_map.get('day_rate')),
                'days': _get_int_value(ws, data_row, col_map.get('days')),
                'overtime_hours': _get_float_value(ws, data_row, col_map.get('overtime_hours')),
                'overtime_cost': _get_float_value(ws, data_row, col_map.get('overtime_cost')),
                'insurance_cost': _get_float_value(ws, data_row, col_map.get('insurance_cost')),
                'social_security': _get_float_value(ws, data_row, col_map.get('social_security')),
                'expenses': _get_float_value(ws, data_row, col_map.get('expenses')),
                'additional_total': _get_float_value(ws, data_row, col_map.get('additional_total')),
                'monthly_salary': _get_float_value(ws, data_row, col_map.get('monthly_salary')),
                'monthly_charge': _get_float_value(ws, data_row, col_map.get('monthly_charge'))
            }
            
            all_employees.append(employee)
            data_row += 1
            
            # Safety limit
            if data_row > header_row + 200:
                break
    
    wb.close()
    return all_employees


def _extract_value(ws, row: int, col: int, prefix: str) -> Optional[str]:
    """Extract value from cell, removing prefix if present"""
    cell_value = ws.cell(row=row, column=col).value
    if not cell_value:
        return None
    
    value_str = str(cell_value).strip()
    if prefix and value_str.startswith(prefix):
        return value_str[len(prefix):].strip()
    return value_str


def _find_header_row(ws) -> Optional[int]:
    """Find the row containing column headers"""
    for row_idx in range(1, 20):
        row_values = [ws.cell(row=row_idx, column=c).value for c in range(1, 15)]
        row_str = [str(v).lower() if v else "" for v in row_values]
        
        # Check if this row has both 'name' and 'position'
        if any('name' in s for s in row_str) and any('position' in s for s in row_str):
            return row_idx
    
    return None


def _map_columns(ws, header_row: int) -> Dict[str, int]:
    """Map column names to their indices"""
    col_map = {}
    
    # Column name mappings (lowercase for matching)
    mappings = {
        'name': ['name'],
        'position': ['position'],
        'day_rate': ['day rate', 'rate'],
        'days': ['days'],
        'overtime_hours': ['overtime hours', 'overtime hrs'],
        'overtime_cost': ['overtime cost'],
        'insurance_cost': ['insurance cost', 'insurance'],
        'social_security': ['social security'],
        'expenses': ['expenses'],
        'additional_total': ['additional total', 'additionals'],
        'monthly_salary': ['monthly salary', 'salary'],
        'monthly_charge': ['monthly charge', 'charge']
    }
    
    # Scan header row
    for col_idx in range(1, 20):
        cell_value = ws.cell(row=header_row, column=col_idx).value
        if not cell_value:
            continue
        
        cell_str = str(cell_value).strip().lower()
        
        # Match against mappings
        for key, patterns in mappings.items():
            if any(pattern in cell_str for pattern in patterns):
                col_map[key] = col_idx
                break
    
    return col_map


def _get_cell_value(ws, row: int, col: Optional[int]) -> str:
    """Get cell value as string"""
    if col is None:
        return ""
    value = ws.cell(row=row, column=col).value
    return str(value).strip() if value else ""


def _get_float_value(ws, row: int, col: Optional[int]) -> float:
    """Get cell value as float"""
    if col is None:
        return 0.0
    value = ws.cell(row=row, column=col).value
    try:
        return float(value) if value else 0.0
    except (ValueError, TypeError):
        return 0.0


def _get_int_value(ws, row: int, col: Optional[int]) -> int:
    """Get cell value as integer"""
    if col is None:
        return 0
    value = ws.cell(row=row, column=col).value
    try:
        return int(float(value)) if value else 0
    except (ValueError, TypeError):
        return 0


def extract_period_info(period_str: str) -> Dict[str, str]:
    """
    Extract month and year from period string
    
    Example: "15th - 30th September 2025" -> {"month": "09", "year": "2025"}
    """
    if not period_str:
        return {"month": "", "year": ""}
    
    # Try to extract month name
    months = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    
    period_lower = period_str.lower()
    month = ""
    for month_name, month_num in months.items():
        if month_name in period_lower:
            month = month_num
            break
    
    # Extract year (4 digits)
    year_match = re.search(r'\b(20\d{2})\b', period_str)
    year = year_match.group(1) if year_match else ""
    
    return {"month": month, "year": year}


if __name__ == "__main__":
    # Test the parser
    test_file = Path("dev/DADOS/ABZ - Jifmar - Monthly Rates 1509-3009 New Version.xlsx")
    if test_file.exists():
        print("🧪 Testing Jifmar Parser...")
        employees = parse_jifmar_spreadsheet(str(test_file))
        print(f"\n✅ Parsed {len(employees)} employees")
        
        if employees:
            print("\n📋 First employee:")
            for key, value in employees[0].items():
                print(f"  {key}: {value}")
            
            # Group by vessel
            vessels = {}
            for emp in employees:
                vessel = emp['vessel']
                vessels[vessel] = vessels.get(vessel, 0) + 1
            
            print(f"\n🚢 Employees by vessel:")
            for vessel, count in vessels.items():
                print(f"  {vessel}: {count} employees")
    else:
        print(f"❌ Test file not found: {test_file}")

