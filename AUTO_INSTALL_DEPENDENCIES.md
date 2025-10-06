# Correção: Instalação Automática de Dependências

## 🎯 Problemas Identificados

### Problema 1: python-dotenv não instalado
```
❌ python-dotenv - NÃO INSTALADO
❌ Dependências faltando: python-dotenv
💡 Instale com: pip install -r requirements.txt
❌ Verificações críticas falharam. Corrija os erros antes de continuar.
```

### Problema 2: Módulo database não encontrado
```
⚠️  Erro ao inicializar banco: No module named 'app.api.database'
```

**Causa:** O script tentava importar `app.api.database`, mas o módulo correto é `app.database.database`.

---

## ✅ Soluções Implementadas

### 1. Instalação Automática de Dependências

**Antes:**
```python
if missing:
    print(f"\n❌ Dependências faltando: {', '.join(missing)}")
    print("💡 Instale com: pip install -r requirements.txt")
    return False  # ← Bloqueava o servidor
```

**Depois:**
```python
if missing:
    print(f"\n⚠️  Dependências faltando: {', '.join(missing)}")
    print("📦 Instalando dependências automaticamente...")
    
    # Tentar instalar via requirements.txt primeiro
    if Path('requirements.txt').exists():
        print("   Usando requirements.txt...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos
        )
        if result.returncode == 0:
            print("   ✅ Dependências instaladas via requirements.txt")
            return True
    
    # Instalar pacotes individualmente
    print("   Instalando pacotes individualmente...")
    for package in missing:
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
            print(f"   ❌ Erro ao instalar {package}")
            return False
    
    print("\n✅ Todas as dependências instaladas com sucesso!")
    return True
```

**Benefícios:**
- ✅ Instala automaticamente dependências faltantes
- ✅ Tenta usar `requirements.txt` primeiro (mais rápido)
- ✅ Fallback para instalação individual
- ✅ Timeout de 5 minutos para requirements.txt
- ✅ Timeout de 2 minutos por pacote individual
- ✅ Mensagens claras de progresso

---

### 2. Correção do Caminho do Database

**Antes:**
```python
from app.api.database import init_db  # ← Caminho errado!
```

**Depois:**
```python
# Verificar se o módulo database existe
database_file = Path('app/database/database.py')  # ← Caminho correto!
if not database_file.exists():
    print("⚠️  Módulo database.py não encontrado")
    print("   O servidor continuará sem banco de dados")
    return True

# Importar e inicializar banco
from app.database.database import init_database  # ← Função correta!
init_database()
print("✅ Banco de dados inicializado")
```

**Benefícios:**
- ✅ Verifica se o arquivo existe antes de importar
- ✅ Usa o caminho correto: `app.database.database`
- ✅ Usa a função correta: `init_database()`
- ✅ Não bloqueia o servidor se o banco não existir
- ✅ Mensagens claras sobre o status

---

## 🧪 Comportamento Esperado

### Primeira Execução (com dependências faltando)

```bash
python run_server.py
```

**Output:**
```
============================================================
  SERVIDOR DE DESENVOLVIMENTO - PAYROLL CONVERSION API
============================================================
🔍 Verificando versão do Python...
✅ Python 3.13.3

🔍 Verificando dependências...
  ✅ fastapi
  ✅ uvicorn
  ✅ openpyxl
  ✅ pandas
  ✅ python-multipart
  ✅ supabase
  ✅ pydantic
  ❌ python-dotenv - NÃO INSTALADO

⚠️  Dependências faltando: python-dotenv
📦 Instalando dependências automaticamente...
   Usando requirements.txt...
   ✅ Dependências instaladas via requirements.txt

✅ Todas as dependências instaladas com sucesso!

🔍 Verificando LibreOffice...
✅ LibreOffice encontrado: C:\Program Files\LibreOffice\program\soffice.exe

🔍 Verificando arquivo .env...
✅ Arquivo .env encontrado

🔍 Verificando diretórios...
  ✅ Existe: out
  ✅ Existe: out/sessions
  ✅ Existe: out/invoices
  ✅ Existe: app/ui

🔍 Verificando banco de dados...
✅ Banco de dados inicializado

============================================================
  INICIANDO SERVIDOR...
============================================================

🚀 Executando: python -m uvicorn app.api.server:app --host 0.0.0.0 --port 8000 --reload
⏳ Aguarde alguns segundos para o servidor inicializar...

============================================================
  ✅ SERVIDOR INICIADO COM SUCESSO!
============================================================
```

### Segunda Execução (tudo instalado)

```
🔍 Verificando dependências...
  ✅ fastapi
  ✅ uvicorn
  ✅ openpyxl
  ✅ pandas
  ✅ python-multipart
  ✅ supabase
  ✅ pydantic
  ✅ python-dotenv
✅ Todas as dependências já instaladas
```

---

## 📊 Fluxo de Instalação

```
1. Verificar dependências
         ↓
2. Encontrou faltando?
   ├─ NÃO → Continuar
   └─ SIM → Instalar automaticamente
              ↓
         3. Existe requirements.txt?
            ├─ SIM → pip install -r requirements.txt
            │         ↓
            │    Sucesso? → Continuar
            │         ↓
            │    Falhou? → Instalar individualmente
            │
            └─ NÃO → Instalar individualmente
                      ↓
                 4. Para cada pacote:
                    pip install <pacote>
                      ↓
                 5. Todos instalados? → Continuar
                      ↓
                 6. Algum falhou? → Erro e parar
```

---

## 🔧 Dependências Verificadas

1. ✅ **fastapi** - Framework web
2. ✅ **uvicorn** - Servidor ASGI
3. ✅ **openpyxl** - Manipulação de Excel
4. ✅ **pandas** - Análise de dados
5. ✅ **python-multipart** - Upload de arquivos
6. ✅ **supabase** - Cliente Supabase
7. ✅ **pydantic** - Validação de dados
8. ✅ **python-dotenv** - Variáveis de ambiente

---

## 📁 Arquivo Modificado

- ✅ `run_server.py` - Instalação automática + correção do database

---

## 🎉 Resultado Final

**Agora o script:**

1. ✅ **Verifica** todas as dependências
2. ✅ **Instala automaticamente** as que faltam
3. ✅ **Não bloqueia** o servidor por dependências
4. ✅ **Verifica o database** no caminho correto
5. ✅ **Mensagens claras** de progresso
6. ✅ **Timeouts adequados** para instalação

**Execute novamente:**
```bash
python run_server.py
```

E tudo será instalado e verificado automaticamente! 🚀

---

## ⚙️ Configurações de Timeout

- **requirements.txt**: 5 minutos (300 segundos)
- **Pacote individual**: 2 minutos (120 segundos)

Esses valores podem ser ajustados se necessário, dependendo da velocidade da conexão.

---

## 🛡️ Tratamento de Erros

O script agora trata os seguintes cenários:

1. ✅ Dependência não instalada → Instala automaticamente
2. ✅ requirements.txt não existe → Instala individualmente
3. ✅ Erro ao instalar via requirements.txt → Fallback para individual
4. ✅ Timeout na instalação → Erro claro
5. ✅ Database não existe → Continua sem bloquear
6. ✅ Erro ao inicializar database → Continua com aviso

Tudo foi projetado para **não bloquear o servidor** desnecessariamente! ✅

