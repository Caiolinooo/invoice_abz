# 🎉 Release Notes - Version 12.1

**Release Date:** January 6, 2025  
**Previous Version:** 12.0  
**Repository:** [invoice_abz](https://github.com/Caiolinooo/invoice_abz)  
**Tag:** [v12.1](https://github.com/Caiolinooo/invoice_abz/releases/tag/v12.1)

---

## 🌟 What's New in v12.1

### 📅 Billing Period in Filenames

The **biggest feature** of this release: Invoice filenames now use the **billing period** extracted from the ABZ filename instead of the invoice emission date!

---

## 🎯 The Problem We Solved

### Before v12.1 (❌ Confusing):

When you uploaded an ABZ file for **August 2025** services but generated the invoice in **January 2025**, the filename would show:

```
ABZ Group 141-2025 OMEGA 01 2025 Caio.xlsx
                           ^^
                    (January - emission date)
```

**Problem:** The filename suggested this was for January services, but it was actually for August!

### After v12.1 (✅ Clear):

Now the filename correctly shows the billing period:

```
ABZ Group 141-2025 OMEGA 08 2025 Caio.xlsx
                           ^^
                    (August - billing period from ABZ filename)
```

**Solution:** The filename clearly indicates this invoice is for August 2025 services!

---

## 📊 Real-World Example

### Scenario:
- **ABZ File:** `ABZ - OMEGA - Maximus Project - Monthly Charge Rates 08.2025.xlsx`
- **Services Period:** August 2025
- **Invoice Generated:** January 15, 2025
- **Invoice Emission Date:** 15/01/2025

### Generated Filename:
```
ABZ Group 141-2025 OMEGA 08 2025 Caio.xlsx
```

**Breakdown:**
- `141` = Invoice number
- `2025` = Year
- `OMEGA` = Client name
- `08` = **Billing period (August)** ← From ABZ filename!
- `2025` = Year again
- `Caio` = Employee first name

---

## ✨ Key Benefits

### 1. 📁 Better Organization
Organize your invoices by billing period, not emission date:
```
📂 Invoices/
  📂 2025-08-August/
    ├── ABZ Group 141-2025 OMEGA 08 2025 Caio.xlsx
    ├── ABZ Group 142-2025 OMEGA 08 2025 Filipi.xlsx
    └── ABZ Group 143-2025 OMEGA 08 2025 Gil.xlsx
  📂 2025-09-September/
    ├── ABZ Group 144-2025 OMEGA 09 2025 Caio.xlsx
    └── ABZ Group 145-2025 OMEGA 09 2025 Filipi.xlsx
```

### 2. 🎯 Crystal Clear
No more confusion about which period an invoice covers:
- Filename shows: `08 2025` → August 2025 services
- Not the emission date (January 2025)

### 3. 🔍 Easy Search
Find all invoices for a specific period:
- Search for: `*08 2025*.xlsx`
- Results: All August 2025 invoices

### 4. 🔄 Backward Compatible
If ABZ path is not available, the system falls back to using the invoice emission date (old behavior).

---

## 🛠️ Technical Implementation

### New Function: Period Extraction

```python
def extract_period_from_abz_filename(abz_path: Path) -> tuple[str, str]:
    """
    Extract billing period from ABZ filename
    
    Supported formats:
    - MM.YYYY (e.g., 08.2025)
    - MM YYYY (e.g., 08 2025)
    - MM-YYYY (e.g., 08-2025)
    - YYYY-MM (e.g., 2025-08)
    - YYYY.MM (e.g., 2025.08)
    """
```

### Updated Function: Filename Generation

```python
def generate_standardized_filename(...):
    # PRIORITY: Use billing period from ABZ filename
    if abz_path:
        month, year = extract_period_from_abz_filename(abz_path)
    else:
        # FALLBACK: Use invoice emission date
        month, year = extract_month_year_from_date(invoice_date)
    
    # Build filename with billing period
    filename = f"ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}.{extension}"
    return filename
```

---

## 🧪 Testing

All tests passing with 100% success rate:

### Test 1: Period Extraction
```
✅ ABZ - OMEGA - Charge Rates 08.2025.xlsx → 08/2025
✅ ABZ - FMS - Project 09 2025.xlsx → 09/2025
✅ ABZ - OMEGA - Charge Rates 10.2025.xlsx → 10/2025
✅ ABZ_OMEGA_11-2025.xlsx → 11/2025
✅ ABZ - CLIENT - 2025-12.xlsx → 12/2025
```

### Test 2: Filename Generation
```
✅ Billing Period: 08/2025, Invoice Date: 01/2025
   Generated: ABZ Group 141-2025 OMEGA 08 2025 Caio.xlsx
   (uses 08/2025 from ABZ, NOT 01/2025 from invoice date)

✅ Billing Period: 09/2025, Invoice Date: 02/2025
   Generated: ABZ Group 142-2025 FMS 09 2025 Filipi.xlsx
   (uses 09/2025 from ABZ, NOT 02/2025 from invoice date)

✅ Billing Period: 10/2025, Invoice Date: 03/2025
   Generated: ABZ Group 143-2025 OMEGA 10 2025 Gil.xlsx
   (uses 10/2025 from ABZ, NOT 03/2025 from invoice date)
```

### Test 3: Fallback Behavior
```
✅ No ABZ path provided
   Generated: ABZ Group 999-2025 CLIENT 05 2025 Test.xlsx
   (falls back to invoice date: 05/2025)
```

---

## 📁 Files Modified

### Core Implementation
- **app/utils/filename_standardizer.py**
  - Added `extract_period_from_abz_filename()` function
  - Updated `generate_standardized_filename()` to prioritize billing period
  - Enhanced test cases

### Documentation
- **BILLING_PERIOD_VS_INVOICE_DATE.md** (NEW)
  - Comprehensive guide explaining the difference
  - Technical implementation details
  - Examples and use cases

- **CHANGELOG.md** (UPDATED)
  - Added v12.1 section
  - Detailed feature description
  - Benefits and technical details

- **README.md** (UPDATED)
  - Version badge: 11.3.0 → 12.1.0
  - Added v12.1 features section
  - Updated "What's New" section

---

## 🔄 Breaking Changes

**None!** This release is fully backward compatible.

- If ABZ path is provided → Uses billing period (new behavior)
- If ABZ path is NOT provided → Falls back to invoice date (old behavior)

---

## 📦 Installation & Upgrade

### Fresh Installation

```bash
git clone https://github.com/Caiolinooo/invoice_abz.git
cd invoice_abz
python run_server.py  # Dependencies auto-installed!
```

### Upgrade from v12.0

```bash
git pull origin master
python run_server.py  # You're ready to go!
```

---

## 🎯 Quick Start Guide

### Step 1: Start the Server
```bash
python run_server.py
```

### Step 2: Open Your Browser
Navigate to: http://127.0.0.1:8000/ui/

### Step 3: Upload ABZ File
Make sure your ABZ filename includes the billing period:
```
✅ ABZ - OMEGA - Maximus Project - Monthly Charge Rates 08.2025.xlsx
✅ ABZ - FMS - Project 09 2025.xlsx
✅ ABZ_OMEGA_10.2025.xlsx
```

### Step 4: Generate Invoices
Click "Generate Invoices" and watch the magic happen!

### Step 5: Check Filenames
Your generated files will have the billing period:
```
ABZ Group 141-2025 OMEGA 08 2025 Caio.xlsx
ABZ Group 142-2025 OMEGA 08 2025 Filipi.xlsx
```

---

## 📚 Documentation

### New Documentation
- **BILLING_PERIOD_VS_INVOICE_DATE.md**
  - Complete guide on billing period vs invoice date
  - Technical implementation details
  - Examples and best practices

### Updated Documentation
- **CHANGELOG.md** - Version 12.1 section added
- **README.md** - Updated to reflect v12.1 features

### Existing Documentation
- **RELEASE_NOTES_v12.0.md** - Previous release notes
- **AUTO_INSTALL_DEPENDENCIES.md** - Auto-install guide
- **EXPENSES_FALLBACK_SUMMARY.md** - Expenses handling

---

## 🐛 Bug Fixes

No bugs fixed in this release (feature-only release).

---

## 🔮 What's Next?

### Planned for v12.2
- Enhanced period detection for edge cases
- Support for quarterly billing periods
- Improved error messages for invalid ABZ filenames

### Planned for v13.0
- Multi-currency support enhancements
- Batch processing improvements
- Advanced reporting features

---

## 📊 Release Statistics

| Metric | Value |
|--------|-------|
| **Version** | 12.1.0 |
| **Release Date** | January 6, 2025 |
| **Commits** | 3 |
| **Files Modified** | 4 |
| **Lines Added** | ~400 |
| **Lines Removed** | ~20 |
| **Tests** | 9 (all passing) |
| **Documentation** | 3 files |
| **Breaking Changes** | 0 |

---

## 🙏 Acknowledgments

Special thanks to:
- The ABZ Group team for feedback and requirements
- All users who reported the filename confusion issue
- The development team for implementing this feature

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
1. Check the documentation in the `/docs` folder
2. Review the CHANGELOG for recent changes
3. Open an issue on GitHub
4. Contact the development team

---

## 🔗 Links

- **Repository:** https://github.com/Caiolinooo/invoice_abz
- **Release v12.1:** https://github.com/Caiolinooo/invoice_abz/releases/tag/v12.1
- **Release v12.0:** https://github.com/Caiolinooo/invoice_abz/releases/tag/v12.0
- **Issues:** https://github.com/Caiolinooo/invoice_abz/issues
- **Commits:** https://github.com/Caiolinooo/invoice_abz/commits/master

---

## 📝 Version History

- **v12.1** (2025-01-06) - Billing Period in Filenames
- **v12.0** (2025-01-06) - Expenses Override + AN-FIN Upload + Auto-Install
- **v11.3** (2024-12-XX) - Database Integration & System Diagnostics
- **v11.2** (2024-12-XX) - Login System Fix
- **v11.1** (2024-12-XX) - Expenses Correction

---

**🎉 Happy Invoicing with v12.1! 🎉**

*Developed with ❤️ for ABZ Group Invoice System*

---

*Last updated: January 6, 2025*

