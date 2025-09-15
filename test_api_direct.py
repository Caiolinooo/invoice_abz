import sys
sys.path.append('app')

import asyncio
from pathlib import Path
import json
from api.server import GenerateRequest, api_generate_pdf

async def test_api():
    # Simulate the API call directly
    session_id = 'c4c3fe2ff1e64cdb8b126c5c80744369'

    # Create the request object
    req = GenerateRequest(
        session_id=session_id,
        invoice_date='11/09/2025',
        invoice_no='108',
        call_off='P25-122'
    )

    print(f"Testing API call with session_id: {session_id}")

    try:
        # Call the API function directly (await since it's async)
        result = await api_generate_pdf(req)

        print(f"Result type: {type(result)}")
        print(f"Files generated: {len(result.get('files', []))}")
        print(f"Warnings: {len(result.get('warnings', []))}")

        if result.get('warnings'):
            print("Warnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")

        if result.get('files'):
            print("Generated files:")
            for file in result['files']:
                print(f"  - {file['name']}: {file.get('url_xlsx', 'N/A')}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api())
