from pathlib import Path
from app.api.server import _build_preview_single_file

abz = Path(r'out\sessions\c6edd65f89e94d528fb703903ff33cab\ABZ - OMEGA - Maximus Project  -Monthly Charge Rates 08.2025 (1).xlsx')
preview = _build_preview_single_file(abz)
rows = preview['employees']
for r in rows:
    services = r.get('services',[])
    add = next((s['final'] for s in services if s['description']=='Brazilian Payroll Additional'),0)
    exp = next((s['final'] for s in services if s['description']=='Expenses'),0)
    print(r['name'], '| ADD:', add, '| EXP:', exp)
print('TOTAL EMPLOYEES:', len(rows))

