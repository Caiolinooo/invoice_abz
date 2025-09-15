#!/usr/bin/env python3
"""
Test script for the new single-file API endpoint
"""
import sys
import requests
from pathlib import Path

# Add app to path
sys.path.append('app')

def test_single_file_import():
    """Test the new single-file import endpoint"""
    
    # Path to the ABZ file
    abz_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
    
    if not abz_path.exists():
        print(f"ABZ file not found: {abz_path}")
        return False
    
    print(f"Testing single-file import with: {abz_path}")
    
    # Test the API endpoint
    url = "http://localhost:8000/api/import"
    
    try:
        with open(abz_path, 'rb') as f:
            files = {'abz': (abz_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Import successful!")
            print(f"Session ID: {data.get('session_id')}")
            print(f"Employees: {data.get('employees')}")
            return data.get('session_id')
        else:
            print(f"❌ Import failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_preview(session_id):
    """Test the preview endpoint"""
    if not session_id:
        return False
        
    url = f"http://localhost:8000/api/preview?session_id={session_id}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("✅ Preview successful!")
            preview = data.get('preview', {})
            for name, details in preview.items():
                print(f"\n👤 {name}:")
                for item in details.get('items', []):
                    print(f"  - {item.get('description')}: £{item.get('final', 0):.2f}")
            return True
        else:
            print(f"❌ Preview failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Preview error: {e}")
        return False

def test_direct_parsing():
    """Test direct parsing without API"""
    from utils.abz_charge_rate_parser import read_charge_rate_table
    
    abz_path = Path('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
    
    print("\n🔍 Testing direct parsing...")
    try:
        df = read_charge_rate_table(abz_path, 'Charge Rate')
        print(f"✅ Parsed {len(df)} rows")
        print("Columns:", df.columns.tolist())
        
        # Show sample data
        for name in df['Name'].dropna().unique()[:2]:
            sub = df[df['Name'] == name]
            print(f"\n👤 {name}:")
            for _, row in sub.iterrows():
                days = row.get('Days', 0)
                rate = row.get('Charge Rate (GBP)', 0)
                additional = row.get('Brazilian Payroll Additionals (GBP)', 0)
                expenses = row.get('Expenses', 0)
                print(f"  - Days: {days}, Rate: £{rate}, Additional: £{additional}, Expenses: £{expenses}")
        
        return True
    except Exception as e:
        print(f"❌ Direct parsing error: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Single-File API ===\n")
    
    # Test direct parsing first
    if not test_direct_parsing():
        print("Direct parsing failed, stopping tests")
        sys.exit(1)
    
    # Test API import
    session_id = test_single_file_import()
    
    if session_id:
        # Test preview
        test_preview(session_id)
    
    print("\n=== Test Complete ===")
