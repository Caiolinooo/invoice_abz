from __future__ import annotations
from pathlib import Path
import json
import uuid
import zipfile
from typing import Dict, List, Optional, Callable
import datetime as dt

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Local imports (support running as package or script)
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
    from utils.libreoffice_export import xlsx_to_pdf, ensure_libreoffice

app = FastAPI(title="Payroll Conversion API", version="0.1.0")

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
    overrides: Optional[Dict[str, object]] = None


def _save_upload(dst: Path, uf: UploadFile) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    data = uf.file.read()
    dst.write_bytes(data)
    return dst


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


def _build_preview_single_file(abz: Path) -> Dict[str, Dict]:
    """Build preview using only the ABZ charge rate file.
    Global rule: one invoice per person. If a name appears multiple times
    with different positions/rates, create multiple service lines in the
    same invoice, each with its own unit_price and quantity.
    """
    charge_df = read_charge_rate_table(abz, "Charge Rate")
    names = sorted(set(charge_df['Name'].astype(str).dropna().tolist()))

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

        # Additional and Expenses totals (single lines each)
        add_total = float(agg[agg['Type'] == 'additional']['Final Price (GBP)'].sum()) if agg is not None and not agg.empty else 0.0
        if add_total and abs(add_total) > 1e-6:
            preview_items.append({"description": "Brazilian Payroll Additional", "final": round(add_total, 2)})
        exp_total = float(agg[agg['Type'] == 'expenses']['Final Price (GBP)'].sum()) if agg is not None and not agg.empty else 0.0
        if exp_total and abs(exp_total) > 1e-6:
            preview_items.append({"description": "Expenses", "final": round(exp_total, 2)})

        preview[name] = {
            "items": preview_items,
            "meta": meta,
        }
    wb.close()
    return preview


def _build_preview(abz: Path, anfin: Path) -> Dict[str, Dict]:
    """Legacy function for backward compatibility - delegates to single file version."""
    return _build_preview_single_file(abz)


@app.post("/api/import")
async def api_import(abz: UploadFile = File(...)):
    sid = uuid.uuid4().hex
    sdir = SESSIONS / sid
    sdir.mkdir(parents=True, exist_ok=True)

    abz_path = _save_upload(sdir / abz.filename, abz)

    preview = _build_preview_single_file(abz_path)

    (sdir / "meta.json").write_text(
        json.dumps({
            "abz": abz.filename,  # Store relative filename, not full path
            "preview": preview,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return {"session_id": sid, "employees": list(preview.keys())}


@app.post("/api/import-legacy")
async def api_import_legacy(abz: UploadFile = File(...), anfin: UploadFile = File(...)):
    """Legacy endpoint for backward compatibility with two files."""
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
async def api_preview(session_id: str):
    sdir = SESSIONS / session_id
    meta_f = sdir / "meta.json"
    if not meta_f.exists():
        raise HTTPException(404, "session not found")
    meta = _read_json(meta_f)
    return {"session_id": session_id, "preview": meta.get("preview", {})}



@app.get("/api/progress")
async def api_progress(session_id: str):
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

@app.post("/api/generate/pdf")
async def api_generate_pdf(req: GenerateRequest):
    sdir = SESSIONS / req.session_id
    meta_f = sdir / "meta.json"
    if not meta_f.exists():
        raise HTTPException(404, "session not found")
    meta = _read_json(meta_f)

    # First, get the uploaded ABZ file path (absolute path)
    uploaded_abz_path = sdir / meta["abz"]
    abz = uploaded_abz_path

    # Check if this is a legacy session with anfin file
    if "anfin" in meta:
        anfin = sdir / meta["anfin"]  # Also make anfin absolute
        preview = meta.get("preview") or _build_preview(uploaded_abz_path, anfin)
    else:
        preview = meta.get("preview") or _build_preview_single_file(uploaded_abz_path)

    # Check if the uploaded file has invoice templates
    from openpyxl import load_workbook
    try:
        wb = load_workbook(abz, read_only=True)
        sheets = wb.sheetnames
        invoice_sheets = [s for s in sheets if s.lower().strip().endswith('_invoice')]
        wb.close()

        if not invoice_sheets:
            # Fallback to DADOS directory if uploaded file has no templates
            print(f"Warning: Uploaded file has no invoice templates, trying DADOS fallback...")
            dados_dir = Path("DADOS")
            abz_files = list(dados_dir.glob("*ABZ*.xlsx"))
            if abz_files:
                abz = abz_files[0]  # Use first ABZ file as fallback
                print(f"Using fallback ABZ file: {abz}")
            else:
                raise HTTPException(500, "No invoice templates found in uploaded file and no fallback ABZ file in DADOS/")
        else:
            print(f"Using uploaded ABZ file with {len(invoice_sheets)} invoice templates")

    except Exception as e:
        print(f"Error checking uploaded file: {e}")
        # Try DADOS fallback
        dados_dir = Path("DADOS")
        abz_files = list(dados_dir.glob("*ABZ*.xlsx"))
        if abz_files:
            abz = abz_files[0]
            print(f"Using fallback ABZ file: {abz}")
        else:
            raise HTTPException(500, f"Cannot read uploaded file and no fallback available: {e}")

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
    if not soffice:
        warnings.append("LibreOffice não encontrado; PDFs não serão gerados (tentativa de instalação pode ter falhado).")

    i = 0
    invoice_sheets = [s for s in sheets if s.lower().strip().endswith('_invoice')]

    # Invoice number sequencing (persistent)
    seq = _seq_read()
    last_used = int(seq.get("last", 0) or 0)
    # If a numeric invoice_no was provided, start from it; otherwise continue sequence
    try:
        start_no = int(str(req.invoice_no).strip()) if (req.invoice_no is not None and str(req.invoice_no).strip().isdigit()) else (last_used + 1)
    except Exception:
        start_no = last_used + 1
    assigned = 0

    for name, pdata in preview.items():
        i += 1
        _update_progress(sdir, stage=f"Gerando {i}/{total} – {name}", current=i, total=total, percent=int(i*100/total))

        tpl = _find_template_for_employee(name, invoice_sheets)
        if not tpl:
            warnings.append(
                f"Template não encontrado para {name}. Abas de invoice disponíveis: {', '.join(invoice_sheets) if invoice_sheets else 'nenhuma'}"
            )
            _update_progress(sdir, warnings=warnings)
            continue  # não impede os demais

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
        xlsx_path = generate_from_abz_template(
            abz_xlsx=abz,
            template_sheet_name=tpl,
            employee_name=name,
            line_items=items,
            out_dir=xlsx_dir,
            invoice_date=m.get("invoice_date"),
            invoice_no=display_inv_no,
            call_off=m.get("call_off"),
        )
        pdf_path = pdf_dir / (xlsx_path.stem + ".pdf")
        url_xlsx = f"/out/sessions/{req.session_id}/xlsx/{xlsx_path.name}"
        url_pdf = None
        if soffice:
            try:
                _update_progress(sdir, stage=f"Convertendo PDF – {name}")
                xlsx_to_pdf(xlsx_path, pdf_path, soffice_path=soffice)
                if pdf_path.exists():
                    url_pdf = f"/out/sessions/{req.session_id}/pdf/{pdf_path.name}"
            except Exception as e:
                warnings.append(f"Falha ao converter PDF de {name}: {e}")
                _update_progress(sdir, warnings=warnings)
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
            _seq_write(start_no + assigned - 1)
    except Exception:
        pass

    wb.close()
    _update_progress(sdir, stage="Concluído", percent=100, done=True, warnings=warnings)
    return {"session_id": req.session_id, "files": produced, "warnings": warnings}


@app.get("/api/session/{session_id}/files")
async def api_session_files(session_id: str):
    sdir = SESSIONS / session_id
    if not sdir.exists():
        raise HTTPException(404, "session not found")
    xlsx = sorted([str(p) for p in (sdir / "xlsx").glob("*.xlsx")]) if (sdir / "xlsx").exists() else []
    pdf = sorted([str(p) for p in (sdir / "pdf").glob("*.pdf")]) if (sdir / "pdf").exists() else []
    return {"session_id": session_id, "xlsx": xlsx, "pdf": pdf}


@app.get("/api/session/{session_id}/zip")
async def api_session_zip(session_id: str, kind: str = "pdf"):
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


@app.get("/")
async def root():
    return RedirectResponse(url="/ui/")


@app.get("/health")
async def health():
    return {"ok": True}

