#!/usr/bin/env python3
"""
Robust server startup script for the Payroll Conversion API.
Works on both Windows and Linux environments.
"""
import sys
import subprocess
import os
from pathlib import Path

def install_requirements():
    """Install required packages from requirements.txt"""
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        print("Installing requirements...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ])
            print("Requirements installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install requirements: {e}")
            return False
    else:
        print("No requirements.txt found, skipping package installation.")
    return True

def ensure_directories():
    """Create required directories"""
    directories = [
        Path("out"),
        Path("out/sessions"),
        Path("out/invoices"),
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Ensured directory exists: {directory}")

def install_api_requirements():
    """Install API-specific requirements"""
    api_requirements = [
        "fastapi",
        "uvicorn[standard]", 
        "python-multipart",
        "openpyxl",
        "pandas",
        "reportlab"
    ]
    
    print("Installing API requirements...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade"
        ] + api_requirements)
        print("API requirements installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install API requirements: {e}")
        return False

def start_api_server():
    """Start the FastAPI server"""
    # Add the project root to Python path
    project_root = Path(__file__).resolve().parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        import uvicorn
        # Try to import enhanced server first, fallback to original
        try:
            from app.api.enhanced_server import app as fastapi_app
            print("✓ Using enhanced server with database integration")
        except ImportError:
            from app.api.server import app as fastapi_app
            print("⚠️ Falling back to original server")
        from server_config import get_config, ensure_required_directories, validate_environment

        # Validate environment
        if not validate_environment():
            print("Environment validation failed. Exiting.")
            return False

        # Ensure directories exist
        ensure_required_directories()

        # Get configuration
        config = get_config()

        print("Starting Payroll Conversion API server...")
        print(f"Server will be available at: http://localhost:{config['port']}")
        print(f"API documentation at: http://localhost:{config['port']}/docs")
        print(f"Web interface at: http://localhost:{config['port']}/ui/")
        print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        print("\nPress Ctrl+C to stop the server")

        # Remove reload from config if present since we're passing the app object directly
        config_copy = config.copy()
        config_copy.pop('reload', None)

        uvicorn.run(fastapi_app, **config_copy)

    except ImportError as e:
        print(f"Failed to import required modules: {e}")
        print("Make sure all dependencies are installed.")
        return False
    except Exception as e:
        print(f"Failed to start server: {e}")
        return False

    return True

def main():
    """Main startup sequence"""
    print("=== Payroll Conversion API Startup ===")
    
    # Step 1: Install basic requirements
    if not install_requirements():
        print("Failed to install basic requirements. Exiting.")
        sys.exit(1)
    
    # Step 2: Install API-specific requirements
    if not install_api_requirements():
        print("Failed to install API requirements. Exiting.")
        sys.exit(1)
    
    # Step 3: Ensure directories exist
    ensure_directories()
    
    # Step 4: Start the server
    if not start_api_server():
        print("Failed to start server. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
