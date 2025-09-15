from pathlib import Path
p = Path('out/invoices/pdf/Bárbara_Chapeta_Mattoso_Franco_Invoice.pdf')
print('exists:', p.exists())
if p.exists():
    print('size:', p.stat().st_size)

