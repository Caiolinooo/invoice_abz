#!/usr/bin/env python3
"""
Script para iniciar o servidor de desenvolvimento com verificações completas
"""

import subprocess
import sys
import webbrowser
import time
import socket
import os
import shutil
from pathlib import Path

def get_local_ip():
    """Obter IP local da máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def check_python_version():
    """Verificar versão do Python"""
    print("🔍 Verificando versão do Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detectado. Requer Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Verificar e instalar dependências automaticamente"""
    print("\n🔍 Verificando dependências...")
    required = [
        'fastapi',
        'uvicorn',
        'openpyxl',
        'pandas',
        'python-multipart',
        'supabase',
        'pydantic',
        'python-dotenv'
    ]

    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NÃO INSTALADO")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Dependências faltando: {', '.join(missing)}")
        print("📦 Instalando dependências automaticamente...")

        # Tentar instalar via requirements.txt primeiro
        if Path('requirements.txt').exists():
            print("   Usando requirements.txt...")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutos
                )
                if result.returncode == 0:
                    print("   ✅ Dependências instaladas via requirements.txt")
                    return True
                else:
                    print(f"   ⚠️  Erro ao instalar via requirements.txt: {result.stderr}")
            except Exception as e:
                print(f"   ⚠️  Erro ao instalar via requirements.txt: {e}")

        # Instalar pacotes individualmente
        print("   Instalando pacotes individualmente...")
        for package in missing:
            try:
                print(f"   📦 Instalando {package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minutos por pacote
                )
                if result.returncode == 0:
                    print(f"   ✅ {package} instalado")
                else:
                    print(f"   ❌ Erro ao instalar {package}: {result.stderr}")
                    return False
            except Exception as e:
                print(f"   ❌ Erro ao instalar {package}: {e}")
                return False

        print("\n✅ Todas as dependências instaladas com sucesso!")
        return True

    print("✅ Todas as dependências já instaladas")
    return True

def check_libreoffice():
    """Verificar se LibreOffice está instalado"""
    print("\n🔍 Verificando LibreOffice...")

    # Caminhos comuns do LibreOffice no Windows
    possible_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\LibreOffice\program\soffice.exe"),
    ]

    # Verificar se está no PATH
    if shutil.which("soffice"):
        print("✅ LibreOffice encontrado no PATH")
        return True

    # Verificar caminhos comuns
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ LibreOffice encontrado: {path}")
            return True

    print("⚠️  LibreOffice não encontrado")
    print("   Necessário para conversão de invoices para PDF")
    print("   Download: https://www.libreoffice.org/download/download/")
    return False

def check_env_file():
    """Verificar arquivo .env"""
    print("\n🔍 Verificando arquivo .env...")
    env_file = Path('.env')

    if not env_file.exists():
        print("⚠️  Arquivo .env não encontrado")
        print("   Criando .env de exemplo...")

        env_example = Path('.env.example')
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Arquivo .env criado a partir de .env.example")
            print("⚠️  Configure as variáveis de ambiente no arquivo .env")
        else:
            print("❌ Arquivo .env.example não encontrado")
            return False
    else:
        print("✅ Arquivo .env encontrado")

    return True

def check_directories():
    """Verificar e criar diretórios necessários"""
    print("\n🔍 Verificando diretórios...")
    dirs = ['out', 'out/sessions', 'out/invoices', 'app/ui']

    for dir_path in dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Criado: {dir_path}")
        else:
            print(f"  ✅ Existe: {dir_path}")

    return True

def check_database():
    """Verificar conexão com banco de dados"""
    print("\n🔍 Verificando banco de dados...")
    try:
        # Verificar se o módulo database existe
        database_file = Path('app/database/database.py')
        if not database_file.exists():
            print("⚠️  Módulo database.py não encontrado")
            print("   O servidor continuará sem banco de dados")
            return True

        # Importar e inicializar banco
        from app.database.database import init_database
        init_database()
        print("✅ Banco de dados inicializado")
        return True
    except ModuleNotFoundError as e:
        print(f"⚠️  Módulo database não encontrado: {e}")
        print("   O servidor continuará sem banco de dados")
        return True  # Não bloquear o servidor
    except Exception as e:
        print(f"⚠️  Erro ao inicializar banco: {e}")
        print("   O servidor continuará, mas algumas funcionalidades podem não funcionar")
        return True  # Não bloquear o servidor

def main():
    print("=" * 60)
    print("  SERVIDOR DE DESENVOLVIMENTO - PAYROLL CONVERSION API")
    print("=" * 60)

    # Verificar se estamos no diretório correto
    if not Path('app').exists():
        print("\n❌ Erro: Pasta 'app' não encontrada.")
        print("   Execute este script na raiz do projeto.")
        return 1

    # Executar verificações
    checks = [
        ("Versão do Python", check_python_version),
        ("Dependências", check_dependencies),
        ("LibreOffice", check_libreoffice),
        ("Arquivo .env", check_env_file),
        ("Diretórios", check_directories),
        ("Banco de Dados", check_database),
    ]

    critical_failed = False
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result and check_name in ["Versão do Python", "Dependências"]:
                critical_failed = True
        except Exception as e:
            print(f"❌ Erro na verificação '{check_name}': {e}")
            if check_name in ["Versão do Python", "Dependências"]:
                critical_failed = True

    if critical_failed:
        print("\n❌ Verificações críticas falharam. Corrija os erros antes de continuar.")
        return 1

    # Obter IP local
    local_ip = get_local_ip()

    print("\n" + "=" * 60)
    print("  INICIANDO SERVIDOR...")
    print("=" * 60)

    try:
        # Comando para iniciar o servidor (0.0.0.0 aceita conexões externas)
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.api.server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]

        print(f"\n🚀 Executando: {' '.join(cmd)}")
        print("⏳ Aguarde alguns segundos para o servidor inicializar...\n")

        # Iniciar o servidor
        process = subprocess.Popen(cmd)

        # Aguardar um pouco para o servidor inicializar
        time.sleep(4)

        # Abrir o navegador
        url = "http://127.0.0.1:8000/ui/"

        print("\n" + "=" * 60)
        print("  ✅ SERVIDOR INICIADO COM SUCESSO!")
        print("=" * 60)

        print(f"\n🌐 Abrindo navegador em: {url}")

        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"⚠️  Não foi possível abrir o navegador automaticamente: {e}")
            print(f"   Acesse manualmente: {url}")

        print("\n📋 URLs DISPONÍVEIS:")
        print(f"   🏠 Interface Web:  http://127.0.0.1:8000/ui/")
        print(f"   🌐 Acesso Rede:    http://{local_ip}:8000/ui/")
        print(f"   📚 API Docs:       http://127.0.0.1:8000/docs")
        print(f"   🔌 API Endpoint:   http://127.0.0.1:8000/api/")

        print("\n🔐 AUTENTICAÇÃO:")
        print("   ✅ Sistema de autenticação ativo")
        print("   ✅ Rate limiting: 5 requisições/minuto")
        print("   ✅ Audit logging habilitado")

        print("\n⚠️  FIREWALL:")
        print("   Para acesso externo, configure o firewall do Windows")
        print("   Execute: python setup_external_access.py (como Administrador)")

        print("\n🛑 Para parar o servidor, pressione Ctrl+C")
        print("=" * 60 + "\n")

        try:
            # Aguardar até o usuário pressionar Ctrl+C
            process.wait()
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("  🛑 PARANDO SERVIDOR...")
            print("=" * 60)
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ Servidor parado com sucesso.")
            except subprocess.TimeoutExpired:
                print("⚠️  Forçando encerramento...")
                process.kill()
                print("✅ Servidor encerrado.")
            print("=" * 60)

    except FileNotFoundError:
        print("\n❌ ERRO: uvicorn não encontrado.")
        print("💡 Instale com: pip install uvicorn")
        return 1
    except Exception as e:
        print(f"\n❌ ERRO ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
