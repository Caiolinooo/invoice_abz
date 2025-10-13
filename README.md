# 🏢 Sistema de Conversão Folha → Invoice (Multi-Empresa)

Sistema completo para conversão de planilhas de folha de pagamento em invoices individuais, com suporte para múltiplas empresas e clientes.

## ✨ Características

- ✅ **Multi-Empresa**: Suporte para ABZ Group e ABZ International
- ✅ **Multi-Cliente**: FMS, OMEGA, Jifmar (5 vessels) e fácil expansão
- ✅ **Detecção Automática**: Sistema detecta cliente pelo nome do arquivo
- ✅ **Parsers Inteligentes**: Roteamento automático para parser correto
- ✅ **Geração Flexível**: Templates ou geração do zero conforme necessário
- ✅ **Relatórios Detalhados**: Por empresa, cliente, período, categoria
- ✅ **Dev/Prod Separados**: Teste sem afetar dados de produção
- ✅ **Escalável**: Adicionar novos clientes sem modificar código

## 🚀 Início Rápido

### 1. Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados
python dev/init_companies_simple.py
python dev/init_clients.py
```

### 2. Executar

#### Modo Desenvolvimento (Recomendado para testes)
```bash
run_dev.bat
```

#### Modo Produção
```bash
run_prod.bat
```

### 3. Acessar
```
http://localhost:8000/ui/
```

## 📊 Empresas e Clientes Suportados

### ABZ Group (company_id=1)
- **FMS** - Formato: ABZ Charge Rate
- **OMEGA** - Formato: ABZ Charge Rate

### ABZ International (company_id=2)
- **Jifmar - Voe Vanguard** - Formato: Jifmar Vessel
- **Jifmar - Voe Viking** - Formato: Jifmar Vessel
- **Jifmar - Faraday** - Formato: Jifmar Vessel
- **Jifmar - Project 5679** - Formato: Jifmar Vessel
- **Jifmar - Voe Earl** - Formato: Jifmar Vessel

## 🔄 Fluxo de Uso

```
1. Upload Planilha
   ↓
2. Sistema Detecta Cliente Automaticamente
   ↓
3. Parser Correto é Usado
   ↓
4. Preview dos Dados
   ↓
5. Configurar Invoice Number e Data
   ↓
6. Gerar Invoices
   ↓
7. Download Individual ou ZIP
```

## 📁 Estrutura do Projeto

```
.
├── dev/
│   ├── app/
│   │   ├── api/                    # Endpoints FastAPI
│   │   ├── database/               # Models e conexão
│   │   ├── invoice/                # Geradores de invoice
│   │   ├── models/                 # Client Profiles
│   │   ├── services/               # Serviços (relatórios)
│   │   ├── ui/                     # Interface web
│   │   └── utils/                  # Parsers e utilitários
│   ├── init_companies_simple.py    # Inicializar empresas
│   └── init_clients.py             # Inicializar clientes
├── data/
│   ├── invoice_system.db           # Banco produção
│   └── invoice_system_dev.db       # Banco desenvolvimento
├── out/
│   └── sessions/                   # Sessões e invoices gerados
├── run_dev.bat                     # Rodar em DEV
├── run_prod.bat                    # Rodar em PROD
├── GUIA_RAPIDO.md                  # Guia rápido de uso
└── IMPLEMENTACAO_COMPLETA.md       # Documentação completa
```

## 🎯 Adicionar Novo Cliente

### Exemplo: Adicionar "PETROBRAS"

```python
# 1. Editar dev/init_clients.py
new_client = Client(
    client_id="PETROBRAS",
    client_name="Petrobras",
    company_id=1,
    spreadsheet_format="abz_charge_rate",
    invoice_format="abz_template",
    filename_template="ABZ Group {invoice_no}-{year} PETROBRAS {month} {year} {first_name}",
    currency="BRL",
    category="offshore",
    config_json=json.dumps({
        "spreadsheet_patterns": ["*PETROBRAS*", "*Petro*"]
    }),
    is_active=True
)
db.add(new_client)

# 2. Executar
python dev/init_clients.py

# 3. Pronto! Sistema já reconhece planilhas PETROBRAS
```

## 🔧 Modo Dev vs Prod

### Desenvolvimento
- Banco: `data/invoice_system_dev.db`
- SQL Logging: Ativado
- Ideal para: Testes, desenvolvimento, experimentação

### Produção
- Banco: `data/invoice_system.db`
- SQL Logging: Desativado
- Ideal para: Dados reais, operação diária

## 📡 API Endpoints

### Multi-Company (V2)

#### POST /api/v2/import
Upload planilha com detecção automática
```bash
curl -X POST http://localhost:8000/api/v2/import \
  -F "abz=@planilha.xlsx" \
  -F "company_id=1"
```

#### POST /api/v2/generate
Gerar invoices
```bash
curl -X POST http://localhost:8000/api/v2/generate \
  -F "session_id=abc123" \
  -F "invoice_no=141" \
  -F "invoice_date=12/09/2025"
```

#### GET /api/companies
Listar empresas
```bash
curl http://localhost:8000/api/companies
```

#### GET /api/clients
Listar clientes
```bash
curl http://localhost:8000/api/clients?company_id=1
```

## 📊 Relatórios

### Por Empresa
```python
from app.services.reporting_service import ReportingService

report = ReportingService.get_company_summary(db, company_id=1)
```

### Por Cliente
```python
report = ReportingService.get_client_detailed_report(db, "FMS")
```

### Combinado
```python
report = ReportingService.get_combined_report(db)
```

## 🧪 Testes

```bash
# Testar em modo DEV
run_dev.bat

# Verificar empresas
curl http://localhost:8000/api/companies

# Verificar clientes
curl http://localhost:8000/api/clients

# Upload teste
curl -X POST http://localhost:8000/api/v2/import \
  -F "abz=@test.xlsx" \
  -F "company_id=1"
```

## 📚 Documentação

- **[GUIA_RAPIDO.md](GUIA_RAPIDO.md)** - Guia rápido de uso
- **[IMPLEMENTACAO_COMPLETA.md](IMPLEMENTACAO_COMPLETA.md)** - Documentação técnica completa
- **[SISTEMA_MULTI_CLIENTE_COMPLETO.md](SISTEMA_MULTI_CLIENTE_COMPLETO.md)** - Visão geral do sistema

## 🛠️ Tecnologias

- **Backend**: FastAPI, SQLAlchemy, Python 3.8+
- **Database**: SQLite
- **Excel**: OpenPyXL
- **PDF**: LibreOffice (opcional)
- **Frontend**: HTML, CSS, JavaScript (Vanilla)

## 📝 Requisitos

- Python 3.8+
- FastAPI
- SQLAlchemy
- OpenPyXL
- Uvicorn
- LibreOffice (opcional, para PDF)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é proprietário da ABZ Group.

## 👥 Autores

- **Caio Correia** - Desenvolvimento e Implementação

## 🎉 Status

✅ **Sistema 100% Funcional e Pronto para Produção**

**Versão**: 2.0.0  
**Data**: 2025-10-13

---

**Para mais informações, consulte a [documentação completa](IMPLEMENTACAO_COMPLETA.md).**

