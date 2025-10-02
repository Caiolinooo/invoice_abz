# Guia de Instalação do LibreOffice

O LibreOffice é **necessário** para converter arquivos XLSX em PDF. Sem ele, as invoices serão geradas apenas em formato XLSX.

## 🔍 Verificar se está instalado

Acesse a página de diagnóstico do sistema:
```
http://seu-servidor:8000/ui/system-check.html
```

Ou verifique manualmente no terminal:
```bash
soffice --version
```

## 📦 Instalação

### Windows

#### Opção 1: Instalação Automática (via interface web)
1. Acesse: `http://localhost:8000/ui/system-check.html`
2. Clique em "📥 Instalar LibreOffice"
3. Aguarde a instalação automática

#### Opção 2: Instalação Manual
1. Baixe o instalador: https://www.libreoffice.org/download/download/
2. Execute o instalador
3. Reinicie o servidor

#### Opção 3: Via Winget (PowerShell como Admin)
```powershell
winget install --id TheDocumentFoundation.LibreOffice --silent
```

#### Opção 4: Via Chocolatey (PowerShell como Admin)
```powershell
choco install libreoffice -y
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install libreoffice -y
```

### Linux (CentOS/RHEL/Fedora)

```bash
sudo yum install libreoffice -y
# ou
sudo dnf install libreoffice -y
```

### Linux (Arch)

```bash
sudo pacman -S libreoffice-fresh
```

### macOS

```bash
brew install --cask libreoffice
```

## 🔧 Configuração de Variável de Ambiente (Opcional)

Se o LibreOffice foi instalado em um local não padrão, defina a variável de ambiente:

### Windows (PowerShell)
```powershell
$env:LIBREOFFICE_PATH = "C:\Program Files\LibreOffice\program\soffice.exe"
```

### Linux/macOS
```bash
export LIBREOFFICE_PATH="/usr/bin/soffice"
```

Para tornar permanente, adicione ao `.bashrc` ou `.zshrc`:
```bash
echo 'export LIBREOFFICE_PATH="/usr/bin/soffice"' >> ~/.bashrc
source ~/.bashrc
```

## ✅ Verificar Instalação

Após instalar, verifique se funciona:

```bash
soffice --version
```

Ou teste a conversão:
```bash
soffice --headless --convert-to pdf --outdir . arquivo.xlsx
```

## 🚀 Reiniciar o Servidor

Após instalar o LibreOffice, **reinicie o servidor** para que ele detecte a instalação:

```bash
# Pare o servidor (Ctrl+C)
# Inicie novamente
python start_server.py
```

## 🐛 Problemas Comuns

### "LibreOffice not found"
- Verifique se o LibreOffice está no PATH
- Tente definir a variável `LIBREOFFICE_PATH`
- Reinicie o terminal/servidor após a instalação

### "Permission denied" (Linux)
```bash
sudo chmod +x /usr/bin/soffice
```

### Conversão falha silenciosamente
- Verifique se há espaço em disco
- Verifique permissões de escrita na pasta `out/`
- Tente converter manualmente um arquivo para testar

### Windows: "soffice.exe não é reconhecido"
- Adicione o LibreOffice ao PATH:
  1. Painel de Controle → Sistema → Configurações Avançadas
  2. Variáveis de Ambiente
  3. Adicione: `C:\Program Files\LibreOffice\program`

## 📊 Monitoramento

Após instalar, monitore os logs do servidor para confirmar que PDFs estão sendo gerados:

```
✅ PDF generated: out/sessions/.../pdf/invoice.pdf
```

Se aparecer:
```
⚠️ PDF generation failed
```

Verifique os logs detalhados e a instalação do LibreOffice.

## 🆘 Suporte

Se continuar com problemas:
1. Acesse `/ui/system-check.html` para diagnóstico completo
2. Verifique os logs do servidor
3. Teste a conversão manual com `soffice --convert-to pdf`
4. Verifique permissões de arquivo e espaço em disco

