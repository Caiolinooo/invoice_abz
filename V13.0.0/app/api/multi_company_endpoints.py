"""
Multi-Company API Endpoints
New endpoints that support multiple companies and clients
"""
from pathlib import Path
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session

# Import existing utilities
try:
    from app.utils.abz_charge_rate_parser import read_charge_rate_table
    from app.utils.jifmar_parser import parse_jifmar_spreadsheet
    from app.models.client_profile import get_client_profile_manager, SpreadsheetFormat
    from app.database.database import get_db
    from app.database.models import Company, Client
except ModuleNotFoundError:
    from utils.abz_charge_rate_parser import read_charge_rate_table
    from utils.jifmar_parser import parse_jifmar_spreadsheet
    from models.client_profile import get_client_profile_manager, SpreadsheetFormat
    from database.database import get_db
    from database.models import Company, Client


def detect_client_and_parse(
    file_path: Path,
    filename: str,
    company_id: int
) -> Dict[str, Any]:
    """
    Detect client from filename and parse using appropriate parser
    
    Returns:
    {
        "client_id": str,
        "client_name": str,
        "client_profile": ClientProfile,
        "employees": List[Dict],
        "parser_used": str
    }
    """
    manager = get_client_profile_manager()
    
    # Detect client profile from filename
    profile = manager.detect_client_from_filename(filename)
    
    if not profile:
        raise HTTPException(
            status_code=400,
            detail=f"Could not detect client from filename: {filename}. "
                   f"Please ensure filename contains client identifier (e.g., FMS, OMEGA, Jifmar)"
        )
    
    # Verify company_id matches
    if profile.company_id != company_id:
        raise HTTPException(
            status_code=400,
            detail=f"Client '{profile.client_name}' belongs to company_id={profile.company_id}, "
                   f"but you selected company_id={company_id}"
        )
    
    # Parse based on spreadsheet format
    employees = []
    parser_used = ""
    
    if profile.spreadsheet_format == SpreadsheetFormat.ABZ_CHARGE_RATE:
        # Use existing ABZ parser
        parser_used = "abz_charge_rate"
        charge_rate_data = read_charge_rate_table(file_path)
        
        # Convert to standard format
        for emp_name, emp_data in charge_rate_data.items():
            employees.append({
                "name": emp_name,
                "position": emp_data.get("position", ""),
                "charge_rate": emp_data.get("charge_rate", 0),
                "days": emp_data.get("days", 0),
                "monthly_total": emp_data.get("monthly_total", 0),
                "client": profile.client_name,
                "client_id": profile.client_id
            })
    
    elif profile.spreadsheet_format == SpreadsheetFormat.JIFMAR_VESSEL:
        # Use Jifmar parser
        parser_used = "jifmar_vessel"
        jifmar_data = parse_jifmar_spreadsheet(str(file_path))
        
        # Filter by vessel if subcategory specified
        if profile.subcategory:
            jifmar_data = [
                emp for emp in jifmar_data
                if emp.get("vessel") == profile.subcategory
            ]
        
        # Add client info
        for emp in jifmar_data:
            emp["client"] = profile.client_name
            emp["client_id"] = profile.client_id
        
        employees = jifmar_data
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported spreadsheet format: {profile.spreadsheet_format}"
        )
    
    return {
        "client_id": profile.client_id,
        "client_name": profile.client_name,
        "client_profile": profile,
        "employees": employees,
        "parser_used": parser_used,
        "spreadsheet_format": profile.spreadsheet_format.value
    }


async def api_import_multi_company(
    abz: UploadFile = File(...),
    company_id: int = Form(1),
    db: Session = Depends(get_db)
):
    """
    Import file with multi-company support
    
    Automatically detects client from filename and uses appropriate parser
    
    Args:
        abz: Uploaded spreadsheet file
        company_id: Company ID (1=ABZ Group, 2=ABZ International)
        db: Database session
    
    Returns:
        {
            "session_id": str,
            "company_id": int,
            "company_name": str,
            "client_id": str,
            "client_name": str,
            "employees": List[str],
            "parser_used": str
        }
    """
    print(f"[DEBUG] Multi-company import started")
    print(f"[DEBUG] File: {abz.filename}")
    print(f"[DEBUG] Company ID: {company_id}")
    
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Company with ID {company_id} not found"
        )
    
    print(f"[DEBUG] Company: {company.name}")
    
    # Create session
    sid = uuid.uuid4().hex
    from pathlib import Path
    SESSIONS = Path("out/sessions")
    SESSIONS.mkdir(parents=True, exist_ok=True)
    sdir = SESSIONS / sid
    sdir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file
    file_path = sdir / abz.filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    data = abz.file.read()
    file_path.write_bytes(data)
    
    print(f"[DEBUG] File saved to: {file_path}")
    
    # Detect client and parse
    try:
        parse_result = detect_client_and_parse(
            file_path=file_path,
            filename=abz.filename,
            company_id=company_id
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Parse failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse file: {str(e)}"
        )
    
    print(f"[DEBUG] Client detected: {parse_result['client_name']}")
    print(f"[DEBUG] Parser used: {parse_result['parser_used']}")
    print(f"[DEBUG] Employees found: {len(parse_result['employees'])}")
    
    # Build preview data
    preview = {}
    for emp in parse_result['employees']:
        emp_name = emp.get("name", "Unknown")
        preview[emp_name] = emp
    
    # Save session metadata
    meta = {
        "abz": abz.filename,
        "company_id": company_id,
        "company_name": company.name,
        "client_id": parse_result["client_id"],
        "client_name": parse_result["client_name"],
        "parser_used": parse_result["parser_used"],
        "spreadsheet_format": parse_result["spreadsheet_format"],
        "preview": preview,
        "created_at": datetime.now().isoformat()
    }
    
    (sdir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    print(f"[DEBUG] Session created: {sid}")
    
    return {
        "session_id": sid,
        "company_id": company_id,
        "company_name": company.name,
        "client_id": parse_result["client_id"],
        "client_name": parse_result["client_name"],
        "employees": list(preview.keys()),
        "parser_used": parse_result["parser_used"],
        "total_employees": len(preview)
    }


async def api_get_companies(db: Session = Depends(get_db)):
    """
    Get list of all active companies
    
    Returns:
        List of companies with their clients
    """
    companies = db.query(Company).filter(Company.is_active == True).all()
    
    result = []
    for company in companies:
        # Get clients for this company
        clients = db.query(Client).filter(
            Client.company_id == company.id,
            Client.is_active == True
        ).all()
        
        result.append({
            "id": company.id,
            "name": company.name,
            "domain": company.domain,
            "clients": [
                {
                    "client_id": c.client_id,
                    "client_name": c.client_name,
                    "category": c.category,
                    "subcategory": c.subcategory
                }
                for c in clients
            ],
            "total_clients": len(clients)
        })
    
    return result


async def api_get_clients(
    company_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of clients, optionally filtered by company

    Args:
        company_id: Optional company ID to filter by

    Returns:
        List of clients
    """
    query = db.query(Client).filter(Client.is_active == True)

    if company_id:
        query = query.filter(Client.company_id == company_id)

    clients = query.all()

    return [
        {
            "client_id": c.client_id,
            "client_name": c.client_name,
            "company_id": c.company_id,
            "spreadsheet_format": c.spreadsheet_format,
            "invoice_format": c.invoice_format,
            "category": c.category,
            "subcategory": c.subcategory,
            "currency": c.currency
        }
        for c in clients
    ]


async def api_generate_invoices_multi_company(
    session_id: str,
    invoice_no: str,
    invoice_date: str,
    call_off: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Generate invoices with multi-company support

    Uses unified generator that routes to correct format based on client profile

    Args:
        session_id: Session ID from import
        invoice_no: Starting invoice number
        invoice_date: Invoice date
        call_off: Call off reference (optional)
        db: Database session

    Returns:
        {
            "session_id": str,
            "total": int,
            "successful": int,
            "failed": int,
            "invoices": List[Dict]
        }
    """
    from pathlib import Path
    import json

    print(f"[DEBUG] Multi-company generation started")
    print(f"[DEBUG] Session: {session_id}")
    print(f"[DEBUG] Invoice No: {invoice_no}")

    # Load session metadata
    SESSIONS = Path("out/sessions")
    sdir = SESSIONS / session_id
    meta_file = sdir / "meta.json"

    if not meta_file.exists():
        raise HTTPException(404, "Session not found")

    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    company_id = meta.get('company_id', 1)
    client_id = meta.get('client_id')
    preview = meta.get('preview', {})
    abz_filename = meta.get('abz')

    print(f"[DEBUG] Company ID: {company_id}")
    print(f"[DEBUG] Client ID: {client_id}")
    print(f"[DEBUG] Employees: {len(preview)}")

    # Get client profile
    manager = get_client_profile_manager()
    profile = manager.get_profile(client_id)

    if not profile:
        raise HTTPException(404, f"Client profile not found: {client_id}")

    # Get ABZ file path (for template-based generation)
    abz_path = sdir / abz_filename if abz_filename else None

    # Prepare output directory
    output_dir = sdir / "invoices"
    output_dir.mkdir(exist_ok=True)

    # Convert preview to employees list
    employees_data = list(preview.values())

    # Generate invoices using unified generator
    try:
        from app.invoice.unified_invoice_generator import generate_invoices_batch
    except ModuleNotFoundError:
        from invoice.unified_invoice_generator import generate_invoices_batch

    results = generate_invoices_batch(
        employees_data=employees_data,
        client_profile=profile,
        invoice_no_start=int(invoice_no),
        invoice_date=invoice_date,
        output_dir=output_dir,
        abz_path=abz_path
    )

    print(f"[DEBUG] Generation complete:")
    print(f"  Total: {results['total']}")
    print(f"  Successful: {results['successful']}")
    print(f"  Failed: {results['failed']}")

    # Save invoices to database
    try:
        from app.database.models import Invoice
    except ModuleNotFoundError:
        from database.models import Invoice

    for invoice_result in results['invoices']:
        invoice = Invoice(
            company_id=company_id,
            session_id=session_id,
            invoice_number=invoice_result.get('filename', '').split()[2].split('-')[0],  # Extract number
            employee_name=invoice_result['employee_name'],
            employee_position=invoice_result.get('employee_position'),
            invoice_date=datetime.strptime(invoice_date, "%d/%m/%Y"),
            call_off=call_off,
            client_id=invoice_result['client_id'],
            client_name=invoice_result['client_name'],
            client_category=invoice_result.get('client_category'),
            client_subcategory=invoice_result.get('client_subcategory'),
            file_path_xlsx=str(invoice_result['xlsx_path']),
            file_path_pdf=str(invoice_result['pdf_path']) if invoice_result.get('pdf_path') else None,
            total_amount=invoice_result['total_amount'],
            currency="GBP",
            base_amount=invoice_result['financial_breakdown'].get('base_amount'),
            overtime_amount=invoice_result['financial_breakdown'].get('overtime_amount'),
            expenses_amount=invoice_result['financial_breakdown'].get('expenses_amount'),
            insurance_amount=invoice_result['financial_breakdown'].get('insurance_amount'),
            other_amount=invoice_result['financial_breakdown'].get('other_amount'),
            status="generated",
            invoice_metadata=json.dumps({
                "vessel": invoice_result.get('vessel'),
                "period": invoice_result.get('period'),
                "invoice_format": invoice_result.get('invoice_format')
            })
        )
        db.add(invoice)

    db.commit()

    print(f"[DEBUG] Saved {len(results['invoices'])} invoices to database")

    return {
        "session_id": session_id,
        "total": results['total'],
        "successful": results['successful'],
        "failed": results['failed'],
        "invoices": [
            {
                "filename": inv['filename'],
                "employee_name": inv['employee_name'],
                "total_amount": inv['total_amount'],
                "client_name": inv['client_name']
            }
            for inv in results['invoices']
        ],
        "errors": results.get('errors', [])
    }

