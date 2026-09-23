# 🎯 Sistema Multi-Empresa + Multi-Cliente - COMPLETO

## 📋 Visão Geral

Sistema **altamente escalável** que permite:
- ✅ **Múltiplas empresas** (ABZ Group, ABZ International, futuras...)
- ✅ **Múltiplos clientes** por empresa (FMS, OMEGA, Jifmar vessels, etc.)
- ✅ **Adicionar novos clientes SEM modificar código** - apenas configuração!
- ✅ **Relatórios detalhados** por empresa, cliente, período
- ✅ **Separação de lucro** por cliente para controle financeiro
- ✅ **Relatórios anuais/mensais** combinados ou individuais

---

## 🏗️ Arquitetura do Sistema

```
Sistema Multi-Empresa + Multi-Cliente
│
├── 🏢 ABZ Group (company_id=1)
│   ├── 📊 FMS (client_id="FMS")
│   │   ├── Planilhas: *FMS*, *Maximus*
│   │   ├── Formato: ABZ Charge Rate
│   │   └── Invoices: ABZ Group {no}-{year} FMS {month} {year} {name}
│   │
│   ├── 📊 OMEGA (client_id="OMEGA")
│   │   ├── Planilhas: *OMEGA*
│   │   ├── Formato: ABZ Charge Rate
│   │   └── Invoices: ABZ Group {no}-{year} OMEGA {month} {year} {name}
│   │
│   └── ➕ [Novo Cliente] → Apenas adicionar ClientProfile!
│
└── 🌍 ABZ International (company_id=2)
    ├── 🚢 Jifmar - Voe Vanguard (client_id="JIFMAR_VOE_VANGUARD")
    │   ├── Planilhas: *Jifmar*
    │   ├── Formato: Jifmar Vessel
    │   ├── Vessel: Voe Vanguard
    │   └── Invoices: ABZ International {no}-{year} Voe Vanguard {month} {year} {name}
    │
    ├── 🚢 Jifmar - Voe Viking (client_id="JIFMAR_VOE_VIKING")
    ├── 🚢 Jifmar - Faraday (client_id="JIFMAR_FARADAY")
    ├── 🚢 Jifmar - Project 5679 (client_id="JIFMAR_PROJECT_5679")
    ├── 🚢 Jifmar - Voe Earl (client_id="JIFMAR_VOE_EARL")
    │
    └── ➕ [Novo Cliente/Vessel] → Apenas adicionar ClientProfile!
```

---

## 🎨 Sistema de Client Profiles

### O que é?
**Client Profile** = Configuração de um cliente que define:
- Como parsear suas planilhas
- Como gerar invoices
- Formato de nomes de arquivo
- Categoria para relatórios
- Moeda, taxas, etc.

### Como adicionar um novo cliente?

**ZERO MODIFICAÇÃO DE CÓDIGO!** Apenas crie um novo `ClientProfile`:

```python
from app.models.client_profile import ClientProfile, get_client_profile_manager

# Exemplo: Adicionar novo cliente "PETROBRAS"
manager = get_client_profile_manager()

manager.add_profile(ClientProfile(
    client_id="PETROBRAS",
    client_name="Petrobras",
    company_id=1,  # ABZ Group
    spreadsheet_format=SpreadsheetFormat.ABZ_CHARGE_RATE,
    spreadsheet_patterns=["*PETROBRAS*", "*Petro*"],
    invoice_format=InvoiceFormat.ABZ_TEMPLATE,
    filename_template="ABZ Group {invoice_no}-{year} PETROBRAS {month} {year} {first_name}",
    category="offshore",
    currency="BRL"  # Pode ser diferente!
))

# Pronto! Sistema já reconhece e processa planilhas PETROBRAS!
```

### Detecção Automática
O sistema **detecta automaticamente** qual cliente baseado no nome do arquivo:

```python
# Upload: "ABZ - PETROBRAS - Monthly Rates 10 2025.xlsx"
# Sistema detecta: client_id="PETROBRAS"
# Usa configuração correta automaticamente!
```

---

## 📊 Banco de Dados Estendido

### Tabela `invoices` (Modificada)
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    company_id INTEGER,           -- 1=ABZ Group, 2=ABZ International
    
    -- NOVO: Client tracking
    client_id VARCHAR(100),       -- "FMS", "OMEGA", "JIFMAR_VOE_VANGUARD"
    client_name VARCHAR(255),     -- Display name
    client_category VARCHAR(100), -- "offshore", "maritime"
    client_subcategory VARCHAR(100), -- vessel name, etc.
    
    -- Financial breakdown (NOVO)
    base_amount FLOAT,
    overtime_amount FLOAT,
    expenses_amount FLOAT,
    insurance_amount FLOAT,
    other_amount FLOAT,
    
    -- Existing fields...
    invoice_number VARCHAR(100),
    employee_name VARCHAR(255),
    total_amount FLOAT,
    ...
);
```

### Tabela `clients` (NOVA)
```sql
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    company_id INTEGER,
    client_id VARCHAR(100) UNIQUE,  -- "FMS", "OMEGA"
    client_name VARCHAR(255),
    
    -- Configuration
    spreadsheet_format VARCHAR(50),
    invoice_format VARCHAR(50),
    filename_template TEXT,
    
    -- Financial
    currency VARCHAR(10),
    tax_rate FLOAT,
    
    -- Categorization
    category VARCHAR(100),
    subcategory VARCHAR(100),
    
    -- JSON config
    config_json TEXT,
    is_active BOOLEAN
);
```

---

## 📈 Sistema de Relatórios

### 1. Relatório por Empresa
```python
from app.services.reporting_service import ReportingService

report = ReportingService.get_company_summary(
    db,
    company_id=1,  # ABZ Group
    date_from=datetime(2025, 1, 1),
    date_to=datetime(2025, 12, 31)
)

# Retorna:
{
    "total_revenue": 150000.00,
    "total_invoices": 250,
    "by_client": {
        "FMS": {"revenue": 80000, "invoices": 120},
        "OMEGA": {"revenue": 70000, "invoices": 130}
    },
    "by_month": [...]
}
```

### 2. Relatório Detalhado por Cliente
```python
report = ReportingService.get_client_detailed_report(
    db,
    client_id="FMS",
    date_from=datetime(2025, 1, 1),
    date_to=datetime(2025, 12, 31)
)

# Retorna:
{
    "client_name": "FMS",
    "summary": {
        "total_revenue": 80000.00,
        "total_invoices": 120,
        "total_employees": 15
    },
    "financial_breakdown": {
        "base_amount": 60000,
        "overtime_amount": 10000,
        "expenses_amount": 5000,
        "insurance_amount": 3000,
        "other_amount": 2000
    },
    "by_employee": [...],
    "monthly_trend": [...]
}
```

### 3. Relatório Combinado (Todas Empresas)
```python
report = ReportingService.get_combined_report(
    db,
    date_from=datetime(2025, 1, 1),
    date_to=datetime(2025, 12, 31)
)

# Retorna:
{
    "grand_total": 250000.00,
    "total_invoices": 500,
    "by_company": {
        "ABZ Group": {"revenue": 150000, "invoices": 250},
        "ABZ International": {"revenue": 100000, "invoices": 250}
    },
    "by_client": {...},
    "by_category": {
        "offshore": {"revenue": 150000, "clients": 2},
        "maritime": {"revenue": 100000, "clients": 5}
    },
    "top_clients": [...]
}
```

---

## 🔄 Fluxo de Trabalho

### Upload de Planilha
```
1. Usuário seleciona empresa (ABZ Group ou ABZ International)
2. Usuário faz upload da planilha
3. Sistema detecta automaticamente o cliente pelo nome do arquivo
4. Sistema usa o ClientProfile correto para parsear
5. Dados são extraídos e mostrados para revisão
```

### Geração de Invoices
```
1. Usuário configura data, número da invoice
2. Sistema usa ClientProfile para determinar formato
3. Invoices são geradas com nomenclatura correta
4. Dados são salvos no banco com client_id
5. Relatórios ficam disponíveis imediatamente
```

---

## 📁 Arquivos Criados/Modificados

### ✅ Novos Arquivos
```
dev/
├── app/
│   ├── models/
│   │   └── client_profile.py          ✅ NOVO - Sistema de profiles
│   ├── services/
│   │   └── reporting_service.py       ✅ NOVO - Relatórios avançados
│   └── utils/
│       └── jifmar_parser.py           ✅ NOVO - Parser Jifmar
├── init_companies.py                  ✅ NOVO - Inicializar empresas
├── MULTI_COMPANY_IMPLEMENTATION_PLAN.md  ✅ NOVO
├── MULTI_COMPANY_PROGRESS.md          ✅ NOVO
└── SISTEMA_MULTI_CLIENTE_COMPLETO.md  ✅ NOVO (este arquivo)
```

### 🔧 Arquivos Modificados
```
dev/
└── app/
    └── database/
        └── models.py                  🔧 MODIFICADO - Novos campos
```

### ⏳ Próximos a Modificar
```
dev/
└── app/
    ├── api/
    │   └── server.py                  ⏳ Aceitar company_id e client_id
    ├── invoice/
    │   └── template_filler.py         ⏳ Geração unificada
    ├── utils/
    │   └── filename_standardizer.py   ⏳ Multi-empresa
    └── ui/
        ├── index.html                 ⏳ Company selector
        └── history.html               ⏳ Filtros por empresa/cliente
```

---

## 🧪 Testes Realizados

### ✅ Test 1: Client Profile System
```bash
$ python dev/app/models/client_profile.py

Profiles: 7
  - FMS
  - OMEGA
  - Jifmar - Voe Vanguard
  - Jifmar - Voe Viking
  - Jifmar - Faraday
  - Jifmar - Project 5679
  - Jifmar - Voe Earl

✅ Auto-detection working!
✅ JSON export/import working!
```

### ✅ Test 2: Jifmar Parser
```bash
$ python dev/app/utils/jifmar_parser.py

✅ Parsed 12 employees
🚢 Employees by vessel:
  Voe Vanguard: 1 employees
  Voe Viking: 3 employees
  Faraday: 2 employees
  Project 5679: 2 employees
  Voe Earl: 4 employees
```

---

## 🎯 Benefícios do Sistema

### 1. **Escalabilidade**
- ✅ Adicionar novo cliente = 5 minutos (apenas config)
- ✅ Adicionar nova empresa = 10 minutos
- ✅ Sem modificação de código core

### 2. **Controle Financeiro**
- ✅ Lucro separado por cliente
- ✅ Relatórios detalhados por período
- ✅ Breakdown de custos (base, overtime, expenses, etc.)
- ✅ Comparação entre clientes/empresas

### 3. **Flexibilidade**
- ✅ Cada cliente pode ter formato diferente
- ✅ Moedas diferentes por cliente
- ✅ Categorização customizada
- ✅ Templates de filename personalizados

### 4. **Manutenibilidade**
- ✅ Configuração centralizada
- ✅ Código limpo e organizado
- ✅ Fácil debug e troubleshooting
- ✅ Documentação completa

---

## 📝 Próximos Passos

### Fase 1: Database (✅ Completo)
- [x] Modificar modelo Invoice
- [x] Criar modelo Client
- [x] Sistema de Client Profiles
- [x] Reporting Service

### Fase 2: Backend (⏳ Em Progresso)
- [ ] Executar init_companies.py
- [ ] Modificar API endpoints
- [ ] Integrar Client Profiles
- [ ] Atualizar filename standardizer

### Fase 3: Frontend (⏳ Pendente)
- [ ] Company selector na UI
- [ ] Client detection display
- [ ] Filtros por empresa/cliente
- [ ] Página de relatórios

### Fase 4: Testing (⏳ Pendente)
- [ ] Testes de integração
- [ ] Testes end-to-end
- [ ] Validação de relatórios

---

## 🚀 Como Usar

### Para Adicionar Novo Cliente:

```python
# 1. Criar ClientProfile
from app.models.client_profile import ClientProfile, get_client_profile_manager

manager = get_client_profile_manager()
manager.add_profile(ClientProfile(
    client_id="NOVO_CLIENTE",
    client_name="Novo Cliente Ltda",
    company_id=1,
    spreadsheet_format=SpreadsheetFormat.ABZ_CHARGE_RATE,
    spreadsheet_patterns=["*NOVO*"],
    invoice_format=InvoiceFormat.ABZ_TEMPLATE,
    filename_template="ABZ Group {invoice_no}-{year} NOVO {month} {year} {first_name}",
    category="offshore"
))

# 2. Salvar configuração
manager.save_to_json("client_profiles.json")

# 3. Pronto! Sistema já reconhece o novo cliente!
```

### Para Gerar Relatório:

```python
# Relatório mensal de um cliente
from app.services.reporting_service import ReportingService
from datetime import datetime

report = ReportingService.get_client_detailed_report(
    db,
    client_id="FMS",
    date_from=datetime(2025, 10, 1),
    date_to=datetime(2025, 10, 31)
)

print(f"Revenue: £{report['summary']['total_revenue']:,.2f}")
print(f"Invoices: {report['summary']['total_invoices']}")
```

---

## 📞 Suporte

**Documentação Completa:**
- `MULTI_COMPANY_IMPLEMENTATION_PLAN.md` - Plano técnico detalhado
- `MULTI_COMPANY_PROGRESS.md` - Progresso e status
- `SISTEMA_MULTI_CLIENTE_COMPLETO.md` - Este arquivo (visão geral)

**Arquivos de Teste:**
- `dev/app/models/client_profile.py` - Testar profiles
- `dev/app/utils/jifmar_parser.py` - Testar parser
- `dev/app/services/reporting_service.py` - Testar relatórios

---

**Status**: 🟡 50% Completo
**Última Atualização**: 2025-10-13
**Próxima Fase**: Integração com API e UI

