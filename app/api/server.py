from __future__ import annotations
from pathlib import Path
import json
import uuid
import zipfile
from typing import Dict, List, Optional, Callable, Any, Tuple
import datetime as dt
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body, Depends
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Local imports (support running as package or script)
try:
    from app.utils.abz_charge_rate_parser import read_charge_rate_table
    from app.utils.anfin_parser import extract_individual_totals, extract_costs_gbp
    from app.utils.excel_abz_template import get_invoice_meta
    from app.invoice.template_filler import generate_from_abz_template
    from app.utils.libreoffice_export import xlsx_to_pdf, ensure_libreoffice
    from app.database.services import InvoiceService
    from app.database.database import get_db
except ModuleNotFoundError:
    from utils.abz_charge_rate_parser import read_charge_rate_table
    from utils.anfin_parser import extract_individual_totals, extract_costs_gbp
    from utils.excel_abz_template import get_invoice_meta
    from invoice.template_filler import generate_from_abz_template
    from utils.libreoffice_export import xlsx_to_pdf, ensure_libreoffice
    from database.services import InvoiceService
    from database.database import get_db

app = FastAPI(title="Payroll Conversion API", version="0.1.0")

# Configure CORS
import os
from dotenv import load_dotenv
load_dotenv()

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")

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
except ImportError:
    print("⚠️  Warning: Could not load authentication routes")
    # Create dummy dependencies if auth not available
    async def require_manager_or_admin():
        return None
    async def get_current_user():
        return None
    AuthUser = None

# Add security middleware (order matters: CORS -> Auth -> RateLimit -> AuditLog)
try:
    from app.auth.middleware import AuthMiddleware, RateLimitMiddleware, AuditLogMiddleware

    # Authentication middleware (must be added AFTER CORS but BEFORE other middlewares)
    app.add_middleware(AuthMiddleware)
    print("✅ Authentication middleware enabled")

    # Rate limiting (5 login attempts per minute by default)
    rate_limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "5"))
    app.add_middleware(RateLimitMiddleware, requests_per_minute=rate_limit)
    print(f"✅ Rate limiting enabled: {rate_limit} requests/minute")

    # Audit logging
    app.add_middleware(AuditLogMiddleware)
    print("✅ Audit logging enabled")

except ImportError as e:
    print(f"⚠️  Warning: Could not load security middleware: {e}")

# Ensure required directories exist before mounting static files
OUT_DIR = Path("out")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Serve outputs and UI statically
app.mount("/out", StaticFiles(directory="out"), name="out")
app.mount("/ui", StaticFiles(directory="app/ui", html=True), name="ui")

SESSIONS = Path("out/sessions")
SESSIONS.mkdir(parents=True, exist_ok=True)

# Persistent invoice sequence storage
SEQ_FILE = Path("out/invoice_seq.json")

def _seq_read() -> dict:
    try:
        if SEQ_FILE.exists():
            return json.loads(SEQ_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"last": 0}

def _seq_write(last: int) -> None:
    SEQ_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        SEQ_FILE.write_text(json.dumps({"last": int(last)}, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # best-effort
        pass


# Simple progress tracking per session
def _progress_path(sdir: Path) -> Path:
    return sdir / "progress.json"

def _update_progress(sdir: Path, **kwargs):
    p = _progress_path(sdir)
    current = {}
    if p.exists():
        try:
            current = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            current = {}
    current.update(kwargs)
    p.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")



def _read_json(path: Path) -> dict:
    """Read JSON with robust encoding fallback (utf-8 first, then latin-1)."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return json.loads(path.read_text(encoding="latin-1"))


class GenerateRequest(BaseModel):
    session_id: str
    invoice_date: Optional[str] = None
    invoice_no: Optional[str] = None
    call_off: Optional[str] = None
    # Optional overrides by employee
    # Backward compatible:
    #  - {name: {quantity, unit_price}}  -> aplica na 1ª linha de serviço
    # Novo formato (suportado adicionalmente):
    #  - {name: [{line: <idx>, quantity?, unit_price?}, ...]}
    overrides: Optional[Dict[str, Any]] = None


def _save_upload(dst: Path, uf: UploadFile) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    data = uf.file.read()
    dst.write_bytes(data)
    return dst

class _GenReq:
    def __init__(self, data: Dict[str, Any]):
        self.session_id = str(data.get('session_id') or '').strip()
        self.invoice_date = data.get('invoice_date')
        self.invoice_no = data.get('invoice_no')
        self.call_off = data.get('call_off')
        self.overrides = data.get('overrides') or {}


def _friendly_name(full: str) -> str:
    parts = str(full).split()
    if len(parts) >= 2:
        return " ".join(parts[:2])
    return str(full)

# normalize (remove acentos e não-alfanuméricos) para comparar nomes e abas
import unicodedata, re

def _norm(s: str) -> str:
    s = unicodedata.normalize('NFD', str(s))
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '', s.lower())


def _find_template_for_employee(employee_name: str, invoice_sheets: list) -> str:
    """
    Advanced template matching algorithm for diverse situations:
    1. Handle accented characters (Brandão → Brandao)
    2. Use first name as default, second name for disambiguation
    3. Handle complex names and various sheet naming patterns
    4. Try multiple strategies for maximum compatibility
    """
    words = employee_name.split()
    if not words:
        return None

    # Strategy 1: Exact first name match
    first = _norm(words[0])
    first_matches = [s for s in invoice_sheets if first in _norm(s)]

    if len(first_matches) == 1:
        return first_matches[0]

    elif len(first_matches) > 1:
        # Multiple matches with first name, disambiguate with second name
        if len(words) >= 2:
            second = _norm(words[1])
            refined_matches = [s for s in first_matches if second in _norm(s)]
            if refined_matches:
                return refined_matches[0]

        # Try with any other word for disambiguation
        for word in words[1:]:
            word_norm = _norm(word)
            if len(word_norm) > 2:  # Skip short words like "de", "da", "do"
                refined_matches = [s for s in first_matches if word_norm in _norm(s)]
                if refined_matches:
                    return refined_matches[0]

        # If still ambiguous, return first match
        return first_matches[0]

    # Strategy 2: No first name match, try compound names (Filipi Brandão → Filipi Brandao)
    if len(words) >= 2:
        compound_patterns = [
            f"{words[0]} {words[1]}",  # "Filipi Brandão"
            f"{words[0]}_{words[1]}",  # "Filipi_Brandão"
            f"{words[0]}{words[1]}",   # "FilipiBrandão"
        ]

        for pattern in compound_patterns:
            pattern_norm = _norm(pattern)
            matches = [s for s in invoice_sheets if pattern_norm in _norm(s)]
            if matches:
                return matches[0]

    # Strategy 3: Try any significant word in the name
    for word in words:
        word_norm = _norm(word)
        if len(word_norm) > 2:  # Skip very short words
            matches = [s for s in invoice_sheets if word_norm in _norm(s)]
            if matches:
                return matches[0]

    # Strategy 4: Fuzzy matching - try partial matches
    for sheet in invoice_sheets:
        sheet_norm = _norm(sheet)
        # Check if any word from employee name appears in sheet name
        for word in words:
            word_norm = _norm(word)
            if len(word_norm) > 3 and word_norm in sheet_norm:
                return sheet

    return None


def _build_preview_single_file(abz: Path, anfin: Path = None) -> Dict[str, Dict]:
    """Build preview using ABZ charge rate file and optionally AN-FIN for expenses.
    Global rule: one invoice per person. If a name appears multiple times
    with different positions/rates, create multiple service lines in the
    same invoice, each with its own unit_price and quantity.

    EXPENSES PRIORITY:
    1. AN-FIN (Costs sheet) - Most accurate, preferred source
    2. ABZ Expenses column - Fallback if AN-FIN not available
    3. £0.00 - If neither source has data
    """
    print(f"[DEBUG] Processing file: {abz}")
    print(f"[DEBUG] File exists: {abz.exists()}")
    print(f"[DEBUG] File size: {abz.stat().st_size if abz.exists() else 'N/A'} bytes")

    charge_df = read_charge_rate_table(abz, "Charge Rate")

    print(f"[DEBUG] DataFrame shape: {charge_df.shape}")
    print(f"[DEBUG] DataFrame columns: {list(charge_df.columns)}")

    if not charge_df.empty:
        print(f"[DEBUG] First few rows of Name column:")
        if 'Name' in charge_df.columns:
            names = charge_df['Name'].dropna().unique()
            print(f"[DEBUG] Unique names found: {list(names)}")
            for i, name in enumerate(names[:5]):  # Show first 5 names
                print(f"[DEBUG]   {i+1}. {name}")
        else:
            print("[DEBUG] No 'Name' column found!")

    try:
        if 'Brazilian Payroll Additionals (GBP)' in charge_df.columns:
            print('[DEBUG] Additional sum:', float(charge_df['Brazilian Payroll Additionals (GBP)'].fillna(0).sum()))
        if 'Expenses' in charge_df.columns:
            print('[DEBUG] Expenses column in ABZ (will be used as fallback):', float(charge_df['Expenses'].fillna(0).sum()))
    except Exception as e:
        print(f"[DEBUG] Error calculating sums: {e}")
    names = sorted(set(charge_df['Name'].astype(str).dropna().tolist()))

    # Extract expenses from AN-FIN if available (PREFERRED SOURCE FOR EXPENSES)
    costs_gbp = {}
    if anfin and anfin.exists():
        try:
            print(f"[DEBUG] ✅ Loading expenses from AN-FIN: {anfin}")
            ind = extract_individual_totals(anfin)
            costs_gbp = extract_costs_gbp(anfin, {k: v['exchange_rate'] for k, v in ind.items()})
            print(f"[DEBUG] Expenses from AN-FIN loaded for {len(costs_gbp)} employees")
            for emp_name, cost in costs_gbp.items():
                if cost > 0:
                    print(f"[DEBUG]   {emp_name}: £{cost:.2f}")
        except Exception as e:
            print(f"[DEBUG] ❌ Error loading AN-FIN expenses: {e}")
            import traceback
            traceback.print_exc()
            costs_gbp = {}
    else:
        print(f"[DEBUG] ⚠️  No AN-FIN file provided - will use expenses from ABZ as fallback")

    from openpyxl import load_workbook
    wb = load_workbook(abz, read_only=True)
    sheets = wb.sheetnames
    invoice_sheets = [s for s in sheets if s.lower().strip().endswith('_invoice')]


    preview: Dict[str, Dict] = {}
    # Import aggregator (handles multi-position employees)
    try:
        from app.utils.abz_charge_rate_parser import aggregate_employee  # type: ignore
    except Exception:
        from utils.abz_charge_rate_parser import aggregate_employee  # type: ignore

    for name in names:
        sub = charge_df[charge_df['Name'].astype(str) == name]

        # Template meta using improved matching
        template_sheet = _find_template_for_employee(name, invoice_sheets)
        meta = {'invoice_no': None, 'invoice_date': None, 'call_off': None}
        # Do not read call_off from template - only use form values
        if template_sheet:
            template_meta = get_invoice_meta(abz, template_sheet)
            meta['invoice_no'] = template_meta.get('invoice_no')
            meta['invoice_date'] = template_meta.get('invoice_date')
            # Explicitly ignore call_off from template

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
                desc = f"{_friendly_name(name)} - {desc_role}"
                # do not append Call-Off here; it will be controlled only by the form during generation
                unit = float(r.get('Unit Price (GBP)') or 0.0)
                qty = float(r.get('Quantity') or 0.0)
                preview_items.append({
                    "description": desc,
                    "unit_price": round(unit, 2),
                    "quantity": qty,
                    "final": round(unit * qty, 2),
                })

        # Additional totals from aggregator
        add_total = float(agg[agg['Type'] == 'additional']['Final Price (GBP)'].sum()) if agg is not None and not agg.empty else 0.0

        # Expenses from aggregator (ABZ data)
        exp_total_abz = float(agg[agg['Type'] == 'expenses']['Final Price (GBP)'].sum()) if agg is not None and not agg.empty else 0.0

        # EXPENSES: Prefer AN-FIN data, but fallback to ABZ if AN-FIN not available
        exp_total = 0.0
        exp_source = "none"

        # Try AN-FIN first (most reliable)
        if costs_gbp:
            if name in costs_gbp:
                exp_total = costs_gbp[name]
                exp_source = "AN-FIN (exact match)"
                print(f"[DEBUG] {name} - Expenses from AN-FIN (exact match): £{exp_total:.2f}")
            else:
                # Try fuzzy match by first name
                for k, v in costs_gbp.items():
                    if k.lower().split()[0] == name.lower().split()[0]:
                        exp_total = v
                        exp_source = f"AN-FIN (fuzzy match '{k}')"
                        print(f"[DEBUG] {name} - Expenses from AN-FIN (fuzzy match '{k}'): £{exp_total:.2f}")
                        break

        # Fallback to ABZ Expenses from aggregator if AN-FIN not available or no match found
        if exp_total == 0.0 and exp_total_abz > 0:
            exp_total = exp_total_abz
            exp_source = "ABZ Charge Rate (aggregator)"
            print(f"[DEBUG] {name} - Expenses from ABZ (fallback): £{exp_total:.2f}")
        elif exp_total == 0.0:
            print(f"[DEBUG] {name} - No expenses found in AN-FIN or ABZ")

        print(f"[DEBUG] {name} - From aggregator: Additional={add_total}")

        # Fallback for Additional from raw ABZ data
        try:
            if (not add_total or abs(add_total) <= 1e-6) and 'Brazilian Payroll Additionals (GBP)' in sub.columns:
                add_total = float(sub['Brazilian Payroll Additionals (GBP)'].fillna(0).sum())
                print(f"[DEBUG] {name} - Additional from raw ABZ data: {add_total}")
        except Exception as e:
            print(f"[DEBUG] {name} - Error in Additional fallback calculation: {e}")

        print(f"[DEBUG] Final totals for {name}: Additional={add_total}, Expenses={exp_total}")

        # Adicionar Additional apenas se > 0
        if add_total and abs(add_total) > 1e-6:
            print(f"[DEBUG] {name} - Adding Additional: £{round(add_total, 2)}")
            preview_items.append({"description": "Brazilian Payroll Additional", "final": round(add_total, 2)})
        else:
            print(f"[DEBUG] {name} - Skipping Additional (value: {add_total})")

        # Adicionar Expenses apenas se > 0
        if exp_total and abs(exp_total) > 1e-6:
            print(f"[DEBUG] {name} - Adding Expenses: £{round(exp_total, 2)}")
            preview_items.append({"description": "Expenses", "final": round(exp_total, 2)})
        else:
            print(f"[DEBUG] {name} - Skipping Expenses (value: {exp_total})")

        preview[name] = {
            "items": preview_items,
            "meta": meta,
        }
    wb.close()
    return preview


def _build_preview(abz: Path, anfin: Path) -> Dict[str, Dict]:
    """Legacy function for backward compatibility - delegates to single file version with AN-FIN."""
    return _build_preview_single_file(abz, anfin)


@app.post("/api/import")
async def api_import(
    abz: UploadFile = File(...),
    anfin: UploadFile = File(None),
    current_user: AuthUser = Depends(get_current_user)
):
    """Import ABZ file and optionally AN-FIN file for expenses data (requires authentication).

    IMPORTANT: If AN-FIN is not provided, all expenses will be £0.00.
    The Expenses column in ABZ is unreliable and will be ignored.
    """
    print(f"[DEBUG] Starting import process")
    print(f"[DEBUG] Uploaded ABZ file: {abz.filename}")
    print(f"[DEBUG] ABZ file size: {abz.size} bytes")

    sid = uuid.uuid4().hex
    sdir = SESSIONS / sid
    sdir.mkdir(parents=True, exist_ok=True)

    print(f"[DEBUG] Created session: {sid}")
    print(f"[DEBUG] Session directory: {sdir}")

    abz_path = _save_upload(sdir / abz.filename, abz)
    print(f"[DEBUG] ABZ file saved to: {abz_path}")
    print(f"[DEBUG] Saved file exists: {abz_path.exists()}")

    # Validate that the ABZ file has the required "Charge Rate" sheet
    try:
        from openpyxl import load_workbook
        wb = load_workbook(abz_path, read_only=True)
        sheets = wb.sheetnames
        wb.close()

        if "Charge Rate" not in sheets:
            print(f"[ERROR] File does not contain 'Charge Rate' sheet. Available sheets: {sheets}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid ABZ file: Missing 'Charge Rate' sheet. This file appears to be an AN-FIN file or has incorrect format. Available sheets: {', '.join(sheets)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to validate ABZ file: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read ABZ file: {str(e)}"
        )

    # Handle optional AN-FIN file
    anfin_path = None
    if anfin and anfin.filename:
        anfin_path = _save_upload(sdir / anfin.filename, anfin)
        print(f"[DEBUG] AN-FIN file uploaded: {anfin.filename}")
        print(f"[DEBUG] AN-FIN file saved to: {anfin_path}")
    else:
        print(f"[DEBUG] ⚠️  No AN-FIN file provided - all expenses will be £0.00")

    preview = _build_preview_single_file(abz_path, anfin_path)
    print(f"[DEBUG] Preview generated with {len(preview)} employees")

    meta_data = {
        "abz": abz.filename,  # Store relative filename, not full path
        "preview": preview,
    }
    if anfin_path:
        meta_data["anfin"] = anfin.filename

    (sdir / "meta.json").write_text(
        json.dumps(meta_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"[DEBUG] Meta.json saved successfully")
    print(f"[DEBUG] Returning session_id: {sid} with employees: {list(preview.keys())}")

    return {"session_id": sid, "employees": list(preview.keys())}


@app.post("/api/import-legacy")
async def api_import_legacy(
    abz: UploadFile = File(...),
    anfin: UploadFile = File(...),
    current_user: AuthUser = Depends(get_current_user)
):
    """Legacy endpoint for backward compatibility with two files (requires authentication)."""
    sid = uuid.uuid4().hex
    sdir = SESSIONS / sid
    sdir.mkdir(parents=True, exist_ok=True)

    abz_path = _save_upload(sdir / abz.filename, abz)
    anfin_path = _save_upload(sdir / anfin.filename, anfin)

    preview = _build_preview(abz_path, anfin_path)

    (sdir / "meta.json").write_text(
        json.dumps({
            "abz": abz.filename,  # Store relative filename, not full path
            "anfin": anfin.filename,  # Store relative filename, not full path
            "preview": preview,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return {"session_id": sid, "employees": list(preview.keys())}


@app.get("/api/preview")
async def api_preview(
    session_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get preview data for a session (requires authentication)"""
    sdir = SESSIONS / session_id
    meta_f = sdir / "meta.json"
    if not meta_f.exists():
        raise HTTPException(404, "session not found")
    meta = _read_json(meta_f)
    return {"session_id": session_id, "preview": meta.get("preview", {})}



@app.get("/api/progress")
async def api_progress(
    session_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get generation progress for a session (requires authentication)"""
    sdir = SESSIONS / session_id
    p = _progress_path(sdir)
    if not p.exists():
        return {"session_id": session_id, "stage": "idle", "percent": 0, "done": False}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        data = {"stage": "unknown", "percent": 0}
    data["session_id"] = session_id
    return data

@app.post("/api/generate")
async def api_generate(
    payload: Dict[str, Any] = Body(...),
    current_user: AuthUser = Depends(get_current_user)
):
    """Start asynchronous invoice generation (requires authentication)
    Accepts a generic JSON body to avoid Pydantic validation issues from the UI structure.
    """
    import asyncio
    import threading
    import traceback

    try:
        # Normalize request
        req = _GenReq(payload or {})
        if not req.session_id:
            return JSONResponse(status_code=400, content={"detail": "session_id inválido"})

        sdir = SESSIONS / req.session_id
        meta_f = sdir / "meta.json"
        if not meta_f.exists():
            return JSONResponse(status_code=404, content={"detail": "session não encontrada"})

        # Start generation in background thread
        def run_generation():
            try:
                # Call the existing PDF generation logic
                asyncio.run(api_generate_pdf_internal(req))
            except Exception as e:
                # Log full traceback to help debugging instead of failing silently
                print("[api_generate] Background generation error:\n" + traceback.format_exc())
                # Update progress with error
                progress_f = sdir / "progress.json"
                progress_data = {
                    "stage": "Erro na geração",
                    "percent": 0,
                    "current": 0,
                    "total": 0,
                    "warnings": [str(e)]
                }
                try:
                    progress_f.write_text(json.dumps(progress_data, ensure_ascii=False), encoding="utf-8")
                except Exception:
                    pass

        # Start background thread
        thread = threading.Thread(target=run_generation, name=f"gen-{req.session_id[:8]}")
        thread.daemon = True
        thread.start()

        # Return immediately with session info
        return {
            "session_id": req.session_id,
            "status": "started",
            "message": "Generation started in background"
        }

    except HTTPException as he:
        # Preserve HTTPException codes
        return JSONResponse(status_code=he.status_code, content={"detail": he.detail})
    except Exception as e:
        # Avoid raw 500 without message; surface the reason
        print("[api_generate] Error starting generation:", e)
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.post("/api/generate/pdf")
async def api_generate_pdf(
    payload: Dict[str, Any] = Body(...),
    current_user: AuthUser = Depends(get_current_user)
):
    """Legacy endpoint - redirects to new async endpoint (requires authentication)"""
    return await api_generate(payload, current_user)

async def api_generate_pdf_internal(req):
    # CRITICAL DEBUG: Log function entry
    with open("debug_log.txt", "a", encoding="utf-8") as f:
        f.write(f"🚀 CRITICAL: api_generate_pdf_internal called with session_id: {req.session_id}\n")

    sdir = SESSIONS / req.session_id
    meta_f = sdir / "meta.json"
    if not meta_f.exists():
        raise HTTPException(404, "session not found")
    meta = _read_json(meta_f)

    # First, get the uploaded ABZ file path (absolute path)
    uploaded_abz_path = sdir / meta["abz"]
    abz = uploaded_abz_path

    # Check if this is a session with anfin file
    anfin_path = None
    if "anfin" in meta:
        anfin_path = sdir / meta["anfin"]  # Make anfin absolute
        print(f"[DEBUG] Session has AN-FIN file: {anfin_path}")
        preview = meta.get("preview") or _build_preview(uploaded_abz_path, anfin_path)
    else:
        print(f"[DEBUG] ⚠️  Session has no AN-FIN file - expenses will be £0.00")
        preview = meta.get("preview") or _build_preview_single_file(uploaded_abz_path, None)

    # Check if the uploaded file has invoice templates
    from openpyxl import load_workbook
    try:
        wb = load_workbook(abz, read_only=True)
        sheets = wb.sheetnames
        invoice_sheets = [s for s in sheets if s.lower().strip().endswith('_invoice')]
        wb.close()

        if not invoice_sheets:
            # No templates in uploaded file - will use default template
            print(f"🔧 Uploaded file has no invoice templates, will use default template")
        else:
            print(f"📋 Using uploaded ABZ file with {len(invoice_sheets)} invoice templates")

    except Exception as e:
        print(f"⚠️ Error checking uploaded file: {e}")
        print("🔧 Will proceed with default template")

    from openpyxl import load_workbook
    wb = load_workbook(abz, read_only=True)
    sheets = wb.sheetnames

    xlsx_dir = sdir / "xlsx"
    pdf_dir = sdir / "pdf"
    xlsx_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)

    produced: List[Dict] = []
    warnings: List[str] = []

    total = len(preview)
    _update_progress(sdir, stage="Iniciando geração…", current=0, total=total, percent=0, done=False, warnings=[])

    # Ensure LibreOffice, with live progress
    soffice = ensure_libreoffice(auto_install=True, progress_cb=lambda msg: _update_progress(sdir, stage=msg))
    print(f"🔍 DEBUG: LibreOffice detection result: {soffice}")
    with open("debug_log.txt", "a", encoding="utf-8") as f:
        f.write(f"🔍 DEBUG: LibreOffice detection result: {soffice}\n")
    if not soffice:
        warnings.append("LibreOffice não encontrado; PDFs não serão gerados (tentativa de instalação pode ter falhado).")
        print(f"⚠️ WARNING: LibreOffice not found, PDFs will not be generated")
        with open("debug_log.txt", "a", encoding="utf-8") as f:
            f.write(f"⚠️ WARNING: LibreOffice not found, PDFs will not be generated\n")

    i = 0
    invoice_sheets = [s for s in sheets if s.lower().strip().endswith('_invoice')]

    # Invoice number sequencing (persistent)
    seq = _seq_read()
    last_used = int(seq.get("last", 0) or 0)

    # Check if user provided a manual invoice number
    manual_invoice_no = None
    if req.invoice_no is not None:
        manual_str = str(req.invoice_no).strip()
        if manual_str.isdigit():
            manual_invoice_no = int(manual_str)

    # If manual number provided, use it as base; otherwise continue sequence
    start_no = manual_invoice_no if manual_invoice_no is not None else (last_used + 1)
    assigned = 0

    print(f"🔍 Starting generation for {total} employees")
    print(f"📋 Invoice sheets available: {invoice_sheets}")

    for name, pdata in preview.items():
        i += 1
        print(f"🔄 Processing {i}/{total}: {name}")
        print(f"🔍 DEBUG: Starting processing for employee: {name}")
        _update_progress(sdir, stage=f"Gerando {i}/{total} – {name}", current=i, total=total, percent=int(i*100/total))

        tpl = _find_template_for_employee(name, invoice_sheets)
        use_default_template = False

        if not tpl:
            # No template found in ABZ file - use default template
            use_default_template = True
            tpl = "default_template"  # placeholder name for default template
            print(f"🔧 No template found for {name}, using default template")
        else:
            print(f"📋 Using ABZ template: {tpl} for {name}")

        # Check if employee has data to process
        items = list(pdata.get("items") or [])
        print(f"📊 Employee {name} has {len(items)} line items")

        # merge meta: request overrides > preview meta
        m = dict(pdata.get("meta") or {})
        if req.invoice_date is not None:
            m["invoice_date"] = req.invoice_date
        if req.invoice_no is not None:
            m["invoice_no"] = req.invoice_no
        # Only set call_off if it has meaningful content
        if req.call_off is not None:
            co_str = str(req.call_off).strip()
            if co_str and co_str.lower() not in ('none', 'null', 'n/a', 'nan', '-', ''):
                m["call_off"] = co_str
            else:
                m["call_off"] = None

        # items (now may include multiple service lines)
        items = list(pdata.get("items") or [])
        # apply overrides if present (backward compatible + per-line)
        ov = (req.overrides or {}).get(name)
        try:
            # Per-employee Call-Off override (applies to invoice header)
            if isinstance(ov, dict) and "call_off" in ov:
                co = str(ov.get("call_off") or "").strip()
                m["call_off"] = co if co else None

            # Per-employee Additional override
            if isinstance(ov, dict) and "additional" in ov:
                additional_override = float(ov.get("additional"))
                print(f"[DEBUG] {name} - Applying Additional override: £{additional_override:.2f}")

                # Find existing Additional item
                additional_idx = None
                for idx, item in enumerate(items):
                    if item.get("description") == "Brazilian Payroll Additional":
                        additional_idx = idx
                        break

                if additional_override > 0:
                    if additional_idx is not None:
                        # Update existing Additional item
                        items[additional_idx]["final"] = round(additional_override, 2)
                        print(f"[DEBUG] {name} - Updated existing Additional item to £{additional_override:.2f}")
                    else:
                        # Create new Additional item
                        items.append({
                            "description": "Brazilian Payroll Additional",
                            "final": round(additional_override, 2)
                        })
                        print(f"[DEBUG] {name} - Created new Additional item: £{additional_override:.2f}")
                else:
                    # Remove Additional item if override is 0
                    if additional_idx is not None:
                        items.pop(additional_idx)
                        print(f"[DEBUG] {name} - Removed Additional item (override = 0)")

            # Per-employee Expenses override
            if isinstance(ov, dict) and "expenses" in ov:
                expenses_override = float(ov.get("expenses"))
                print(f"[DEBUG] {name} - Applying Expenses override: £{expenses_override:.2f}")

                # Find existing Expenses item
                expenses_idx = None
                for idx, item in enumerate(items):
                    if item.get("description") == "Expenses":
                        expenses_idx = idx
                        break

                if expenses_override > 0:
                    if expenses_idx is not None:
                        # Update existing Expenses item
                        items[expenses_idx]["final"] = round(expenses_override, 2)
                        print(f"[DEBUG] {name} - Updated existing Expenses item to £{expenses_override:.2f}")
                    else:
                        # Create new Expenses item
                        items.append({
                            "description": "Expenses",
                            "final": round(expenses_override, 2)
                        })
                        print(f"[DEBUG] {name} - Created new Expenses item: £{expenses_override:.2f}")
                else:
                    # Remove Expenses item if override is 0
                    if expenses_idx is not None:
                        items.pop(expenses_idx)
                        print(f"[DEBUG] {name} - Removed Expenses item (override = 0)")

            # Backward compatible dict form -> apply to first service line
            if isinstance(ov, dict) and items:
                if "quantity" in ov:
                    q = float(ov["quantity"])
                    items[0]["quantity"] = q
                    unit = float(items[0].get("unit_price") or 0.0)
                    items[0]["final"] = round(unit * q, 2)
                if "unit_price" in ov:
                    u = float(ov["unit_price"])
                    items[0]["unit_price"] = round(u, 2)
                    q = float(items[0].get("quantity") or 0.0)
                    items[0]["final"] = round(items[0]["unit_price"] * q, 2)

                # Support web UI nested format: ov = { overrides: { lineIdx: {quantity?, unit_price?}, ... } }
                if isinstance(ov.get('overrides'), dict):
                    for k_line, ent in ov['overrides'].items():
                        try:
                            idx = int(k_line)
                        except Exception:
                            continue
                        if 0 <= idx < len(items) and isinstance(ent, dict):
                            if "quantity" in ent:
                                q = float(ent["quantity"])
                                items[idx]["quantity"] = q
                                unit = float(items[idx].get("unit_price") or 0.0)
                                items[idx]["final"] = round(unit * q, 2)
                            if "unit_price" in ent:
                                u = float(ent["unit_price"])
                                items[idx]["unit_price"] = round(u, 2)
                                q = float(items[idx].get("quantity") or 0.0)
                                items[idx]["final"] = round(items[idx]["unit_price"] * q, 2)

            # New list form -> [{line, quantity?, unit_price?}, ...] and optional per-entry call_off
            elif isinstance(ov, list):
                for ent in ov:
                    # Per-entry call_off override
                    if isinstance(ent, dict) and "call_off" in ent:
                        co = str(ent.get("call_off") or "").strip()
                        m["call_off"] = co if co else None
                        continue
                    try:
                        idx = int(ent.get("line", -1))
                    except Exception:
                        idx = -1
                    if 0 <= idx < len(items):
                        if "quantity" in ent:
                            q = float(ent["quantity"])
                            items[idx]["quantity"] = q
                            unit = float(items[idx].get("unit_price") or 0.0)
                            items[idx]["final"] = round(unit * q, 2)
                        if "unit_price" in ent:
                            u = float(ent["unit_price"])
                            items[idx]["unit_price"] = round(u, 2)
                            q = float(items[idx].get("quantity") or 0.0)
                            items[idx]["final"] = round(items[idx]["unit_price"] * q, 2)
        except Exception:
            pass

        # Assign sequential invoice number for this employee
        assigned += 1
        m["invoice_no"] = str(start_no + assigned - 1)

        # Format display invoice number as zero-padded + '/YYYY'
        try:
            import re
            # Year from invoice_date if present; otherwise current year
            year_str = None
            if isinstance(req.invoice_date, str) and req.invoice_date.strip():
                mm = re.search(r"(\d{4})", req.invoice_date)
                if mm:
                    year_str = mm.group(1)
            if not year_str:
                year_str = str(dt.datetime.now().year)
            # Determine padding width: at least 7, or respect digits typed by user
            input_no = str(req.invoice_no).strip() if req.invoice_no is not None else ''
            digit_seq = ''.join(ch for ch in input_no if ch.isdigit())
            pad_width = max(7, len(digit_seq))
            padded_no = str(m.get('invoice_no')).zfill(pad_width)
            display_inv_no = f"{padded_no}/{year_str}"
        except Exception:
            display_inv_no = str(m.get('invoice_no'))

        # Generate single-sheet XLSX from template
        # Use template-based generator by default for better formatting
        xlsx_path = generate_from_abz_template(
            abz_xlsx=abz,
            template_sheet_name=tpl,
            employee_name=name,
            line_items=items,
            out_dir=xlsx_dir,
            invoice_date=m.get("invoice_date"),
            invoice_no=display_inv_no,
            call_off=m.get("call_off"),
            use_default_template=use_default_template,
            use_template_based=True,  # Use the new template-based generator
        )

        print(f"✅ XLSX generated successfully for {name}: {xlsx_path}")

        # Write to log file for debugging
        with open("debug_log.txt", "a", encoding="utf-8") as f:
            f.write(f"✅ XLSX generated successfully for {name}: {xlsx_path}\n")

        # Save invoice to database - DETAILED DEBUG VERSION
        # Generate PDF first (before saving to database)
        pdf_path = pdf_dir / (xlsx_path.stem + ".pdf")
        url_xlsx = f"/api/session/{req.session_id}/file/{xlsx_path.name}"
        url_pdf = None

        print(f"🔍 DEBUG: About to generate PDF for {name}")
        print(f"🔍 DEBUG: soffice = {soffice}")
        print(f"🔍 DEBUG: xlsx_path = {xlsx_path}")
        print(f"🔍 DEBUG: pdf_path = {pdf_path}")
        with open("debug_log.txt", "a", encoding="utf-8") as f:
            f.write(f"🔍 DEBUG: About to generate PDF for {name}\n")
            f.write(f"🔍 DEBUG: soffice = {soffice}\n")
            f.write(f"🔍 DEBUG: xlsx_path = {xlsx_path}\n")
            f.write(f"🔍 DEBUG: pdf_path = {pdf_path}\n")

        if soffice:
            try:
                _update_progress(sdir, stage=f"Convertendo PDF – {name}")
                print(f"🔄 Calling xlsx_to_pdf...")
                xlsx_to_pdf(xlsx_path, pdf_path, soffice_path=soffice)
                print(f"🔍 DEBUG: After xlsx_to_pdf, checking if PDF exists...")
                if pdf_path.exists():
                    url_pdf = f"/api/session/{req.session_id}/file/{pdf_path.name}"
                    print(f"✅ PDF generated: {pdf_path}")
                    with open("debug_log.txt", "a", encoding="utf-8") as f:
                        f.write(f"✅ PDF generated: {pdf_path}\n")
                else:
                    print(f"⚠️ PDF file does not exist after conversion: {pdf_path}")
                    with open("debug_log.txt", "a", encoding="utf-8") as f:
                        f.write(f"⚠️ PDF file does not exist after conversion: {pdf_path}\n")
            except Exception as e:
                warnings.append(f"Falha ao converter PDF de {name}: {e}")
                _update_progress(sdir, warnings=warnings)
                print(f"⚠️ PDF generation failed for {name}: {e}")
                with open("debug_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"⚠️ PDF generation failed for {name}: {e}\n")
                import traceback
                print(f"📋 Full traceback: {traceback.format_exc()}")
                with open("debug_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"📋 Full traceback: {traceback.format_exc()}\n")
        else:
            print(f"⚠️ Skipping PDF generation because soffice is None")
            with open("debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"⚠️ Skipping PDF generation because soffice is None\n")

        # Now save to database with PDF path
        try:
            with open("debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"🔄 DEBUG: Attempting to save invoice to database for {name}...\n")

            # Simple calculation
            total_amount = sum(float(item.get("final", 0)) for item in items)

            with open("debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"📊 DEBUG: Calculated total amount: £{total_amount:.2f}\n")

            # Simple database save with PDF path
            db = next(get_db())

            # Check if PDF exists before saving
            pdf_exists = pdf_path.exists()
            print(f"🔍 DEBUG: Before saving to DB - pdf_path.exists() = {pdf_exists}")
            print(f"🔍 DEBUG: pdf_path = {pdf_path}")
            with open("debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"🔍 DEBUG: Before saving to DB - pdf_path.exists() = {pdf_exists}\n")
                f.write(f"🔍 DEBUG: pdf_path = {pdf_path}\n")

            invoice_data = {
                "company_id": 1,
                "invoice_number": display_inv_no,
                "employee_name": name,
                "employee_position": "Data Processor",
                "invoice_date": dt.date.today(),
                "total_amount": total_amount,
                "file_path_xlsx": str(xlsx_path),
                "file_path_pdf": str(pdf_path) if pdf_exists else None,
                "session_id": req.session_id
            }

            with open("debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"💾 DEBUG: Invoice data to save: {invoice_data}\n")
                f.write(f"📄 DEBUG: PDF path: {invoice_data['file_path_pdf']}\n")
                f.write(f"📄 DEBUG: PDF exists: {pdf_exists}\n")

            created_invoice = InvoiceService.create_invoice(db, invoice_data)

            with open("debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"✅ DEBUG: Successfully saved invoice to database: {display_inv_no} for {name} (£{total_amount:.2f})\n")
                if invoice_data['file_path_pdf']:
                    f.write(f"📄 DEBUG: PDF saved in database: {invoice_data['file_path_pdf']}\n")

        except BaseException as e:
            print(f"❌ Error saving invoice to database for {name}: {e}")
            with open("debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"❌ Error saving invoice to database for {name}: {e}\n")
            import traceback
            print(f"📋 Full traceback: {traceback.format_exc()}")
            with open("debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"📋 Full traceback: {traceback.format_exc()}\n")
            # Don't fail the generation if database save fails
            pass
        produced.append({
            "name": name,
            "xlsx": str(xlsx_path),
            "pdf": str(pdf_path) if pdf_path.exists() else None,
            "url_xlsx": url_xlsx,
            "url_pdf": url_pdf,
        })

    # Persist the last used invoice number
    try:
        if assigned > 0:
            final_invoice_no = start_no + assigned - 1
            _seq_write(final_invoice_no)
            print(f"💾 Saved last invoice number: {final_invoice_no}")
    except Exception:
        pass

    wb.close()
    _update_progress(sdir, stage="Concluído", percent=100, done=True, warnings=warnings)
    return {"session_id": req.session_id, "files": produced, "warnings": warnings}


@app.get("/api/session/{session_id}/files")
async def api_session_files(
    session_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get list of generated files for a session (requires authentication)"""
    sdir = SESSIONS / session_id
    if not sdir.exists():
        raise HTTPException(404, "session not found")

    meta_f = sdir / "meta.json"
    if not meta_f.exists():
        raise HTTPException(404, "session metadata not found")

    meta = _read_json(meta_f)
    files = []

    # Check for generated files
    xlsx_dir = sdir / "xlsx"
    pdf_dir = sdir / "pdf"

    if xlsx_dir.exists() or pdf_dir.exists():
        # Get all xlsx files
        xlsx_files = list(xlsx_dir.glob("*.xlsx")) if xlsx_dir.exists() else []
        pdf_files = list(pdf_dir.glob("*.pdf")) if pdf_dir.exists() else []

        # Create a map of employee names to files
        employee_files = {}

        # Process xlsx files
        for xlsx_file in xlsx_files:
            # Extract employee name from filename (format: "ABZ Group 0001001-2025 OMEGA 09 2025 Bárbara.xlsx")
            # The employee name is the last part after the last space
            filename_parts = xlsx_file.stem.split(' ')
            if len(filename_parts) >= 1:
                emp_name = filename_parts[-1]  # Last part is the employee name
                if emp_name not in employee_files:
                    employee_files[emp_name] = {"name": emp_name}
                employee_files[emp_name]["url_xlsx"] = f"/api/session/{session_id}/file/{xlsx_file.name}"

        # Process pdf files
        for pdf_file in pdf_files:
            # Extract employee name from filename (format: "ABZ Group 0001001-2025 OMEGA 09 2025 Bárbara.pdf")
            # The employee name is the last part after the last space
            filename_parts = pdf_file.stem.split(' ')
            if len(filename_parts) >= 1:
                emp_name = filename_parts[-1]  # Last part is the employee name
                if emp_name not in employee_files:
                    employee_files[emp_name] = {"name": emp_name}
                employee_files[emp_name]["url_pdf"] = f"/api/session/{session_id}/file/{pdf_file.name}"

        files = list(employee_files.values())

    return {
        "session_id": session_id,
        "files": files
    }


@app.get("/api/session/{session_id}/file/{filename}")
async def api_session_file(
    session_id: str,
    filename: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Serve individual files from a session (requires authentication)"""
    sdir = SESSIONS / session_id
    if not sdir.exists():
        raise HTTPException(404, "session not found")

    # Check in both xlsx and pdf directories
    file_path = None
    media_type = "application/octet-stream"

    if filename.endswith('.xlsx'):
        xlsx_path = sdir / "xlsx" / filename
        if xlsx_path.exists():
            file_path = xlsx_path
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.endswith('.pdf'):
        pdf_path = sdir / "pdf" / filename
        if pdf_path.exists():
            file_path = pdf_path
            media_type = "application/pdf"

    if not file_path:
        raise HTTPException(404, "file not found")

    from fastapi.responses import FileResponse
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media_type
    )


@app.get("/api/session/{session_id}/zip")
async def api_session_zip(
    session_id: str,
    kind: str = "pdf",
    current_user: AuthUser = Depends(get_current_user)
):
    sdir = SESSIONS / session_id
    if not sdir.exists():
        raise HTTPException(404, "session not found")
    kinds = {"pdf", "xlsx", "all"}
    if kind not in kinds:
        raise HTTPException(400, f"kind must be one of {kinds}")

    files: List[Path] = []
    if kind in ("pdf", "all") and (sdir / "pdf").exists():
        files += sorted((sdir / "pdf").glob("*.pdf"))
    if kind in ("xlsx", "all") and (sdir / "xlsx").exists():
        files += sorted((sdir / "xlsx").glob("*.xlsx"))

    if not files:
        raise HTTPException(404, f"no files for kind={kind}")

    zip_path = sdir / f"session_{session_id}_{kind}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, arcname=f.name)
    return FileResponse(str(zip_path), media_type="application/zip", filename=zip_path.name)


@app.get("/api/invoice-seq")
async def api_invoice_seq():
    data = _seq_read()
    return {"last": int(data.get("last", 0) or 0)}


# History and Configuration endpoints
@app.get("/api/invoices/stats")
async def get_invoice_stats(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get invoice statistics for dashboard (requires authentication)"""
    try:
        print("📊 Getting invoice statistics from database...")

        # Get database session
        db = next(get_db())

        # Get statistics from database (correct method name)
        stats = InvoiceService.get_invoice_stats(db, company_id=1)

        print(f"📈 Database stats: {stats}")

        # Calculate pending invoices from status breakdown
        status_breakdown = stats.get('status_breakdown', {})
        pending_invoices = status_breakdown.get('pending', 0) + status_breakdown.get('draft', 0)

        return {
            "total_invoices": stats.get('total_invoices', 0),
            "total_amount": stats.get('total_amount', 0.0),
            "current_month_amount": stats.get('current_month_amount', 0.0),
            "last_month_amount": stats.get('last_month_amount', 0.0),
            "recent_invoices": stats.get('recent_invoices', 0),
            "pending_invoices": pending_invoices,
            "status_breakdown": status_breakdown,
            "success_rate": 100  # All database invoices are considered successful
        }

    except Exception as e:
        print(f"❌ Error getting stats from database: {e}")
        import traceback
        print(f"📋 Full traceback: {traceback.format_exc()}")

        # Fallback to file-based system
        print("🔄 Falling back to file-based stats...")
        try:
            # Count sessions with generated invoices
            total_sessions = len([d for d in SESSIONS.iterdir() if d.is_dir()])

            # Count total generated files
            total_invoices = 0
            total_pdfs = 0
            for session_dir in SESSIONS.iterdir():
                if session_dir.is_dir():
                    xlsx_dir = session_dir / "xlsx"
                    pdf_dir = session_dir / "pdf"
                    if xlsx_dir.exists():
                        total_invoices += len(list(xlsx_dir.glob("*.xlsx")))
                    if pdf_dir.exists():
                        total_pdfs += len(list(pdf_dir.glob("*.pdf")))

            return {
                "total_invoices": total_invoices,
                "total_amount": 0.0,
                "recent_invoices": 0,
                "pending_invoices": 0,
                "success_rate": round((total_pdfs / max(total_invoices, 1)) * 100, 1)
            }
        except Exception as fallback_error:
            print(f"❌ Fallback stats also failed: {fallback_error}")
            return {
                "total_invoices": 0,
                "total_amount": 0.0,
                "recent_invoices": 0,
                "pending_invoices": 0,
                "success_rate": 0
            }


@app.get("/api/invoices/{invoice_id}/download")
async def download_invoice(
    invoice_id: int,
    current_user: AuthUser = Depends(get_current_user)
):
    """Download invoice XLSX file (requires authentication)"""
    try:
        print(f"📥 Downloading invoice {invoice_id}")

        # Get database session
        db = next(get_db())

        # Get invoice from database
        invoice = InvoiceService.get_invoice_by_id(db, invoice_id, company_id=1)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Try to find the file
        file_path = Path(invoice.file_path_xlsx)
        if not file_path.exists():
            # Try relative to current working directory
            file_path = Path.cwd() / invoice.file_path_xlsx
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Invoice file not found on disk")

        print(f"✅ Serving file: {file_path}")

        return FileResponse(
            path=str(file_path),
            filename=f"{invoice.employee_name.replace(' ', '_')}_Invoice_{invoice.invoice_number}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error downloading invoice: {e}")
        import traceback
        print(f"📋 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@app.get("/api/invoices/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: int,
    current_user: AuthUser = Depends(get_current_user)
):
    """Download or view invoice PDF file (requires authentication)"""
    try:
        print(f"📄 Getting PDF for invoice {invoice_id}")

        # Get database session
        db = next(get_db())

        # Get invoice from database
        invoice = InvoiceService.get_invoice_by_id(db, invoice_id, company_id=1)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        if not invoice.file_path_pdf:
            raise HTTPException(status_code=404, detail="PDF not generated for this invoice")

        # Try to find the PDF file
        pdf_path = Path(invoice.file_path_pdf)
        if not pdf_path.exists():
            # Try relative to current working directory
            pdf_path = Path.cwd() / invoice.file_path_pdf
            if not pdf_path.exists():
                raise HTTPException(status_code=404, detail="PDF file not found on disk")

        print(f"✅ Serving PDF: {pdf_path}")

        return FileResponse(
            path=str(pdf_path),
            filename=f"{invoice.employee_name.replace(' ', '_')}_Invoice_{invoice.invoice_number}.pdf",
            media_type="application/pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting PDF: {e}")
        import traceback
        print(f"📋 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"PDF download failed: {str(e)}")


@app.get("/api/invoices/{invoice_id}/view")
async def view_invoice(
    invoice_id: int,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get invoice details for viewing with service lines (requires authentication)"""
    try:
        print(f"👁️ Viewing invoice {invoice_id}")

        # Get database session
        db = next(get_db())

        # Get invoice from database
        invoice = InvoiceService.get_invoice_by_id(db, invoice_id, company_id=1)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Check if file exists
        file_path = Path(invoice.file_path_xlsx)
        file_exists = file_path.exists()
        if not file_exists:
            file_path = Path.cwd() / invoice.file_path_xlsx
            file_exists = file_path.exists()

        # Extract service lines from Excel if file exists
        service_lines = []
        additional_total = 0.0
        expenses_total = 0.0

        if file_exists:
            try:
                from openpyxl import load_workbook
                wb = load_workbook(file_path, data_only=True)

                # Find the invoice sheet (usually the first or named after employee)
                sheet_name = None
                for sn in wb.sheetnames:
                    if 'invoice' in sn.lower() or invoice.employee_name.lower() in sn.lower():
                        sheet_name = sn
                        break
                if not sheet_name:
                    sheet_name = wb.sheetnames[0]

                ws = wb[sheet_name]

                # Find the service table headers
                from app.utils.excel_abz_template import find_invoice_table_coords
                coords = find_invoice_table_coords(file_path, sheet_name)

                if coords:
                    services_col = coords.get('services_col', 1)
                    unit_col = coords.get('unit_col', 2)
                    qty_col = coords.get('qty_col', 3)
                    final_col = coords.get('final_col', 4)
                    first_row = coords.get('first_data_row', 1)

                    # Read service lines
                    for row in range(first_row, first_row + 50):
                        desc = ws.cell(row=row, column=services_col).value
                        if not desc:
                            break

                        desc_str = str(desc).strip()
                        unit_val = ws.cell(row=row, column=unit_col).value
                        qty_val = ws.cell(row=row, column=qty_col).value
                        final_val = ws.cell(row=row, column=final_col).value

                        # Parse values
                        try:
                            unit_price = float(unit_val) if unit_val else None
                        except:
                            unit_price = None

                        try:
                            quantity = float(qty_val) if qty_val else None
                        except:
                            quantity = None

                        try:
                            final_price = float(final_val) if final_val else 0.0
                        except:
                            final_price = 0.0

                        # Categorize line
                        if 'additional' in desc_str.lower():
                            additional_total += final_price
                        elif 'expense' in desc_str.lower():
                            expenses_total += final_price
                        else:
                            service_lines.append({
                                'description': desc_str,
                                'unit_price': unit_price,
                                'quantity': quantity,
                                'final_price': final_price
                            })

                wb.close()
            except Exception as e:
                print(f"⚠️ Error reading invoice content: {e}")
                # Continue without service lines

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
            "file_exists": file_exists,
            "service_lines": service_lines,
            "additional_total": additional_total,
            "expenses_total": expenses_total
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error viewing invoice: {e}")
        import traceback
        print(f"📋 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"View failed: {str(e)}")


@app.put("/api/invoices/{invoice_id}/status")
async def update_invoice_status(
    invoice_id: int,
    status: str = Form(...),
    current_user: AuthUser = Depends(get_current_user)
):
    """Update invoice status (requires authentication)"""
    try:
        print(f"🔄 Updating invoice {invoice_id} status to: {status}")

        # Get database session
        db = next(get_db())

        # Update status
        invoice = InvoiceService.update_invoice_status(db, invoice_id, company_id=1, status=status)

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        print(f"✅ Invoice status updated successfully")

        return {
            "success": True,
            "message": "Status updated successfully",
            "invoice": {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "status": invoice.status
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating invoice status: {e}")
        import traceback
        print(f"📋 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Status update failed: {str(e)}")


@app.get("/api/invoices")
async def get_invoices(
    skip: int = 0,
    limit: int = 20,
    employee_name: str = None,
    status: str = None,
    date_from: str = None,
    date_to: str = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get paginated list of invoices from database (requires authentication)"""
    try:
        print(f"🔍 Getting invoices from database: skip={skip}, limit={limit}, employee_name={employee_name}, status={status}")

        # Get database session
        db = next(get_db())

        # Parse date filters if provided
        date_from_dt = None
        date_to_dt = None
        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from)
            except:
                pass
        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to)
            except:
                pass

        # Get invoices from database using the service (returns a List[Invoice])
        invoices_list = InvoiceService.get_invoices(
            db,
            company_id=1,  # Default company ID
            skip=skip,
            limit=limit,
            employee_name=employee_name,
            status=status,
            date_from=date_from_dt,
            date_to=date_to_dt
        )

        print(f"📊 Found {len(invoices_list)} invoices in database")

        # Get total count for pagination
        from app.database.models import Invoice as InvoiceModel
        total_query = db.query(InvoiceModel).filter(InvoiceModel.company_id == 1)
        if employee_name:
            total_query = total_query.filter(InvoiceModel.employee_name.ilike(f"%{employee_name}%"))
        if status:
            total_query = total_query.filter(InvoiceModel.status == status)
        if date_from_dt:
            total_query = total_query.filter(InvoiceModel.invoice_date >= date_from_dt)
        if date_to_dt:
            total_query = total_query.filter(InvoiceModel.invoice_date <= date_to_dt)
        total_count = total_query.count()

        # Convert database models to API response format
        formatted_invoices = []
        for invoice in invoices_list:
            # Format the invoice data for the frontend
            formatted_invoice = {
                "id": invoice.id,  # Keep as integer for JavaScript
                "invoice_number": invoice.invoice_number,
                "employee_name": invoice.employee_name,
                "employee_position": invoice.employee_position or "-",
                "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                "total_amount": float(invoice.total_amount) if invoice.total_amount else 0.0,
                "status": invoice.status or "generated",
                "session_id": invoice.session_id,
                "file_path_xlsx": invoice.file_path_xlsx,
                "file_path_pdf": invoice.file_path_pdf,
                "created_at": invoice.created_at.isoformat() if invoice.created_at else None,
                "updated_at": invoice.updated_at.isoformat() if invoice.updated_at else None,
                "currency": invoice.currency or "GBP"
            }
            formatted_invoices.append(formatted_invoice)

        print(f"✅ Successfully formatted {len(formatted_invoices)} invoices for API response")

        return {
            "invoices": formatted_invoices,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        print(f"❌ Error getting invoices from database: {e}")
        import traceback
        print(f"📋 Full traceback: {traceback.format_exc()}")

        # Fallback to old file-based system if database fails
        print("🔄 Falling back to file-based system...")
        try:
            invoices = []

            # Scan all sessions for generated invoices
            for session_dir in SESSIONS.iterdir():
                if not session_dir.is_dir():
                    continue

                session_id = session_dir.name
                xlsx_dir = session_dir / "xlsx"
                pdf_dir = session_dir / "pdf"

                if not xlsx_dir.exists():
                    continue

                # Get session metadata
                try:
                    progress_file = session_dir / "progress.json"
                    if progress_file.exists():
                        progress_data = _read_json(progress_file)
                        created_at = progress_data.get("created_at", "")
                    else:
                        created_at = ""
                except:
                    created_at = ""

                # List all xlsx files in this session
                for xlsx_file in xlsx_dir.glob("*.xlsx"):
                    employee_name = xlsx_file.stem
                    pdf_file = pdf_dir / f"{employee_name}.pdf"

                    invoices.append({
                        "id": f"{session_id}_{employee_name}",
                        "invoice_number": "undefined",
                        "session_id": session_id,
                        "employee_name": employee_name,
                        "employee_position": "-",
                        "invoice_date": None,
                        "total_amount": 0.0,
                        "status": "generated" if pdf_file.exists() else "pending",
                        "created_at": created_at,
                        "file_path_xlsx": str(xlsx_file),
                        "file_path_pdf": str(pdf_file) if pdf_file.exists() else None
                    })

            # Sort by creation date (newest first)
            invoices.sort(key=lambda x: x["created_at"], reverse=True)

            # Apply pagination
            total = len(invoices)
            paginated = invoices[skip:skip + limit]

            return {
                "invoices": paginated,
                "total": total,
                "skip": skip,
                "limit": limit
            }

        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            return {
                "invoices": [],
                "total": 0,
                "skip": skip,
                "limit": limit,
                "error": str(e)
            }


@app.get("/api/configurations")
async def get_configurations(
    config_type: str = "general",
    current_user: AuthUser = Depends(get_current_user)
):
    """Get configuration settings (requires authentication)"""
    config_file = Path("out/config.json")

    try:
        if config_file.exists():
            config_data = json.loads(config_file.read_text(encoding="utf-8"))
        else:
            config_data = {}

        # Default configurations
        defaults = {
            "general": {
                "company_name": "ABZ Group",
                "default_currency": "BRL",
                "date_format": "dd/mm/yyyy",
                "language": "pt-BR"
            },
            "email": {
                "smtp_server": "",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
                "from_email": "",
                "auto_send": False
            }
        }

        return config_data.get(config_type, defaults.get(config_type, {}))

    except Exception as e:
        # Return defaults on error
        defaults = {
            "general": {
                "company_name": "ABZ Group",
                "default_currency": "BRL",
                "date_format": "dd/mm/yyyy",
                "language": "pt-BR"
            },
            "email": {
                "smtp_server": "",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
                "from_email": "",
                "auto_send": False
            }
        }
        return defaults.get(config_type, {})


@app.post("/api/configurations")
async def save_configurations(
    config_type: str,
    config_data: dict,
    current_user: AuthUser = Depends(get_current_user)
):
    """Save configuration settings (requires authentication)"""
    config_file = Path("out/config.json")

    try:
        # Load existing config
        if config_file.exists():
            all_config = json.loads(config_file.read_text(encoding="utf-8"))
        else:
            all_config = {}

        # Update specific config type
        all_config[config_type] = config_data

        # Save back to file
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(json.dumps(all_config, indent=2), encoding="utf-8")

        return {"success": True, "message": "Configuration saved successfully"}

    except Exception as e:
        return {"success": False, "error": str(e)}


# Database reset endpoint
class ResetRequest(BaseModel):
    password: str

@app.post("/api/reset-database")
async def reset_database(
    request: ResetRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Reset all invoices and sessions - requires authentication and password

    This endpoint uses DROP/CREATE approach to avoid Windows file locking issues.
    It does NOT delete the database file, only clears and recreates the tables.
    """
    # Require Admin role for database reset (case-insensitive)
    if current_user and hasattr(current_user, 'role') and current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Only Admin users can reset the database")

    if request.password != "2122":
        raise HTTPException(status_code=403, detail="Invalid password")

    try:
        print("\n" + "="*60)
        print("🔄 DATABASE RESET STARTED")
        print("="*60)

        # Count items before deletion
        sessions_count = 0
        invoices_count = 0
        pdfs_count = 0
        db_invoices_count = 0
        db_sessions_count = 0

        # Count database records before reset
        db = next(get_db())
        try:
            from app.database.models import Invoice as InvoiceModel, Session as SessionModel, EmailLog
        except ImportError:
            from database.models import Invoice as InvoiceModel, Session as SessionModel, EmailLog

        db_invoices_count = db.query(InvoiceModel).count()
        db_sessions_count = db.query(SessionModel).count()
        print(f"📊 Database records: {db_invoices_count} invoices, {db_sessions_count} sessions")
        db.close()

        # Count file system items
        if SESSIONS.exists():
            for session_dir in SESSIONS.iterdir():
                if session_dir.is_dir():
                    sessions_count += 1
                    xlsx_dir = session_dir / "xlsx"
                    pdf_dir = session_dir / "pdf"
                    if xlsx_dir.exists():
                        invoices_count += len(list(xlsx_dir.glob("*.xlsx")))
                    if pdf_dir.exists():
                        pdfs_count += len(list(pdf_dir.glob("*.pdf")))

        print(f"📁 File system: {sessions_count} sessions, {invoices_count} invoices, {pdfs_count} PDFs")

        # Step 1: Create backup of database file
        import shutil
        from datetime import datetime
        db_path = Path("data/invoice_system.db")
        backup_path = None

        if db_path.exists():
            backup_path = Path(f"data/invoice_system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            try:
                shutil.copy(db_path, backup_path)
                print(f"📦 Database backed up to: {backup_path}")
            except Exception as backup_error:
                print(f"⚠️ Warning: Could not create backup: {backup_error}")
                backup_path = None

        # Step 2: Delete all session directories
        print("🗑️ Deleting session directories...")
        if SESSIONS.exists():
            try:
                shutil.rmtree(SESSIONS)
                SESSIONS.mkdir(parents=True, exist_ok=True)
                print(f"✅ Deleted {sessions_count} session directories")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete some session directories: {e}")

        # Step 3: Reset invoice sequence
        print("🔄 Resetting invoice sequence...")
        seq_file = Path("out/invoice_seq.json")
        if seq_file.exists():
            try:
                seq_file.unlink()
                print("✅ Invoice sequence reset")
            except Exception as e:
                print(f"⚠️ Warning: Could not reset invoice sequence: {e}")

        # Step 4: Reset database using DROP/CREATE approach (avoids file locking)
        print("🗑️ Resetting database tables...")
        try:
            from app.database.database import engine, init_database
            from app.database.models import Base

            # Dispose of all connections in the pool
            print("   Closing database connections...")
            engine.dispose()

            # Drop all tables
            print("   Dropping all tables...")
            Base.metadata.drop_all(bind=engine)
            print("   ✅ All tables dropped")

            # Recreate all tables
            print("   Creating all tables...")
            Base.metadata.create_all(bind=engine)
            print("   ✅ All tables created")

            # Reinitialize with default data
            print("   Initializing default data...")
            init_database()
            print("   ✅ Default data initialized")

            print("✅ Database reset successfully")

        except Exception as db_error:
            print(f"❌ Error resetting database: {db_error}")
            import traceback
            traceback.print_exc()

            # Provide helpful error message
            error_msg = str(db_error)
            if "WinError 32" in error_msg or "being used by another process" in error_msg:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Database is locked",
                        "message": "The database file is being used by another process",
                        "solution": "Try again in a few seconds, or use the offline reset script",
                        "instructions": [
                            "1. Stop the server (Ctrl+C)",
                            "2. Run: python reset_database.py",
                            "3. Follow the prompts",
                            "4. Restart the server"
                        ]
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to reset database: {error_msg}"
                )

        print("="*60)
        print("✅ DATABASE RESET COMPLETED")
        print("="*60 + "\n")

        return {
            "success": True,
            "message": "Database reset successfully. All data has been cleared and tables recreated.",
            "backup": str(backup_path) if backup_path else None,
            "deleted": {
                "sessions": sessions_count,
                "invoices": invoices_count,
                "pdfs": pdfs_count,
                "db_invoices": db_invoices_count,
                "db_sessions": db_sessions_count
            },
            "note": "The database file was not deleted, only the data was cleared. This avoids file locking issues."
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error during database reset: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error resetting database: {str(e)}")


@app.get("/")
async def root():
    return RedirectResponse(url="/ui/")


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/api/invoices/{invoice_id}/regenerate")
async def regenerate_invoice(
    invoice_id: int,
    data: Dict[str, Any] = Body(...),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Regenerate invoice with updated data (requires authentication)
    This endpoint allows editing invoice details and regenerating both XLSX and PDF
    """
    try:
        print(f"🔄 Regenerating invoice {invoice_id} with updated data")

        # Get database session
        db = next(get_db())

        # Get existing invoice
        invoice = InvoiceService.get_invoice_by_id(db, invoice_id, company_id=1)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Extract updated data
        employee_name = data.get('employee_name', invoice.employee_name)
        position = data.get('position', invoice.employee_position)
        invoice_date = data.get('invoice_date', invoice.invoice_date)
        call_off = data.get('call_off', invoice.call_off)
        currency = data.get('currency', invoice.currency or 'GBP')
        service_lines = data.get('service_lines', [])
        total_amount = data.get('total_amount', invoice.total_amount)

        # Update invoice in database
        invoice.employee_name = employee_name
        invoice.employee_position = position
        invoice.invoice_date = invoice_date
        invoice.call_off = call_off
        invoice.currency = currency
        invoice.total_amount = total_amount
        invoice.status = 'generated'  # Reset status to generated

        db.commit()

        # Regenerate files
        from app.invoice.template_based_generator import TemplateBasedGenerator
        from app.invoice.pdf_rl import generate_pdf_from_items

        # Prepare items for generation
        items = []
        for line in service_lines:
            items.append({
                'description': line.get('description', ''),
                'unit_price': line.get('unit_price', 0),
                'quantity': line.get('quantity', 0),
                'final': line.get('final', 0)
            })

        # Get session directory
        session_id = invoice.session_id
        session_dir = SESSIONS / session_id
        xlsx_dir = session_dir / "xlsx"
        pdf_dir = session_dir / "pdf"

        xlsx_dir.mkdir(parents=True, exist_ok=True)
        pdf_dir.mkdir(parents=True, exist_ok=True)

        # Generate XLSX
        generator = TemplateBasedGenerator()
        xlsx_filename = f"{employee_name.replace(' ', '_')}_Invoice.xlsx"
        xlsx_path = xlsx_dir / xlsx_filename

        generator.generate_invoice(
            employee_name=employee_name,
            line_items=items,
            invoice_number=invoice.invoice_number,
            invoice_date=invoice_date,
            call_off=call_off,
            output_path=str(xlsx_path)
        )

        # Generate PDF
        pdf_filename = f"{employee_name.replace(' ', '_')}_Invoice.pdf"
        pdf_path = pdf_dir / pdf_filename

        generate_pdf_from_items(
            items=items,
            invoice_number=invoice.invoice_number,
            invoice_date=invoice_date,
            employee_name=employee_name,
            call_off=call_off,
            output_path=str(pdf_path)
        )

        # Update file paths in database
        invoice.file_path_xlsx = str(xlsx_path)
        invoice.file_path_pdf = str(pdf_path)
        db.commit()

        print(f"✅ Invoice {invoice_id} regenerated successfully")

        return {
            "success": True,
            "message": "Invoice regenerated successfully",
            "invoice_id": invoice_id,
            "files": {
                "xlsx": str(xlsx_path),
                "pdf": str(pdf_path)
            }
        }

    except Exception as e:
        print(f"❌ Error regenerating invoice {invoice_id}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to regenerate invoice: {str(e)}")


@app.post("/api/invoices/{invoice_id}/regenerate-pdf")
async def regenerate_invoice_pdf(
    invoice_id: int,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Regenerate PDF for a specific invoice (requires authentication)
    Useful when PDF generation failed or is pending
    """
    try:
        print(f"🔄 Regenerating PDF for invoice {invoice_id}")

        # Get database session
        db = next(get_db())

        # Get invoice from database
        invoice = InvoiceService.get_invoice_by_id(db, invoice_id, company_id=1)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Check if XLSX exists
        xlsx_path = Path(invoice.file_path_xlsx)
        if not xlsx_path.exists():
            xlsx_path = Path.cwd() / invoice.file_path_xlsx
            if not xlsx_path.exists():
                raise HTTPException(status_code=404, detail="XLSX file not found")

        print(f"📄 Found XLSX: {xlsx_path}")

        # Determine PDF path
        pdf_path = xlsx_path.parent.parent / "pdf" / (xlsx_path.stem + ".pdf")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"🎯 Target PDF: {pdf_path}")

        # Ensure LibreOffice is available
        from app.utils.libreoffice_export import ensure_libreoffice, xlsx_to_pdf

        soffice = ensure_libreoffice(auto_install=False)
        if not soffice:
            raise HTTPException(
                status_code=500,
                detail="LibreOffice not found. Please install LibreOffice to generate PDFs."
            )

        print(f"✅ LibreOffice found: {soffice}")

        # Generate PDF
        try:
            print(f"🔄 Converting XLSX to PDF...")
            xlsx_to_pdf(xlsx_path, pdf_path, soffice_path=soffice)

            if not pdf_path.exists():
                raise Exception("PDF file was not created")

            print(f"✅ PDF generated successfully: {pdf_path}")

            # Update database with PDF path
            invoice.file_path_pdf = str(pdf_path.relative_to(Path.cwd()))
            invoice.status = "generated"
            db.commit()

            print(f"✅ Database updated with PDF path")

            return {
                "success": True,
                "message": "PDF regenerated successfully",
                "pdf_path": str(pdf_path),
                "invoice": {
                    "id": invoice.id,
                    "invoice_number": invoice.invoice_number,
                    "employee_name": invoice.employee_name,
                    "status": invoice.status,
                    "file_path_pdf": invoice.file_path_pdf
                }
            }

        except Exception as pdf_error:
            print(f"❌ PDF generation failed: {pdf_error}")
            import traceback
            print(traceback.format_exc())

            raise HTTPException(
                status_code=500,
                detail=f"PDF generation failed: {str(pdf_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error regenerating PDF: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to regenerate PDF: {str(e)}")


@app.post("/api/invoices/regenerate-all-pending-pdfs")
async def regenerate_all_pending_pdfs(
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Regenerate PDFs for all invoices with pending status (requires authentication)
    """
    try:
        print("🔄 Regenerating all pending PDFs...")

        # Get database session
        db = next(get_db())

        # Get all invoices with pending status or no PDF
        from app.database.models import Invoice as InvoiceModel
        pending_invoices = db.query(InvoiceModel).filter(
            (InvoiceModel.file_path_pdf == None) |
            (InvoiceModel.status == 'pending') |
            (InvoiceModel.status == 'pdf_pending')
        ).all()

        if not pending_invoices:
            return {
                "success": True,
                "message": "No pending PDFs found",
                "processed": 0,
                "succeeded": 0,
                "failed": 0
            }

        print(f"📊 Found {len(pending_invoices)} invoices with pending PDFs")

        # Ensure LibreOffice is available
        from app.utils.libreoffice_export import ensure_libreoffice, xlsx_to_pdf

        soffice = ensure_libreoffice(auto_install=False)
        if not soffice:
            raise HTTPException(
                status_code=500,
                detail="LibreOffice not found. Please install LibreOffice to generate PDFs."
            )

        succeeded = 0
        failed = 0
        errors = []

        for invoice in pending_invoices:
            try:
                print(f"🔄 Processing: {invoice.employee_name} (ID: {invoice.id})")

                # Check if XLSX exists
                xlsx_path = Path(invoice.file_path_xlsx)
                if not xlsx_path.exists():
                    xlsx_path = Path.cwd() / invoice.file_path_xlsx
                    if not xlsx_path.exists():
                        raise Exception(f"XLSX file not found: {invoice.file_path_xlsx}")

                # Determine PDF path
                pdf_path = xlsx_path.parent.parent / "pdf" / (xlsx_path.stem + ".pdf")
                pdf_path.parent.mkdir(parents=True, exist_ok=True)

                # Generate PDF
                xlsx_to_pdf(xlsx_path, pdf_path, soffice_path=soffice)

                if not pdf_path.exists():
                    raise Exception("PDF file was not created")

                # Update database
                invoice.file_path_pdf = str(pdf_path.relative_to(Path.cwd()))
                invoice.status = "generated"

                succeeded += 1
                print(f"✅ Success: {invoice.employee_name}")

            except Exception as e:
                failed += 1
                error_msg = f"{invoice.employee_name}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ Failed: {error_msg}")

        # Commit all changes
        db.commit()

        result = {
            "success": True,
            "message": f"Processed {len(pending_invoices)} invoices",
            "processed": len(pending_invoices),
            "succeeded": succeeded,
            "failed": failed
        }

        if errors:
            result["errors"] = errors

        print(f"✅ Batch regeneration complete: {succeeded} succeeded, {failed} failed")

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in batch regeneration: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Batch regeneration failed: {str(e)}")


@app.get("/api/system/libreoffice-check")
async def check_libreoffice():
    """Check LibreOffice installation status and attempt auto-install if needed"""
    try:
        from app.utils.libreoffice_export import find_soffice, ensure_libreoffice
        import platform

        print(f"🔍 LibreOffice check requested")

        result = {
            "system": platform.system(),
            "found": False,
            "path": None,
            "auto_install_attempted": False,
            "auto_install_success": False,
            "message": ""
        }

        # First check without auto-install
        soffice = find_soffice()

        if soffice:
            result["found"] = True
            result["path"] = soffice
            result["message"] = f"LibreOffice encontrado em: {soffice}"
            print(f"✅ LibreOffice found: {soffice}")
        else:
            print(f"⚠️ LibreOffice not found, attempting auto-install...")
            result["message"] = "LibreOffice não encontrado. Tentando instalação automática..."
            result["auto_install_attempted"] = True

            # Try auto-install
            soffice = ensure_libreoffice(auto_install=True)

            if soffice:
                result["found"] = True
                result["path"] = soffice
                result["auto_install_success"] = True
                result["message"] = f"LibreOffice instalado com sucesso em: {soffice}"
                print(f"✅ LibreOffice installed successfully: {soffice}")
            else:
                result["message"] = (
                    "LibreOffice não pôde ser instalado automaticamente. "
                    "Por favor, instale manualmente em: https://www.libreoffice.org/download/"
                )
                print(f"❌ LibreOffice auto-install failed")

        return result

    except Exception as e:
        print(f"❌ Error checking LibreOffice: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"LibreOffice check failed: {str(e)}")


@app.post("/api/system/libreoffice-install")
async def install_libreoffice():
    """Force LibreOffice installation attempt"""
    try:
        from app.utils.libreoffice_export import ensure_libreoffice
        import platform

        print(f"🔧 LibreOffice installation requested")

        if platform.system().lower() != "windows":
            return {
                "success": False,
                "message": "Instalação automática disponível apenas no Windows. Por favor, instale manualmente."
            }

        soffice = ensure_libreoffice(auto_install=True)

        if soffice:
            return {
                "success": True,
                "path": soffice,
                "message": f"LibreOffice instalado/encontrado em: {soffice}"
            }
        else:
            return {
                "success": False,
                "message": (
                    "Falha ao instalar LibreOffice automaticamente. "
                    "Certifique-se de que winget ou chocolatey estão instalados, "
                    "ou instale manualmente em: https://www.libreoffice.org/download/"
                )
            }

    except Exception as e:
        print(f"❌ Error installing LibreOffice: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"LibreOffice installation failed: {str(e)}")

