# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [12.0] - 2025-01-06

### 🎉 Major Release - Expenses Management & Auto-Install

#### Added
- **Expenses Override System**
  - Override fields for Brazilian Payroll Additional
  - Override fields for Expenses
  - Real-time preview updates when overriding values
  - Per-employee override capability
  - Bilingual support (PT/EN) for new fields

- **AN-FIN File Upload (Optional)**
  - New upload field for AN-FIN file in UI
  - Intelligent fallback system: AN-FIN → ABZ → £0.00
  - Expenses priority: AN-FIN (most accurate) > ABZ (fallback)
  - Clear UI messages about optional nature
  - Automatic detection and processing

- **Auto-Install Dependencies**
  - Automatic dependency installation on startup
  - Tries requirements.txt first (faster batch install)
  - Falls back to individual package installation
  - No more manual pip install needed
  - Smart timeout handling (5min for requirements.txt, 2min per package)
  - Clear progress messages during installation

- **Enhanced Server Startup Script (run_server.py)**
  - Complete pre-flight checks before starting
  - Verifies Python version (3.8+ required)
  - Checks all dependencies
  - Verifies LibreOffice installation
  - Validates .env file
  - Checks database connectivity
  - Creates missing directories automatically
  - Beautiful, informative console output with emojis

#### Fixed
- **Critical: Expenses Not Showing in Preview**
  - Root Cause: `aggregate_employee()` was modified to exclude expenses
  - Fix: Restored expenses support in aggregator with type 'expenses'
  - Result: Expenses now appear correctly from ABZ or AN-FIN
  - Added detailed debug logging

- **Database Module Path Error**
  - Root Cause: Wrong import path (app.api.database vs app.database.database)
  - Fix: Corrected import path and added existence check
  - Result: Database initializes correctly without blocking server

#### Changed
- Updated expense extraction logic to use aggregator data
- Improved error messages and user feedback
- Enhanced logging for troubleshooting
- Better handling of missing dependencies

#### Documentation
- Added AUTO_INSTALL_DEPENDENCIES.md
- Added EXPENSES_ADDITIONAL_OVERRIDE_IMPLEMENTATION.md
- Added EXPENSES_FALLBACK_SUMMARY.md
- Added FINAL_FIX_EXPENSES_AND_SERVER.md
- Added FIX_EXPENSES_UPLOAD.md

#### Technical Details
- **Files Modified**:
  - Frontend: app/ui/index.html, app/ui/i18n.js, app/ui/app.js
  - Backend: app/api/server.py, app/utils/abz_charge_rate_parser.py
  - Infrastructure: run_server.py (complete rewrite)
- **Breaking Changes**: None - Fully backward compatible
- **Performance**: Faster startup with requirements.txt batch install
- **Testing**: ABZ only, ABZ + AN-FIN, Override functionality, Auto-install

## [11.4] - 2024-12-XX

### Previous Stable Version
- Authentication system
- Rate limiting
- Audit logging
- Invoice generation
- PDF export
- Template-based system
- Multi-position employee support
- Database integration

## [8.0.0] - 2025-01-17

### 🔤 Typography Enhancement - Fonte Calibri Universal

#### Added
- **Sistema de Fontes Calibri**: Aplicação universal da fonte Calibri em toda a invoice
- **Hierarquia Tipográfica**: Diferentes tamanhos de Calibri para organização visual
  - Título principal: Calibri 14pt Bold (A7)
  - Cabeçalhos importantes: Calibri 12pt Bold (C12, C13, C14)
  - Cabeçalhos de tabela: Calibri 11pt Bold (linha 16)
  - Conteúdo geral: Calibri 11pt (serviços, totais)
  - Detalhes corporativos: Calibri 10pt (linhas 43-50)
- **Legibilidade Otimizada**: Fonte escolhida para máxima legibilidade em tela e impressão
- **Estética Profissional**: Aparência consistente e corporativa em toda a invoice

#### Changed
- **Sistema de Preservação de Fontes**: Migrado de preservação do template para aplicação ativa de Calibri
- **Método `_preserve_template_fonts()`**: Completamente reescrito para aplicar Calibri universalmente
- **Validação de Fontes**: 100% das células com conteúdo agora usam Calibri

#### Technical Implementation
- Aplicação automática de fonte Calibri em todas as células com conteúdo
- Sistema inteligente de detecção de tipo de célula para aplicar tamanho apropriado
- Validação completa garantindo 100% de conformidade com Calibri
- Teste abrangente `test_calibri_fonts.py` para verificação de qualidade

#### Benefits
- **Legibilidade Superior**: Calibri é otimizada para leitura digital e impressa
- **Consistência Visual**: Toda a invoice mantém aparência uniforme
- **Profissionalismo**: Fonte corporativa padrão da Microsoft Office
- **Compatibilidade**: Disponível em todos os sistemas Windows por padrão

## [2.0.0] - 2025-01-16

### 🎉 Major Release - Template-Based Invoice System

#### Added
- **Template-Based Invoice Generator**: Sistema completamente novo baseado no `Template_Invoice_Geral.xlsx`
- **Call-off Integration**: Call-off agora aparece em dois locais:
  - Campo dedicado em C14: `Call-Off: P25-XXX`
  - Integrado nas descrições dos serviços: `Nome - Função - Call-off`
- **Standardized Filename Generation**: Nomes de arquivo padronizados incluindo nome do colaborador
  - Formato: `ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}.xlsx`
  - Exemplo: `ABZ Group 145-2025 OMEGA 09 2025 Maria.xlsx`
- **Corporate Account Details Formatting**: Seção formatada com centralização e bordas preservadas
- **Notes to Invoice Above**: Estrutura compacta preservada do template original
- **Font Preservation System**: Fontes do template original mantidas (Calibri, Aptos Narrow)
- **Single Page Layout**: Configuração automática para impressão em uma única página
- **Service Table Cleaning**: Limpeza automática da tabela antes de preencher novos dados

#### Changed
- **Invoice Generation Engine**: Migração completa para sistema baseado em template
- **File Naming Convention**: Nomes de arquivo agora incluem informações completas do projeto
- **Service Description Format**: Descrições agora incluem call-off automaticamente
- **Template Structure**: Preservação completa da estrutura e formatação do template original

#### Fixed
- **Merged Cell Handling**: Correção completa do manuseio de células mescladas
- **Expenses Duplication**: Eliminação de duplicação de itens "Brazilian Payroll Additional" e "Expenses"
- **Call-off Display**: Call-off agora aparece corretamente em múltiplos locais
- **Font Consistency**: Fontes mantidas consistentes com o template original
- **Layout Issues**: Problemas de layout em múltiplas páginas resolvidos

#### Technical Improvements
- **Template Copying System**: Cópia completa do template preservando imagens e formatação
- **Merged Cell Value Setting**: Sistema robusto para definir valores em células mescladas
- **Page Setup Optimization**: Configurações otimizadas para impressão em A4
- **Error Handling**: Tratamento de erros melhorado em todas as operações
- **Validation System**: Sistema de validação abrangente para conformidade com template

### 🔧 Internal Changes
- Criação do módulo `template_based_generator.py`
- Atualização do `template_filler.py` para suportar novo gerador
- Modificação do `server.py` para usar template-based por padrão
- Implementação de testes abrangentes para todas as funcionalidades

## [1.0.0] - 2024-XX-XX

### Added
- Sistema inicial de geração de invoices
- Suporte a arquivos ABZ e AN-FIN
- Interface web com Streamlit
- Geração de PDF via LibreOffice
- Sistema de sessões para processamento em lote

### Features
- Upload de arquivos Excel
- Processamento de dados de folha de pagamento
- Geração automática de invoices
- Exportação para PDF
- Interface web intuitiva

---

## Tipos de Mudanças
- `Added` para novas funcionalidades
- `Changed` para mudanças em funcionalidades existentes
- `Deprecated` para funcionalidades que serão removidas em breve
- `Removed` para funcionalidades removidas
- `Fixed` para correções de bugs
- `Security` para correções relacionadas à segurança
