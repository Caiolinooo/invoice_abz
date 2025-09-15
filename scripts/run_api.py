import sys
import subprocess
from pathlib import Path

# Ensure repository root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REQUIRED = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn[standard]"),
    ("multipart", "python-multipart"),
    ("openpyxl", "openpyxl"),
    ("pandas", "pandas"),
]
# reportlab pode já estar instalado; instala se faltar
OPTIONAL = [("reportlab", "reportlab")]


def ensure_packages():
    missing = []
    for mod, pkg in REQUIRED + OPTIONAL:
        try:
            __import__(mod)
        except Exception:
            missing.append(pkg)
    if missing:
        print("Installing missing packages:", missing)
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + missing
        subprocess.check_call(cmd)


def ensure_directories():
    """Ensure required directories exist before starting the server."""
    from pathlib import Path

    # Create required directories
    out_dir = Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)

    sessions_dir = out_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    print(f"Created directories: {out_dir}, {sessions_dir}")


def main():
    ensure_packages()
    ensure_directories()
    import uvicorn
    from app.api.server import app as fastapi_app
    print("Starting API on http://localhost:8000 ...")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
