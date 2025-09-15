import unicodedata
import re
from pathlib import Path
from openpyxl import load_workbook

def _norm(s: str) -> str:
    s = unicodedata.normalize('NFD', str(s))
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '', s.lower())

# Test the name matching logic
dados_dir = Path('DADOS')
abz_files = list(dados_dir.glob('*ABZ*.xlsx'))

if abz_files:
    abz = abz_files[0]
    print('Using ABZ file:', abz)
    
    wb = load_workbook(abz, read_only=True)
    sheets = wb.sheetnames
    invoice_sheets = [s for s in sheets if s.lower().endswith('_invoice')]
    
    print('Available invoice sheets:', invoice_sheets)
    print()
    
    # Test names from the preview
    test_names = [
        'Caio Cesar Silva Nascimento',
        'Daniel Vieira Silva Nunes',
        'Fabricio Oliveira Addor Pereira',
        'Gabriel Leone',
        'Kaue Toste Patrocinio',
        'Otavio Augusto Ribeiro',
        'Rafael Cabral Marcilio',
        'Rafael de Souza da Silva',
        'Rodrigo Gralha oliveira Do Rego',
        'Semaias Felicissimo Araujo Pinto',
        'Vinicius Brandao da Silva'
    ]
    
    for name in test_names:
        first = _norm(name.split()[0])
        print(f'Name: {name}')
        print(f'First normalized: "{first}"')
        
        tpl_candidates = [s for s in invoice_sheets if first in _norm(s)]
        print(f'Template candidates: {tpl_candidates}')
        
        # Debug: show normalized sheet names
        for sheet in invoice_sheets:
            norm_sheet = _norm(sheet)
            contains = first in norm_sheet
            print(f'  Sheet: {sheet} -> normalized: "{norm_sheet}" -> contains "{first}"? {contains}')
        print('-' * 50)
    
    wb.close()
else:
    print('No ABZ files found')
