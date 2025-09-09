# Conversor Invoice (ABZ Group)

Conversor Invoice é um módulo interno (separado do Employee Hub) para gerar invoices individuais (XLSX e PDF) a partir de planilhas ABZ Charge Rate e AN-FIN (Medição). Possui suporte a i18n (Português/English), progresso em tempo real (incluindo instalação automática do LibreOffice) e avisos detalhados por colaborador.

## Sumário
- Visão geral
- Recursos
- Requisitos
- Instalação e execução
- Uso passo a passo
- Idiomas (i18n)
- Avisos e progresso
- Estrutura do projeto
- Desenvolvimento
- Créditos / Autor
- Licença

## Visão geral
- Entrada: arquivos XLSX da ABZ (Charge Rate) e AN-FIN (Medição)
- Saída: invoices individuais por colaborador em XLSX e PDF
- Geração baseada em templates por colaborador (nome com/sem acento é suportado)
- Valores monetários com 2 casas decimais e formatação apropriada
- Acompanhamento de progresso e instalação automática do LibreOffice (Windows)

## Recursos
- 3 linhas garantidas em cada invoice: Service, Brazilian Payroll Additional e Expenses
- Normalização de nomes para localizar aba/template (e.g., “Bárbara” → “Barbara_Invoice”)
- Formatação monetária no XLSX (0.00 e £#,##0.00 conforme coluna)
- Progresso em tempo real via /api/progress (estágio, % e N/N)
- Avisos detalhados sem bloquear a geração (ex.: colaborador sem aba de template)
- i18n (PT-BR/EN) com persistência da escolha no navegador (localStorage)

## Requisitos
- Python 3.10+
- LibreOffice (instalação automática é tentada via winget ou choco no Windows)
- Windows recomendado para o fluxo de instalação automática

## Instalação e execução
1. (Opcional) Crie um virtualenv e instale dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o servidor API + UI:
   ```bash
   python scripts/run_api.py
   ```
3. Acesse a UI:
   - http://localhost:8000/ui/

Obs.: Se o LibreOffice não estiver instalado, a primeira geração tentará instalá-lo automaticamente (silencioso). Dependendo de políticas do Windows, pode ser necessário aceitar um prompt do sistema.

## Uso passo a passo
1) Importar arquivos
- Clique em “Selecionar arquivo” para ABZ e AN-FIN (ou em inglês, “Select file”).
- Depois clique em “Importar / Import”.

2) Preview e ajustes
- Clique em “Carregar Preview / Load Preview”.
- Ajuste opcionalmente Quantity e Unit Price por colaborador.

3) Gerar invoices
- Preencha Invoice Date, Invoice No e Call-Off (opcional).
- Clique em “Gerar Invoices / Generate Invoices”.
- Acompanhe o bloco “Progresso / Progress”.
- Baixe os arquivos (links XLSX e PDF por colaborador e ZIPs agregados).

## Idiomas (i18n)
- Seletor de idioma no cabeçalho (PT-BR/EN).
- Placeholders e rótulos variam conforme idioma.
- O placeholder da data segue o idioma:
  - PT-BR: dd/mm/aaaa
  - EN: dd/mm/yyyy

## Avisos e progresso
- O backend publica progresso com percentuais/estágios e lista de avisos.
- O frontend exibe os avisos em tempo real sem interromper a geração.
- Exemplos de estágios: Verificando/Instalando LibreOffice, Gerando N/N, Convertendo PDF.

## Estrutura do projeto (parcial)
- app/api: Endpoints FastAPI (import/preview/generate/progress)
- app/invoice: Preenchimento do template XLSX
- app/ui: HTML/JS/CSS da interface
- app/utils: Utilitários (export para PDF, instalação do LibreOffice)
- scripts/run_api.py: Inicialização local do servidor

## Desenvolvimento
- UI utiliza Tailwind CDN e fonte Inter (Google Fonts). Se quiser alinhar o tema exatamente ao Employee Hub, compartilhe a configuração de tema/paleta para replicarmos 1:1.
- Mensagens dinâmicas do progresso podem ser padronizadas com “codes” no backend caso necessite tradução perfeita (sem heurísticas no cliente).

## Créditos / Autor
- Desenvolvedor: Caio Correia
- GitHub: https://github.com/Caiolinooo
- Contato: 35239127+Caiolinooo@users.noreply.github.com

Se desejar incluir outras informações do desenvolvedor (empresa, site, perfis), envie os dados ou o README do Employee Hub para replicarmos aqui.

## Licença
A licença deve ser a mesma do Employee Hub. Por favor, forneça/autorize a cópia do texto exato da licença daquele projeto para inclusão neste repositório (arquivo LICENSE). Enquanto isso, este projeto não contém um arquivo de licença definitivo.

