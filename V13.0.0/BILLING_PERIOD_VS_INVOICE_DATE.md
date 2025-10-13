# Billing Period vs Invoice Date - Implementation Guide

## 📋 Overview

This document explains the difference between **Billing Period** and **Invoice Date**, and how they are used in the invoice generation system.

---

## 🎯 Key Concepts

### 1. Billing Period (Período de Faturamento)
- **Definition**: The month/year that the services were provided
- **Source**: Extracted from the ABZ filename
- **Usage**: Used in the generated invoice filenames (XLSX and PDF)
- **Example**: If ABZ file is `ABZ - OMEGA - Charge Rates 08.2025.xlsx`, the billing period is **August 2025**

### 2. Invoice Date (Data de Emissão)
- **Definition**: The date when the invoice is issued/generated
- **Source**: Provided by the user or system at generation time
- **Usage**: Used internally in the invoice document, NOT in the filename
- **Example**: Invoice might be issued on **January 15, 2025** for services provided in **August 2025**

---

## 🔍 Why This Matters

### Problem Before Fix:
The system was using the **Invoice Date** (emission date) in the filename, which caused confusion:
- Invoice issued in January for August services would have "01 2025" in the filename
- This made it difficult to identify which billing period the invoice was for

### Solution After Fix:
The system now uses the **Billing Period** from the ABZ filename:
- Invoice issued in January for August services will have "08 2025" in the filename
- This makes it clear which period the invoice covers

---

## 📁 Filename Format

### Current Format:
```
ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}.{extension}
```

### Example:
```
ABZ Group 141-2025 OMEGA 08 2025 Caio.xlsx
```

**Breakdown:**
- `141` = Invoice number
- `2025` = Year (from billing period)
- `OMEGA` = Client name (from ABZ filename)
- `08` = Month (from billing period in ABZ filename)
- `2025` = Year again (from billing period)
- `Caio` = Employee first name

---

## 🔧 Technical Implementation

### 1. Period Extraction Function

Located in: `app/utils/filename_standardizer.py`

```python
def extract_period_from_abz_filename(abz_path: Path) -> tuple[str, str]:
    """
    Extract period (month and year) from ABZ filename
    
    Examples:
    - "ABZ - OMEGA - Charge Rates 08.2025.xlsx" -> ("08", "2025")
    - "ABZ - FMS - Project 09 2025.xlsx" -> ("09", "2025")
    """
```

**Supported Patterns:**
- `MM.YYYY` (e.g., `08.2025`)
- `MM YYYY` (e.g., `08 2025`)
- `MM-YYYY` (e.g., `08-2025`)
- `YYYY-MM` or `YYYY.MM` (e.g., `2025-08`)

### 2. Filename Generation

```python
def generate_standardized_filename(
    employee_name: str,
    invoice_no: Optional[str] = None,
    invoice_date: Optional[str] = None,  # NOT used in filename!
    abz_path: Optional[Path] = None,     # Used to extract billing period
    extension: str = "xlsx"
) -> str:
    """
    Generate standardized filename with BILLING PERIOD from ABZ filename
    """
    # Extract billing period from ABZ filename
    if abz_path:
        month, year = extract_period_from_abz_filename(abz_path)
    else:
        # Fallback to invoice date if ABZ path not available
        month, year = extract_month_year_from_date(invoice_date)
    
    # Build filename with billing period
    filename = f"ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}.{extension}"
    return filename
```

---

## 📊 Examples

### Example 1: August 2025 Services, Issued in January 2025

**ABZ Filename:**
```
ABZ - OMEGA - Maximus Project - Monthly Charge Rates 08.2025.xlsx
```

**Invoice Date (Emission):**
```
15/01/2025
```

**Generated Filename:**
```
ABZ Group 141-2025 OMEGA 08 2025 Caio.xlsx
```

**Note:** Uses `08 2025` from ABZ filename, NOT `01 2025` from invoice date!

---

### Example 2: September 2025 Services, Issued in February 2025

**ABZ Filename:**
```
ABZ - FMS - Project 09 2025.xlsx
```

**Invoice Date (Emission):**
```
10/02/2025
```

**Generated Filename:**
```
ABZ Group 142-2025 FMS 09 2025 Gil.xlsx
```

**Note:** Uses `09 2025` from ABZ filename, NOT `02 2025` from invoice date!

---

## 🧪 Testing

Run the test suite to verify the implementation:

```bash
python app/utils/filename_standardizer.py
```

**Expected Output:**
```
🧪 Testing filename standardization...
📌 IMPORTANT: Filename should use BILLING PERIOD from ABZ filename, NOT invoice emission date

  1. ✅ ABZ Group 141-2025 FMS 09 2025 Filipi.xlsx
     Billing Period: 09/2025 (from ABZ filename)
     Invoice Date: 01/2025 (emission date, NOT used in filename)

  2. ✅ ABZ Group 142-2025 OMEGA 04 2025 Gil.xlsx
     Billing Period: 04/2025 (from ABZ filename)
     Invoice Date: 02/2025 (emission date, NOT used in filename)

  3. ✅ ABZ Group 143-2025 OMEGA 08 2025 Caio.xlsx
     Billing Period: 08/2025 (from ABZ filename)
     Invoice Date: 03/2025 (emission date, NOT used in filename)
```

---

## 📝 Files Modified

### 1. `app/utils/filename_standardizer.py`
- ✅ Added `extract_period_from_abz_filename()` function
- ✅ Updated `generate_standardized_filename()` to use billing period
- ✅ Updated test cases to verify correct behavior

### 2. `app/invoice/template_filler.py`
- ✅ Already passes `abz_path` to `generate_standardized_filename()`
- ✅ No changes needed (already compatible)

### 3. `app/api/server.py`
- ✅ Already passes `abz_xlsx` to `generate_from_abz_template()`
- ✅ No changes needed (already compatible)

---

## ✅ Verification Checklist

- [x] Period extraction function implemented
- [x] Filename generation updated to use billing period
- [x] Test cases added and passing
- [x] Documentation created
- [x] Backward compatibility maintained (fallback to invoice date if ABZ path not available)

---

## 🔄 Backward Compatibility

The system maintains backward compatibility:
- If `abz_path` is provided → Uses billing period from filename
- If `abz_path` is NOT provided → Falls back to invoice date

This ensures the system works even in edge cases where the ABZ path might not be available.

---

## 📚 Related Files

- `app/utils/filename_standardizer.py` - Core implementation
- `app/invoice/template_filler.py` - Invoice generation
- `app/api/server.py` - API endpoints
- `BILLING_PERIOD_VS_INVOICE_DATE.md` - This documentation

---

## 🎉 Benefits

1. **Clarity**: Filenames now clearly indicate the billing period
2. **Organization**: Easier to organize invoices by billing period
3. **Accuracy**: No confusion between emission date and billing period
4. **Consistency**: All invoices follow the same naming convention

---

**Version:** 12.1  
**Date:** 2025-01-06  
**Author:** ABZ Group Invoice System Team

---

*For questions or issues, please refer to the main documentation or contact the development team.*

