# Configuração do Servidor - Conversão da Folha

## Problema Resolvido

O erro `RuntimeError("Directory '{directory}' does not exist")` foi corrigido. O problema ocorria porque o diretório `out` não existia quando o FastAPI tentava montar o StaticFiles.

## Soluções Implementadas

### 1. Correção no `app/api/server.py`
- Adicionada criação automática do diretório `out` antes de montar o StaticFiles
- Garantia de que todos os diretórios necessários existem na inicialização

### 2. Correção no `scripts/run_api.py`
- Adicionada função `ensure_directories()` para criar diretórios necessários
- Chamada da função antes de iniciar o servidor

### 3. Novo Script de Inicialização Robusto: `start_server.py`
- Script principal para inicialização do servidor
- Instalação automática de dependências
- Criação automática de diretórios
- Configuração para diferentes ambientes

### 4. Configuração de Ambiente: `server_config.py`
- Configurações específicas para desenvolvimento, produção e nuvem
- Validação automática do ambiente
- Criação de diretórios necessários

## Como Executar

### Opção 1: Script Robusto (Recomendado)
```bash
python start_server.py
```

### Opção 2: Script Original (Corrigido)
```bash
cd scripts
python run_api.py
```

### Opção 3: Arquivo Batch (Windows)
```bash
start-conversao_folha.bat
```

## Configuração de Ambiente

### Desenvolvimento
```bash
export ENVIRONMENT=development
python start_server.py
```

### Produção/Nuvem
```bash
export ENVIRONMENT=production
export PORT=8000
export WORKERS=2
python start_server.py
```

## Diretórios Criados Automaticamente

- `out/` - Diretório principal de saída
- `out/sessions/` - Sessões de conversão
- `out/invoices/` - Invoices geradas

## Verificação

Após iniciar o servidor, verifique:

1. **API**: http://localhost:8000/docs
2. **Interface Web**: http://localhost:8000/ui/
3. **Health Check**: http://localhost:8000/health

## Logs

O servidor agora exibe logs detalhados sobre:
- Criação de diretórios
- Validação do ambiente
- Status da inicialização
- Configuração aplicada

## Troubleshooting

### Se ainda houver erro de diretório:
1. Verifique se o script tem permissões de escrita
2. Execute manualmente:
   ```bash
   mkdir -p out/sessions
   mkdir -p out/invoices
   ```
3. Use o script `start_server.py` que é mais robusto

### Se houver erro de dependências:
```bash
pip install -r requirements.txt
pip install fastapi uvicorn[standard] python-multipart
```

## Estrutura de Diretórios Esperada

```
projeto/
├── app/
│   ├── api/
│   │   └── server.py
│   └── ui/
├── out/                    # Criado automaticamente
│   ├── sessions/          # Criado automaticamente
│   └── invoices/          # Criado automaticamente
├── scripts/
│   └── run_api.py
├── start_server.py        # Novo script robusto
├── server_config.py       # Configurações
└── requirements.txt
```
