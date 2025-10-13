"""
Unified Invoice Generator
Routes to appropriate generator based on client profile
"""
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from app.models.client_profile import ClientProfile, InvoiceFormat
    from app.invoice.template_filler import generate_from_abz_template
    from app.invoice.jifmar_invoice_generator import generate_jifmar_invoice
    from app.utils.filename_standardizer import generate_filename_from_profile
except ModuleNotFoundError:
    from models.client_profile import ClientProfile, InvoiceFormat
    from invoice.template_filler import generate_from_abz_template
    from invoice.jifmar_invoice_generator import generate_jifmar_invoice
    from utils.filename_standardizer import generate_filename_from_profile


def generate_invoice(
    employee_data: Dict[str, Any],
    client_profile: ClientProfile,
    invoice_no: str,
    invoice_date: str,
    output_dir: Path,
    abz_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Unified invoice generator that routes to correct format based on client profile
    
    Args:
        employee_data: Dictionary with employee information
        client_profile: ClientProfile object with configuration
        invoice_no: Invoice number
        invoice_date: Invoice date string
        output_dir: Directory to save invoices
        abz_path: Path to source ABZ file (for template-based generation)
    
    Returns:
        Dictionary with generation results:
        {
            "success": bool,
            "xlsx_path": Path,
            "pdf_path": Path (optional),
            "filename": str,
            "employee_name": str,
            "total_amount": float,
            "client_id": str,
            "client_name": str,
            "invoice_format": str
        }
    """
    employee_name = employee_data.get('name', 'Unknown')
    
    # Generate filename using profile
    vessel_name = employee_data.get('vessel') if client_profile.subcategory else None
    
    filename = generate_filename_from_profile(
        employee_name=employee_name,
        invoice_no=invoice_no,
        invoice_date=invoice_date,
        client_profile=client_profile,
        abz_path=abz_path,
        vessel_name=vessel_name,
        extension="xlsx"
    )
    
    output_path = output_dir / filename
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Route to appropriate generator
    if client_profile.invoice_format == InvoiceFormat.ABZ_TEMPLATE:
        # Use existing template-based generation (ABZ Group)
        if not abz_path or not abz_path.exists():
            raise ValueError(f"ABZ template file required for {client_profile.client_name}")
        
        result_path = generate_from_abz_template(
            abz_path=abz_path,
            employee_name=employee_name,
            invoice_no=invoice_no,
            invoice_date=invoice_date,
            output_path=output_path,
            call_off=employee_data.get('call_off', ''),
            overrides={}
        )
        
        total_amount = employee_data.get('monthly_total', 0)
        
    elif client_profile.invoice_format == InvoiceFormat.GENERATED:
        # Generate from scratch (ABZ International / Jifmar)
        company_name = "ABZ Group" if client_profile.company_id == 1 else "ABZ International Ltd"
        
        result_path = generate_jifmar_invoice(
            employee_data=employee_data,
            invoice_no=invoice_no,
            invoice_date=invoice_date,
            output_path=output_path,
            company_name=company_name
        )
        
        total_amount = employee_data.get('monthly_charge', 0)
    
    else:
        raise ValueError(f"Unsupported invoice format: {client_profile.invoice_format}")
    
    # Extract financial breakdown for database
    financial_breakdown = {
        "base_amount": employee_data.get('day_rate', 0) * employee_data.get('days', 0) if 'day_rate' in employee_data else employee_data.get('charge_rate', 0) * employee_data.get('days', 0),
        "overtime_amount": employee_data.get('overtime_cost', 0),
        "expenses_amount": employee_data.get('expenses', 0),
        "insurance_amount": employee_data.get('insurance_cost', 0),
        "other_amount": employee_data.get('additional_total', 0) + employee_data.get('social_security', 0)
    }
    
    return {
        "success": True,
        "xlsx_path": result_path,
        "pdf_path": None,  # PDF generation happens separately
        "filename": filename,
        "employee_name": employee_name,
        "employee_position": employee_data.get('position', ''),
        "total_amount": total_amount,
        "client_id": client_profile.client_id,
        "client_name": client_profile.client_name,
        "client_category": client_profile.category,
        "client_subcategory": client_profile.subcategory,
        "invoice_format": client_profile.invoice_format.value,
        "financial_breakdown": financial_breakdown,
        "vessel": employee_data.get('vessel'),
        "period": employee_data.get('period')
    }


def generate_invoices_batch(
    employees_data: list,
    client_profile: ClientProfile,
    invoice_no_start: int,
    invoice_date: str,
    output_dir: Path,
    abz_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Generate invoices for multiple employees
    
    Args:
        employees_data: List of employee dictionaries
        client_profile: ClientProfile object
        invoice_no_start: Starting invoice number
        invoice_date: Invoice date string
        output_dir: Directory to save invoices
        abz_path: Path to source ABZ file
    
    Returns:
        Dictionary with batch results:
        {
            "total": int,
            "successful": int,
            "failed": int,
            "invoices": List[Dict],
            "errors": List[Dict]
        }
    """
    results = {
        "total": len(employees_data),
        "successful": 0,
        "failed": 0,
        "invoices": [],
        "errors": []
    }
    
    current_invoice_no = invoice_no_start
    
    for employee_data in employees_data:
        try:
            result = generate_invoice(
                employee_data=employee_data,
                client_profile=client_profile,
                invoice_no=str(current_invoice_no),
                invoice_date=invoice_date,
                output_dir=output_dir,
                abz_path=abz_path
            )
            
            results["invoices"].append(result)
            results["successful"] += 1
            current_invoice_no += 1
            
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "employee_name": employee_data.get('name', 'Unknown'),
                "error": str(e)
            })
            print(f"❌ Error generating invoice for {employee_data.get('name')}: {e}")
    
    return results


if __name__ == "__main__":
    # Test the unified generator
    print("🧪 Testing Unified Invoice Generator...")
    
    from app.models.client_profile import get_client_profile_manager
    
    manager = get_client_profile_manager()
    
    # Test ABZ International (Jifmar)
    print("\n1. Testing ABZ International (Jifmar)...")
    profile = manager.get_profile("JIFMAR_VOE_VANGUARD")
    
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
        "monthly_charge": 4525.0
    }
    
    output_dir = Path("out/test_invoices")
    
    result = generate_invoice(
        employee_data=test_employee,
        client_profile=profile,
        invoice_no="142",
        invoice_date="13/10/2025",
        output_dir=output_dir
    )
    
    print(f"✅ Invoice generated:")
    print(f"   File: {result['filename']}")
    print(f"   Employee: {result['employee_name']}")
    print(f"   Client: {result['client_name']}")
    print(f"   Total: £{result['total_amount']:,.2f}")
    print(f"   Format: {result['invoice_format']}")
    
    print("\n✅ Unified Invoice Generator working!")

