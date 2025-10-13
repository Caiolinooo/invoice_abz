"""
Configurar acesso externo ao servidor
"""
import socket
import subprocess
import sys

def get_local_ip():
    """Obter IP local da máquina"""
    try:
        # Conectar a um servidor externo para descobrir o IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def setup_firewall():
    """Configurar firewall do Windows para permitir porta 8000"""
    print("\n" + "=" * 60)
    print("CONFIGURANDO FIREWALL DO WINDOWS")
    print("=" * 60)
    
    # Comando para adicionar regra no firewall
    rule_name = "Invoice System - Port 8000"
    
    # Remover regra antiga se existir
    print(f"\n🔥 Removendo regra antiga (se existir)...")
    try:
        subprocess.run(
            f'netsh advfirewall firewall delete rule name="{rule_name}"',
            shell=True,
            capture_output=True
        )
    except Exception:
        pass
    
    # Adicionar nova regra
    print(f"🔥 Adicionando regra no firewall...")
    try:
        result = subprocess.run(
            f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=allow protocol=TCP localport=8000',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Regra adicionada com sucesso!")
            return True
        else:
            print(f"❌ Erro ao adicionar regra: {result.stderr}")
            print(f"\n⚠️  Execute este script como Administrador!")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        print(f"\n⚠️  Execute este script como Administrador!")
        return False

def main():
    print("=" * 60)
    print("CONFIGURAÇÃO DE ACESSO EXTERNO")
    print("=" * 60)
    
    # Obter IP local
    local_ip = get_local_ip()
    
    print(f"\n📍 Seu IP local: {local_ip}")
    print(f"\n🌐 URLs de acesso:")
    print(f"   Local:    http://127.0.0.1:8000/ui/")
    print(f"   Rede:     http://{local_ip}:8000/ui/")
    print(f"   API Docs: http://{local_ip}:8000/docs")
    
    # Configurar firewall
    print(f"\n⚠️  IMPORTANTE: Este script precisa ser executado como Administrador")
    print(f"   para configurar o firewall do Windows!")
    
    response = input(f"\n❓ Deseja configurar o firewall agora? (s/n): ")
    
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        success = setup_firewall()
        
        if success:
            print(f"\n✅ Configuração concluída!")
            print(f"\n📱 Agora você pode acessar de outros dispositivos na mesma rede:")
            print(f"   http://{local_ip}:8000/ui/")
        else:
            print(f"\n❌ Falha na configuração do firewall")
            print(f"\n📝 Para configurar manualmente:")
            print(f"   1. Abra o Firewall do Windows")
            print(f"   2. Vá em 'Regras de Entrada'")
            print(f"   3. Crie uma nova regra para a porta TCP 8000")
    else:
        print(f"\n📝 Para configurar manualmente o firewall:")
        print(f"   1. Execute este script como Administrador, OU")
        print(f"   2. Abra o Firewall do Windows e adicione regra para porta 8000")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()

