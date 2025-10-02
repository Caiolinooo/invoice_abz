from __future__ import annotations
from pathlib import Path
import os
import shutil
import subprocess
import platform
from typing import Optional

COMMON_SOFFICE_PATHS = [
    r"C:\\Program Files\\LibreOffice\\program\\soffice.exe",
    r"C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe",
    "/usr/bin/soffice",
    "/usr/local/bin/soffice",
]


def find_soffice(explicit: Optional[str] = None) -> Optional[str]:
    """Return a path to LibreOffice's soffice executable if available."""
    if explicit and Path(explicit).exists():
        return explicit
    env = os.environ.get("LIBREOFFICE_PATH")
    if env and Path(env).exists():
        return env
    which = shutil.which("soffice") or shutil.which("soffice.bin")
    if which:
        return which
    for p in COMMON_SOFFICE_PATHS:
        if Path(p).exists():
            return p
    return None


def ensure_libreoffice(auto_install: bool = True, progress_cb=None) -> Optional[str]:
    """Ensure LibreOffice is available. On Windows, optionally installs silently via winget/choco.

    Returns the path to 'soffice' if available after attempts, otherwise None.
    """
    soffice = find_soffice()
    if soffice or not auto_install:
        return soffice

    # Try auto-install only on Windows
    if platform.system().lower() == "windows":
        if progress_cb:
            progress_cb("Verificando LibreOffice…")
        # 1) winget
        wg = shutil.which("winget")
        if wg and not find_soffice():
            try:
                if progress_cb:
                    progress_cb("Instalando LibreOffice via winget (silencioso)…")
                subprocess.run([
                    wg,
                    "install",
                    "--id",
                    "TheDocumentFoundation.LibreOffice",
                    "--silent",
                    "--accept-package-agreements",
                    "--accept-source-agreements",
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception:
                if progress_cb:
                    progress_cb("Falha ao instalar via winget. Tentando via Chocolatey…")
        # 2) chocolatey (fallback)
        choco = shutil.which("choco")
        if choco and not find_soffice():
            try:
                subprocess.run([choco, "install", "libreoffice", "-y", "--no-progress"],
                               check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception:
                if progress_cb:
                    progress_cb("Falha ao instalar via Chocolatey.")
    # Check again
    soffice = find_soffice()
    if progress_cb:
        progress_cb("LibreOffice disponível." if soffice else "LibreOffice não disponível.")
    return soffice


def xlsx_to_pdf(xlsx_path: Path, out_pdf_path: Path, soffice_path: Optional[str] = None) -> Path:
    """
    Convert an XLSX to PDF using LibreOffice in headless mode (no Excel required).
    Produces a PDF exactly like the Excel sheet formatting.
    """
    xlsx_path = Path(xlsx_path)
    out_pdf_path = Path(out_pdf_path)
    out_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    soffice = find_soffice(soffice_path)
    if not soffice:
        error_msg = (
            "LibreOffice 'soffice' not found. Install LibreOffice and/or set LIBREOFFICE_PATH env var.\n"
            "Visit http://localhost:8000/ui/system-check.html for installation instructions."
        )
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg)

    print(f"🔄 Converting XLSX to PDF using LibreOffice: {xlsx_path.name}")
    print(f"   LibreOffice path: {soffice}")

    # Convert in the output directory; LibreOffice writes to the folder, keeping base name
    cmd = [
        soffice,
        "--headless",
        "--norestore",
        "--nolockcheck",
        "--convert-to",
        "pdf",
        "--outdir",
        str(out_pdf_path.parent),
        str(xlsx_path.resolve()),
    ]

    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        if result.stdout:
            print(f"   LibreOffice stdout: {result.stdout.decode('utf-8', errors='ignore')}")
        if result.stderr:
            print(f"   LibreOffice stderr: {result.stderr.decode('utf-8', errors='ignore')}")
    except subprocess.TimeoutExpired:
        print(f"⚠️ LibreOffice conversion timeout for {xlsx_path.name}")
        raise RuntimeError(f"PDF conversion timeout for {xlsx_path.name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ LibreOffice conversion failed for {xlsx_path.name}")
        print(f"   Return code: {e.returncode}")
        print(f"   stdout: {e.stdout.decode('utf-8', errors='ignore') if e.stdout else 'N/A'}")
        print(f"   stderr: {e.stderr.decode('utf-8', errors='ignore') if e.stderr else 'N/A'}")
        raise

    # LibreOffice names the PDF with the same base name as XLSX
    produced = out_pdf_path.parent / (xlsx_path.stem + ".pdf")

    if not produced.exists():
        print(f"❌ PDF was not created by LibreOffice: {produced}")
        raise RuntimeError(f"LibreOffice did not create PDF: {produced}")

    print(f"✅ PDF created: {produced}")

    if produced != out_pdf_path:
        try:
            if out_pdf_path.exists():
                out_pdf_path.unlink()
            produced.rename(out_pdf_path)
            print(f"✅ PDF renamed to: {out_pdf_path}")
        except Exception as e:
            print(f"⚠️ Failed to rename, copying instead: {e}")
            # fallback: copy
            import shutil as _sh
            _sh.copyfile(produced, out_pdf_path)
            print(f"✅ PDF copied to: {out_pdf_path}")

    return out_pdf_path
