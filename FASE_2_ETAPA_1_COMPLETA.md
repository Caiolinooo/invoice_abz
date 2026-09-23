# ✅ Fase 2 - Etapa 1: API Endpoints - COMPLETO!

## 🎯 Objetivo
Modificar API para suportar multi-empresa e multi-cliente com detecção automática.

---

## ✅ Implementações Realizadas

### 1. **Sistema de DB Dev/Prod** ✅

#### Arquivos Criados:
- `dev/app/database/database.py` (modificado)
- `dev/set_env.py`
- `run_dev.bat`
- `run_prod.bat`

#### Como Funciona:
```bash
# Modo DESENVOLVIMENTO (para testes)
run_dev.bat
# Usa: data/invoice_system_dev.db
# SQL Logging: Ativado

# Modo PRODUÇÃO (dados reais)
run_prod.bat
# Usa: data/invoice_system.db
# SQL Logging: Desativado
```

#### Variável de Ambiente:
```bash
# Windows
set INVOICE_ENV=dev    # Desenvolvimento
set INVOICE_ENV=prod   # Produção

# Linux/Mac
export INVOICE_ENV=dev
export INVOICE_ENV=prod
```

#### Benefícios:
- ✅ **Testes sem perder dados de produção**
- ✅ **Rastreabilidade completa** (dois bancos separados)
- ✅ **SQL logging automático em dev**
- ✅ **Fácil alternância** (apenas rodar .bat diferente)

---

### 2. **Novos Endpoints Multi-Empresa** ✅

#### Arquivo: `dev/app/api/multi_company_endpoints.py`

#### Endpoints Criados:

##### **POST /api/v2/import** (Novo)
```python
# Upload com detecção automática de cliente
POST /api/v2/import
Form Data:
  - abz: UploadFile (planilha)
  - company_id: int (1=ABZ Group, 2=ABZ International)

Response:
{
  "session_id": "abc123...",
  "company_id": 1,
  "company_name": "ABZ Group",
  "client_id": "FMS",
  "client_name": "FMS",
  "employees": ["Filipi Brandão", "Gil Anderson", ...],
  "parser_used": "abz_charge_rate",
  "total_employees": 15
}
```

**Funcionalidades:**
- ✅ Detecta cliente automaticamente pelo nome do arquivo
- ✅ Usa parser correto baseado no ClientProfile
- ✅ Valida company_id
- ✅ Retorna informações completas do cliente

**Exemplo de Uso:**
```javascript
// Frontend
const formData = new FormData();
formData.append('abz', file);
formData.append('company_id', 1); // ABZ Group

const response = await fetch('/api/v2/import', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log(`Cliente detectado: ${result.client_name}`);
console.log(`Parser usado: ${result.parser_used}`);
console.log(`Funcionários: ${result.total_employees}`);
```

##### **GET /api/companies** (Novo)
```python
# Lista todas as empresas com seus clientes
GET /api/companies

Response:
[
  {
    "id": 1,
    "name": "ABZ Group",
    "domain": "abzgroup.com",
    "clients": [
      {
        "client_id": "FMS",
        "client_name": "FMS",
        "category": "offshore",
        "subcategory": null
      },
      {
        "client_id": "OMEGA",
        "client_name": "OMEGA",
        "category": "offshore",
        "subcategory": null
      }
    ],
    "total_clients": 2
  },
  {
    "id": 2,
    "name": "ABZ International",
    "domain": "abzinternational.com",
    "clients": [
      {
        "client_id": "JIFMAR_VOE_VANGUARD",
        "client_name": "Jifmar - Voe Vanguard",
        "category": "maritime",
        "subcategory": "Voe Vanguard"
      },
      ...
    ],
    "total_clients": 5
  }
]
```

##### **GET /api/clients** (Novo)
```python
# Lista clientes, opcionalmente filtrados por empresa
GET /api/clients?company_id=1

Response:
[
  {
    "client_id": "FMS",
    "client_name": "FMS",
    "company_id": 1,
    "spreadsheet_format": "abz_charge_rate",
    "invoice_format": "abz_template",
    "category": "offshore",
    "subcategory": null,
    "currency": "GBP"
  },
  ...
]
```

---

### 3. **Detecção Automática de Cliente** ✅

#### Função: `detect_client_and_parse()`

**Como Funciona:**
```python
# 1. Detecta cliente pelo nome do arquivo
filename = "ABZ - FMS - Maximus Project - Monthly Rates 09.2025.xlsx"
profile = manager.detect_client_from_filename(filename)
# Resultado: ClientProfile(client_id="FMS", ...)

# 2. Valida company_id
if profile.company_id != company_id:
    raise HTTPException("Cliente não pertence a esta empresa")

# 3. Usa parser correto
if profile.spreadsheet_format == SpreadsheetFormat.ABZ_CHARGE_RATE:
    data = read_charge_rate_table(file_path)
elif profile.spreadsheet_format == SpreadsheetFormat.JIFMAR_VESSEL:
    data = parse_jifmar_spreadsheet(file_path)

# 4. Retorna dados padronizados
return {
    "client_id": "FMS",
    "client_name": "FMS",
    "employees": [...],
    "parser_used": "abz_charge_rate"
}
```

**Suporta:**
- ✅ ABZ Group (FMS, OMEGA)
- ✅ ABZ International (Jifmar vessels)
- ✅ Futuros clientes (apenas adicionar ClientProfile)

---

### 4. **Integração com Server Principal** ✅

#### Arquivo: `dev/app/api/server.py` (modificado)

**Adicionado:**
```python
# Linha 15: Import Session
from sqlalchemy.orm import Session

# Linhas 2378-2420: Multi-company endpoints
@app.post("/api/v2/import")
async def import_multi_company(...):
    return await api_import_multi_company(...)

@app.get("/api/companies")
async def get_companies(...):
    return await api_get_companies(...)

@app.get("/api/clients")
async def get_clients(...):
    return await api_get_clients(...)
```

---

## 📊 Fluxo Completo

### Upload de Planilha ABZ Group (FMS):
```
1. Usuário seleciona empresa: ABZ Group (company_id=1)
2. Usuário faz upload: "ABZ - FMS - Rates 09.2025.xlsx"
3. POST /api/v2/import com company_id=1
4. Sistema detecta: client_id="FMS"
5. Sistema usa parser: abz_charge_rate
6. Sistema retorna: 15 funcionários encontrados
7. Dados salvos com client_id="FMS" para relatórios
```

### Upload de Planilha ABZ International (Jifmar):
```
1. Usuário seleciona empresa: ABZ International (company_id=2)
2. Usuário faz upload: "ABZ - Jifmar - Monthly Rates 1509-3009.xlsx"
3. POST /api/v2/import com company_id=2
4. Sistema detecta: client_id="JIFMAR_VOE_VANGUARD" (primeiro vessel)
5. Sistema usa parser: jifmar_vessel
6. Sistema retorna: 12 funcionários encontrados (todos vessels)
7. Dados salvos com client_id e vessel para relatórios
```

---

## 🧪 Como Testar

### 1. Iniciar em Modo DEV:
```bash
# Windows
run_dev.bat

# Ou manualmente
set INVOICE_ENV=dev
cd dev
python -m uvicorn app.api.server:app --reload --host 0.0.0.0 --port 8000
```

### 2. Testar Endpoint de Empresas:
```bash
curl http://localhost:8000/api/companies
```

### 3. Testar Endpoint de Clientes:
```bash
# Todos os clientes
curl http://localhost:8000/api/clients

# Clientes da ABZ Group
curl http://localhost:8000/api/clients?company_id=1

# Clientes da ABZ International
curl http://localhost:8000/api/clients?company_id=2
```

### 4. Testar Upload Multi-Empresa:
```bash
# Upload planilha FMS
curl -X POST http://localhost:8000/api/v2/import \
  -F "abz=@path/to/ABZ-FMS-Rates.xlsx" \
  -F "company_id=1"

# Upload planilha Jifmar
curl -X POST http://localhost:8000/api/v2/import \
  -F "abz=@path/to/ABZ-Jifmar-Rates.xlsx" \
  -F "company_id=2"
```

---

## 📁 Arquivos Criados/Modificados

```
✅ dev/app/database/database.py          - Sistema Dev/Prod
✅ dev/set_env.py                        - Helper para alternar env
✅ run_dev.bat                           - Rodar em modo DEV
✅ run_prod.bat                          - Rodar em modo PROD
✅ dev/app/api/multi_company_endpoints.py - Novos endpoints
🔧 dev/app/api/server.py                 - Integração endpoints
✅ FASE_2_ETAPA_1_COMPLETA.md            - Este arquivo
```

---

## ✅ Checklist de Implementação

### Sistema Dev/Prod:
- [x] Variável de ambiente INVOICE_ENV
- [x] Banco dev separado (invoice_system_dev.db)
- [x] Banco prod separado (invoice_system.db)
- [x] SQL logging em dev
- [x] Scripts .bat para Windows
- [x] Helper set_env.py

### Endpoints Multi-Empresa:
- [x] POST /api/v2/import
- [x] GET /api/companies
- [x] GET /api/clients
- [x] Detecção automática de cliente
- [x] Roteamento de parser
- [x] Validação de company_id
- [x] Integração com server.py

### Funcionalidades:
- [x] Suporte ABZ Group (FMS, OMEGA)
- [x] Suporte ABZ International (Jifmar)
- [x] Parser ABZ Charge Rate
- [x] Parser Jifmar Vessel
- [x] Metadata de sessão com client_id
- [x] Resposta padronizada

---

## 🎯 Próximos Passos (Etapa 2)

### Invoice Generator para Jifmar:
1. Criar `generate_abz_international_invoice()`
2. Geração sem templates (from scratch)
3. Usar dados do Jifmar parser
4. Suportar múltiplos clientes Jifmar (mesmo formato)

### Modificar Endpoint de Geração:
1. Atualizar `/api/generate/pdf`
2. Usar ClientProfile para determinar formato
3. Gerar filename correto por empresa
4. Salvar invoice com client tracking

---

## 📝 Notas Importantes

### Para Adicionar Novo Cliente:
```python
# 1. Criar ClientProfile
manager = get_client_profile_manager()
manager.add_profile(ClientProfile(
    client_id="NOVO_CLIENTE",
    client_name="Novo Cliente",
    company_id=1,
    spreadsheet_patterns=["*NOVO*"],
    spreadsheet_format=SpreadsheetFormat.ABZ_CHARGE_RATE,
    invoice_format=InvoiceFormat.ABZ_TEMPLATE,
    ...
))

# 2. Salvar no banco
python dev/init_clients.py

# 3. Pronto! Sistema já reconhece automaticamente!
```

### Para Testar Sem Afetar Produção:
```bash
# Sempre use modo DEV para testes
run_dev.bat

# Dados ficam em: data/invoice_system_dev.db
# Produção fica intacta em: data/invoice_system.db
```

---

**Status**: ✅ **ETAPA 1 COMPLETA!**
**Próximo**: Etapa 2 - Invoice Generator Multi-Empresa
**Última Atualização**: 2025-10-13

