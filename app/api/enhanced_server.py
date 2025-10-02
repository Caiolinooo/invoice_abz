"""
Enhanced FastAPI server with database integration
"""
from __future__ import annotations
from pathlib import Path
import json
import uuid
import zipfile
import asyncio
import threading
import os
from typing import Dict, List, Optional, Any
import datetime as dt
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Database imports
try:
    from app.database.database import get_db, init_database
    from app.database.services import (
        InvoiceService, ConfigurationService, TemplateService, 
        SessionService, EmailLogService
    )
    from app.database.models import Invoice, Configuration, Template
except ImportError:
    from database.database import get_db, init_database
    from database.services import (
        InvoiceService, ConfigurationService, TemplateService, 
        SessionService, EmailLogService
    )
    from database.models import Invoice, Configuration, Template

# Original imports
try:
    from app.utils.abz_charge_rate_parser import read_charge_rate_table
    from app.utils.anfin_parser import extract_individual_totals, extract_costs_gbp
    from app.utils.excel_abz_template import get_invoice_meta
    from app.invoice.template_filler import generate_from_abz_template
    from app.utils.libreoffice_export import xlsx_to_pdf, ensure_libreoffice
except ModuleNotFoundError:
    from utils.abz_charge_rate_parser import read_charge_rate_table
    from utils.anfin_parser import extract_individual_totals, extract_costs_gbp
    from utils.excel_abz_template import get_invoice_meta
    from invoice.template_filler import generate_from_abz_template
    from utils.libreoffice_export import xlsx_to_pdf, ensure_libreoffice, find_soffice

# Initialize database on startup
try:
    init_database()
    print("✓ Database initialized successfully")
except Exception as e:
    print(f"⚠️ Database initialization warning: {e}")

app = FastAPI(
    title="Invoice System API",
    version="2.0.0",
    description="Enhanced Invoice Generation System with Database Integration"
)

# Configure CORS
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include authentication routes
try:
    from app.auth.routes import router as auth_router
    from app.auth.dependencies import require_manager_or_admin, get_current_user
    from app.auth.models import User as AuthUser
    app.include_router(auth_router)
    print("✅ Authentication routes loaded")
except ImportError as e:
    print(f"⚠️  Warning: Could not load authentication routes: {e}")
    # Create dummy dependencies if auth not available
    async def require_manager_or_admin():
        return None
    async def get_current_user():
        return None
    AuthUser = None

# Add security middleware
try:
    from app.auth.middleware import RateLimitMiddleware, AuditLogMiddleware

    # Rate limiting (5 login attempts per minute by default)
    rate_limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "5"))
    app.add_middleware(RateLimitMiddleware, requests_per_minute=rate_limit)
    print(f"✅ Rate limiting enabled: {rate_limit} requests/minute")

    # Audit logging
    app.add_middleware(AuditLogMiddleware)
    print("✅ Audit logging enabled")
except ImportError as e:
    print(f"⚠️  Warning: Could not load security middleware: {e}")

# Ensure required directories exist
OUT_DIR = Path("out")
OUT_DIR.mkdir(parents=True, exist_ok=True)
SESSIONS = Path("out/sessions")
SESSIONS.mkdir(parents=True, exist_ok=True)

# Serve outputs and UI statically
app.mount("/out", StaticFiles(directory="out"), name="out")
app.mount("/ui", StaticFiles(directory="app/ui", html=True), name="ui")

# Default company ID (for backward compatibility)
DEFAULT_COMPANY_ID = 1

# Pydantic models
class GenerateRequest(BaseModel):
    session_id: str
    invoice_date: Optional[str] = None
    invoice_no: Optional[str] = None
    call_off: Optional[str] = None
    overrides: Optional[Dict[str, object]] = None


class InvoiceResponse(BaseModel):
    id: int
    session_id: str
    invoice_number: str
    employee_name: str
    employee_position: Optional[str]
    invoice_date: datetime
    call_off: Optional[str]
    file_path_xlsx: Optional[str]
    file_path_pdf: Optional[str]
    total_amount: Optional[float]
    currency: str
    status: str
    created_at: datetime


class ConfigurationRequest(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    config_type: str = "general"


class ConfigurationResponse(BaseModel):
    id: int
    key: str
    value: str
    description: Optional[str]
    config_type: str


class TemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    file_path: str
    is_default: bool
    client_specific: Optional[str]
    version: str
    created_at: datetime


class SessionResponse(BaseModel):
    id: int
    session_id: str
    abz_filename: Optional[str]
    anfin_filename: Optional[str]
    status: str
    employee_count: int
    invoices_generated: int
    created_at: datetime


# Helper functions
def _save_upload(path: Path, upload: UploadFile) -> Path:
    """Save uploaded file and return path"""
    with open(path, "wb") as f:
        f.write(upload.file.read())
    return path


def _read_json(path: Path) -> dict:
    """Read JSON with robust encoding fallback"""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return json.loads(path.read_text(encoding="latin-1"))


def _progress_path(session_dir: Path) -> Path:
    """Get progress file path for session"""
    return session_dir / "progress.json"


def _update_progress(session_dir: Path, stage: str, percent: int, done: bool = False, error: str = None):
    """Update progress for session"""
    progress_data = {
        "stage": stage,
        "percent": percent,
        "done": done,
        "timestamp": datetime.now().isoformat()
    }
    if error:
        progress_data["error"] = error

    progress_file = _progress_path(session_dir)
    try:
        progress_file.write_text(json.dumps(progress_data, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"Warning: Could not update progress: {e}")


def _build_preview_single_file(abz: Path) -> Dict[str, Dict]:
    """Build preview using only the ABZ charge rate file.
    Global rule: one invoice per person. If a name appears multiple times
    with different positions/rates, create multiple service lines in the
    same invoice, each with its own unit_price and quantity.
    """
    try:
        charge_df = read_charge_rate_table(abz, "Charge Rate")
        print("[preview] Columns:", list(charge_df.columns))
        if 'Brazilian Payroll Additionals (GBP)' in charge_df.columns:
            print('[preview] Additional sum:', float(charge_df['Brazilian Payroll Additionals (GBP)'].fillna(0).sum()))
        if 'Expenses' in charge_df.columns:
            print('[preview] Expenses sum:', float(charge_df['Expenses'].fillna(0).sum()))

        # Get unique employee names
        names = charge_df['Name'].dropna().astype(str).unique()

        # Import aggregator (handles multi-position employees)
        from app.utils.abz_charge_rate_parser import aggregate_employee

        preview: Dict[str, Dict] = {}

        for name in names:
            sub = charge_df[charge_df['Name'].astype(str) == name]

            # Build service lines per Position/Rate using aggregator
            agg = aggregate_employee(sub)
            preview_items: List[Dict] = []

            # service lines
            if agg is not None and not agg.empty:
                services = agg[agg['Type'] == 'service']
                for _, r in services.iterrows():
                    # r['Description'] comes as "<Name> - <Position>"; keep Position only for description
                    desc_role = str(r.get('Description') or '')
                    if ' - ' in desc_role:
                        desc_role = desc_role.split(' - ', 1)[-1]
                    desc = f"{name} - {desc_role}"
                    unit = float(r.get('Unit Price (GBP)') or 0.0)
                    qty = float(r.get('Quantity') or 0.0)
                    preview_items.append({
                        "description": desc,
                        "unit_price": round(unit, 2),
                        "quantity": qty,
                        "final": round(unit * qty, 2),
                    })

            # Additional and Expenses totals
            add_total = float(agg[agg['Type'] == 'additional']['Final Price (GBP)'].sum()) if agg is not None and not agg.empty else 0.0
            exp_total = float(agg[agg['Type'] == 'expense']['Final Price (GBP)'].sum()) if agg is not None and not agg.empty else 0.0

            if add_total and abs(add_total) > 1e-6:
                preview_items.append({"description": "Brazilian Payroll Additional", "final": round(add_total, 2)})
            if exp_total and abs(exp_total) > 1e-6:
                preview_items.append({"description": "Expenses", "final": round(exp_total, 2)})

            preview[name] = {
                "items": preview_items,
                "meta": {},
            }

        return preview
    except Exception as e:
        print(f"Error building preview: {e}")
        import traceback
        traceback.print_exc()
        return {}


# API Endpoints

@app.get("/")
async def root():
    """Redirect to UI"""
    return RedirectResponse(url="/ui/")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0", "database": "connected"}


@app.get("/api/system/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Get overall system statistics"""
    try:
        from app.database.models import Session as SessionModel

        # Invoice stats
        invoice_stats = InvoiceService.get_invoice_stats(db, DEFAULT_COMPANY_ID)

        # Session stats
        total_sessions = db.query(SessionModel).filter(
            SessionModel.company_id == DEFAULT_COMPANY_ID
        ).count()

        active_sessions = db.query(SessionModel).filter(
            SessionModel.company_id == DEFAULT_COMPANY_ID,
            SessionModel.status == "active"
        ).count()

        # Template stats
        total_templates = len(TemplateService.get_templates(db, DEFAULT_COMPANY_ID))

        # Configuration stats
        total_configs = len(ConfigurationService.get_all_configs(db, DEFAULT_COMPANY_ID))

        return {
            "invoices": invoice_stats,
            "sessions": {
                "total": total_sessions,
                "active": active_sessions,
                "completed": total_sessions - active_sessions
            },
            "templates": {
                "total": total_templates
            },
            "configurations": {
                "total": total_configs
            },
            "system": {
                "version": "2.0.0",
                "database": "SQLite",
                "features": [
                    "Invoice History",
                    "Configurable Settings",
                    "Template Management",
                    "Multi-format Export",
                    "Batch Processing"
                ]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system stats: {str(e)}")


# Invoice History Endpoints
@app.get("/api/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get invoice history with filters"""
    try:
        print(f"[DEBUG] GET /api/invoices - Filters: employee_name={employee_name}, status={status}, date_from={date_from}, date_to={date_to}")

        # Parse date filters
        date_from_dt = datetime.fromisoformat(date_from) if date_from else None
        date_to_dt = datetime.fromisoformat(date_to) if date_to else None

        print(f"[DEBUG] Parsed dates: date_from_dt={date_from_dt}, date_to_dt={date_to_dt}")

        invoices = InvoiceService.get_invoices(
            db=db,
            company_id=DEFAULT_COMPANY_ID,
            skip=skip,
            limit=limit,
            employee_name=employee_name,
            status=status,
            date_from=date_from_dt,
            date_to=date_to_dt
        )

        print(f"[DEBUG] Found {len(invoices)} invoices")
        
        return [InvoiceResponse(
            id=inv.id,
            session_id=inv.session_id,
            invoice_number=inv.invoice_number,
            employee_name=inv.employee_name,
            employee_position=inv.employee_position,
            invoice_date=inv.invoice_date,
            call_off=inv.call_off,
            file_path_xlsx=inv.file_path_xlsx,
            file_path_pdf=inv.file_path_pdf,
            total_amount=inv.total_amount,
            currency=inv.currency,
            status=inv.status,
            created_at=inv.created_at
        ) for inv in invoices]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching invoices: {str(e)}")


@app.get("/api/invoices/stats")
async def get_invoice_stats(db: Session = Depends(get_db)):
    """Get invoice statistics"""
    try:
        stats = InvoiceService.get_invoice_stats(db, DEFAULT_COMPANY_ID)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@app.get("/api/invoices/{invoice_id}/download")
async def download_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Download invoice file"""
    try:
        invoice = InvoiceService.get_invoice_by_id(db, invoice_id, DEFAULT_COMPANY_ID)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        file_path = Path(invoice.file_path_xlsx)
        if not file_path.exists():
            # Try relative to current working directory
            file_path = Path.cwd() / invoice.file_path_xlsx
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Invoice file not found")

        return FileResponse(
            path=str(file_path),
            filename=f"{invoice.employee_name.replace(' ', '_')}_Invoice_{invoice.invoice_number}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@app.get("/api/invoices/{invoice_id}/view")
async def view_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Get invoice details for viewing"""
    try:
        invoice = InvoiceService.get_invoice_by_id(db, invoice_id, DEFAULT_COMPANY_ID)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        return {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "employee_name": invoice.employee_name,
            "employee_position": invoice.employee_position,
            "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
            "call_off": invoice.call_off,
            "total_amount": float(invoice.total_amount) if invoice.total_amount else 0,
            "currency": invoice.currency,
            "status": invoice.status,
            "created_at": invoice.created_at.isoformat() if invoice.created_at else None,
            "file_exists": Path(invoice.file_path_xlsx).exists() or Path(Path.cwd() / invoice.file_path_xlsx).exists()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"View failed: {str(e)}")


@app.get("/api/invoice-seq")
async def get_invoice_sequence(db: Session = Depends(get_db)):
    """Get the last invoice number for sequence suggestion"""
    try:
        # Get the highest invoice number from the database
        last_invoice = InvoiceService.get_last_invoice_number(db, DEFAULT_COMPANY_ID)

        # Extract numeric part from invoice number (e.g., "INV-001" -> 1)
        last_number = 0
        if last_invoice and last_invoice.invoice_number:
            import re
            match = re.search(r'(\d+)', last_invoice.invoice_number)
            if match:
                last_number = int(match.group(1))

        return {"last": last_number}

    except Exception as e:
        # Return default if there's an error
        return {"last": 0}


@app.put("/api/invoices/{invoice_id}/status")
async def update_invoice_status(
    invoice_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update invoice status"""
    try:
        print(f"[DEBUG] PUT /api/invoices/{invoice_id}/status - New status: {status}")

        invoice = InvoiceService.update_invoice_status(
            db, invoice_id, DEFAULT_COMPANY_ID, status
        )

        if not invoice:
            print(f"[DEBUG] Invoice {invoice_id} not found")
            raise HTTPException(status_code=404, detail="Invoice not found")

        print(f"[DEBUG] Invoice {invoice_id} status updated to {status}")

        return {"message": "Status updated successfully", "status": status}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Error updating status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")


# Configuration Endpoints
@app.get("/api/configurations", response_model=List[ConfigurationResponse])
async def get_configurations(
    config_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get system configurations"""
    try:
        if config_type:
            configs = ConfigurationService.get_configs_by_type(
                db, DEFAULT_COMPANY_ID, config_type
            )
        else:
            configs = ConfigurationService.get_configs_by_type(
                db, DEFAULT_COMPANY_ID, "general"
            )
        
        return [ConfigurationResponse(
            id=config.id,
            key=config.key,
            value=config.value if not config.is_encrypted else "***",
            description=config.description,
            config_type=config.config_type
        ) for config in configs]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching configurations: {str(e)}")


@app.post("/api/configurations", response_model=ConfigurationResponse)
async def set_configuration(
    config: ConfigurationRequest,
    db: Session = Depends(get_db)
):
    """Set configuration value"""
    try:
        saved_config = ConfigurationService.set_config(
            db=db,
            company_id=DEFAULT_COMPANY_ID,
            key=config.key,
            value=config.value,
            description=config.description,
            config_type=config.config_type
        )
        
        return ConfigurationResponse(
            id=saved_config.id,
            key=saved_config.key,
            value=saved_config.value if not saved_config.is_encrypted else "***",
            description=saved_config.description,
            config_type=saved_config.config_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting configuration: {str(e)}")


# Template Endpoints
@app.get("/api/templates", response_model=List[TemplateResponse])
async def get_templates(db: Session = Depends(get_db)):
    """Get all templates"""
    try:
        templates = TemplateService.get_templates(db, DEFAULT_COMPANY_ID)

        return [TemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            file_path=template.file_path,
            is_default=template.is_default,
            client_specific=template.client_specific,
            version=template.version,
            created_at=template.created_at
        ) for template in templates]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")


@app.post("/api/templates/{template_id}/set-default")
async def set_default_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Set template as default"""
    try:
        success = TemplateService.set_default_template(db, DEFAULT_COMPANY_ID, template_id)

        if not success:
            raise HTTPException(status_code=404, detail="Template not found")

        return {"message": "Default template updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting default template: {str(e)}")


# Session Endpoints
@app.get("/api/sessions", response_model=List[SessionResponse])
async def get_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get sessions history"""
    try:
        from app.database.models import Session as SessionModel

        sessions = db.query(SessionModel).filter(
            SessionModel.company_id == DEFAULT_COMPANY_ID
        ).order_by(SessionModel.created_at.desc()).offset(skip).limit(limit).all()

        return [SessionResponse(
            id=session.id,
            session_id=session.session_id,
            abz_filename=session.abz_filename,
            anfin_filename=session.anfin_filename,
            status=session.status,
            employee_count=session.employee_count,
            invoices_generated=session.invoices_generated,
            created_at=session.created_at
        ) for session in sessions]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}")


@app.get("/api/sessions/{session_id}")
async def get_session_details(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get session details"""
    try:
        session = SessionService.get_session(db, session_id, DEFAULT_COMPANY_ID)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get invoices for this session
        invoices = InvoiceService.get_invoices(
            db=db,
            company_id=DEFAULT_COMPANY_ID,
            skip=0,
            limit=1000,
            employee_name=None,
            status=None,
            date_from=None,
            date_to=None
        )

        session_invoices = [inv for inv in invoices if inv.session_id == session_id]

        return {
            "session": SessionResponse(
                id=session.id,
                session_id=session.session_id,
                abz_filename=session.abz_filename,
                anfin_filename=session.anfin_filename,
                status=session.status,
                employee_count=session.employee_count,
                invoices_generated=session.invoices_generated,
                created_at=session.created_at
            ),
            "invoices": [InvoiceResponse(
                id=inv.id,
                session_id=inv.session_id,
                invoice_number=inv.invoice_number,
                employee_name=inv.employee_name,
                employee_position=inv.employee_position,
                invoice_date=inv.invoice_date,
                call_off=inv.call_off,
                file_path_xlsx=inv.file_path_xlsx,
                file_path_pdf=inv.file_path_pdf,
                total_amount=inv.total_amount,
                currency=inv.currency,
                status=inv.status,
                created_at=inv.created_at
            ) for inv in session_invoices]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching session details: {str(e)}")


# Original endpoints (maintaining backward compatibility)
@app.post("/api/import")
async def api_import(
    abz: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import ABZ file and create session"""
    try:
        sid = uuid.uuid4().hex
        sdir = SESSIONS / sid
        sdir.mkdir(parents=True, exist_ok=True)

        abz_path = _save_upload(sdir / abz.filename, abz)
        preview = _build_preview_single_file(abz_path)

        # Save session metadata
        meta_data = {
            "abz": abz.filename,
            "preview": preview,
        }
        
        (sdir / "meta.json").write_text(
            json.dumps(meta_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        # Create session record in database
        try:
            SessionService.create_session(db, {
                "company_id": DEFAULT_COMPANY_ID,
                "session_id": sid,
                "abz_filename": abz.filename,
                "status": "active",
                "employee_count": len(preview)
            })
        except Exception as e:
            print(f"Warning: Could not create session record: {e}")

        return {"session_id": sid, "employees": list(preview.keys())}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@app.get("/api/progress")
async def api_progress(session_id: str = Query(...)):
    """Get progress data for session"""
    try:
        sdir = SESSIONS / session_id
        progress_file = sdir / "progress.json"

        if not progress_file.exists():
            return {"session_id": session_id, "stage": "idle", "percent": 0, "done": False}

        try:
            data = _read_json(progress_file)
            return {"session_id": session_id, **data}
        except Exception:
            return {"session_id": session_id, "stage": "idle", "percent": 0, "done": False}

    except Exception as e:
        return {"session_id": session_id, "stage": "error", "percent": 0, "done": False, "error": str(e)}


@app.get("/api/preview")
async def api_preview(session_id: str = Query(...)):
    """Get preview data for session"""
    try:
        sdir = SESSIONS / session_id
        if not sdir.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        meta_file = sdir / "meta.json"
        if not meta_file.exists():
            raise HTTPException(status_code=404, detail="Session metadata not found")

        meta = _read_json(meta_file)
        preview = meta.get("preview", {})

        return {"preview": preview}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


def _generate_invoices_background(session_id: str, request_data: dict):
    """Background task for invoice generation"""
    try:
        sdir = SESSIONS / session_id
        _update_progress(sdir, "initializing", 0)

        meta_file = sdir / "meta.json"
        meta = _read_json(meta_file)
        abz_path = sdir / meta["abz"]

        # Create directories
        xlsx_dir = sdir / "xlsx"
        xlsx_dir.mkdir(exist_ok=True)

        # Create invoice metadata from request parameters
        invoice_meta = {
            'invoice_date': request_data.get('invoice_date'),
            'invoice_no': request_data.get('invoice_no'),
            'call_off': request_data.get('call_off')
        }

        employees = list(meta["preview"].keys())
        total_employees = len(employees)
        results = []

        _update_progress(sdir, "generating", 10)

        # Generate for each employee
        for i, employee_name in enumerate(employees):
            try:
                # Update progress
                progress = 10 + int((i / total_employees) * 80)  # 10-90%
                _update_progress(sdir, f"generating_invoice_for_{employee_name}", progress)

                # Get line items from preview data
                employee_data = meta["preview"][employee_name]
                line_items = employee_data.get("items", [])

                result_path = generate_from_abz_template(
                    abz_xlsx=abz_path,
                    template_sheet_name="dummy",  # Not used when use_template_based=True
                    employee_name=employee_name,
                    line_items=line_items,
                    out_dir=xlsx_dir,
                    invoice_date=invoice_meta['invoice_date'],
                    invoice_no=invoice_meta['invoice_no'],
                    call_off=invoice_meta['call_off'],
                    use_template_based=True
                )

                if result_path:
                    # Generate PDF from XLSX
                    pdf_path = None
                    try:
                        pdf_dir = sdir / "pdf"
                        pdf_dir.mkdir(exist_ok=True)
                        pdf_path = pdf_dir / f"{result_path.stem}.pdf"

                        # Try to convert to PDF
                        soffice = find_soffice()
                        if soffice:
                            print(f"🔄 Converting to PDF: {employee_name}")
                            xlsx_to_pdf(result_path, pdf_path, soffice_path=soffice)
                            print(f"✅ PDF created: {pdf_path}")
                        else:
                            print(f"⚠️ LibreOffice not found, skipping PDF generation for {employee_name}")
                    except Exception as pdf_error:
                        print(f"⚠️ Failed to generate PDF for {employee_name}: {pdf_error}")
                        pdf_path = None

                    results.append({
                        "employee": employee_name,
                        "success": True,
                        "file": str(result_path),
                        "pdf": str(pdf_path) if pdf_path and pdf_path.exists() else None
                    })

                    # Save invoice to database
                    try:
                        # Calculate total amount from line items
                        total_amount = sum(float(item.get("final", 0)) for item in line_items)

                        # Convert invoice_date from DD/MM/YYYY to datetime.date
                        invoice_date_obj = None
                        if invoice_meta.get('invoice_date'):
                            try:
                                date_parts = invoice_meta['invoice_date'].split('/')
                                if len(date_parts) == 3:
                                    day, month, year = date_parts
                                    invoice_date_obj = dt.date(int(year), int(month), int(day))
                            except (ValueError, IndexError):
                                pass

                        if not invoice_date_obj:
                            invoice_date_obj = dt.date.today()

                        # Get employee position from preview data
                        employee_position = None
                        if line_items and len(line_items) > 0:
                            first_item = line_items[0]
                            employee_position = first_item.get('description', '')

                        # Create invoice record
                        db = next(get_db())

                        # Ensure invoice_number is never None
                        invoice_number = invoice_meta.get('invoice_no')
                        if not invoice_number or str(invoice_number).strip() == '' or str(invoice_number).lower() == 'none':
                            invoice_number = f"INV-{session_id[:8]}-{i+1:03d}"

                        invoice_data = {
                            "company_id": DEFAULT_COMPANY_ID,
                            "session_id": session_id,
                            "invoice_number": str(invoice_number),
                            "employee_name": employee_name,
                            "employee_position": employee_position,
                            "invoice_date": invoice_date_obj,
                            "call_off": invoice_meta.get('call_off'),
                            "total_amount": total_amount,
                            "currency": "GBP",
                            "file_path_xlsx": str(result_path),
                            "file_path_pdf": str(pdf_path) if pdf_path and pdf_path.exists() else None,
                            "status": "generated"
                        }

                        created_invoice = InvoiceService.create_invoice(db, invoice_data)
                        print(f"✅ Invoice saved to database: {invoice_number} for {employee_name} (£{total_amount:.2f})")

                    except Exception as db_error:
                        print(f"⚠️ Failed to save invoice to database for {employee_name}: {db_error}")
                        # Don't fail the generation if database save fails

                else:
                    results.append({
                        "employee": employee_name,
                        "success": False,
                        "error": "Failed to generate invoice"
                    })

            except Exception as e:
                results.append({
                    "employee": employee_name,
                    "success": False,
                    "error": str(e)
                })

        # Save results
        _update_progress(sdir, "saving_results", 95)
        results_file = sdir / "results.json"
        results_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

        # Complete
        _update_progress(sdir, "completed", 100, done=True)

    except Exception as e:
        _update_progress(sdir, "error", 0, done=True, error=str(e))


@app.post("/api/generate")
async def api_generate(request: GenerateRequest):
    """Start asynchronous invoice generation"""
    try:
        sdir = SESSIONS / request.session_id
        if not sdir.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        meta_file = sdir / "meta.json"
        if not meta_file.exists():
            raise HTTPException(status_code=404, detail="Session metadata not found")

        # Start background generation
        request_data = {
            'invoice_date': request.invoice_date,
            'invoice_no': request.invoice_no,
            'call_off': request.call_off,
            'overrides': request.overrides
        }

        # Start in background thread
        thread = threading.Thread(
            target=_generate_invoices_background,
            args=(request.session_id, request_data)
        )
        thread.daemon = True
        thread.start()

        return {"message": "Generation started", "session_id": request.session_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/api/progress")
async def api_progress(session_id: str = Query(...)):
    """Get generation progress for session"""
    try:
        sdir = SESSIONS / session_id
        if not sdir.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        progress_file = _progress_path(sdir)
        if not progress_file.exists():
            return {
                "session_id": session_id,
                "stage": "idle",
                "percent": 0,
                "done": False
            }

        progress_data = _read_json(progress_file)
        progress_data["session_id"] = session_id
        return progress_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Progress check failed: {str(e)}")


@app.get("/api/results")
async def api_results(session_id: str = Query(...)):
    """Get generation results for session"""
    try:
        sdir = SESSIONS / session_id
        if not sdir.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        results_file = sdir / "results.json"
        if not results_file.exists():
            return {
                "session_id": session_id,
                "results": [],
                "total": 0,
                "successful": 0
            }

        results = _read_json(results_file)
        return {
            "session_id": session_id,
            "results": results,
            "total": len(results),
            "successful": sum(1 for r in results if r.get("success", False))
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Results check failed: {str(e)}")


@app.post("/api/generate-pdf")
async def api_generate_pdf(session_id: str = Form(...)):
    """Generate PDF files for session"""
    try:
        sdir = SESSIONS / session_id
        xlsx_dir = sdir / "xlsx"
        pdf_dir = sdir / "pdf"

        if not xlsx_dir.exists():
            raise HTTPException(status_code=404, detail="No Excel files found")

        pdf_dir.mkdir(exist_ok=True)

        # Ensure LibreOffice is available
        ensure_libreoffice()

        results = []
        for xlsx_file in xlsx_dir.glob("*.xlsx"):
            try:
                pdf_path = pdf_dir / f"{xlsx_file.stem}.pdf"
                success = xlsx_to_pdf(xlsx_file, pdf_path)

                if success:
                    results.append({
                        "file": xlsx_file.name,
                        "success": True,
                        "pdf_path": str(pdf_path.relative_to(Path.cwd()))
                    })
                else:
                    results.append({
                        "file": xlsx_file.name,
                        "success": False,
                        "error": "PDF conversion failed"
                    })

            except Exception as e:
                results.append({
                    "file": xlsx_file.name,
                    "success": False,
                    "error": str(e)
                })

        return {
            "session_id": session_id,
            "results": results,
            "total": len(results),
            "successful": sum(1 for r in results if r["success"])
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.get("/api/session/{session_id}/files")
async def get_session_files(session_id: str):
    """Get list of generated files for a session"""
    try:
        sdir = SESSIONS / session_id
        if not sdir.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        files = {
            "xlsx": [],
            "pdf": []
        }

        # List XLSX files
        xlsx_dir = sdir / "xlsx"
        if xlsx_dir.exists():
            for file in xlsx_dir.glob("*.xlsx"):
                files["xlsx"].append({
                    "name": file.name,
                    "path": f"/out/sessions/{session_id}/xlsx/{file.name}",
                    "size": file.stat().st_size
                })

        # List PDF files
        pdf_dir = sdir / "pdf"
        if pdf_dir.exists():
            for file in pdf_dir.glob("*.pdf"):
                files["pdf"].append({
                    "name": file.name,
                    "path": f"/out/sessions/{session_id}/pdf/{file.name}",
                    "size": file.stat().st_size
                })

        return files

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@app.get("/api/sessions/{session_id}/download/{format}")
async def download_session_files(session_id: str, format: str):
    """Download session files as ZIP"""
    try:
        sdir = SESSIONS / session_id
        if not sdir.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        if format not in ["xlsx", "pdf", "all"]:
            raise HTTPException(status_code=400, detail="Invalid format")

        zip_path = sdir / f"session_{session_id}_{format}.zip"

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            if format in ["xlsx", "all"]:
                xlsx_dir = sdir / "xlsx"
                if xlsx_dir.exists():
                    for file in xlsx_dir.glob("*.xlsx"):
                        zipf.write(file, f"xlsx/{file.name}")

            if format in ["pdf", "all"]:
                pdf_dir = sdir / "pdf"
                if pdf_dir.exists():
                    for file in pdf_dir.glob("*.pdf"):
                        zipf.write(file, f"pdf/{file.name}")

        return FileResponse(
            path=zip_path,
            filename=f"session_{session_id}_{format}.zip",
            media_type="application/zip"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@app.get("/api/system/libreoffice-status")
async def check_libreoffice_status():
    """Check if LibreOffice is installed and available"""
    import platform
    import shutil

    soffice_path = find_soffice()

    status = {
        "installed": soffice_path is not None,
        "path": soffice_path,
        "platform": platform.system(),
        "winget_available": shutil.which("winget") is not None,
        "choco_available": shutil.which("choco") is not None,
    }

    if soffice_path:
        # Try to get version
        try:
            import subprocess
            result = subprocess.run(
                [soffice_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            status["version"] = result.stdout.strip()
        except Exception as e:
            status["version_error"] = str(e)

    return status


@app.post("/api/system/install-libreoffice")
async def install_libreoffice_endpoint():
    """Attempt to install LibreOffice (Windows only)"""
    import platform

    if platform.system().lower() != "windows":
        raise HTTPException(
            status_code=400,
            detail="Auto-installation is only supported on Windows. Please install LibreOffice manually."
        )

    try:
        soffice = ensure_libreoffice(auto_install=True)

        if soffice:
            return {
                "success": True,
                "message": "LibreOffice installed successfully",
                "path": soffice
            }
        else:
            return {
                "success": False,
                "message": "Failed to install LibreOffice. Please install manually from https://www.libreoffice.org/download/download/"
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Installation failed: {str(e)}"
        )


@app.post("/api/reset-database")
async def reset_database(db: Session = Depends(get_db)):
    """Reset the database (delete all data and recreate tables)"""
    try:
        import shutil
        from pathlib import Path
        import time
        import gc

        # Close the current database connection
        db.close()

        # Force close all connections in the pool
        try:
            from app.database.database import engine
            engine.dispose()
            print("🔌 Database engine disposed")
        except Exception as e:
            print(f"⚠️ Warning disposing engine: {e}")

        # Force garbage collection to release file handles
        gc.collect()
        time.sleep(0.5)  # Give OS time to release file handles

        # Path to the database file
        db_path = Path("data/invoice_system.db")
        backup_path = None

        if db_path.exists():
            # Backup the old database
            backup_path = Path(f"data/invoice_system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            shutil.copy(db_path, backup_path)
            print(f"📦 Database backed up to: {backup_path}")

            # Try to delete the database file with retries
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    db_path.unlink()
                    print(f"🗑️ Database deleted: {db_path}")
                    break
                except PermissionError as e:
                    if attempt < max_retries - 1:
                        print(f"⏳ Retry {attempt + 1}/{max_retries} - waiting for file release...")
                        time.sleep(1)
                        gc.collect()
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail="Database is locked. Please stop the server, delete the file manually, and restart."
                        )

        # Reinitialize the database
        init_database()
        print("✅ Database reinitialized successfully")

        return {
            "success": True,
            "message": "Database reset successfully",
            "backup": str(backup_path) if backup_path else None
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to reset database: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset database: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
