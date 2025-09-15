import requests
import json

# Test the invoice generation
data = {
    'session_id': 'c4c3fe2ff1e64cdb8b126c5c80744369',
    'invoice_date': '11/09/2025',
    'invoice_no': '108',
    'call_off': 'P25-122'
}

try:
    response = requests.post('http://localhost:8000/api/generate/pdf', json=data)
    print('Status:', response.status_code)
    result = response.json()
    print('Files generated:', len(result.get('files', [])))
    print('Warnings:', len(result.get('warnings', [])))
    if result.get('warnings'):
        for warning in result['warnings']:
            print(f'  - {warning}')
    if result.get('files'):
        for file in result['files']:
            print(f'  Generated: {file["name"]}')
except Exception as e:
    print('Erro:', e)
