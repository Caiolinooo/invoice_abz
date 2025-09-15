import PyPDF2
from pathlib import Path

pdf_path = Path('out/invoices/pdf/Caio_Cesar_Silva_Nascimento_Invoice.pdf')

if not pdf_path.exists():
    print("PDF not found!")
    exit(1)

try:
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        print(f"PDF has {len(pdf_reader.pages)} pages")
        
        # Extract text from first page
        page = pdf_reader.pages[0]
        text = page.extract_text()
        
        print("\n=== PDF Content ===")
        print(text)
        
        # Check for specific issues
        print("\n=== Checking Issues ===")
        
        # Check invoice date spacing
        if "Invoice date:10/09/2025" in text:
            print("✓ Invoice date: NO space after colon")
        elif "Invoice date: 10/09/2025" in text:
            print("✗ Invoice date: Still has space after colon")
        else:
            print("? Invoice date: Not found in expected format")
        
        # Check invoice number prefix
        if "xx/" in text.lower():
            print("✗ Invoice number: Still has 'xx/' prefix")
        elif "0000001/2025" in text:
            print("✓ Invoice number: No 'xx/' prefix")
        else:
            print("? Invoice number: Not found in expected format")
            
        # Check for alignment (harder to detect in text, but we can check values)
        if "£770.00" in text and "£850.00" in text and "£871.63" in text:
            print("✓ Values: All expected values present")
        else:
            print("? Values: Some expected values missing")

except Exception as e:
    print(f"Error reading PDF: {e}")
