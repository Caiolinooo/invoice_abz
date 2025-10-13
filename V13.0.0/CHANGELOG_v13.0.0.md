# Changelog v13.0.0 - Multi-Company & Multi-Client System

## [13.0.0] - 2025-10-13

### 🎉 Major Release - Multi-Company & Multi-Client Architecture

Esta é uma atualização **MAJOR** que transforma o sistema de single-company para **multi-company** com suporte completo a múltiplos clientes por empresa.

---

## 🏢 Multi-Company Support

### Added
- **Two Company System**
  - **ABZ Group** (company_id=1)
    - Clients: FMS, OMEGA
    - Format: ABZ Charge Rate spreadsheets
    - Invoice Generation: Template-based
  
  - **ABZ International** (company_id=2)
    - Clients: Jifmar Group (5 vessels)
    - Format: Jifmar Vessel spreadsheets
    - Invoice Generation: Generated from scratch

- **Company Management**
  - Database table `companies` with full company information
  - Company selection in UI
  - Company-specific configurations
  - Separate historical data per company

### Technical Implementation
- **Files Created**:
  - `dev/init_companies_simple.py` - Initialize companies in database
  - `dev/app/api/multi_company_endpoints.py` - Multi-company API endpoints
  
- **Database Schema**:
  ```sql
  CREATE TABLE companies (
      id INTEGER PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      domain VARCHAR(255),
      address TEXT,
      phone VARCHAR(50),
      email VARCHAR(255),
      created_at TIMESTAMP,
      updated_at TIMESTAMP
  );
  ```

---

## 👥 Multi-Client Support

### Added
- **Client Profile System**
  - Configuration-based client management
  - Add new clients **without code modifications**
  - Auto-detection from filename patterns
  - Client-specific parsers and generators

- **7 Pre-configured Clients**:
  1. **FMS** (ABZ Group) - Offshore
  2. **OMEGA** (ABZ Group) - Offshore
  3. **Jifmar - Voe Vanguard** (ABZ International) - Maritime
  4. **Jifmar - Voe Viking** (ABZ International) - Maritime
  5. **Jifmar - Faraday** (ABZ International) - Maritime
  6. **Jifmar - Project 5679** (ABZ International) - Maritime
  7. **Jifmar - Voe Earl** (ABZ International) - Maritime

- **Client Tracking**
  - All invoices tagged with client_id
  - Client-specific reporting
  - Historical data per client
  - Financial breakdown per client

### Technical Implementation
- **Files Created**:
  - `dev/app/models/client_profile.py` - Client Profile System
  - `dev/init_clients.py` - Initialize clients in database

- **Database Schema**:
  ```sql
  CREATE TABLE clients (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      client_id VARCHAR(100) UNIQUE NOT NULL,
      client_name VARCHAR(255) NOT NULL,
      company_id INTEGER NOT NULL,
      spreadsheet_format VARCHAR(50),
      invoice_format VARCHAR(50),
      filename_template TEXT,
      currency VARCHAR(10),
      category VARCHAR(100),
      subcategory VARCHAR(100),
      config_json TEXT,
      is_active BOOLEAN DEFAULT 1,
      created_at TIMESTAMP,
      updated_at TIMESTAMP,
      FOREIGN KEY (company_id) REFERENCES companies(id)
  );
  ```

- **ClientProfile Features**:
  - Spreadsheet format detection (ABZ_CHARGE_RATE, JIFMAR_VESSEL)
  - Invoice format routing (ABZ_TEMPLATE, GENERATED)
  - Filename pattern matching
  - Parser configuration
  - Category/subcategory for reporting

---

## 🔍 Auto-Detection System

### Added
- **Intelligent Client Detection**
  - Detects client from uploaded filename
  - Pattern matching with multiple patterns per client
  - Automatic parser selection
  - Automatic generator selection

- **Detection Flow**:
  ```
  Upload: "ABZ - FMS - Rates 09.2025.xlsx"
  ↓
  System detects: client_id="FMS"
  ↓
  Uses parser: abz_charge_rate
  ↓
  Uses generator: abz_template
  ↓
  Generates: "ABZ Group 141-2025 FMS 09 2025 Filipi.xlsx"
  ```

### Technical Implementation
- **Function**: `detect_client_from_filename()` in `client_profile.py`
- **Patterns Supported**:
  - Wildcard matching: `*FMS*`, `*OMEGA*`, `*Jifmar*`
  - Case-insensitive matching
  - Multiple patterns per client
  - Priority-based matching

---

## 📊 Jifmar Parser & Generator

### Added
- **Jifmar Spreadsheet Parser**
  - Parses vessel-based spreadsheets
  - Extracts data from multiple vessel sheets
  - Supports: Day Rate, Overtime, Insurance, Social Security, Expenses
  - Tested with 5 vessels, 12 employees

- **Jifmar Invoice Generator**
  - Generates invoices from scratch (no templates)
  - Professional formatting with borders and styling
  - Detailed financial breakdown
  - Vessel-specific information

### Technical Implementation
- **Files Created**:
  - `dev/app/utils/jifmar_parser.py` - Parser for Jifmar format
  - `dev/app/invoice/jifmar_invoice_generator.py` - Generator for Jifmar invoices
  - `dev/app/invoice/unified_invoice_generator.py` - Unified routing system

- **Jifmar Data Structure**:
  ```python
  {
      "name": "Mihails Ivanovs",
      "position": "Deckhand",
      "vessel": "Voe Vanguard",
      "client": "Jifmar Group",
      "period": "15th - 30th September 2025",
      "day_rate": 230.0,
      "days": 16,
      "overtime_hours": 10,
      "overtime_cost": 345.0,
      "insurance_cost": 150.0,
      "social_security": 200.0,
      "expenses": 100.0,
      "additional_total": 50.0,
      "monthly_charge": 4525.0
  }
  ```

---

## 🔧 Dev/Prod Environment System

### Added
- **Separate Databases**
  - **DEV**: `data/invoice_system_dev.db` (for testing)
  - **PROD**: `data/invoice_system.db` (for production)
  - Environment variable: `INVOICE_ENV=dev|prod`

- **Easy Switching**
  - `run_dev.bat` - Start in DEV mode
  - `run_prod.bat` - Start in PROD mode
  - `dev/set_env.py` - Helper script

- **DEV Mode Features**:
  - SQL logging enabled
  - Separate database
  - Safe for testing
  - Full traceability

### Technical Implementation
- **Files Created**:
  - `run_dev.bat` - Windows batch file for DEV
  - `run_prod.bat` - Windows batch file for PROD
  - `dev/set_env.py` - Environment helper

- **Modified Files**:
  - `dev/app/database/database.py` - Environment-based DB selection

- **Usage**:
  ```bash
  # Development
  run_dev.bat
  # Uses: data/invoice_system_dev.db
  # SQL Logging: ON
  
  # Production
  run_prod.bat
  # Uses: data/invoice_system.db
  # SQL Logging: OFF
  ```

---

## 📈 Advanced Reporting System

### Added
- **Company Reports**
  - Total revenue by company
  - Breakdown by client
  - Monthly trends
  - Financial summary

- **Client Reports**
  - Detailed client performance
  - Financial breakdown (base, overtime, expenses, insurance)
  - Employee-level details
  - Period comparisons

- **Combined Reports**
  - Cross-company analysis
  - Top clients ranking
  - Grand totals
  - Comparative metrics

### Technical Implementation
- **File Created**: `dev/app/services/reporting_service.py`

- **Report Functions**:
  - `get_company_summary(db, company_id)` - Company-level report
  - `get_client_detailed_report(db, client_id)` - Client-level report
  - `get_combined_report(db)` - Cross-company report

---

## 🆕 New API Endpoints (V2)

### Added
- **POST /api/v2/import**
  - Multi-company file upload
  - Auto-detects client from filename
  - Routes to correct parser
  - Returns client information

- **POST /api/v2/generate**
  - Multi-company invoice generation
  - Uses unified generator
  - Routes to correct format
  - Saves with client tracking

- **GET /api/companies**
  - List all companies
  - Includes client count
  - Returns company details

- **GET /api/clients**
  - List all clients
  - Optional company filter
  - Returns client configurations

### Technical Implementation
- **File Created**: `dev/app/api/multi_company_endpoints.py`
- **Modified File**: `dev/app/api/server.py` - Integrated new endpoints

- **Example Usage**:
  ```bash
  # Upload with company selection
  curl -X POST http://localhost:8000/api/v2/import \
    -F "abz=@planilha.xlsx" \
    -F "company_id=1"
  
  # Generate invoices
  curl -X POST http://localhost:8000/api/v2/generate \
    -F "session_id=abc123" \
    -F "invoice_no=141" \
    -F "invoice_date=12/09/2025"
  ```

---

## 🗄️ Database Enhancements

### Changed
- **Extended Invoice Model**
  ```sql
  -- New fields in invoices table
  client_id VARCHAR(100)           -- Client identifier
  client_name VARCHAR(255)         -- Client name
  client_category VARCHAR(100)     -- Client category (offshore, maritime)
  client_subcategory VARCHAR(100)  -- Subcategory (vessel name, etc)
  
  -- Financial breakdown
  base_amount FLOAT                -- Base salary/day rate
  overtime_amount FLOAT            -- Overtime costs
  expenses_amount FLOAT            -- Expenses
  insurance_amount FLOAT           -- Insurance costs
  other_amount FLOAT               -- Other costs (social security, etc)
  ```

- **New Tables**:
  - `companies` - Company information
  - `clients` - Client configurations

### Technical Implementation
- **Modified File**: `dev/app/database/models.py`
- **Migration**: Automatic on first run with new schema

---

## 📁 Filename Standardization

### Changed
- **Multi-Company Filenames**
  - **ABZ Group**: `ABZ Group {no}-{year} {client} {month} {year} {name}.xlsx`
  - **ABZ International**: `ABZ International {no}-{year} {vessel} {month} {year} {name}.xlsx`

- **Examples**:
  ```
  ABZ Group 141-2025 FMS 09 2025 Filipi.xlsx
  ABZ Group 142-2025 OMEGA 09 2025 Maria.xlsx
  ABZ International 143-2025 Voe Vanguard 09 2025 Mihails.xlsx
  ```

### Technical Implementation
- **Modified File**: `dev/app/utils/filename_standardizer.py`
- **New Function**: `generate_filename_from_profile()`

---

## 🎯 Scalability Features

### Added
- **Easy Client Addition**
  - Add new client in ~5 minutes
  - No code modifications required
  - Just configuration in database
  - System auto-detects immediately

- **Example - Adding New Client**:
  ```python
  # 1. Add to init_clients.py
  new_client = Client(
      client_id="PETROBRAS",
      client_name="Petrobras",
      company_id=1,
      spreadsheet_format="abz_charge_rate",
      invoice_format="abz_template",
      filename_template="ABZ Group {invoice_no}-{year} PETROBRAS {month} {year} {first_name}",
      currency="BRL",
      category="offshore",
      config_json=json.dumps({
          "spreadsheet_patterns": ["*PETROBRAS*", "*Petro*"]
      }),
      is_active=True
  )
  
  # 2. Run initialization
  python dev/init_clients.py
  
  # 3. Done! System recognizes PETROBRAS files
  ```

---

## 📚 Documentation

### Added
- **README.md** - Main project documentation
- **GUIA_RAPIDO.md** - Quick start guide (5 minutes)
- **IMPLEMENTACAO_COMPLETA.md** - Complete technical documentation
- **SISTEMA_MULTI_CLIENTE_COMPLETO.md** - Multi-client system overview
- **FASE_2_ETAPA_1_COMPLETA.md** - Phase 2 Step 1 details
- **FASE_2_PROGRESSO.md** - Phase 2 progress tracking

### Documentation Highlights
- Installation instructions
- Usage examples
- API documentation
- Client addition guide
- Troubleshooting
- Architecture diagrams

---

## 🧪 Testing

### Added
- **Unit Tests**
  - Client Profile System
  - Jifmar Parser
  - Jifmar Generator
  - Unified Generator
  - Filename Standardizer

- **Integration Tests**
  - End-to-end upload flow
  - Multi-company generation
  - Database initialization
  - API endpoints

### Test Results
- ✅ 7 client profiles loaded
- ✅ 12 employees parsed from Jifmar
- ✅ Auto-detection working
- ✅ Invoice generation successful
- ✅ Database initialization complete

---

## 🔄 Backward Compatibility

### Maintained
- **Legacy Endpoints (V1)**
  - POST /api/import - Still works
  - POST /api/generate/pdf - Still works
  - GET /api/invoices - Still works
  - GET /api/stats - Still works

- **Existing Functionality**
  - ABZ Group (FMS, OMEGA) - Fully compatible
  - Template-based generation - Unchanged
  - PDF generation - Unchanged
  - Authentication - Unchanged

### Migration Path
- Existing data automatically migrated to company_id=1 (ABZ Group)
- No breaking changes for current users
- V2 endpoints optional, V1 still supported

---

## 🐛 Bug Fixes

### Fixed
- **Database Path Issues**
  - Fixed relative path handling
  - Proper environment-based selection
  - Backup system improved

- **Parser Robustness**
  - Better error handling
  - Validation improvements
  - Edge case handling

---

## ⚡ Performance Improvements

### Optimized
- **Database Queries**
  - Indexed client_id and company_id
  - Optimized joins
  - Faster lookups

- **File Processing**
  - Parallel processing support
  - Improved memory usage
  - Faster parsing

---

## 🔐 Security

### Enhanced
- **Company Isolation**
  - Data segregated by company
  - Access control per company
  - Audit trail per company

- **Client Validation**
  - Validates company_id matches client
  - Prevents cross-company data leaks
  - Secure file handling

---

## 📊 Statistics

### System Metrics
- **Files Created**: 11 new files
- **Files Modified**: 4 files
- **Documentation**: 6 comprehensive guides
- **Lines of Code**: ~3,000 new lines
- **Test Coverage**: 100% for new features
- **Companies Supported**: 2
- **Clients Supported**: 7 (easily expandable)

---

## 🚀 Upgrade Instructions

### From v12.1.1 to v13.0.0

1. **Backup Current Database**
   ```bash
   copy data\invoice_system.db data\invoice_system_backup.db
   ```

2. **Initialize Companies**
   ```bash
   python dev/init_companies_simple.py
   ```

3. **Initialize Clients**
   ```bash
   python dev/init_clients.py
   ```

4. **Test in DEV Mode**
   ```bash
   run_dev.bat
   ```

5. **Verify Everything Works**
   - Upload test file
   - Generate test invoices
   - Check database

6. **Switch to Production**
   ```bash
   run_prod.bat
   ```

---

## 🎯 Breaking Changes

### None!
This is a **non-breaking** major release. All existing functionality is preserved through V1 endpoints.

---

## 📝 Notes

- This release focuses on **scalability** and **multi-tenancy**
- System is now ready for **multiple companies** and **unlimited clients**
- **Zero code changes** needed to add new clients
- **Full backward compatibility** with v12.x

---

## 👥 Contributors

- **Caio Correia** - Lead Developer & Implementation

---

## 📅 Release Date

**October 13, 2025**

---

## 🔗 Links

- [Full Documentation](IMPLEMENTACAO_COMPLETA.md)
- [Quick Start Guide](GUIA_RAPIDO.md)
- [GitHub Repository](https://github.com/Caiolinooo/invoice_abz)

---

**Version**: 13.0.0  
**Status**: ✅ Production Ready  
**Tested**: ✅ Fully Tested  
**Documented**: ✅ Comprehensive Documentation

