# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
