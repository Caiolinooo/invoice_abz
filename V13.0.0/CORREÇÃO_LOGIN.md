# Correção do Sistema de Login

## Problema Identificado

O sistema de login estava retornando erro 500 porque estava tentando usar o Supabase Auth (`client.auth.sign_in_with_password()`) para autenticar usuários que foram criados diretamente na tabela `users_unified` sem passar pelo sistema de autenticação do Supabase.

## Análise Comparativa

### Employee Hub (painelabz) - Funcionando ✅
- Usa bcrypt para verificar senhas diretamente contra o hash na tabela
- Não depende do Supabase Auth para autenticação
- Busca usuário na tabela `users_unified`
- Verifica o hash da senha com bcrypt.checkpw()
- Gera JWT próprio após autenticação bem-sucedida

### Projeto Atual - Com Erro ❌
- Tentava usar `client.auth.sign_in_with_password()`
- Falhava porque os usuários não estão no Supabase Auth
- Retornava erro 400: "Invalid login credentials"

## Solução Implementada

Modificada a função `verify_user_credentials` em `app/auth/supabase_client.py` para:

1. **Buscar usuário diretamente na tabela** `users_unified`
2. **Verificar senha com bcrypt** em vez de usar Supabase Auth
3. **Retornar dados do usuário** se autenticação for bem-sucedida

### Código Corrigido

```python
async def verify_user_credentials(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verify user credentials by checking password hash directly in database
    (Similar to Employee Hub implementation)
    """
    try:
        import bcrypt
        
        client = get_supabase_client()
        print(f"🔐 Attempting authentication for: {email}")
        
        # Get user data from users_unified table
        user_data = await get_user_by_email(email)

        if not user_data:
            print(f"❌ User not found: {email}")
            return None

        # Check if user has a password hash
        password_hash = user_data.get("password") or user_data.get("password_hash")
        
        if not password_hash:
            print(f"❌ User has no password set: {email}")
            return None

        # Verify password using bcrypt (like Employee Hub)
        password_bytes = password.encode('utf-8') if isinstance(password, str) else password
        hash_bytes = password_hash.encode('utf-8') if isinstance(password_hash, str) else password_hash
        
        is_valid = bcrypt.checkpw(password_bytes, hash_bytes)
        
        if not is_valid:
            print(f"❌ Invalid password for: {email}")
            return None

        # Check if user is active
        if not user_data.get("active", False):
            print(f"❌ User account is inactive: {email}")
            return None

        # Build full name and return user data
        first_name = user_data.get("first_name", "")
        last_name = user_data.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()

        return {
            "id": user_data.get("id"),
            "email": user_data.get("email"),
            "name": full_name or email.split("@")[0],
            "role": user_data.get("role", "USER"),
            "is_active": user_data.get("active", True),
            "created_at": user_data.get("created_at")
        }

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return None
```

## Dependências

Certifique-se de que o bcrypt está instalado:

```bash
pip install bcrypt
```

## Próximos Passos

1. ✅ Código corrigido em `app/auth/supabase_client.py`
2. ⏳ Testar login no servidor
3. ⏳ Verificar se JWT é gerado corretamente
4. ⏳ Testar acesso às rotas protegidas

## Notas Importantes

- Os usuários devem ter senhas hash armazenadas na coluna `password` ou `password_hash` da tabela `users_unified`
- O hash deve ser gerado com bcrypt
- A coluna `active` deve ser `true` para o usuário poder fazer login
- O sistema agora funciona igual ao Employee Hub, que está em produção e funcionando corretamente

