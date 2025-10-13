# 🔄 Como Resetar o Banco de Dados

Este guia explica como resetar o banco de dados do sistema de invoices.

---

## 🎯 Método 1: Reset Online (Recomendado)

**Vantagens:**
- ✅ Não precisa parar o servidor
- ✅ Funciona direto pela interface web
- ✅ Backup automático
- ✅ Evita problemas de arquivo em uso (WinError 32)

**Como fazer:**

1. **Acesse a interface de administração:**
   ```
   http://localhost:8000/ui/index.html
   ```

2. **Faça login como Admin:**
   - Email: `admin@abzgroup.com`
   - Senha: `admin123`

3. **Vá para Settings (Configurações)**

4. **Na seção "Database Management":**
   - Digite a senha de confirmação: `2122`
   - Clique em "Reset All Data"
   - Confirme as 3 vezes que o sistema pedir

5. **Aguarde a conclusão:**
   - O sistema irá:
     - ✅ Criar backup automático
     - ✅ Deletar todas as sessões e arquivos
     - ✅ Limpar todas as tabelas do banco
     - ✅ Recriar as tabelas vazias
     - ✅ Inicializar dados padrão

6. **Pronto!** O banco está resetado e pronto para uso.

---

## 🛠️ Método 2: Reset Offline (Alternativo)

Use este método se o reset online falhar ou se preferir ter controle total.

**Vantagens:**
- ✅ 100% confiável (sem problemas de arquivo em uso)
- ✅ Backup automático
- ✅ Limpa arquivos auxiliares (journal, WAL, SHM)

**Como fazer:**

1. **Pare o servidor:**
   ```powershell
   # Pressione Ctrl+C no terminal do servidor
   ```

2. **Execute o script de reset:**
   ```powershell
   python reset_database.py
   ```

3. **Siga as instruções:**
   ```
   Is the server stopped? (yes/no): yes
   Are you sure you want to reset the database? (yes/no): yes
   ```

4. **Aguarde a conclusão:**
   ```
   📦 Database backed up to: data\invoice_system_backup_20251002_143000.db
   🗑️  Database deleted: data\invoice_system.db
   🗑️  Deleted: data\invoice_system.db-journal
   🗑️  Deleted: data\invoice_system.db-wal
   🗑️  Deleted: data\invoice_system.db-shm
   ✅ Database reset successfully!
   ```

5. **Reinicie o servidor:**
   ```powershell
   python start_server.py
   ```
   ou
   ```powershell
   uvicorn app.api.server:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Pronto!** O servidor criará um novo banco de dados automaticamente.

---

## 🚨 Método 3: Reset Manual (Último Recurso)

Use apenas se os métodos anteriores falharem.

**Como fazer:**

1. **Pare o servidor:**
   ```powershell
   # Pressione Ctrl+C no terminal do servidor
   ```

2. **Faça backup manual (opcional mas recomendado):**
   ```powershell
   # Windows PowerShell
   Copy-Item data\invoice_system.db data\invoice_system_backup_manual.db
   ```

3. **Delete os arquivos do banco:**
   ```powershell
   # Windows PowerShell
   Remove-Item data\invoice_system.db
   Remove-Item data\invoice_system.db-journal -ErrorAction SilentlyContinue
   Remove-Item data\invoice_system.db-wal -ErrorAction SilentlyContinue
   Remove-Item data\invoice_system.db-shm -ErrorAction SilentlyContinue
   ```

4. **Delete as sessões (opcional):**
   ```powershell
   Remove-Item out\sessions -Recurse -Force -ErrorAction SilentlyContinue
   ```

5. **Reinicie o servidor:**
   ```powershell
   python start_server.py
   ```

6. **Pronto!** O servidor criará um novo banco de dados automaticamente.

---

## 📋 O que é resetado?

Quando você reseta o banco de dados, os seguintes itens são removidos:

### Dados do Banco de Dados:
- ✅ Todas as invoices
- ✅ Todas as sessões
- ✅ Todos os logs de email
- ✅ Todos os logs de auditoria

### Arquivos no Sistema:
- ✅ Todas as pastas de sessão em `out/sessions/`
- ✅ Todos os arquivos XLSX gerados
- ✅ Todos os arquivos PDF gerados
- ✅ Sequência de numeração de invoices

### O que NÃO é resetado:
- ❌ Usuários (admin, manager, etc.)
- ❌ Configurações da empresa
- ❌ Templates de invoice
- ❌ Configurações do sistema

---

## 🔍 Verificando o Reset

Após o reset, você pode verificar se funcionou:

1. **Acesse a interface:**
   ```
   http://localhost:8000/ui/index.html
   ```

2. **Faça login**

3. **Verifique:**
   - Lista de invoices deve estar vazia
   - Contador de invoices deve estar em 0
   - Não deve haver sessões antigas

---

## ⚠️ Problemas Comuns

### Erro: "Database is locked" ou "WinError 32"

**Causa:** O arquivo do banco de dados está sendo usado por outro processo.

**Solução:**
1. Use o **Método 1 (Reset Online)** - ele evita esse problema
2. Se ainda falhar, use o **Método 2 (Reset Offline)**
3. Certifique-se de que o servidor está realmente parado

### Erro: "Permission denied"

**Causa:** Você não tem permissão para deletar os arquivos.

**Solução:**
1. Execute o PowerShell como Administrador
2. Ou use o **Método 1 (Reset Online)** que não precisa de permissões especiais

### Erro: "Module not found"

**Causa:** Você está executando o script do diretório errado.

**Solução:**
1. Certifique-se de estar no diretório raiz do projeto
2. Execute: `cd d:\Projeto\Finalizados\Conversão da Folha-Invoice-Financeiro\dev`

---

## 💡 Dicas

1. **Sempre faça backup antes de resetar** - os métodos automáticos já fazem isso
2. **Use o Método 1 sempre que possível** - é o mais conveniente
3. **Guarde os backups** - eles ficam em `data/invoice_system_backup_*.db`
4. **Teste após o reset** - gere uma invoice de teste para confirmar

---

## 📞 Suporte

Se nenhum dos métodos funcionar, verifique:

1. **Logs do servidor** - procure por mensagens de erro
2. **Permissões de arquivo** - certifique-se de ter acesso à pasta `data/`
3. **Processos em execução** - feche todos os programas que possam estar usando o banco

---

## 🎉 Pronto!

Agora você sabe como resetar o banco de dados de 3 formas diferentes. Use o método que melhor se adequar à sua situação!

