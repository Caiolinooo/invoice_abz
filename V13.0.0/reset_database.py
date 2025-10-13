#!/usr/bin/env python3
"""
Script to reset the database when the server is stopped.
This script should be run when the server is NOT running.

Usage:
    python reset_database.py
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime


def reset_database():
    """Reset the database by deleting and recreating it"""
    
    print("=" * 60)
    print("🔄 DATABASE RESET SCRIPT")
    print("=" * 60)
    print()
    
    # Check if server is running
    print("⚠️  WARNING: Make sure the server is STOPPED before running this script!")
    print()
    response = input("Is the server stopped? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("❌ Aborted. Please stop the server first.")
        sys.exit(1)
    
    # Path to the database file
    db_path = Path("data/invoice_system.db")
    
    if not db_path.exists():
        print("ℹ️  Database file does not exist. Nothing to reset.")
        print("✅ You can start the server and it will create a new database.")
        sys.exit(0)
    
    # Confirm reset
    print()
    print(f"📁 Database file: {db_path.absolute()}")
    print()
    print("⚠️  This will:")
    print("   1. Backup the current database")
    print("   2. Delete the database file")
    print("   3. The server will create a new database on next startup")
    print()
    
    response = input("Are you sure you want to reset the database? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("❌ Aborted.")
        sys.exit(1)
    
    try:
        # Backup the old database
        backup_path = Path(f"data/invoice_system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        shutil.copy(db_path, backup_path)
        print(f"📦 Database backed up to: {backup_path}")
        
        # Delete the database file
        db_path.unlink()
        print(f"🗑️  Database deleted: {db_path}")
        
        # Delete journal and WAL files if they exist
        journal_path = Path("data/invoice_system.db-journal")
        wal_path = Path("data/invoice_system.db-wal")
        shm_path = Path("data/invoice_system.db-shm")
        
        for extra_file in [journal_path, wal_path, shm_path]:
            if extra_file.exists():
                extra_file.unlink()
                print(f"🗑️  Deleted: {extra_file}")
        
        print()
        print("✅ Database reset successfully!")
        print()
        print("📝 Next steps:")
        print("   1. Start the server: python start_server.py")
        print("   2. The server will automatically create a new database")
        print("   3. Default admin user will be created")
        print()
        print(f"💾 Backup saved at: {backup_path}")
        
    except Exception as e:
        print(f"❌ Failed to reset database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    reset_database()

