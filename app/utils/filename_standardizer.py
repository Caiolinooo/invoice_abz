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


def extract_period_from_abz_filename(abz_path: Path) -> tuple[str, str]:
    """
    Extract period (month and year) from ABZ filename
    This is the BILLING PERIOD, not the invoice emission date.

    Examples:
    - "ABZ - OMEGA - Maximus Project - Monthly Charge Rates 08.2025.xlsx" -> ("08", "2025")
    - "ABZ - FMS - Project 09 2025.xlsx" -> ("09", "2025")
    - "ABZ_OMEGA_Charge_Rates_10.2025.xlsx" -> ("10", "2025")
    """
    filename = abz_path.name

    # Pattern 1: MM.YYYY (most common)
    match = re.search(r'(\d{2})\.(\d{4})', filename)
    if match:
        month, year = match.groups()
        return month, year

    # Pattern 2: MM YYYY (space separated)
    match = re.search(r'(\d{2})\s+(\d{4})', filename)
    if match:
        month, year = match.groups()
        return month, year

    # Pattern 3: MM-YYYY (dash separated)
    match = re.search(r'(\d{2})-(\d{4})', filename)
    if match:
        month, year = match.groups()
        return month, year

    # Pattern 4: YYYY-MM or YYYY.MM
    match = re.search(r'(\d{4})[-.](\d{2})', filename)
    if match:
        year, month = match.groups()
        return month, year

    # Fallback: use current date
    now = datetime.now()
    return f"{now.month:02d}", str(now.year)


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

    IMPORTANT: The month/year in the filename represents the BILLING PERIOD (from ABZ filename),
    NOT the invoice emission date. These are two different things:
    - Billing Period: extracted from ABZ filename (e.g., "08.2025" in "ABZ - OMEGA - Charge Rates 08.2025.xlsx")
    - Invoice Date: the date when the invoice is issued (used internally, not in filename)

    Example: "ABZ Group 141-2025 FMS 08 2025 Gil.xlsx"
             (141 = invoice number, 08 2025 = billing period from ABZ filename)
    """
    # Extract components
    first_name = get_first_name(employee_name)
    clean_invoice = clean_invoice_number(invoice_no)

    # CRITICAL: Use billing period from ABZ filename, NOT invoice emission date
    if abz_path:
        month, year = extract_period_from_abz_filename(abz_path)
        client = extract_client_from_abz_filename(abz_path)
    else:
        # Fallback to invoice date if ABZ path not available
        month, year = extract_month_year_from_date(invoice_date)
        client = "CLIENT"

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
            "invoice_date": "12/01/2025",  # Invoice emission date (January)
            "abz_path": Path("ABZ - FMS - Maximus Project - Monthly Charge Rates 09.2025.xlsx"),  # Billing period (September)
            "expected": "ABZ Group 141-2025 FMS 09 2025 Filipi.xlsx"  # Should use 09 from filename, not 01 from date
        },
        {
            "employee_name": "Gil Anderson Reiser",
            "invoice_no": "142",
            "invoice_date": "15/02/2025",  # Invoice emission date (February)
            "abz_path": Path("ABZ - OMEGA - Project 04 2025.xlsx"),  # Billing period (April)
            "expected": "ABZ Group 142-2025 OMEGA 04 2025 Gil.xlsx"  # Should use 04 from filename, not 02 from date
        },
        {
            "employee_name": "Caio Correia",
            "invoice_no": "143",
            "invoice_date": "10/03/2025",  # Invoice emission date (March)
            "abz_path": Path("ABZ - OMEGA - Maximus Project - Monthly Charge Rates 08.2025.xlsx"),  # Billing period (August)
            "expected": "ABZ Group 143-2025 OMEGA 08 2025 Caio.xlsx"  # Should use 08 from filename, not 03 from date
        }
    ]

    print("🧪 Testing filename standardization...")
    print("📌 IMPORTANT: Filename should use BILLING PERIOD from ABZ filename, NOT invoice emission date\n")

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

        # Show extracted period
        month, year = extract_period_from_abz_filename(case["abz_path"])
        print(f"     Billing Period: {month}/{year} (from ABZ filename)")
        inv_month, inv_year = extract_month_year_from_date(case["invoice_date"])
        print(f"     Invoice Date: {inv_month}/{inv_year} (emission date, NOT used in filename)\n")
