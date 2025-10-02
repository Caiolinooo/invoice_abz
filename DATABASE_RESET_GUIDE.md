# 🔄 Database Reset Guide

## 📋 Problema Identificado

Ao tentar resetar o banco de dados através do endpoint `/api/reset-database`, ocorre o seguinte erro:

```
❌ Failed to reset database: [WinError 32] The process cannot access the file 
because it is being used by another process: 'data\\invoice_system.db'
```

### Causa

O SQLite mantém conexões abertas através do SQLAlchemy, e o Windows não permite deletar arquivos que estão sendo usados por processos ativos.

---

## ✅ Soluções Implementadas

### Solução 1: Endpoint Melhorado (Servidor Rodando)

O endpoint `/api/reset-database` foi melhorado com:

1. **Dispose do Engine**: Fecha todas as conexões do pool
2. **Garbage Collection**: Força liberação de handles de arquivo
3. **Retry Logic**: Tenta deletar o arquivo até 5 vezes com intervalo de 1 segundo
4. **Backup Automático**: Sempre cria backup antes de deletar

**Como usar:**
1. Acesse: `http://localhost:8000/ui/settings.html`
2. Clique em "Reset Database"
3. Confirme a ação
4. Aguarde o processo (pode levar alguns segundos)

**Limitações:**
- Pode falhar se houver muitas conexões ativas
- Requer que o servidor continue rodando após o reset

---

### Solução 2: Script de Reset (Servidor Parado) ⭐ RECOMENDADO

Um script Python foi criado para resetar o banco quando o servidor está parado.

**Como usar:**

1. **Parar o servidor:**
   ```bash
   # Pressione Ctrl+C no terminal do servidor
   ```

2. **Executar o script:**
   ```bash
   python reset_database.py
   ```

3. **Seguir as instruções:**
   - Confirmar que o servidor está parado
   - Confirmar o reset
   - Aguardar conclusão

4. **Reiniciar o servidor:**
   ```bash
   python start_server.py
   ```

**Vantagens:**
- ✅ 100% confiável (sem problemas de arquivo em uso)
- ✅ Backup automático
- ✅ Limpa arquivos auxiliares (journal, WAL, SHM)
- ✅ Instruções claras passo a passo

---

### Solução 3: Reset Manual

Se ambas as soluções falharem, você pode resetar manualmente:

1. **Parar o servidor:**
   ```bash
   # Pressione Ctrl+C no terminal do servidor
   ```

2. **Fazer backup (opcional mas recomendado):**
   ```bash
   # Windows PowerShell
   Copy-Item data\invoice_system.db data\invoice_system_backup_manual.db
   
   # Linux/Mac
   cp data/invoice_system.db data/invoice_system_backup_manual.db
   ```

3. **Deletar arquivos do banco:**
   ```bash
   # Windows PowerShell
   Remove-Item data\invoice_system.db
   Remove-Item data\invoice_system.db-journal -ErrorAction SilentlyContinue
   Remove-Item data\invoice_system.db-wal -ErrorAction SilentlyContinue
   Remove-Item data\invoice_system.db-shm -ErrorAction SilentlyContinue
   
   # Linux/Mac
   rm data/invoice_system.db
   rm -f data/invoice_system.db-journal
   rm -f data/invoice_system.db-wal
   rm -f data/invoice_system.db-shm
   ```

4. **Reiniciar o servidor:**
   ```bash
   python start_server.py
   ```

5. **Verificar:**
   - Novo banco será criado automaticamente
   - Usuário admin padrão será criado
   - Configurações padrão serão aplicadas

---

## 🔍 Troubleshooting

### Problema: "Database is locked"

**Sintoma:**
```
sqlite3.OperationalError: database is locked
```

**Solução:**
1. Parar o servidor
2. Deletar arquivos de lock:
   ```bash
   rm data/invoice_system.db-journal
   rm data/invoice_system.db-wal
   rm data/invoice_system.db-shm
   ```
3. Reiniciar o servidor

---

### Problema: "Permission denied"

**Sintoma:**
```
PermissionError: [Errno 13] Permission denied: 'data/invoice_system.db'
```

**Solução:**
1. Verificar se o servidor está realmente parado
2. Verificar se outro processo está usando o arquivo:
   ```bash
   # Windows
   tasklist | findstr python
   
   # Linux/Mac
   ps aux | grep python
   ```
3. Fechar todos os processos Python
4. Tentar novamente

---

### Problema: Backup não foi criado

**Sintoma:**
Banco resetado mas sem backup

**Solução:**
1. Verificar pasta `data/` para backups anteriores:
   ```bash
   ls data/invoice_system_backup_*.db
   ```
2. Se não houver backups, o banco foi perdido
3. **Prevenção:** Sempre fazer backup manual antes de operações críticas

---

## 📊 Arquivos do Banco de Dados

### Arquivos Principais

| Arquivo | Descrição |
|---------|-----------|
| `invoice_system.db` | Banco de dados principal |
| `invoice_system.db-journal` | Journal para transações (SQLite) |
| `invoice_system.db-wal` | Write-Ahead Log (modo WAL) |
| `invoice_system.db-shm` | Shared memory (modo WAL) |

### Arquivos de Backup

| Padrão | Exemplo |
|--------|---------|
| `invoice_system_backup_YYYYMMDD_HHMMSS.db` | `invoice_system_backup_20251002_163743.db` |

---

## 🎯 Recomendações

### Para Desenvolvimento

1. **Use o script de reset** (`reset_database.py`)
   - Mais confiável
   - Sem problemas de arquivo em uso
   - Backup automático

2. **Faça backups regulares**
   ```bash
   python -c "import shutil; from datetime import datetime; shutil.copy('data/invoice_system.db', f'data/backup_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.db')"
   ```

3. **Mantenha backups importantes**
   - Antes de mudanças grandes
   - Antes de testes destrutivos
   - Antes de deploys

### Para Produção

1. **NUNCA use reset em produção**
   - Perda total de dados
   - Sem recuperação

2. **Use migrations para mudanças de schema**
   ```bash
   alembic revision --autogenerate -m "description"
   alembic upgrade head
   ```

3. **Backups automáticos**
   - Configure backups diários
   - Armazene em local seguro
   - Teste restauração regularmente

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs do servidor
2. Tente o script de reset com servidor parado
3. Verifique permissões de arquivo
4. Verifique se há processos Python rodando
5. Como último recurso, delete manualmente

---

**Última atualização:** 02/10/2025

