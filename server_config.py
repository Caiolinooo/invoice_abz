"""
Server configuration for different environments
"""
import os
from pathlib import Path

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

# Base configuration
BASE_CONFIG = {
    "host": "0.0.0.0",
    "port": int(os.getenv("PORT", 8000)),
    "reload": False,
    "access_log": True,
    "log_level": "info"
}

# Environment-specific configurations
CONFIGS = {
    "development": {
        **BASE_CONFIG,
        "reload": True,
        "log_level": "debug"
    },
    "production": {
        **BASE_CONFIG,
        "workers": int(os.getenv("WORKERS", 1)),
        "log_level": "warning"
    },
    "cloud": {
        **BASE_CONFIG,
        "workers": int(os.getenv("WORKERS", 2)),
        "log_level": "info"
    }
}

def get_config():
    """Get configuration for current environment"""
    return CONFIGS.get(ENVIRONMENT, BASE_CONFIG)

def ensure_required_directories():
    """Ensure all required directories exist"""
    directories = [
        Path("out"),
        Path("out/sessions"), 
        Path("out/invoices"),
        Path("app/ui"),  # Ensure UI directory exists
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ensured: {directory}")

def validate_environment():
    """Validate that the environment is properly set up"""
    required_files = [
        Path("app/api/server.py"),
        Path("app/ui"),
    ]
    
    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path))
    
    if missing_files:
        print("❌ Missing required files/directories:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✓ Environment validation passed")
    return True
