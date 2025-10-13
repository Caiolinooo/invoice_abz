#!/usr/bin/env python3
"""
Database Initialization Script

This script initializes the invoice system database.
It can be run manually to:
- Create the database if it doesn't exist
- Create all required tables
- Set up default company and configurations
- Migrate existing data from JSON files

Usage:
    python scripts/init_database.py [--force] [--migrate]

Options:
    --force     Force recreation of tables even if they exist
    --migrate   Migrate existing data from out/sessions directory
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.database import (
    init_database,
    migrate_existing_data,
    verify_database_schema,
    DATABASE_FILE,
    DATABASE_DIR
)


def main():
    """Main initialization function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Initialize the invoice system database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize database (safe - won't overwrite existing data)
  python scripts/init_database.py
  
  # Force recreation of tables
  python scripts/init_database.py --force
  
  # Initialize and migrate existing data
  python scripts/init_database.py --migrate
  
  # Force recreation and migrate
  python scripts/init_database.py --force --migrate
        """
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force recreation of tables even if they exist'
    )
    
    parser.add_argument(
        '--migrate',
        action='store_true',
        help='Migrate existing data from out/sessions directory'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Only verify database schema without making changes'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🗄️  INVOICE SYSTEM - DATABASE INITIALIZATION")
    print("="*70)
    print(f"📁 Database directory: {DATABASE_DIR.absolute()}")
    print(f"📄 Database file: {DATABASE_FILE.absolute()}")
    print(f"📊 Database exists: {'Yes' if DATABASE_FILE.exists() else 'No'}")
    
    if DATABASE_FILE.exists():
        size_mb = DATABASE_FILE.stat().st_size / (1024 * 1024)
        print(f"💾 Database size: {size_mb:.2f} MB")
    
    print("="*70 + "\n")
    
    try:
        if args.verify:
            # Only verify schema
            print("🔍 Verifying database schema...\n")
            schema_ok = verify_database_schema()
            
            if schema_ok:
                print("\n✅ Database schema is valid")
                return 0
            else:
                print("\n⚠️  Database schema has issues")
                print("💡 Run without --verify to fix")
                return 1
        
        # Initialize database
        init_database(force=args.force)
        
        # Migrate existing data if requested
        if args.migrate:
            print("\n" + "="*70)
            print("📦 MIGRATING EXISTING DATA")
            print("="*70 + "\n")
            migrate_existing_data()
        
        print("\n" + "="*70)
        print("✅ DATABASE INITIALIZATION SUCCESSFUL")
        print("="*70)
        print("\n💡 Next steps:")
        print("   1. Start the server: python -m uvicorn app.api.server:app --reload")
        print("   2. Access the UI: http://localhost:8000/ui/")
        print("   3. Check API docs: http://localhost:8000/docs")
        print()
        
        return 0
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ DATABASE INITIALIZATION FAILED")
        print("="*70)
        print(f"\nError: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check if the database file is locked by another process")
        print("   2. Verify you have write permissions to the data directory")
        print("   3. Try running with --force to recreate tables")
        print()
        
        import traceback
        traceback.print_exc()
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

