# 🏢 Multi-Company Implementation Plan
## ABZ Group + ABZ International Support

---

## 📋 Overview

Implementar suporte para duas empresas no sistema:
1. **ABZ Group** (atual) - FMS, OMEGA, etc.
2. **ABZ International** (novo) - Jifmar Group

---

## 🎯 Objetivos

1. ✅ **Seletor de Empresa** - Usuário escolhe qual empresa está emitindo invoices
2. ✅ **Dados Separados** - Histórico, faturamento e sessões separados por empresa
3. ✅ **Parsers Diferentes** - Suporte para formatos diferentes de planilhas
4. ✅ **Relatórios Combinados** - Função para combinar dados de ambas empresas
5. ✅ **Nomenclatura Padronizada** - Nomes de arquivo seguem padrão de cada empresa

---

## 📊 Diferenças Entre Formatos

### ABZ Group (Atual)
```
Estrutura:
- Sheet "Charge Rate" com dados agregados
- Sheets individuais "{Nome}_Invoice" com templates pré-preenchidos
- Colunas: Name, Position, Charge Rate, Days, Monthly Total, Expenses

Cliente: FMS, OMEGA, etc.
Formato Invoice: "ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}.xlsx"
```

### ABZ International (Jifmar)
```
Estrutura:
- Cada sheet = Vessel/Projeto (Voe Vanguard, Voe Viking, Faraday, etc.)
- Dados diretos sem templates pré-existentes
- Colunas: Name, Position, Day Rate, Days, Overtime Hours, Overtime Cost, 
           Insurance Cost, Social Security, Expenses, Additional Total, 
           Monthly Salary, Monthly Charge

Cliente: Jifmar Group
Formato Invoice: "ABZ International {invoice_no}-{year} {vessel} {month} {year} {first_name}.xlsx"
```

---

## 🔧 Implementação

### Fase 1: Database & Models ✅ (Já existe)
- [x] Company model com id, name, settings
- [x] Invoice.company_id foreign key
- [x] Session.company_id foreign key
- [x] Configuration.company_id foreign key

### Fase 2: UI - Company Selector
**Arquivo**: `dev/app/ui/index.html`

```html
<!-- Adicionar no início da seção de upload -->
<div class="form-group">
  <label class="form-label">
    <span class="material-icons">business</span>
    Empresa Emissora
  </label>
  <select id="companySelector" class="form-select">
    <option value="1">ABZ Group (FMS, OMEGA, etc.)</option>
    <option value="2">ABZ International (Jifmar)</option>
  </select>
  <div class="form-help">Selecione qual empresa está emitindo as invoices</div>
</div>
```

**JavaScript**: Armazenar company_id selecionado e enviar em todas requisições

### Fase 3: Parser para Jifmar
**Novo arquivo**: `dev/app/utils/jifmar_parser.py`

```python
def parse_jifmar_spreadsheet(file_path: str) -> List[Dict]:
    """
    Parse ABZ International (Jifmar) spreadsheet format
    
    Returns list of employees with structure:
    {
        'name': str,
        'position': str,
        'vessel': str,  # Sheet name
        'day_rate': float,
        'days': int,
        'overtime_hours': float,
        'overtime_cost': float,
        'insurance_cost': float,
        'social_security': float,
        'expenses': float,
        'additional_total': float,
        'monthly_salary': float,
        'monthly_charge': float
    }
    """
```

### Fase 4: Unified Invoice Generator
**Modificar**: `dev/app/invoice/template_filler.py`

```python
def generate_invoice(employee_data: Dict, company_id: int, **kwargs):
    """
    Generate invoice based on company format
    
    Args:
        employee_data: Employee data dict
        company_id: 1 = ABZ Group, 2 = ABZ International
        **kwargs: Additional parameters (invoice_no, date, etc.)
    """
    if company_id == 1:
        return generate_abz_group_invoice(employee_data, **kwargs)
    elif company_id == 2:
        return generate_abz_international_invoice(employee_data, **kwargs)
```

### Fase 5: Filename Standardization
**Modificar**: `dev/app/utils/filename_standardizer.py`

```python
def generate_standardized_filename(
    employee_name: str,
    invoice_no: str,
    invoice_date: str,
    company_id: int,
    client_or_vessel: str,
    extension: str = "xlsx"
) -> str:
    """
    Generate standardized filename based on company
    
    ABZ Group (1): "ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}.xlsx"
    ABZ International (2): "ABZ International {invoice_no}-{year} {vessel} {month} {year} {first_name}.xlsx"
    """
```

### Fase 6: API Endpoints Update
**Modificar**: `dev/app/api/server.py`

Atualizar todos endpoints para aceitar `company_id` do request:
- `/api/upload` - Receber company_id
- `/api/generate/pdf` - Usar company_id correto
- `/api/invoices` - Filtrar por company_id
- `/api/stats` - Calcular por company_id

### Fase 7: Combined Reporting
**Novo endpoint**: `/api/reports/combined`

```python
@app.get("/api/reports/combined")
async def get_combined_report(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """
    Get combined financial report from both companies
    
    Returns:
    {
        "total_revenue": float,
        "by_company": {
            "ABZ Group": {
                "revenue": float,
                "invoices_count": int,
                "employees_count": int
            },
            "ABZ International": {
                "revenue": float,
                "invoices_count": int,
                "employees_count": int
            }
        },
        "by_month": [...],
        "by_client": [...]
    }
    """
```

### Fase 8: History Page Update
**Modificar**: `dev/app/ui/history.html`

Adicionar filtro por empresa:
```html
<select id="filterCompany" class="form-input">
  <option value="">Todas as Empresas</option>
  <option value="1">ABZ Group</option>
  <option value="2">ABZ International</option>
</select>
```

### Fase 9: Database Initialization
**Script**: `dev/init_companies.py`

```python
from app.database.models import Company
from app.database.connection import get_db

def init_companies():
    db = next(get_db())
    
    # ABZ Group
    abz_group = Company(
        id=1,
        name="ABZ Group",
        settings=json.dumps({
            "clients": ["FMS", "OMEGA"],
            "filename_format": "ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}",
            "currency": "GBP"
        })
    )
    
    # ABZ International
    abz_intl = Company(
        id=2,
        name="ABZ International",
        settings=json.dumps({
            "clients": ["Jifmar Group"],
            "filename_format": "ABZ International {invoice_no}-{year} {vessel} {month} {year} {first_name}",
            "currency": "GBP"
        })
    )
    
    db.add(abz_group)
    db.add(abz_intl)
    db.commit()
```

---

## 📁 Estrutura de Arquivos

```
dev/
├── app/
│   ├── utils/
│   │   ├── jifmar_parser.py          # NOVO - Parser para Jifmar
│   │   ├── filename_standardizer.py  # MODIFICAR - Suporte multi-empresa
│   │   └── abz_charge_rate_parser.py # EXISTENTE - Parser ABZ Group
│   ├── invoice/
│   │   └── template_filler.py        # MODIFICAR - Geração unificada
│   ├── api/
│   │   └── server.py                 # MODIFICAR - Company_id em endpoints
│   └── ui/
│       ├── index.html                # MODIFICAR - Company selector
│       ├── history.html              # MODIFICAR - Filtro por empresa
│       └── reports.html              # NOVO - Relatórios combinados
├── init_companies.py                 # NOVO - Inicializar empresas no DB
└── DADOS/
    ├── ABZ - FMS - *.xlsx           # ABZ Group
    └── ABZ - Jifmar - *.xlsx        # ABZ International
```

---

## 🧪 Testing Plan

### Test 1: Jifmar Parser
```python
# test_jifmar_parser.py
from app.utils.jifmar_parser import parse_jifmar_spreadsheet

data = parse_jifmar_spreadsheet("DADOS/ABZ - Jifmar - Monthly Rates 1509-3009 New Version.xlsx")
assert len(data) > 0
assert data[0]['vessel'] in ['Voe Vanguard', 'Voe Viking', 'Faraday']
```

### Test 2: Multi-Company Invoice Generation
```python
# test_multi_company_generation.py
# Test ABZ Group
abz_group_invoice = generate_invoice(employee_data, company_id=1, client="FMS")
assert "ABZ Group" in abz_group_invoice.filename

# Test ABZ International
abz_intl_invoice = generate_invoice(employee_data, company_id=2, vessel="Voe Vanguard")
assert "ABZ International" in abz_intl_invoice.filename
```

### Test 3: Combined Reporting
```python
# test_combined_reporting.py
report = get_combined_report()
assert "ABZ Group" in report['by_company']
assert "ABZ International" in report['by_company']
assert report['total_revenue'] > 0
```

---

## 📊 Success Criteria

- [ ] Usuário pode selecionar empresa na UI
- [ ] Planilhas Jifmar são parseadas corretamente
- [ ] Invoices são geradas com nomenclatura correta para cada empresa
- [ ] Histórico mostra dados separados por empresa
- [ ] Relatório combinado agrega dados de ambas empresas
- [ ] Dados não se misturam entre empresas
- [ ] Sistema mantém compatibilidade com ABZ Group existente

---

## 🚀 Deployment Steps

1. Backup database atual
2. Executar `init_companies.py` para criar registros de empresas
3. Deploy código atualizado
4. Testar com planilha Jifmar
5. Validar relatórios combinados
6. Documentar para usuários finais

---

## 📝 Notes

- Company_id 1 = ABZ Group (mantém compatibilidade com dados existentes)
- Company_id 2 = ABZ International (novo)
- Todos dados históricos existentes serão associados a company_id=1
- Sistema suporta expansão futura para mais empresas (company_id 3, 4, etc.)

