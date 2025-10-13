"""
Helper script to set environment (DEV or PROD)
"""
import os
import sys

def set_dev():
    """Set to development environment"""
    os.environ["INVOICE_ENV"] = "dev"
    print("=" * 80)
    print("🔧 DEVELOPMENT MODE ACTIVATED")
    print("=" * 80)
    print(f"Database: data/invoice_system_dev.db")
    print(f"SQL Logging: Enabled")
    print(f"\nYou can now test without affecting production data!")
    print("=" * 80)

def set_prod():
    """Set to production environment"""
    os.environ["INVOICE_ENV"] = "prod"
    print("=" * 80)
    print("🚀 PRODUCTION MODE ACTIVATED")
    print("=" * 80)
    print(f"Database: data/invoice_system.db")
    print(f"SQL Logging: Disabled")
    print(f"\n⚠️  WARNING: Changes will affect production data!")
    print("=" * 80)

def show_current():
    """Show current environment"""
    env = os.getenv("INVOICE_ENV", "prod")
    is_dev = env.lower() == "dev"
    
    print("=" * 80)
    print("📊 CURRENT ENVIRONMENT")
    print("=" * 80)
    print(f"Mode: {'🔧 DEVELOPMENT' if is_dev else '🚀 PRODUCTION'}")
    print(f"Database: data/invoice_system{'_dev' if is_dev else ''}.db")
    print(f"SQL Logging: {'Enabled' if is_dev else 'Disabled'}")
    print("=" * 80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python dev/set_env.py dev   - Set to development mode")
        print("  python dev/set_env.py prod  - Set to production mode")
        print("  python dev/set_env.py show  - Show current environment")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == "dev":
        set_dev()
    elif mode == "prod":
        set_prod()
    elif mode == "show":
        show_current()
    else:
        print(f"❌ Unknown mode: {mode}")
        print("Use: dev, prod, or show")
        sys.exit(1)

