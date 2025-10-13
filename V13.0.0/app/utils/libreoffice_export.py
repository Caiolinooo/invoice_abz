from __future__ import annotations
from pathlib import Path
import os
import shutil
import subprocess
import platform
from typing import Optional

COMMON_SOFFICE_PATHS = [
    # Windows paths - most common first
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    # Try different versions
    r"C:\Program Files\LibreOffice 7\program\soffice.exe",
    r"C:\Program Files\LibreOffice 24\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice 7\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice 24\program\soffice.exe",
    # User-specific installations
    os.path.expanduser(r"~\AppData\Local\Programs\LibreOffice\program\soffice.exe"),
    # Linux/Mac paths
    "/usr/bin/soffice",
    "/usr/local/bin/soffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


def find_soffice(explicit: Optional[str] = None) -> Optional[str]:
    """Return a path to LibreOffice's soffice executable if available."""
    # 1. Check explicit path
    if explicit:
        if Path(explicit).exists():
            print(f"   ✅ Found via explicit path: {explicit}")
            return explicit
        else:
            print(f"   ❌ Explicit path does not exist: {explicit}")

    # 2. Check environment variable
    env = os.environ.get("LIBREOFFICE_PATH")
    if env:
        if Path(env).exists():
            print(f"   ✅ Found via LIBREOFFICE_PATH env var: {env}")
            return env
        else:
            print(f"   ❌ LIBREOFFICE_PATH env var path does not exist: {env}")

    # 3. Check system PATH
    which = shutil.which("soffice") or shutil.which("soffice.bin")
    if which:
        print(f"   ✅ Found in system PATH: {which}")
        return which

    # 4. Check common installation paths
    print(f"   🔍 Checking {len(COMMON_SOFFICE_PATHS)} common installation paths...")
    for p in COMMON_SOFFICE_PATHS:
        if Path(p).exists():
            print(f"   ✅ Found at common path: {p}")
            return p

    print(f"   ❌ LibreOffice not found in any common location")
    return None


def ensure_libreoffice(auto_install: bool = True, progress_cb=None) -> Optional[str]:
    """Ensure LibreOffice is available. On Windows, optionally installs silently via winget/choco.

    Returns the path to 'soffice' if available after attempts, otherwise None.
    """
    print(f"🔍 Checking for LibreOffice installation...")
    soffice = find_soffice()

    if soffice:
        print(f"✅ LibreOffice found at: {soffice}")
        if progress_cb:
            progress_cb(f"LibreOffice encontrado: {soffice}")
        return soffice

    print(f"⚠️ LibreOffice not found in common locations")

    if not auto_install:
        print(f"❌ Auto-install disabled, returning None")
        return None

    # Try auto-install only on Windows
    system = platform.system().lower()
    print(f"🖥️ Operating system: {system}")

    if system == "windows":
        if progress_cb:
            progress_cb("LibreOffice não encontrado. Tentando instalar automaticamente...")

        print(f"🔍 Searching for package managers...")

        # 1) winget
        wg = shutil.which("winget")
        print(f"   winget: {'✅ Found' if wg else '❌ Not found'}")

        if wg and not find_soffice():
            try:
                if progress_cb:
                    progress_cb("Instalando LibreOffice via winget (silencioso)…")
                print(f"📦 Installing LibreOffice via winget...")

                result = subprocess.run([
                    wg,
                    "install",
                    "--id",
                    "TheDocumentFoundation.LibreOffice",
                    "--silent",
                    "--accept-package-agreements",
                    "--accept-source-agreements",
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)

                print(f"✅ winget installation completed")
                if result.stdout:
                    print(f"   stdout: {result.stdout.decode('utf-8', errors='ignore')}")
                if result.stderr:
                    print(f"   stderr: {result.stderr.decode('utf-8', errors='ignore')}")

            except subprocess.TimeoutExpired:
                print(f"⚠️ winget installation timeout")
                if progress_cb:
                    progress_cb("Timeout ao instalar via winget. Tentando via Chocolatey…")
            except Exception as e:
                print(f"⚠️ winget installation failed: {e}")
                if progress_cb:
                    progress_cb("Falha ao instalar via winget. Tentando via Chocolatey…")

        # 2) chocolatey (fallback)
        choco = shutil.which("choco")
        print(f"   chocolatey: {'✅ Found' if choco else '❌ Not found'}")

        if choco and not find_soffice():
            try:
                if progress_cb:
                    progress_cb("Instalando LibreOffice via Chocolatey…")
                print(f"📦 Installing LibreOffice via Chocolatey...")

                result = subprocess.run([choco, "install", "libreoffice", "-y", "--no-progress"],
                               check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)

                print(f"✅ Chocolatey installation completed")
                if result.stdout:
                    print(f"   stdout: {result.stdout.decode('utf-8', errors='ignore')}")
                if result.stderr:
                    print(f"   stderr: {result.stderr.decode('utf-8', errors='ignore')}")

            except subprocess.TimeoutExpired:
                print(f"⚠️ Chocolatey installation timeout")
                if progress_cb:
                    progress_cb("Timeout ao instalar via Chocolatey.")
            except Exception as e:
                print(f"⚠️ Chocolatey installation failed: {e}")
                if progress_cb:
                    progress_cb("Falha ao instalar via Chocolatey.")

        # If no package manager found, provide manual installation instructions
        if not wg and not choco:
            print(f"❌ No package manager found (winget or chocolatey)")
            if progress_cb:
                progress_cb("Nenhum gerenciador de pacotes encontrado. Instale manualmente.")
    else:
        print(f"⚠️ Auto-install only supported on Windows")
        if progress_cb:
            progress_cb("Instalação automática disponível apenas no Windows.")

    # Check again after installation attempts
    print(f"🔍 Checking for LibreOffice after installation attempts...")
    soffice = find_soffice()

    if soffice:
        print(f"✅ LibreOffice now available at: {soffice}")
        if progress_cb:
            progress_cb(f"LibreOffice instalado com sucesso: {soffice}")
    else:
        print(f"❌ LibreOffice still not available after installation attempts")
        if progress_cb:
            progress_cb("LibreOffice não disponível. Instale manualmente em: https://www.libreoffice.org/download/")

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
