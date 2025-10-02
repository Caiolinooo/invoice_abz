"""
Database connection and session management with automatic initialization
"""
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from pathlib import Path
from .models import Base

# Database configuration
DATABASE_DIR = Path("data")
DATABASE_DIR.mkdir(exist_ok=True, parents=True)
DATABASE_FILE = DATABASE_DIR / "invoice_system.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# Check if database exists
DB_EXISTS = DATABASE_FILE.exists()

# Create engine with connection pooling for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    },
    poolclass=StaticPool,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables"""
    try:
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


def verify_database_schema():
    """Verify that all required tables exist"""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # Required tables from models
        required_tables = [
            'companies',
            'users',
            'configurations',
            'templates',
            'sessions',
            'invoices',
            'email_logs',
            'audit_logs'
        ]

        missing_tables = [table for table in required_tables if table not in existing_tables]

        if missing_tables:
            print(f"⚠️  Missing tables: {', '.join(missing_tables)}")
            print("🔧 Creating missing tables...")
            create_tables()
            return False
        else:
            print(f"✅ All {len(required_tables)} required tables exist")
            return True

    except Exception as e:
        print(f"❌ Error verifying database schema: {e}")
        return False


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Get database session (direct access)"""
    return SessionLocal()


def init_database(force=False):
    """
    Initialize database with default data

    Args:
        force: If True, recreate tables even if they exist
    """
    print("\n" + "="*60)
    print("🚀 INITIALIZING DATABASE")
    print("="*60)

    # Check if database file exists
    if not DB_EXISTS:
        print(f"📁 Database file not found: {DATABASE_FILE}")
        print("🔧 Creating new database...")
    else:
        print(f"✅ Database file exists: {DATABASE_FILE}")

    # Verify schema
    schema_ok = verify_database_schema()

    if force or not schema_ok:
        create_tables()

    # Create default company if none exists
    db = get_db_session()
    try:
        from .models import Company, User, Configuration

        # Check if default company exists
        default_company = db.query(Company).filter(Company.name == "Default Company").first()
        if not default_company:
            print("🏢 Creating default company...")
            # Create default company
            default_company = Company(
                name="Default Company",
                domain="localhost",
                settings='{"theme": "default", "currency": "GBP"}',
                is_active=True
            )
            db.add(default_company)
            db.commit()
            db.refresh(default_company)
            
            # Create default admin user
            admin_user = User(
                email="admin@localhost",
                name="System Administrator",
                company_id=default_company.id,
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            
            # Create default configurations
            default_configs = [
                {
                    "key": "company_name",
                    "value": "ABZ Group",
                    "description": "Company name for invoices",
                    "config_type": "general"
                },
                {
                    "key": "company_address",
                    "value": "123 Business Street, London, UK",
                    "description": "Company address for invoices",
                    "config_type": "general"
                },
                {
                    "key": "default_currency",
                    "value": "GBP",
                    "description": "Default currency for invoices",
                    "config_type": "general"
                },
                {
                    "key": "email_smtp_server",
                    "value": "",
                    "description": "SMTP server for email sending",
                    "config_type": "email"
                },
                {
                    "key": "email_smtp_port",
                    "value": "587",
                    "description": "SMTP port for email sending",
                    "config_type": "email"
                },
                {
                    "key": "email_username",
                    "value": "",
                    "description": "Email username for SMTP authentication",
                    "config_type": "email"
                },
                {
                    "key": "email_password",
                    "value": "",
                    "description": "Email password for SMTP authentication",
                    "config_type": "email",
                    "is_encrypted": True
                },
                {
                    "key": "auto_send_emails",
                    "value": "false",
                    "description": "Automatically send invoices via email",
                    "config_type": "email"
                }
            ]
            
            for config_data in default_configs:
                config = Configuration(
                    company_id=default_company.id,
                    **config_data
                )
                db.add(config)
            
            db.commit()
            print(f"✅ Database initialized with default company: {default_company.name}")
            print(f"👤 Default admin user: admin@localhost")
            print(f"⚙️  Created {len(default_configs)} default configurations")
        else:
            print("✅ Database already initialized")
            print(f"🏢 Company: {default_company.name}")

        # Verify all tables have been created
        inspector = inspect(engine)
        table_count = len(inspector.get_table_names())
        print(f"📊 Total tables in database: {table_count}")

        print("="*60)
        print("✅ DATABASE INITIALIZATION COMPLETE")
        print("="*60 + "\n")

    except Exception as e:
        db.rollback()
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


def ensure_database_ready():
    """
    Ensure database is ready for use.
    This function is called automatically when the module is imported.
    """
    try:
        # Check if database file exists
        if not DATABASE_FILE.exists():
            print(f"\n⚠️  Database file not found: {DATABASE_FILE}")
            print("🔧 Initializing database for the first time...\n")
            init_database()
            return True

        # Verify schema
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if not existing_tables:
            print(f"\n⚠️  Database exists but has no tables")
            print("🔧 Creating database schema...\n")
            init_database()
            return True

        # Quick verification that key tables exist
        required_tables = ['companies', 'invoices', 'sessions']
        missing = [t for t in required_tables if t not in existing_tables]

        if missing:
            print(f"\n⚠️  Missing critical tables: {', '.join(missing)}")
            print("🔧 Recreating database schema...\n")
            init_database()
            return True

        # Database is ready
        return True

    except Exception as e:
        print(f"❌ Error ensuring database is ready: {e}")
        import traceback
        traceback.print_exc()
        return False


def migrate_existing_data():
    """Migrate existing JSON data to SQLite"""
    from pathlib import Path
    import json
    from datetime import datetime
    from .models import Invoice, Session as SessionModel, Company
    
    db = get_db_session()
    try:
        # Get default company
        default_company = db.query(Company).filter(Company.name == "Default Company").first()
        if not default_company:
            print("❌ Default company not found. Please run init_database() first.")
            return
        
        # Migrate invoice sequence
        seq_file = Path("out/invoice_seq.json")
        if seq_file.exists():
            try:
                seq_data = json.loads(seq_file.read_text(encoding="utf-8"))
                print(f"✓ Found invoice sequence: {seq_data}")
            except Exception as e:
                print(f"⚠️ Could not read invoice sequence: {e}")
        
        # Migrate sessions
        sessions_dir = Path("out/sessions")
        if sessions_dir.exists():
            migrated_sessions = 0
            migrated_invoices = 0
            
            for session_dir in sessions_dir.iterdir():
                if session_dir.is_dir():
                    session_id = session_dir.name
                    meta_file = session_dir / "meta.json"
                    
                    if meta_file.exists():
                        try:
                            meta_data = json.loads(meta_file.read_text(encoding="utf-8"))
                            
                            # Check if session already exists
                            existing_session = db.query(SessionModel).filter(
                                SessionModel.session_id == session_id
                            ).first()
                            
                            if not existing_session:
                                # Create session record
                                session_record = SessionModel(
                                    company_id=default_company.id,
                                    session_id=session_id,
                                    abz_filename=meta_data.get("abz"),
                                    anfin_filename=meta_data.get("anfin"),
                                    status="completed",
                                    employee_count=len(meta_data.get("preview", {})),
                                    created_at=datetime.fromtimestamp(session_dir.stat().st_ctime)
                                )
                                db.add(session_record)
                                migrated_sessions += 1
                                
                                # Migrate invoices from this session
                                xlsx_dir = session_dir / "xlsx"
                                pdf_dir = session_dir / "pdf"
                                
                                if xlsx_dir.exists():
                                    for xlsx_file in xlsx_dir.glob("*.xlsx"):
                                        # Extract employee name from filename
                                        filename = xlsx_file.stem
                                        if "Invoice" in filename:
                                            employee_name = filename.replace("_Invoice", "").replace("_", " ")
                                        else:
                                            employee_name = filename.replace("_", " ")
                                        
                                        # Check if invoice already exists
                                        existing_invoice = db.query(Invoice).filter(
                                            Invoice.session_id == session_id,
                                            Invoice.employee_name == employee_name
                                        ).first()
                                        
                                        if not existing_invoice:
                                            # Find corresponding PDF
                                            pdf_file = None
                                            if pdf_dir.exists():
                                                pdf_candidates = list(pdf_dir.glob(f"{filename}*.pdf"))
                                                if pdf_candidates:
                                                    pdf_file = pdf_candidates[0]
                                            
                                            # Create invoice record
                                            invoice_record = Invoice(
                                                company_id=default_company.id,
                                                session_id=session_id,
                                                invoice_number=f"MIGRATED-{session_id[:8]}-{migrated_invoices+1:03d}",
                                                employee_name=employee_name,
                                                invoice_date=datetime.fromtimestamp(xlsx_file.stat().st_ctime),
                                                file_path_xlsx=str(xlsx_file.relative_to(Path.cwd())),
                                                file_path_pdf=str(pdf_file.relative_to(Path.cwd())) if pdf_file else None,
                                                status="generated",
                                                created_at=datetime.fromtimestamp(xlsx_file.stat().st_ctime)
                                            )
                                            db.add(invoice_record)
                                            migrated_invoices += 1
                                
                        except Exception as e:
                            print(f"⚠️ Error migrating session {session_id}: {e}")
                            continue
            
            db.commit()
            print(f"✓ Migrated {migrated_sessions} sessions and {migrated_invoices} invoices")
        else:
            print("ℹ️ No existing sessions found to migrate")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        db.close()


# ============================================================================
# AUTOMATIC INITIALIZATION
# ============================================================================
# This ensures the database is ready when the module is imported
# It will create the database and tables if they don't exist

try:
    # Only run automatic initialization if not in a test environment
    import sys
    if 'pytest' not in sys.modules and 'unittest' not in sys.modules:
        ensure_database_ready()
except Exception as e:
    print(f"⚠️  Warning: Could not auto-initialize database: {e}")
    print("💡 You may need to call init_database() manually")
