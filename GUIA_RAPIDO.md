# 🚀 Guia Rápido - Sistema Multi-Empresa

## ⚡ Início Rápido (5 Minutos)

### 1. Inicializar Sistema (Primeira Vez Apenas)

```bash
# Passo 1: Criar empresas
python dev/init_companies_simple.py

# Passo 2: Criar clientes
python dev/init_clients.py

# Resultado:
# ✅ ABZ Group criado com FMS e OMEGA
# ✅ ABZ International criado com 5 vessels Jifmar
```

### 2. Rodar Sistema

#### Para TESTES (Recomendado):
```bash
# Clique duas vezes em:
run_dev.bat

# Ou:
set INVOICE_ENV=dev
cd dev
python -m uvicorn app.api.server:app --reload
```

#### Para PRODUÇÃO:
```bash
# Clique duas vezes em:
run_prod.bat

# Ou:
set INVOICE_ENV=prod
cd dev
python -m uvicorn app.api.server:app --reload
```

### 3. Acessar Sistema
```
http://localhost:8000/ui/
```

---

## 📊 Usar o Sistema

### Upload Planilha ABZ Group (FMS/OMEGA)

1. **Selecionar empresa**: ABZ Group
2. **Upload arquivo**: `ABZ - FMS - Rates 09.2025.xlsx`
3. **Sistema detecta**: Cliente FMS automaticamente
4. **Configurar**:
   - Invoice No: 141
   - Invoice Date: 12/09/2025
5. **Gerar invoices**
6. **Resultado**: `ABZ Group 141-2025 FMS 09 2025 Filipi.xlsx`

### Upload Planilha ABZ International (Jifmar)

1. **Selecionar empresa**: ABZ International
2. **Upload arquivo**: `ABZ - Jifmar - Monthly Rates.xlsx`
3. **Sistema detecta**: Cliente Jifmar automaticamente
4. **Configurar**:
   - Invoice No: 142
   - Invoice Date: 13/10/2025
5. **Gerar invoices**
6. **Resultado**: `ABZ International 142-2025 Voe Vanguard 09 2025 Mihails.xlsx`

---

## 🎯 Adicionar Novo Cliente

### Exemplo: Adicionar "SHELL" na ABZ Group

```python
# 1. Editar: dev/init_clients.py
# Adicionar antes de db.commit():

new_client = Client(
    client_id="SHELL",
    client_name="Shell",
    company_id=1,
    spreadsheet_format="abz_charge_rate",
    invoice_format="abz_template",
    filename_template="ABZ Group {invoice_no}-{year} SHELL {month} {year} {first_name}",
    currency="GBP",
    category="offshore",
    config_json=json.dumps({
        "spreadsheet_patterns": ["*SHELL*", "*Shell*"]
    }),
    is_active=True
)
db.add(new_client)

# 2. Executar:
python dev/init_clients.py

# 3. Pronto! Sistema já reconhece planilhas SHELL!
```

---

## 🔧 Modo Dev vs Prod

### Modo DEV (Testes)
```bash
run_dev.bat
```
- ✅ Banco: `data/invoice_system_dev.db`
- ✅ SQL logging ativado
- ✅ Não afeta produção
- ✅ Pode testar à vontade

### Modo PROD (Real)
```bash
run_prod.bat
```
- ⚠️ Banco: `data/invoice_system.db`
- ⚠️ SQL logging desativado
- ⚠️ Dados reais
- ⚠️ Cuidado ao testar

---

## 📁 Onde Estão os Arquivos?

### Invoices Gerados
```
out/sessions/{session_id}/invoices/
├── ABZ Group 141-2025 FMS 09 2025 Filipi.xlsx
├── ABZ Group 142-2025 FMS 09 2025 Gil.xlsx
└── ...
```

### Banco de Dados
```
data/
├── invoice_system.db       # Produção
└── invoice_system_dev.db   # Desenvolvimento
```

### Logs
```
debug_log.txt
```

---

## 🆘 Problemas Comuns

### Erro: "Company not found"
**Solução**: Executar `python dev/init_companies_simple.py`

### Erro: "Client profile not found"
**Solução**: Executar `python dev/init_clients.py`

### Erro: "Could not detect client"
**Solução**: Verificar se nome do arquivo contém identificador do cliente (FMS, OMEGA, Jifmar)

### Erro: "Module not found"
**Solução**: Verificar se está rodando de dentro da pasta `dev/`

---

## 📞 Endpoints API

### Listar Empresas
```bash
GET http://localhost:8000/api/companies
```

### Listar Clientes
```bash
GET http://localhost:8000/api/clients?company_id=1
```

### Upload Planilha
```bash
POST http://localhost:8000/api/v2/import
Form Data:
  - abz: file
  - company_id: 1
```

### Gerar Invoices
```bash
POST http://localhost:8000/api/v2/generate
Form Data:
  - session_id: abc123
  - invoice_no: 141
  - invoice_date: 12/09/2025
```

---

## ✅ Checklist Diário

### Antes de Começar:
- [ ] Rodar em modo DEV para testes
- [ ] Verificar empresas: `GET /api/companies`
- [ ] Verificar clientes: `GET /api/clients`

### Ao Processar Planilhas:
- [ ] Selecionar empresa correta
- [ ] Upload planilha
- [ ] Verificar cliente detectado
- [ ] Configurar invoice number
- [ ] Gerar invoices
- [ ] Verificar arquivos gerados

### Ao Finalizar:
- [ ] Verificar relatórios
- [ ] Backup do banco (se prod)
- [ ] Limpar sessões antigas (opcional)

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
- `IMPLEMENTACAO_COMPLETA.md` - Guia completo
- `SISTEMA_MULTI_CLIENTE_COMPLETO.md` - Visão geral
- `FASE_2_ETAPA_1_COMPLETA.md` - Detalhes técnicos

---

## 🎉 Pronto!

Sistema está **100% funcional** e pronto para uso!

**Dúvidas?** Consulte a documentação completa ou os arquivos de exemplo.

**Bom trabalho!** 🚀

