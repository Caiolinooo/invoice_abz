# 🔧 Guia de Solução de Problemas

## ❌ Problema: Invoices geradas em XLSX mas NÃO em PDF

### Sintomas
- ✅ Arquivos XLSX são criados normalmente
- ❌ Arquivos PDF NÃO são criados
- ❌ Endpoint `/api/session/{id}/files` retorna 404
- ⚠️ Logs mostram: "LibreOffice não encontrado"

### Causa
O **LibreOffice não está instalado** no servidor. O sistema precisa do LibreOffice para converter XLSX em PDF.

### Solução

#### 1️⃣ Verificar o Status do Sistema

Acesse a página de diagnóstico:
```
http://seu-servidor:8000/ui/system-check.html
```

Ou via API:
```bash
curl http://localhost:8000/api/system/libreoffice-status
```

#### 2️⃣ Instalar o LibreOffice

**Windows (Automático via Web):**
1. Acesse: `http://localhost:8000/ui/system-check.html`
2. Clique em "📥 Instalar LibreOffice"
3. Aguarde a instalação
4. Reinicie o servidor

**Windows (Manual):**
```powershell
# Via Winget
winget install --id TheDocumentFoundation.LibreOffice --silent

# OU via Chocolatey
choco install libreoffice -y

# OU baixe manualmente
# https://www.libreoffice.org/download/download/
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install libreoffice -y
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install libreoffice -y
```

#### 3️⃣ Reiniciar o Servidor

**IMPORTANTE:** Após instalar o LibreOffice, você **DEVE reiniciar o servidor**:

```bash
# Pare o servidor (Ctrl+C no terminal)
# Inicie novamente
python start_server.py
```

#### 4️⃣ Verificar se Funcionou

Após reiniciar, verifique os logs. Você deve ver:

```
✅ PDF created: out/sessions/.../pdf/invoice.pdf
```

Se ainda aparecer erro, verifique:
```bash
# Teste se o LibreOffice está acessível
soffice --version

# Teste conversão manual
soffice --headless --convert-to pdf --outdir . teste.xlsx
```

---

## ❌ Problema: Erro 404 ao fazer login

### Sintomas
- ❌ POST `/api/auth/login` retorna 404
- ⚠️ Logs mostram: "Could not load authentication routes"

### Causa
Falta o pacote `email-validator` ou o servidor não foi reiniciado após instalação.

### Solução

```bash
# Instalar o pacote
pip install pydantic[email] email-validator

# Reiniciar o servidor (IMPORTANTE!)
# Ctrl+C para parar
python -m uvicorn app.api.enhanced_server:app --host 0.0.0.0 --port 8000 --reload
```

Verifique se as rotas foram carregadas. Você deve ver nos logs:
```
✅ Authentication routes loaded
```

---

## ❌ Problema: Servidor não inicia

### Sintomas
- Erro ao importar módulos
- Erro de porta já em uso

### Soluções

**Módulos faltando:**
```bash
pip install -r requirements.txt
```

**Porta em uso:**
```bash
# Windows - Encontrar processo na porta 8000
netstat -ano | findstr :8000

# Matar processo (substitua PID)
taskkill /PID <PID> /F

# Linux - Encontrar e matar processo
lsof -ti:8000 | xargs kill -9
```

---

## ❌ Problema: Conversão de PDF falha silenciosamente

### Sintomas
- XLSX criado
- Nenhum erro nos logs
- PDF não é criado

### Verificações

1. **Espaço em disco:**
```bash
# Windows
dir C:\
# Linux
df -h
```

2. **Permissões de escrita:**
```bash
# Verificar permissões da pasta out/
ls -la out/
```

3. **LibreOffice funcionando:**
```bash
soffice --version
soffice --headless --convert-to pdf --outdir . arquivo.xlsx
```

4. **Logs detalhados:**
Ative logs detalhados no código ou verifique:
```bash
# Ver logs em tempo real
tail -f logs/server.log
```

---

## ❌ Problema: Erro de CORS

### Sintomas
- Erro no console do navegador: "CORS policy"
- Requisições bloqueadas

### Solução

Verifique o arquivo `.env`:
```env
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://seu-dominio.com
```

Reinicie o servidor após alterar.

---

## ❌ Problema: Banco de dados não inicializa

### Sintomas
- Erro ao acessar `/api/invoices`
- Tabelas não existem

### Solução

```bash
# Deletar banco antigo (CUIDADO: perde dados!)
rm data/invoice_system.db

# Reiniciar servidor (recria automaticamente)
python start_server.py
```

---

## 📊 Logs Úteis

### Ver logs do servidor
```bash
# Logs em tempo real
python start_server.py

# Ou com mais detalhes
python -m uvicorn app.api.enhanced_server:app --host 0.0.0.0 --port 8000 --log-level debug
```

### Verificar status do sistema
```bash
curl http://localhost:8000/api/system/libreoffice-status
```

### Testar conversão PDF
```bash
curl -X POST http://localhost:8000/api/session/{session_id}/convert-pdfs
```

---

## 🆘 Ainda com problemas?

1. ✅ Verifique `/ui/system-check.html`
2. ✅ Leia `LIBREOFFICE_INSTALL.md`
3. ✅ Verifique os logs do servidor
4. ✅ Teste LibreOffice manualmente: `soffice --version`
5. ✅ Verifique permissões de arquivo
6. ✅ Verifique espaço em disco
7. ✅ Reinicie o servidor após qualquer instalação

---

## 📝 Checklist de Instalação Completa

- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas: `pip install -r requirements.txt`
- [ ] LibreOffice instalado: `soffice --version`
- [ ] Banco de dados inicializado (automático no primeiro start)
- [ ] Servidor rodando: `python start_server.py`
- [ ] Diagnóstico OK: `http://localhost:8000/ui/system-check.html`
- [ ] Login funcionando: `http://localhost:8000/ui/login.html`
- [ ] Conversão de PDF funcionando: teste com uma invoice

---

## 🎯 Teste Rápido

```bash
# 1. Verificar LibreOffice
soffice --version

# 2. Verificar servidor
curl http://localhost:8000/api/system/libreoffice-status

# 3. Testar conversão (substitua session_id)
curl -X POST http://localhost:8000/api/session/SEU_SESSION_ID/convert-pdfs

# 4. Verificar arquivos gerados
ls out/sessions/SEU_SESSION_ID/pdf/
```

Se todos os passos funcionarem, o sistema está OK! ✅

