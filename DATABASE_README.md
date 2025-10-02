# 🗄️ Database Management Guide

## Overview

The Invoice System uses **SQLite** as its database, with automatic initialization and schema management. The database is automatically created and configured when you start the application.

---

## 📁 Database Location

```
data/
└── invoice_system.db    # Main SQLite database file
```

---

## 🚀 Automatic Initialization

The database is **automatically initialized** when you:
1. Start the server for the first time
2. Import the `app.database.database` module
3. Access any database-dependent endpoint

### What Happens Automatically:

✅ **Creates database file** if it doesn't exist  
✅ **Creates all required tables** (companies, users, invoices, sessions, etc.)  
✅ **Sets up default company** ("Default Company")  
✅ **Creates admin user** (admin@localhost)  
✅ **Configures default settings** (currency, email, etc.)  
✅ **Verifies schema integrity** on every startup  

---

## 📊 Database Schema

### Tables Created:

| Table | Description |
|-------|-------------|
| `companies` | Company information and settings |
| `users` | System users and authentication |
| `configurations` | System configurations (email, currency, etc.) |
| `templates` | Invoice templates |
| `sessions` | Upload sessions and processing history |
| `invoices` | Generated invoices with metadata |
| `email_logs` | Email sending history and status |

---

## 🛠️ Manual Initialization

If you need to manually initialize or reset the database:

### Basic Initialization
```bash
python scripts/init_database.py
```

### Force Recreation (Recreate Tables)
```bash
python scripts/init_database.py --force
```

### Migrate Existing Data
```bash
python scripts/init_database.py --migrate
```

### Verify Schema Only
```bash
python scripts/init_database.py --verify
```

---

## 🔄 Migration from Old System

If you have existing data in `out/sessions/` directory:

```bash
# Initialize database and migrate existing invoices
python scripts/init_database.py --migrate
```

This will:
- Scan `out/sessions/` for existing session directories
- Import invoice metadata from `meta.json` files
- Create database records for all existing invoices
- Preserve file paths to XLSX and PDF files

---

## 🔧 Troubleshooting

### Database Not Found Error

**Symptom:** `Database file not found` or `No such table` errors

**Solution:**
```bash
# The database will be created automatically, but you can force it:
python scripts/init_database.py --force
```

---

### Database Locked Error

**Symptom:** `database is locked` error

**Causes:**
- Another process is using the database
- Server is still running
- Previous crash left a lock file

**Solution:**
```bash
# 1. Stop all running servers
# 2. Check for .db-journal or .db-wal files
ls data/

# 3. Remove lock files (if safe)
rm data/invoice_system.db-journal
rm data/invoice_system.db-wal

# 4. Restart the server
python -m uvicorn app.api.server:app --reload
```

---

### Missing Tables Error

**Symptom:** `no such table: invoices` or similar

**Solution:**
```bash
# Verify and recreate schema
python scripts/init_database.py --force
```

---

### Reset Database Completely

**Warning:** This will delete ALL data!

```bash
# 1. Stop the server
# 2. Delete the database file
rm data/invoice_system.db

# 3. Restart the server (will auto-create new database)
python -m uvicorn app.api.server:app --reload
```

Or use the UI:
1. Go to Settings → Database Management
2. Enter password: `2122`
3. Click "Reset All Data"

---

## 🔍 Database Inspection

### Using SQLite CLI
```bash
# Open database
sqlite3 data/invoice_system.db

# List tables
.tables

# Show schema
.schema invoices

# Query data
SELECT * FROM invoices LIMIT 10;

# Exit
.quit
```

### Using Python
```python
from app.database.database import get_db_session
from app.database.models import Invoice, Company

db = get_db_session()

# Get all companies
companies = db.query(Company).all()
for company in companies:
    print(f"Company: {company.name}")

# Get recent invoices
invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).limit(10).all()
for invoice in invoices:
    print(f"Invoice: {invoice.invoice_number} - {invoice.employee_name}")

db.close()
```

---

## 📈 Database Maintenance

### Backup Database
```bash
# Create backup
cp data/invoice_system.db data/invoice_system_backup_$(date +%Y%m%d).db

# Or use SQLite backup
sqlite3 data/invoice_system.db ".backup data/backup.db"
```

### Restore Database
```bash
# Stop the server first!
cp data/invoice_system_backup_20250101.db data/invoice_system.db
```

### Optimize Database
```bash
# Vacuum to reclaim space and optimize
sqlite3 data/invoice_system.db "VACUUM;"
```

---

## 🔐 Security Notes

1. **Database File Permissions:**
   - Ensure only the application user can read/write
   - On Linux: `chmod 600 data/invoice_system.db`

2. **Backup Strategy:**
   - Regular backups before major operations
   - Keep backups in a secure location
   - Test restore procedures

3. **Password Protection:**
   - Database reset requires password (`2122`)
   - Change default password in production

---

## 🚦 Health Checks

The system automatically verifies database health on startup:

```
✅ Database file exists: data/invoice_system.db
✅ All 7 required tables exist
✅ Database already initialized
🏢 Company: Default Company
📊 Total tables in database: 7
```

If you see warnings, run:
```bash
python scripts/init_database.py --verify
```

---

## 📞 Support

If you encounter database issues:

1. Check the logs for detailed error messages
2. Run verification: `python scripts/init_database.py --verify`
3. Try force recreation: `python scripts/init_database.py --force`
4. Check file permissions on `data/` directory
5. Ensure no other processes are using the database

---

## 🎯 Best Practices

1. **Always backup before:**
   - Resetting database
   - Running migrations
   - Upgrading the system

2. **Monitor database size:**
   - SQLite works well up to several GB
   - Consider archiving old invoices

3. **Regular maintenance:**
   - Run VACUUM monthly
   - Check for orphaned files
   - Verify data integrity

4. **Development vs Production:**
   - Use separate databases
   - Never test on production data
   - Keep production backups secure

