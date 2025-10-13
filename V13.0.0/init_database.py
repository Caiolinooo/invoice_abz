#!/usr/bin/env python3
"""
Database initialization script for the Invoice System
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database.database import init_database, migrate_existing_data


def main():
    """Initialize database and migrate existing data"""
    print("🚀 Initializing Invoice System Database...")
    
    try:
        # Initialize database with tables and default data
        print("\n📊 Creating database tables and default data...")
        init_database()
        
        # Migrate existing JSON data
        print("\n📦 Migrating existing data...")
        migrate_existing_data()
        
        print("\n✅ Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Start the server: python start_server.py")
        print("2. Access the web interface: http://localhost:8000/ui/")
        print("3. Check the API documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
