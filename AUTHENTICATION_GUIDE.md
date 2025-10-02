# 🔐 Sistema de Autenticação - Guia Completo

## 📋 Visão Geral

O Invoice System agora possui um sistema completo de autenticação integrado com o Supabase do Employee Hub. Apenas usuários com roles **Admin** ou **Gerente** podem acessar o sistema.

---

## 🚀 Configuração Inicial

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Novas dependências:**
- `supabase` - Cliente Supabase
- `python-jose[cryptography]` - JWT tokens
- `passlib[bcrypt]` - Password hashing
- `slowapi` - Rate limiting

### 2. Configurar Variáveis de Ambiente

Edite o arquivo `.env` com as credenciais do Supabase:

```env
# Supabase (Employee Hub)
SUPABASE_URL=https://arzvingdtnttiejcvucs.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8

# Security
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
RATE_LIMIT_PER_MINUTE=5
```

**Como obter as credenciais do Supabase:**
1. Acesse: https://app.supabase.com/project/arzvingdtnttiejcvucs/settings/api
2. Copie a **Project URL** para `SUPABASE_URL`
3. Copie a **anon public** key para `SUPABASE_ANON_KEY`
4. Copie a **service_role** key para `SUPABASE_SERVICE_KEY`

**Gerar JWT Secret Key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Inicializar Banco de Dados

```bash
python scripts/init_database.py
```

Isso criará a tabela `audit_logs` para registrar acessos.

### 4. Iniciar Servidor

```bash
python -m uvicorn app.api.server:app --reload
```

---

## 🔑 Como Funciona

### Fluxo de Autenticação

```
1. Usuário acessa /ui/history.html
   ↓
2. auth.js verifica se JWT existe
   ↓ (não existe)
3. Redireciona para /ui/login.html
   ↓
4. Usuário insere email/password
   ↓
5. POST /api/auth/login
   ↓
6. Backend verifica credenciais no Supabase
   ↓
7. Verifica role (Admin ou Gerente)
   ↓
8. Gera JWT token (válido por 8 horas)
   ↓
9. Frontend salva token no localStorage
   ↓
10. Redireciona para /ui/history.html
```

### Proteção de Rotas

**Rotas Protegidas (requerem autenticação):**
- `POST /api/import` - Upload de arquivos
- `POST /api/generate` - Geração de invoices
- `GET /api/invoices` - Listar invoices
- `GET /api/invoices/{id}/pdf` - Download de PDF
- `POST /api/reset-database` - Reset (apenas Admin)
- `/ui/history.html` - Histórico de invoices
- `/ui/settings.html` - Configurações
- `/ui/index.html` - Página principal

**Rotas Públicas:**
- `POST /api/auth/login` - Login
- `GET /api/auth/verify` - Verificar token
- `/ui/login.html` - Página de login

---

## 🧪 Testes

### Teste 1: Login com Credenciais Válidas

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password123"
  }'
```

**Resposta esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "id": "uuid",
    "email": "admin@example.com",
    "name": "Admin User",
    "role": "Admin"
  }
}
```

### Teste 2: Login com Credenciais Inválidas

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "wrong@example.com",
    "password": "wrongpassword"
  }'
```

**Resposta esperada:**
```json
{
  "detail": "Invalid email or password"
}
```
**Status:** 401 Unauthorized

### Teste 3: Acesso sem Autenticação

```bash
curl -X GET http://localhost:8000/api/invoices
```

**Resposta esperada:**
```json
{
  "detail": "Missing or invalid authorization header",
  "redirect": "/ui/login.html"
}
```
**Status:** 401 Unauthorized

### Teste 4: Acesso com Token Válido

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/api/invoices \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada:**
```json
[
  {
    "id": 1,
    "invoice_number": "000001/2025",
    "employee_name": "João Silva",
    ...
  }
]
```
**Status:** 200 OK

### Teste 5: Rate Limiting

Execute 6 tentativas de login em menos de 1 minuto:

```bash
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"test"}'
  echo ""
done
```

**Na 6ª tentativa, resposta esperada:**
```json
{
  "detail": "Rate limit exceeded. Maximum 5 requests per minute.",
  "retry_after": 60
}
```
**Status:** 429 Too Many Requests

### Teste 6: Usuário sem Permissão

Se um usuário com role "User" tentar fazer login:

**Resposta esperada:**
```json
{
  "detail": "Access denied. Only Admin and Gerente roles can access this system. Your role: User"
}
```
**Status:** 403 Forbidden

---

## 🛡️ Segurança Implementada

### 1. JWT Tokens
- ✅ Assinados com HS256
- ✅ Secret key forte (32+ caracteres)
- ✅ Expiração de 8 horas
- ✅ JWT ID único (previne replay attacks)
- ✅ Payload inclui: user_id, email, role, exp, iat, jti

### 2. Role-Based Access Control (RBAC)
- ✅ Apenas Admin e Gerente podem acessar
- ✅ Verificação de role em cada request
- ✅ Admin tem permissões extras (reset database)

### 3. Rate Limiting
- ✅ Máximo 5 tentativas de login por minuto
- ✅ Previne brute force attacks
- ✅ Baseado em IP address

### 4. CORS
- ✅ Apenas origens permitidas
- ✅ Configurável via .env
- ✅ Suporta credenciais

### 5. Audit Logging
- ✅ Registra todos os logins
- ✅ Registra acessos às rotas
- ✅ IP address e user agent
- ✅ Timestamp de cada ação

### 6. Password Security
- ✅ Senhas nunca armazenadas em plain text
- ✅ Bcrypt hashing
- ✅ Autenticação via Supabase Auth

---

## 📱 Interface do Usuário

### Página de Login (`/ui/login.html`)

**Recursos:**
- Design moderno com gradiente
- Animações suaves
- Mensagens de erro claras
- Seletor de idioma (PT-BR/EN)
- Validação de formulário
- Loading spinner durante login

**Campos:**
- Email (obrigatório)
- Password (obrigatório)

### Botão de Logout

Aparece no header de todas as páginas autenticadas:
- Mostra nome do usuário
- Mostra role (Admin/Gerente)
- Botão de logout com ícone

---

## 🔧 Troubleshooting

### Erro: "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set"

**Solução:** Configure as variáveis no arquivo `.env`

### Erro: "Invalid or expired token"

**Solução:** 
1. Faça logout
2. Faça login novamente
3. Token expira após 8 horas

### Erro: "User account is inactive"

**Solução:** Ative o usuário no Supabase:
```sql
UPDATE users SET is_active = true WHERE email = 'user@example.com';
```

### Erro: "Access denied. Only Admin and Gerente roles"

**Solução:** Atualize o role do usuário no Supabase:
```sql
UPDATE users SET role = 'Admin' WHERE email = 'user@example.com';
```

### Rate Limit Atingido

**Solução:** Aguarde 1 minuto ou aumente o limite no `.env`:
```env
RATE_LIMIT_PER_MINUTE=10
```

---

## 📊 Audit Logs

Todos os acessos são registrados na tabela `audit_logs`:

```sql
SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 10;
```

**Campos:**
- `user_id` - UUID do usuário
- `user_email` - Email do usuário
- `action` - Ação realizada (login, logout, access_denied)
- `resource` - Recurso acessado (/api/invoices)
- `ip_address` - IP do cliente
- `user_agent` - Navegador/cliente
- `success` - Se a ação foi bem-sucedida
- `timestamp` - Data/hora da ação

---

## 🎯 Próximos Passos

### Melhorias Futuras

1. **Two-Factor Authentication (2FA)**
   - Adicionar suporte a TOTP
   - SMS verification

2. **Session Management**
   - Listar sessões ativas
   - Revogar tokens específicos
   - Logout de todos os dispositivos

3. **Password Reset**
   - Endpoint de recuperação de senha
   - Email com link de reset

4. **IP Whitelisting**
   - Permitir apenas IPs específicos
   - Configurável por usuário

5. **Advanced Audit Logging**
   - Dashboard de auditoria
   - Alertas de atividades suspeitas
   - Exportação de logs

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs do servidor
2. Verifique o console do navegador (F12)
3. Verifique as credenciais do Supabase
4. Verifique se o usuário tem role Admin ou Gerente
5. Verifique se o usuário está ativo no Supabase

---

**Sistema de Autenticação Completo e Funcional!** 🎉

