import requests
import json
from pathlib import Path

# Test the API generation with the same parameters
api_url = "http://localhost:8000"

# First, we need to upload files and get a session
files_data = {
    'abz': open('DADOS/ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx', 'rb'),
    'anfin': open('DADOS/AN-FIN-005-R0 - Medição Offshore - Omega 08.2025 (1).xlsx', 'rb')
}

try:
    print("Uploading files...")
    upload_response = requests.post(f"{api_url}/api/upload", files=files_data)
    if upload_response.status_code != 200:
        print("Upload failed:", upload_response.text)
        exit(1)
    
    session_data = upload_response.json()
    session_id = session_data['session_id']
    print(f"Session ID: {session_id}")
    
    # Generate preview
    print("Generating preview...")
    preview_response = requests.post(f"{api_url}/api/preview", 
                                   json={"session_id": session_id})
    if preview_response.status_code != 200:
        print("Preview failed:", preview_response.text)
        exit(1)
    
    # Generate PDFs with test parameters
    print("Generating PDFs...")
    generate_data = {
        "session_id": session_id,
        "invoice_date": "10/09/2025",
        "invoice_no": "xx/0000001/2025",  # Test with xx/ prefix
        "call_off": "P25-122",
        "overrides": {}
    }
    
    generate_response = requests.post(f"{api_url}/api/generate/pdf", 
                                    json=generate_data)
    if generate_response.status_code != 200:
        print("Generation failed:", generate_response.text)
        exit(1)
    
    result = generate_response.json()
    print("Generation result:", json.dumps(result, indent=2))
    
    # Check if files were created
    for item in result.get('produced', []):
        xlsx_path = Path(item['xlsx'])
        pdf_path = Path(item['pdf']) if item['pdf'] else None
        
        print(f"\nChecking {item['name']}:")
        print(f"XLSX exists: {xlsx_path.exists()}")
        if pdf_path:
            print(f"PDF exists: {pdf_path.exists()}")
            if pdf_path.exists():
                print(f"PDF size: {pdf_path.stat().st_size} bytes")

finally:
    # Close files
    for f in files_data.values():
        f.close()
