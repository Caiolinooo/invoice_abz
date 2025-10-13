# 🎉 Release Notes - Version 12.0

**Release Date:** January 6, 2025  
**Previous Version:** 11.4  
**Repository:** [invoice_abz](https://github.com/Caiolinooo/invoice_abz)

---

## 🌟 What's New in v12.0

### 1. 💰 Expenses & Additional Override System

Now you can **manually override** Brazilian Payroll Additional and Expenses values directly in the preview!

**Features:**
- ✅ Override fields for Brazilian Payroll Additional
- ✅ Override fields for Expenses
- ✅ Real-time preview updates
- ✅ Per-employee override capability
- ✅ Bilingual support (Portuguese/English)

**Use Cases:**
- Correct discrepancies in expense values
- Adjust additional payments manually
- Override values when source data is incorrect

**How to Use:**
1. Import your ABZ file
2. In the preview table, find the "Override Additional" and "Override Expenses" columns
3. Enter the new values you want to use
4. Generate invoices - the overridden values will be used!

---

### 2. 📁 AN-FIN File Upload (Optional)

Upload the AN-FIN file for **more accurate expense data**!

**Features:**
- ✅ New upload field for AN-FIN file
- ✅ Intelligent fallback system: AN-FIN → ABZ → £0.00
- ✅ Expenses priority: AN-FIN (most accurate) > ABZ (fallback)
- ✅ Clear UI messages about optional nature

**Expense Priority:**
```
1. AN-FIN (Costs sheet) ← Most accurate, preferred source
   ↓ (if not found)
2. ABZ Expenses column ← Reliable fallback
   ↓ (if no data)
3. £0.00 ← Last resort (can use override)
```

**How to Use:**
1. Select your ABZ file (required)
2. Select your AN-FIN file (optional)
3. Click "Import"
4. Expenses will be loaded from the most accurate source available!

---

### 3. 🚀 Auto-Install Dependencies

No more manual `pip install`! The server now **installs missing dependencies automatically**.

**Features:**
- ✅ Automatic dependency installation on startup
- ✅ Tries requirements.txt first (faster batch install)
- ✅ Falls back to individual package installation
- ✅ Smart timeout handling (5min for requirements.txt, 2min per package)
- ✅ Clear progress messages during installation

**Dependencies Checked:**
- fastapi
- uvicorn
- openpyxl
- pandas
- python-multipart
- supabase
- pydantic
- python-dotenv

**How It Works:**
```
1. Check if dependency is installed
   ↓
2. Missing dependency found?
   ↓
3. Try: pip install -r requirements.txt
   ↓ (if fails)
4. Try: pip install <package> (individually)
   ↓
5. All installed? → Start server!
```

---

### 4. 🔍 Enhanced Server Startup Script

Complete **pre-flight checks** before starting the server!

**Checks Performed:**
- ✅ Python version (3.8+ required)
- ✅ All dependencies installed
- ✅ LibreOffice installation (for PDF export)
- ✅ .env file exists and valid
- ✅ Database connectivity
- ✅ Required directories exist

**Beautiful Console Output:**
```
============================================================
  SERVIDOR DE DESENVOLVIMENTO - PAYROLL CONVERSION API
============================================================

🔍 Verificando versão do Python...
✅ Python 3.13.3

🔍 Verificando dependências...
  ✅ fastapi
  ✅ uvicorn
  ✅ openpyxl
  ...

🔍 Verificando LibreOffice...
✅ LibreOffice encontrado

🔍 Verificando banco de dados...
✅ Banco de dados inicializado

============================================================
  ✅ SERVIDOR INICIADO COM SUCESSO!
============================================================

📋 URLs DISPONÍVEIS:
   🏠 Interface Web:  http://127.0.0.1:8000/ui/
   📚 API Docs:       http://127.0.0.1:8000/docs

🔐 AUTENTICAÇÃO:
   ✅ Sistema de autenticação ativo
   ✅ Rate limiting: 5 requisições/minuto
   ✅ Audit logging habilitado
```

---

## 🐛 Bug Fixes

### Critical: Expenses Not Showing in Preview

**Problem:**
- Expenses were detected in ABZ file but not appearing in preview
- All employees showed £0.00 for expenses

**Root Cause:**
- The `aggregate_employee()` function was modified to exclude expenses
- Server code still depended on aggregator for expense data

**Solution:**
- ✅ Restored expenses support in aggregator with type 'expenses'
- ✅ Added detailed debug logging
- ✅ Expenses now appear correctly from ABZ or AN-FIN

**Result:**
```
[preview] Expenses sum: 4847.95
[DEBUG] ALLAN OLIVEIRA CARNEIRO - Expenses from ABZ (fallback): £263.34
[DEBUG] BRYAN BARRETO RODRIGUES - Expenses from ABZ (fallback): £474.28
```

---

### Database Module Path Error

**Problem:**
```
⚠️  Erro ao inicializar banco: No module named 'app.api.database'
```

**Root Cause:**
- Wrong import path: `app.api.database` vs `app.database.database`

**Solution:**
- ✅ Corrected import path
- ✅ Added existence check before importing
- ✅ Database initializes correctly without blocking server

---

## 📊 Technical Details

### Files Modified

**Frontend:**
- `app/ui/index.html` - Override fields + AN-FIN upload
- `app/ui/i18n.js` - Translations for new features
- `app/ui/app.js` - Override logic + AN-FIN handling

**Backend:**
- `app/api/server.py` - Expenses fallback logic
- `app/utils/abz_charge_rate_parser.py` - Restored expenses support

**Infrastructure:**
- `run_server.py` - Complete rewrite with auto-install + checks

### Documentation Added

- `AUTO_INSTALL_DEPENDENCIES.md`
- `EXPENSES_ADDITIONAL_OVERRIDE_IMPLEMENTATION.md`
- `EXPENSES_FALLBACK_SUMMARY.md`
- `FINAL_FIX_EXPENSES_AND_SERVER.md`
- `FIX_EXPENSES_UPLOAD.md`
- `CHANGELOG.md` (updated)
- `RELEASE_NOTES_v12.0.md` (this file)

---

## 🔄 Breaking Changes

**None!** Version 12.0 is **fully backward compatible** with v11.4.

---

## ⚡ Performance Improvements

- **Faster Startup:** Batch install via requirements.txt is faster than individual packages
- **Reduced Manual Work:** No more manual dependency installation
- **Better Error Handling:** Clear messages guide users to solutions

---

## 🧪 Testing

Tested scenarios:
- ✅ ABZ only (expenses from ABZ column)
- ✅ ABZ + AN-FIN (expenses from AN-FIN, more accurate)
- ✅ Override functionality (manual adjustments)
- ✅ Auto-install on fresh environment
- ✅ All pre-flight checks passing

---

## 📦 Installation & Upgrade

### Fresh Installation

```bash
git clone https://github.com/Caiolinooo/invoice_abz.git
cd invoice_abz
python run_server.py  # Dependencies will be installed automatically!
```

### Upgrade from v11.4

```bash
git pull origin master
python run_server.py  # New dependencies will be installed automatically!
```

---

## 🎯 Quick Start

1. **Start the server:**
   ```bash
   python run_server.py
   ```

2. **Open your browser:**
   - Navigate to: http://127.0.0.1:8000/ui/

3. **Upload files:**
   - Select ABZ file (required)
   - Select AN-FIN file (optional, for accurate expenses)

4. **Review preview:**
   - Check expenses values
   - Use override fields if needed

5. **Generate invoices:**
   - Click "Generate Invoices"
   - Download your invoices!

---

## 📚 Documentation

- [CHANGELOG.md](CHANGELOG.md) - Complete version history
- [AUTO_INSTALL_DEPENDENCIES.md](AUTO_INSTALL_DEPENDENCIES.md) - Auto-install details
- [EXPENSES_FALLBACK_SUMMARY.md](EXPENSES_FALLBACK_SUMMARY.md) - Expense handling
- [README.md](README.md) - Project overview

---

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

For questions or issues:
1. Check the documentation
2. Review the CHANGELOG
3. Open an issue on GitHub
4. Contact the development team

---

## 🙏 Acknowledgments

Developed with ❤️ for **ABZ Group Invoice System**

Special thanks to all contributors and testers!

---

**Version:** 12.0  
**Release Date:** January 6, 2025  
**Git Tag:** v12.0  
**Commit:** [View on GitHub](https://github.com/Caiolinooo/invoice_abz/releases/tag/v12.0)

---

*Happy invoicing! 🎉*

