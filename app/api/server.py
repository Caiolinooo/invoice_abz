from __future__ import annotations
from pathlib import Path
import json
import uuid
import zipfile
from typing import Dict, List, Optional, Callable

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
# Serve outputs and UI statically
app.mount("/out", StaticFiles(directory="out"), name="out")
app.mount("/ui", StaticFiles(directory="app/ui", html=True), name="ui")

SESSIONS = Path("out/sessions")
SESSIONS.mkdir(parents=True, exist_ok=True)


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
    overrides: Optional[Dict[str, Dict]] = None  # {name: {quantity: x, unit_price: y}}


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


def _build_preview(abz: Path, anfin: Path) -> Dict[str, Dict]:
    charge_df = read_charge_rate_table(abz, "Charge Rate")
    ind = extract_individual_totals(anfin)
    costs_gbp = extract_costs_gbp(anfin, {k: v['exchange_rate'] for k, v in ind.items()})

    names = sorted(set(charge_df['Name'].astype(str).dropna().tolist()))

    from openpyxl import load_workbook
    wb = load_workbook(abz, read_only=True)
    sheets = wb.sheetnames

    preview: Dict[str, Dict] = {}
    for name in names:
        sub = charge_df[charge_df['Name'].astype(str) == name]

        # Template meta (normalize to handle accents, e.g., Bárbara -> Barbara)
        first = _norm(name.split()[0])
        tpl_candidates = [s for s in sheets if s.lower().endswith('_invoice') and first in _norm(s)]
        meta = {'invoice_no': None, 'invoice_date': None, 'call_off': None}
        if tpl_candidates:
            meta = get_invoice_meta(abz, tpl_candidates[0])

        # Service row
        days = float(sub['Days'].sum()) if 'Days' in sub.columns else 0.0
        pos = str(sub['Position'].iloc[0]) if 'Position' in sub.columns and not sub['Position'].empty else ''
        rate = float(sub['Charge Rate (GBP)'].iloc[0]) if 'Charge Rate (GBP)' in sub.columns and not sub['Charge Rate (GBP)'].empty else 0.0
        # Round monetary to 2 decimals
        rate = round(rate, 2)

        # description with call-off and month if available
        desc = f"{_friendly_name(name)} - {pos}"
        if meta.get('call_off'):
            desc += f" - Call Off - {meta['call_off']}"
        preview_items: List[Dict] = [
            {"description": desc, "unit_price": rate, "quantity": days, "final": round(rate * days, 2)}
        ]

        # Additional: prefer ABZ, fallback AN-FIN
        add_val = None
        if 'Brazilian Payroll Additionals (GBP)' in sub.columns:
            add_val = float(sub['Brazilian Payroll Additionals (GBP)'].sum())
        if (add_val is None or abs(add_val) < 1e-9):
            if name in ind:
                add_val = ind[name]['additional_gbp']
            else:
                for k, v in ind.items():
                    if k.lower().split()[0] == name.lower().split()[0]:
                        add_val = v['additional_gbp']
                        break
        if add_val and abs(add_val) > 1e-6:
            preview_items.append({"description": "Brazilian Payroll Additional", "final": round(float(add_val), 2)})

        # Expenses
        exp_val = None
        if name in costs_gbp:
            exp_val = costs_gbp[name]
        else:
            for k, v in costs_gbp.items():
                if k.lower().split()[0] == name.lower().split()[0]:
                    exp_val = v
                    break
        if exp_val is None:
            exp_val = float(sub['Expenses'].sum()) if 'Expenses' in sub.columns else 0.0
        if exp_val and abs(exp_val) > 1e-6:
            preview_items.append({"description": "Expenses", "final": round(float(exp_val), 2)})

        preview[name] = {
            "items": preview_items,
            "meta": meta,
        }
    wb.close()
    return preview


@app.post("/api/import")
async def api_import(abz: UploadFile = File(...), anfin: UploadFile = File(...)):
    sid = uuid.uuid4().hex
    sdir = SESSIONS / sid
    sdir.mkdir(parents=True, exist_ok=True)

    abz_path = _save_upload(sdir / abz.filename, abz)
    anfin_path = _save_upload(sdir / anfin.filename, anfin)



    preview = _build_preview(abz_path, anfin_path)

    (sdir / "meta.json").write_text(
        json.dumps({
            "abz": str(abz_path),
            "anfin": str(anfin_path),
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
    abz = Path(meta["abz"])  # type: ignore
    anfin = Path(meta["anfin"])  # kept for parity if needed later

    preview = meta.get("preview") or _build_preview(abz, anfin)

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
    invoice_sheets = [s for s in sheets if s.lower().endswith('_invoice')]

    for name, pdata in preview.items():
        i += 1
        _update_progress(sdir, stage=f"Gerando {i}/{total} – {name}", current=i, total=total, percent=int(i*100/total))

        first = _norm(name.split()[0])
        tpl_candidates = [s for s in invoice_sheets if first in _norm(s)]
        if not tpl_candidates:
            warnings.append(
                f"Template não encontrado para {name} (busca por '{first}'). Abas de invoice disponíveis: {', '.join(invoice_sheets) if invoice_sheets else 'nenhuma'}"
            )
            _update_progress(sdir, warnings=warnings)
            continue  # não impede os demais
        tpl = tpl_candidates[0]

        # merge meta: request overrides > preview meta
        m = dict(pdata.get("meta") or {})
        if req.invoice_date is not None:
            m["invoice_date"] = req.invoice_date
        if req.invoice_no is not None:
            m["invoice_no"] = req.invoice_no
        if req.call_off is not None:
            m["call_off"] = req.call_off

        # items (always three lines layout)
        items = list(pdata.get("items") or [])
        # apply overrides if present
        ov = (req.overrides or {}).get(name)
        if ov:
            if "quantity" in ov and items:
                # apply to the first service row
                q = float(ov["quantity"])
                items[0]["quantity"] = q
                unit = float(items[0].get("unit_price") or 0.0)
                items[0]["final"] = round(unit * q, 2)
            if "unit_price" in ov and items:
                u = float(ov["unit_price"])
                items[0]["unit_price"] = round(u, 2)
                q = float(items[0].get("quantity") or 0.0)
                items[0]["final"] = round(items[0]["unit_price"] * q, 2)

        # Generate single-sheet XLSX from template
        xlsx_path = generate_from_abz_template(
            abz_xlsx=abz,
            template_sheet_name=tpl,
            employee_name=name,
            line_items=items,
            out_dir=xlsx_dir,
            invoice_date=m.get("invoice_date"),
            invoice_no=m.get("invoice_no"),
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


@app.get("/")
async def root():
    return RedirectResponse(url="/ui/")


@app.get("/health")
async def health():
    return {"ok": True}

