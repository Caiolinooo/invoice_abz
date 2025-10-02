# 🚀 Release v9.0.0 - Database Integration & System Diagnostics

**Data de Lançamento:** 02 de Outubro de 2025

## 📋 Resumo

Esta versão traz integração completa com banco de dados, sistema de autenticação, diagnóstico de sistema e correções críticas para geração de PDFs e persistência de dados.

---

## ✨ Novos Recursos

### 🗄️ Sistema de Banco de Dados
- **SQLite Database** com SQLAlchemy ORM
- **Modelos de Dados:**
  - Companies (empresas)
  - Users (usuários com autenticação)
  - Invoices (rastreamento completo de invoices)
  - Templates (gerenciamento de templates)
  - Configurations (configurações do sistema)
  - Sessions (rastreamento de sessões)
  - EmailLogs (histórico de emails)

### 🔐 Sistema de Autenticação
- **Login/Logout** com JWT tokens
- **Gerenciamento de Usuários**
- **Controle de Acesso** por roles (admin, user, viewer)
- **Senha Segura** com bcrypt hashing
- **Sessões Persistentes**

### 📊 Histórico de Invoices
- **Visualização** de todas as invoices geradas
- **Filtros** por data, funcionário, status
- **Busca** por número de invoice
- **Exportação** de dados
- **Estatísticas** de geração

### ⚙️ Página de Configurações
- **Configurações Gerais** (empresa, moeda, timezone)
- **Configurações de Email** (SMTP, templates)
- **Gerenciamento de Templates**
- **Reset de Banco de Dados**

### 🔧 Sistema de Diagnóstico
- **Verificação do LibreOffice**
  - Status de instalação
  - Versão instalada
  - Caminho do executável
- **Instalação Automática** (Windows)
  - Via winget
  - Via chocolatey
- **Página Web de Diagnóstico** (`/ui/system-check.html`)
- **API Endpoints:**
  - `GET /api/system/libreoffice-status`
  - `POST /api/system/install-libreoffice`

---

## 🐛 Correções Críticas

### 1. **Invoice Number NULL no Banco**
- **Problema:** `NOT NULL constraint failed: invoices.invoice_number`
- **Causa:** Campo sendo passado como `None`
- **Solução:** Validação automática com geração de número sequencial
- **Arquivo:** `app/api/enhanced_server.py`

### 2. **PDFs Não Sendo Gerados**
- **Problema:** Apenas XLSX criado, sem PDF
- **Causa:** Código não estava convertendo XLSX para PDF
- **Solução:** Conversão automática após gerar XLSX
- **Arquivo:** `app/api/enhanced_server.py`

### 3. **Endpoint `/api/session/{id}/files` Retornava 404**
- **Problema:** Frontend não conseguia listar arquivos
- **Causa:** Endpoint não existia
- **Solução:** Criado endpoint que lista XLSX e PDF
- **Arquivo:** `app/api/enhanced_server.py`

### 4. **Endpoint `/api/reset-database` Não Existia**
- **Problema:** 404 ao tentar resetar banco
- **Causa:** Endpoint não implementado
- **Solução:** Criado endpoint com backup automático
- **Arquivo:** `app/api/enhanced_server.py`

---

## 🔄 Melhorias

### Logs Detalhados de Conversão PDF
- **Mensagens claras** de erro e sucesso
- **Timeout de 30 segundos** para conversão
- **Logs de stdout/stderr** do LibreOffice
- **Verificação** se PDF foi criado
- **Arquivo:** `app/utils/libreoffice_export.py`

### Interface do Usuário
- **Menu de Navegação** atualizado
- **Link para Diagnóstico** no menu principal
- **Páginas Responsivas**
- **Feedback Visual** melhorado

### Documentação
- **LIBREOFFICE_INSTALL.md** - Guia completo de instalação
- **TROUBLESHOOTING.md** - Solução de problemas comuns
- **DATABASE_README.md** - Documentação do banco de dados
- **AUTHENTICATION_GUIDE.md** - Guia de autenticação

---

## 📁 Arquivos Modificados

### Backend
- ✅ `app/api/enhanced_server.py` - Novos endpoints e correções
- ✅ `app/utils/libreoffice_export.py` - Logs detalhados
- ✅ `app/database/` - Novo módulo de banco de dados
- ✅ `app/auth/` - Novo módulo de autenticação

### Frontend
- ✅ `app/ui/index.html` - Link para diagnóstico
- ✅ `app/ui/system-check.html` - Nova página de diagnóstico
- ✅ `app/ui/login.html` - Nova página de login
- ✅ `app/ui/settings.html` - Nova página de configurações
- ✅ `app/ui/history.html` - Nova página de histórico
- ✅ `app/ui/*.js` - Scripts das novas páginas
- ✅ `app/ui/styles.css` - Estilos atualizados

### Documentação
- ✅ `LIBREOFFICE_INSTALL.md` - Novo
- ✅ `TROUBLESHOOTING.md` - Novo
- ✅ `DATABASE_README.md` - Novo
- ✅ `AUTHENTICATION_GUIDE.md` - Novo
- ✅ `.env.example` - Novo

---

## 🚀 Como Atualizar

### 1. Atualizar o Código
```bash
git pull origin master
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Verificar LibreOffice
```bash
# Acessar página de diagnóstico
http://localhost:8000/ui/system-check.html

# Ou verificar manualmente
soffice --version
```

### 4. Inicializar Banco de Dados
```bash
python init_database.py
```

### 5. Reiniciar Servidor
```bash
python start_server.py
```

---

## 📊 Estatísticas

- **Arquivos Modificados:** 15+
- **Novos Arquivos:** 20+
- **Linhas de Código Adicionadas:** ~3000
- **Bugs Corrigidos:** 4 críticos
- **Novos Endpoints:** 8
- **Documentação:** 4 novos guias

---

## ⚠️ Breaking Changes

### Banco de Dados
- **Migração necessária** se estiver usando versão anterior
- **Backup recomendado** antes de atualizar

### Autenticação
- **Login obrigatório** para acessar o sistema
- **Usuário padrão:**
  - Email: `admin@abzgroup.com`
  - Senha: `admin123` (alterar após primeiro login)

---

## 🔜 Próximas Versões

### v9.1.0 (Planejado)
- [ ] Envio automático de emails
- [ ] Notificações em tempo real
- [ ] Dashboard com gráficos
- [ ] Exportação para outros formatos

### v9.2.0 (Planejado)
- [ ] Multi-tenancy (múltiplas empresas)
- [ ] API REST completa
- [ ] Integração com sistemas externos
- [ ] Mobile app

---

## 🐛 Problemas Conhecidos

1. **LibreOffice no Linux**
   - Instalação manual necessária
   - Solução: `sudo apt install libreoffice -y`

2. **Conversão PDF Lenta**
   - Primeira conversão pode demorar
   - Solução: Normal, conversões seguintes são mais rápidas

---

## 👥 Contribuidores

- **Caio Correia** - Desenvolvimento principal
- **Equipe ABZ Group** - Testes e feedback

---

## 📞 Suporte

- **Documentação:** Ver arquivos `.md` no repositório
- **Diagnóstico:** `http://localhost:8000/ui/system-check.html`
- **Issues:** GitHub Issues

---

## 📝 Notas de Migração

### De v8.0.0 para v9.0.0

1. **Backup do banco de dados** (se existir)
2. **Atualizar código:** `git pull`
3. **Instalar dependências:** `pip install -r requirements.txt`
4. **Inicializar banco:** `python init_database.py`
5. **Verificar LibreOffice:** Acessar `/ui/system-check.html`
6. **Testar geração:** Criar uma invoice de teste

---

**Versão Completa e Estável** ✅

Esta versão resolve todos os problemas críticos identificados e adiciona funcionalidades essenciais para produção.

