#!/usr/bin/env python3
"""
Filename standardization utilities for invoice generation
"""
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


def extract_client_from_abz_filename(abz_path: Path) -> str:
    """
    Extract client name from ABZ filename
    Examples:
    - "ABZ - FMS - Maximus Project.xlsx" -> "FMS"
    - "ABZ - OMEGA - Maximus Project.xlsx" -> "OMEGA"
    """
    filename = abz_path.name
    
    # Pattern: ABZ - CLIENT - ...
    match = re.search(r'ABZ\s*-\s*([^-]+)\s*-', filename, re.IGNORECASE)
    if match:
        client = match.group(1).strip().upper()
        return client
    
    # Fallback: look for common client names
    filename_upper = filename.upper()
    if 'FMS' in filename_upper:
        return 'FMS'
    elif 'OMEGA' in filename_upper:
        return 'OMEGA'
    elif 'MAXIMUS' in filename_upper:
        return 'MAXIMUS'
    
    return 'CLIENT'


def extract_month_year_from_date(date_str: Optional[str]) -> tuple[str, str]:
    """
    Extract month and year from date string
    Examples:
    - "12/09/2025" -> ("09", "2025")
    - "2025-09-12" -> ("09", "2025")
    """
    if not date_str:
        now = datetime.now()
        return f"{now.month:02d}", str(now.year)
    
    # Try different date formats
    date_patterns = [
        r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY or MM/DD/YYYY
        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY or MM-DD-YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                # Assume DD/MM/YYYY format for the first pattern
                if pattern == date_patterns[0]:
                    day, month, year = groups
                    return f"{int(month):02d}", year
                # YYYY-MM-DD format
                elif pattern == date_patterns[1]:
                    year, month, day = groups
                    return f"{int(month):02d}", year
                # DD-MM-YYYY format
                else:
                    day, month, year = groups
                    return f"{int(month):02d}", year
    
    # Fallback to current date
    now = datetime.now()
    return f"{now.month:02d}", str(now.year)


def get_first_name(full_name: str) -> str:
    """
    Extract first name from full name
    Examples:
    - "Filipi Brandão Lagedo" -> "Filipi"
    - "Gil Anderson Reiser" -> "Gil"
    """
    if not full_name:
        return "Employee"
    
    words = full_name.strip().split()
    return words[0] if words else "Employee"


def clean_invoice_number(invoice_no: Optional[str]) -> str:
    """
    Clean and format invoice number
    Examples:
    - "121" -> "121"
    - "xx/121/2025" -> "121"
    - None -> "001"
    """
    if not invoice_no:
        return "001"
    
    # Remove common prefixes and suffixes
    cleaned = str(invoice_no).strip()
    
    # Remove "xx/" prefix if present
    cleaned = re.sub(r'^xx/', '', cleaned, flags=re.IGNORECASE)
    
    # Extract numeric part if it's in format like "121/2025"
    match = re.search(r'(\d+)', cleaned)
    if match:
        return match.group(1)
    
    return cleaned or "001"


def generate_standardized_filename(
    employee_name: str,
    invoice_no: Optional[str] = None,
    invoice_date: Optional[str] = None,
    abz_path: Optional[Path] = None,
    extension: str = "xlsx"
) -> str:
    """
    Generate standardized filename following the pattern:
    "ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}.{extension}"
    
    Example: "ABZ Group 141-2025 FMS 04 2025 Gil.xlsx"
    """
    # Extract components
    first_name = get_first_name(employee_name)
    clean_invoice = clean_invoice_number(invoice_no)
    month, year = extract_month_year_from_date(invoice_date)
    client = extract_client_from_abz_filename(abz_path) if abz_path else "CLIENT"
    
    # Build filename
    filename = f"ABZ Group {clean_invoice}-{year} {client} {month} {year} {first_name}.{extension}"
    
    # Sanitize filename (remove invalid characters)
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    return filename


def generate_legacy_filename(employee_name: str, extension: str = "xlsx") -> str:
    """
    Generate legacy filename format for backward compatibility
    Example: "Filipi_Brandão_Lagedo_Invoice.xlsx"
    """
    sanitized_name = employee_name.replace(' ', '_')
    return f"{sanitized_name}_Invoice.{extension}"


# Test function
if __name__ == "__main__":
    # Test cases
    test_cases = [
        {
            "employee_name": "Filipi Brandão Lagedo",
            "invoice_no": "141",
            "invoice_date": "12/09/2025",
            "abz_path": Path("ABZ - FMS - Maximus Project.xlsx"),
            "expected": "ABZ Group 141-2025 FMS 09 2025 Filipi.xlsx"
        },
        {
            "employee_name": "Gil Anderson Reiser",
            "invoice_no": "142",
            "invoice_date": "15/04/2025",
            "abz_path": Path("ABZ - OMEGA - Project.xlsx"),
            "expected": "ABZ Group 142-2025 OMEGA 04 2025 Gil.xlsx"
        }
    ]
    
    print("🧪 Testing filename standardization...")
    for i, case in enumerate(test_cases, 1):
        result = generate_standardized_filename(
            case["employee_name"],
            case["invoice_no"],
            case["invoice_date"],
            case["abz_path"]
        )
        status = "✅" if result == case["expected"] else "❌"
        print(f"  {i}. {status} {result}")
        if result != case["expected"]:
            print(f"     Expected: {case['expected']}")
