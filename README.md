# 🧾 Invoice Generator (ABZ Group)

Sistema avançado de geração de invoices individuais baseado em templates, desenvolvido para automatizar a criação de faturas profissionais a partir de dados de folha de pagamento e medições.

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/Caiolinooo/invoice_abz/releases)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## 🚀 Novidades da Versão 2.0

- **🎨 Sistema Template-Based**: Geração baseada no `Template_Invoice_Geral.xlsx`
- **📞 Call-off Integrado**: Aparece no cabeçalho e nas descrições dos serviços
- **📁 Nomes Padronizados**: Arquivos incluem nome do colaborador automaticamente
- **🎯 Layout Profissional**: Formatação preservada com bordas e centralização
- **📄 Uma Página**: Configuração automática para impressão otimizada

## 📋 Sumário

- [Visão Geral](#-visão-geral)
- [Recursos](#-recursos)
- [Instalação](#-instalação-e-execução)
- [Uso](#-uso-passo-a-passo)
- [Roadmap](#-roadmap)
- [Changelog](#-changelog)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Desenvolvimento](#-desenvolvimento)
- [Créditos](#-créditos--autor)

## 🎯 Visão Geral

Sistema profissional de geração de invoices que transforma dados de folha de pagamento em faturas padronizadas e prontas para envio.

### Entrada
- **ABZ Charge Rate**: Planilha com dados dos colaboradores e taxas
- **AN-FIN (Medição)**: Dados de medição e valores adicionais
- **Template Invoice**: Template base para formatação profissional

### Saída
- **XLSX**: Invoices individuais formatadas profissionalmente
- **PDF**: Versões para impressão e envio (via LibreOffice)
- **Nomes Padronizados**: `ABZ Group 145-2025 OMEGA 09 2025 Maria.xlsx`

## ✨ Recursos

### 🎨 Template-Based System
- Baseado no `Template_Invoice_Geral.xlsx` fornecido
- Preservação completa de formatação, bordas e imagens
- Layout profissional em uma única página

### 📞 Call-off Integration
- Aparece no cabeçalho da invoice (C14)
- Integrado nas descrições dos serviços
- Formato: `Nome - Função - Call-off`

### 🔧 Funcionalidades Avançadas
- Normalização de nomes (suporte a acentos)
- Formatação monetária automática (£#,##0.00)
- Progresso em tempo real via API
- Sistema de avisos não-bloqueantes
- Suporte a i18n (PT-BR/EN)

## 📦 Instalação e Execução

### Requisitos
- Python 3.10+
- LibreOffice (instalação automática no Windows)
- Windows recomendado para fluxo completo

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/Caiolinooo/invoice_abz.git
   cd invoice_abz
   ```

2. (Opcional) Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Execução

1. Execute o servidor:
   ```bash
   python scripts/run_api.py
   ```

2. Acesse a interface:
   - **UI Principal**: http://localhost:8000/ui/
   - **API Docs**: http://localhost:8000/docs

## 🚀 Uso Passo a Passo

### 1. Importar Arquivos
- Clique em "Selecionar arquivo" para ABZ e AN-FIN
- Clique em "Importar / Import"

### 2. Preview e Ajustes
- Clique em "Carregar Preview / Load Preview"
- Ajuste opcionalmente Quantity e Unit Price por colaborador

### 3. Gerar Invoices
- Preencha Invoice Date, Invoice No e Call-Off
- Clique em "Gerar Invoices / Generate Invoices"
- Acompanhe o progresso em tempo real
- Baixe os arquivos individuais ou ZIPs agregados

## 🗺️ Roadmap

### 🎯 Versão 2.1 (Q1 2025)
- [ ] **Múltiplos Templates**: Suporte a diferentes templates por cliente
- [ ] **Validação Avançada**: Verificação de dados antes da geração
- [ ] **Histórico de Invoices**: Rastreamento de invoices geradas
- [ ] **Configurações Personalizáveis**: Ajustes de formatação via UI

### 🚀 Versão 2.2 (Q2 2025)
- [ ] **API REST Completa**: Endpoints para integração externa
- [ ] **Batch Processing**: Processamento em lote otimizado
- [ ] **Email Integration**: Envio automático de invoices
- [ ] **Dashboard Analytics**: Métricas e relatórios

### 🔮 Versão 3.0 (Q3 2025)
- [ ] **Multi-tenant**: Suporte a múltiplas empresas
- [ ] **Cloud Storage**: Integração com AWS/Azure
- [ ] **Mobile App**: Aplicativo móvel para aprovações
- [ ] **AI Integration**: Detecção automática de anomalias

### 💡 Ideias Futuras
- [ ] **Blockchain Integration**: Assinatura digital de invoices
- [ ] **OCR Support**: Leitura automática de documentos
- [ ] **Real-time Collaboration**: Edição colaborativa
- [ ] **Advanced Reporting**: Relatórios customizáveis

## 📝 Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para detalhes completos das mudanças.

### Versão 2.0.0 (2025-01-16)
- 🎉 Sistema template-based completamente novo
- 📞 Call-off integrado nas descrições
- 📁 Nomes de arquivo padronizados
- 🎯 Layout profissional preservado
- 🔧 Múltiplas correções e melhorias

## 🏗️ Estrutura do Projeto

```
invoice_abz/
├── app/
│   ├── api/                 # Endpoints FastAPI
│   ├── invoice/             # Sistema de geração
│   │   ├── template_based_generator.py  # Gerador principal
│   │   ├── template_filler.py          # Preenchimento
│   │   └── professional_generator.py   # Gerador legado
│   ├── ui/                  # Interface web
│   └── utils/               # Utilitários
├── DADOS/                   # Templates e dados
│   └── Template_Invoice_Geral.xlsx
├── scripts/                 # Scripts de execução
├── tests/                   # Testes automatizados
├── CHANGELOG.md            # Histórico de mudanças
└── README.md              # Este arquivo
```

## 🛠️ Desenvolvimento

### Tecnologias Utilizadas
- **Backend**: FastAPI, Python 3.10+
- **Frontend**: HTML5, JavaScript, Tailwind CSS
- **Excel**: openpyxl para manipulação de planilhas
- **PDF**: LibreOffice para conversão
- **UI**: Interface responsiva com tema moderno

### Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Testes

Execute os testes automatizados:
```bash
python -m pytest tests/
```

## 👨‍💻 Créditos / Autor

**Desenvolvedor**: Caio Correia
- **GitHub**: [@Caiolinooo](https://github.com/Caiolinooo)
- **Email**: 35239127+Caiolinooo@users.noreply.github.com

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">
  <p>Feito com ❤️ para ABZ Group</p>
  <p>
    <a href="https://github.com/Caiolinooo/invoice_abz">⭐ Star no GitHub</a> •
    <a href="https://github.com/Caiolinooo/invoice_abz/issues">🐛 Reportar Bug</a> •
    <a href="https://github.com/Caiolinooo/invoice_abz/issues">💡 Sugerir Feature</a>
  </p>
</div>
