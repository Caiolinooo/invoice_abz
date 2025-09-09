from pathlib import Path
import sys
sys.path.append(str(Path('app')))

from utils.anfin_parser import extract_individual_totals

root = Path('.')
anfin = next(x for x in (root/'DADOS').glob('*.xlsx') if 'AN-FIN' in x.name.upper())
ind = extract_individual_totals(anfin)
for k,v in ind.items():
    if 'Caio' in k or 'Barbara' in k:
        print(k, {kk: round(vv,2) for kk,vv in v.items()})

