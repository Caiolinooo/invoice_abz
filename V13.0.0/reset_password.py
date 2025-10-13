"""
Script para redefinir senha de um usuário
"""
import os
import bcrypt
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def reset_password():
    """Redefinir senha de um usuário"""
    
    print("=" * 60)
    print("REDEFINIR SENHA DE USUÁRIO")
    print("=" * 60)
    
    # Configuração
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    client = create_client(supabase_url, supabase_key)
    
    # Solicitar dados
    email = input("\nDigite o email do usuário: ").strip()
    new_password = input("Digite a nova senha: ").strip()
    
    if not email or not new_password:
        print("❌ Email e senha são obrigatórios!")
        return
    
    print(f"\n1. Buscando usuário: {email}")
    
    # Buscar usuário
    response = client.table("users_unified").select("id, email, name, role").eq("email", email).execute()
    
    if not response.data:
        print("❌ Usuário não encontrado!")
        return
    
    user = response.data[0]
    print(f"✅ Usuário encontrado!")
    print(f"   - ID: {user.get('id')}")
    print(f"   - Nome: {user.get('name')}")
    print(f"   - Email: {user.get('email')}")
    print(f"   - Role: {user.get('role')}")
    
    # Confirmar
    confirm = input(f"\n⚠️  Deseja redefinir a senha deste usuário? (s/n): ").strip().lower()
    
    if confirm != 's':
        print("❌ Operação cancelada!")
        return
    
    # Gerar hash da nova senha
    print(f"\n2. Gerando hash da senha...")
    password_bytes = new_password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    print(f"✅ Hash gerado: {password_hash[:30]}...")
    
    # Atualizar no banco
    print(f"\n3. Atualizando senha no banco...")
    
    update_response = client.table("users_unified").update({
        "password": password_hash,
        "password_hash": password_hash
    }).eq("id", user.get('id')).execute()
    
    if update_response.data:
        print(f"✅ Senha atualizada com sucesso!")
        print(f"\n📋 Credenciais para login:")
        print(f"   Email: {email}")
        print(f"   Senha: {new_password}")
    else:
        print(f"❌ Erro ao atualizar senha!")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    reset_password()

