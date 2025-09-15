#!/usr/bin/env python3
"""
Test the single-file functionality directly without API
"""
import sys
from pathlib import Path

# Add app to path
sys.path.append('app')

def test_single_file_preview():
    """Test the new single-file preview function"""
    from api.server import _build_preview_single_file
    
    abz_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
    
    if not abz_path.exists():
        print(f"ABZ file not found: {abz_path}")
        return False
    
    print(f"Testing single-file preview with: {abz_path}")
    
    try:
        preview = _build_preview_single_file(abz_path)
        
        print("✅ Preview generation successful!")
        print(f"Found {len(preview)} employees:")
        
        for name, details in preview.items():
            print(f"\n👤 {name}:")
            items = details.get('items', [])
            total = sum(item.get('final', 0) for item in items)
            
            for item in items:
                desc = item.get('description', '')
                final = item.get('final', 0)
                unit_price = item.get('unit_price')
                quantity = item.get('quantity')
                
                if unit_price is not None and quantity is not None:
                    print(f"  - {desc}: £{unit_price:.2f} x {quantity} = £{final:.2f}")
                else:
                    print(f"  - {desc}: £{final:.2f}")
            
            print(f"  💰 Total: £{total:.2f}")
            
            # Show meta info if available
            meta = details.get('meta', {})
            if meta.get('invoice_no') or meta.get('invoice_date') or meta.get('call_off'):
                print(f"  📋 Meta: Invoice #{meta.get('invoice_no')}, Date: {meta.get('invoice_date')}, Call-off: {meta.get('call_off')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_with_legacy():
    """Compare single-file vs legacy two-file approach"""
    from api.server import _build_preview_single_file, _build_preview
    
    abz_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
    anfin_path = Path('DADOS/AN-FIN-005-R0 - Medição Offshore - Omega 08.2025 (1).xlsx')
    
    if not abz_path.exists() or not anfin_path.exists():
        print("Missing files for comparison")
        return False
    
    print("\n🔍 Comparing single-file vs legacy approach...")
    
    try:
        # Single file approach
        preview_single = _build_preview_single_file(abz_path)
        
        # Legacy two-file approach
        preview_legacy = _build_preview(abz_path, anfin_path)
        
        print(f"Single-file found {len(preview_single)} employees")
        print(f"Legacy found {len(preview_legacy)} employees")
        
        # Compare a specific employee
        test_name = None
        for name in preview_single.keys():
            if 'Caio' in name:
                test_name = name
                break
        
        if test_name:
            print(f"\n📊 Comparing {test_name}:")
            
            single_items = preview_single[test_name]['items']
            legacy_items = preview_legacy[test_name]['items']
            
            single_total = sum(item.get('final', 0) for item in single_items)
            legacy_total = sum(item.get('final', 0) for item in legacy_items)
            
            print(f"Single-file total: £{single_total:.2f}")
            print(f"Legacy total: £{legacy_total:.2f}")
            print(f"Difference: £{abs(single_total - legacy_total):.2f}")
            
            print("\nSingle-file items:")
            for item in single_items:
                print(f"  - {item.get('description')}: £{item.get('final', 0):.2f}")
            
            print("\nLegacy items:")
            for item in legacy_items:
                print(f"  - {item.get('description')}: £{item.get('final', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Comparison error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Testing Single-File Functionality ===\n")
    
    # Test single-file preview
    if test_single_file_preview():
        print("\n" + "="*50)
        # Compare with legacy
        compare_with_legacy()
    
    print("\n=== Test Complete ===")
