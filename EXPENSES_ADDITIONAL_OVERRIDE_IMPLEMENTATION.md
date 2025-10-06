# Implementação de Override para Expenses e Additional

## Resumo
Implementação de campos de override para **Expenses** e **Brazilian Payroll Additional** no sistema de geração de invoices, permitindo que usuários sobrescrevam manualmente esses valores quando necessário.

## Arquivos Modificados

### 1. Frontend - HTML (`app/ui/index.html`)
**Mudanças:**
- Adicionadas duas novas colunas na tabela de preview:
  - `Override Additional` - Para sobrescrever o valor de Brazilian Payroll Additional
  - `Override Expenses` - Para sobrescrever o valor de Expenses

**Localização:** Linhas 640-653

### 2. Frontend - Traduções (`app/ui/i18n.js`)
**Mudanças:**
- Adicionadas traduções para as novas colunas em Português e Inglês:
  - PT: `'override_additional': 'Sobrescrever Adicional'`
  - PT: `'override_expenses': 'Sobrescrever Despesas'`
  - EN: `'override_additional': 'Override Additional'`
  - EN: `'override_expenses': 'Override Expenses'`

**Localização:** Linhas 82-86 (PT) e 317-321 (EN)

### 3. Frontend - JavaScript (`app/ui/app.js`)

#### 3.1. Função `rowHtml()` - Adição de Campos de Input
**Mudanças:**
- Adicionados campos de input para `additional` e `expenses` em todas as variações de linhas:
  - Linhas com serviços (múltiplas posições)
  - Linhas sem serviços mas com Additional/Expenses
  - Linhas sem dados (entrada manual)

**Comportamento:**
- Para funcionários com múltiplas posições, os campos de override aparecem apenas na primeira linha (outras ficam desabilitadas)
- Campos têm placeholder "ex: 200.50" e "ex: 150.00"
- Largura: `w-24` (consistente com outros campos de override)

**Localização:** Linhas 122-185

#### 3.2. Função `collectOverrides()` - Coleta de Valores
**Mudanças:**
- Modificada para coletar valores de `additional` e `expenses` no nível do funcionário
- Estrutura de dados resultante:
```javascript
{
  "Employee Name": {
    call_off: "P25-122",           // existente
    additional: 200.50,            // NOVO
    expenses: 150.00,              // NOVO
    overrides: {                   // existente (por linha)
      0: {quantity: 160, unit_price: 300}
    }
  }
}
```

**Localização:** Linhas 538-567

### 4. Backend - API (`app/api/server.py`)

#### 4.1. Aplicação de Overrides
**Mudanças:**
- Adicionada lógica para processar overrides de `additional` e `expenses`
- Implementação após o override de `call_off` e antes dos overrides por linha

**Comportamento para Additional:**
1. Se override > 0:
   - Atualiza item existente de "Brazilian Payroll Additional"
   - Ou cria novo item se não existir
2. Se override = 0:
   - Remove item de Additional se existir

**Comportamento para Expenses:**
1. Se override > 0:
   - Atualiza item existente de "Expenses"
   - Ou cria novo item se não existir
2. Se override = 0:
   - Remove item de Expenses se existir

**Logs de Debug:**
- Todos os overrides são logados para facilitar troubleshooting
- Formato: `[DEBUG] {name} - Applying {type} override: £{value:.2f}`

**Localização:** Linhas 767-827

## Fluxo de Dados

### 1. Preview (Leitura)
```
ABZ File → read_charge_rate_table() → Brazilian Payroll Additionals (GBP)
AN-FIN File → extract_costs_gbp() → Expenses
↓
_build_preview_single_file() → Preview JSON
↓
Frontend (app.js) → Renderiza tabela com valores originais
```

### 2. Override (Escrita)
```
Usuário preenche campos "Override Additional" e/ou "Override Expenses"
↓
collectOverrides() → Coleta valores em estrutura JSON
↓
POST /api/generate → Envia overrides para backend
↓
server.py (linhas 767-827) → Aplica overrides aos items
↓
generate_from_abz_template() → Gera invoice com valores atualizados
```

## Casos de Uso

### Caso 1: Funcionário com Expenses no AN-FIN
**Situação:** Expenses detectado automaticamente = £263.34
**Ação:** Usuário quer mudar para £300.00
**Resultado:** Preenche campo "Override Expenses" com 300.00

### Caso 2: Funcionário sem Expenses mas precisa adicionar
**Situação:** Nenhum expense detectado (£0.00)
**Ação:** Usuário quer adicionar £150.00
**Resultado:** Preenche campo "Override Expenses" com 150.00, item é criado

### Caso 3: Remover Additional existente
**Situação:** Additional detectado = £200.00
**Ação:** Usuário quer remover
**Resultado:** Preenche campo "Override Additional" com 0, item é removido

### Caso 4: Funcionário com múltiplas posições
**Situação:** Funcionário tem 2 posições (2 linhas na tabela)
**Ação:** Campos de override aparecem apenas na primeira linha
**Resultado:** Override se aplica ao funcionário inteiro, não por linha

## Validações

### Frontend
- Valores devem ser numéricos (parseFloat)
- Campos vazios são ignorados (não enviados ao backend)
- Campos desabilitados em linhas secundárias (múltiplas posições)

### Backend
- Valores são convertidos para float
- Valores são arredondados para 2 casas decimais
- Valores ≤ 0 resultam em remoção do item
- Erros são capturados e logados (try/except)

## Compatibilidade

### Backward Compatibility
✅ Mantida - Código existente continua funcionando
- Overrides de quantity e unit_price não foram alterados
- Estrutura de dados é estendida, não modificada
- Campos novos são opcionais

### Forward Compatibility
✅ Preparado para extensões futuras
- Padrão estabelecido para novos overrides no nível do funcionário
- Fácil adicionar novos campos seguindo o mesmo padrão

## Testes Recomendados

### Teste 1: Override de Expenses
1. Fazer upload de ABZ + AN-FIN
2. Carregar preview
3. Identificar funcionário com expenses
4. Preencher campo "Override Expenses" com valor diferente
5. Gerar invoice
6. Verificar que o valor no invoice corresponde ao override

### Teste 2: Override de Additional
1. Fazer upload de ABZ
2. Carregar preview
3. Identificar funcionário com Brazilian Payroll Additional
4. Preencher campo "Override Additional" com valor diferente
5. Gerar invoice
6. Verificar que o valor no invoice corresponde ao override

### Teste 3: Criar Expenses onde não existe
1. Fazer upload de ABZ sem AN-FIN
2. Carregar preview (expenses = £0.00)
3. Preencher campo "Override Expenses" com valor
4. Gerar invoice
5. Verificar que expenses aparece no invoice

### Teste 4: Remover Additional
1. Fazer upload de ABZ com Additional
2. Carregar preview
3. Preencher campo "Override Additional" com 0
4. Gerar invoice
5. Verificar que Additional não aparece no invoice

### Teste 5: Múltiplas posições
1. Fazer upload de ABZ com funcionário que tem 2+ posições
2. Carregar preview
3. Verificar que campos de override aparecem apenas na primeira linha
4. Preencher overrides
5. Gerar invoice
6. Verificar que overrides foram aplicados corretamente

## Notas Técnicas

### Estrutura de Items
```javascript
// Service item (com unit_price e quantity)
{
  description: "Employee Name - Position",
  unit_price: 300.00,
  quantity: 160,
  final: 48000.00
}

// Additional/Expenses item (sem unit_price e quantity)
{
  description: "Brazilian Payroll Additional" | "Expenses",
  final: 200.50
}
```

### Ordem de Processamento de Overrides
1. Call-Off (header level)
2. Additional (employee level) ← NOVO
3. Expenses (employee level) ← NOVO
4. Quantity/Unit Price (line level)

### Debug Logs
Todos os overrides geram logs no formato:
```
[DEBUG] {employee_name} - Applying {type} override: £{value:.2f}
[DEBUG] {employee_name} - Updated existing {type} item to £{value:.2f}
[DEBUG] {employee_name} - Created new {type} item: £{value:.2f}
[DEBUG] {employee_name} - Removed {type} item (override = 0)
```

## Conclusão

A implementação adiciona funcionalidade crítica para permitir ajustes manuais de Expenses e Additional, mantendo a arquitetura existente e respeitando os padrões do código. A solução é robusta, bem documentada e fácil de manter.

