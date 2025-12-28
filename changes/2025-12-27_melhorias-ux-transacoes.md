# Melhorias UX de Transações e Correções Críticas

**Data:** 27/12/2025  
**Versão:** 2.2.0 → 2.2.1  
**Tipo:** Feature + Bug Fix  
**Impacto:** Médio (UI/UX + Admin)

## 📋 Resumo

Melhorias significativas na interface de transações, correção de filtros do admin, implementação de rastreamento de classificação automática e confirmação de atualização automática de bases.

## 🎯 Mudanças Principais

### 1. Interface de Transações Melhorada

**Nova Coluna "Parcelado"**
- Badge amarelo com ícone quando `IdParcela` existe
- Permite verificar visualmente se transação é parcelada
- Útil para debug de IdParcela sem expor o hash ao usuário

**Coluna Dashboard Simplificada**
- Removido textos "Ignorado"/"Considerado"
- Apenas switch com tooltip no hover
- Layout mais limpo e compacto

**Modal com IDs de Debug**
- Box azul no topo mostrando:
  - IdTransacao (hash de 64 bits)
  - IdParcela ("Não parcelado" se não houver)
- Facilita troubleshooting de problemas de hash

### 2. Filtros Admin Unificados

**Problema:** Admin usava nomes de parâmetros diferentes (`busca`, `grupo`) enquanto template compartilhado usava (`estabelecimento`, `categoria`)

**Solução:**
- Unificação completa de parâmetros
- Admin agora suporta TODOS os filtros do template:
  - `estabelecimento` (busca por nome)
  - `categoria` (grupo específico)
  - `tipo[]` (múltiplos checkboxes: despesa, cartao, receita)
  - `dashboard` (consideradas vs todas)
- Filtros específicos do admin mantidos (`id_parcela`, `origem`)

### 3. Auto-toggle em Investimentos

**Comportamento Novo:**
- Clicar em qualquer célula de "Investimento Líquido" no breakdown
- Switch automaticamente muda para "Mostrando TODAS" (verde)
- URL inclui `&dashboard_toggle=1&dashboard=todas`
- Mostra investimentos ignorados (muitos têm `IgnorarDashboard=True`)

**Cálculo YTD Corrigido:**
- Removido filtro `IgnorarDashboard.isnot(True)` do investimento_ytd
- Agora mostra TODOS os investimentos no card Year-to-Date
- Alinhado com comportamento do breakdown

### 4. Rastreamento de Classificação (forma_classificacao)

**Novo Campo:** `JournalEntry.forma_classificacao`

**Valores Possíveis:**
- `Automática-BasePadrao` - Classificada por Base_Padroes
- `Automática-IdParcela` - Vinculada a parcela existente
- `Automática-FaturaCartão` - Detectada como fatura de cartão
- `Automática-IgnorarTitular` - Ignorada por ser nome do titular
- `Automática-IgnorarLista` - Ignorada por lista admin
- `Automática-Histórico` - Classificada por Journal Entries histórico
- `Automática-PalavrasChave` - Classificada por regras de keywords
- `Semi-Automática` - Foi automática, depois editada pelo usuário
- `Manual` - Classificada manualmente do zero
- `Não Classificada` - Aguardando classificação

**Fluxo de Atualização:**
1. Auto-classifier marca todas com origem apropriada
2. Ao editar transação automática → vira Semi-Automática
3. Ao classificar transação nova → vira Manual
4. Edições subsequentes mantêm status

### 5. Correção BTG (Valores Brasileiros)

**Problema:** `pd.to_numeric()` não entendia formato "14.830,40"

**Solução:**
```python
def converter_valor_brasileiro(valor_raw):
    # Remove pontos (milhar) e troca vírgula por ponto (decimal)
    valor_str = str(valor_raw).replace('.', '').replace(',', '.')
    return float(valor_str)
```

**Validação Corrigida:**
- Fórmula: `Primeiro Saldo Diário + Σ(transações após) ≈ Último Saldo Diário`
- Tolerância: ±0.10 centavos (era ±0.01, causava falsos positivos)

### 6. Confirmação: Bases Sempre Atualizadas

**✅ VERIFICADO E CONFIRMADO:**

**BaseParcelas:**
- Atualizada automaticamente ANTES de salvar (linhas 580-810 de upload/routes.py)
- Função `sincronizar_base_parcelas()` chamada em todo salvamento
- Registra novas parcelas com IdParcela
- Atualiza contadores (qtd_pagas) de parcelas existentes
- Status mudado para 'finalizado' quando todas pagas

**BasePadrao:**
- Regenerada automaticamente APÓS cada salvamento (linha 812)
- Função `regenerar_padroes()` analisa TODAS as transações
- Detecta padrões de estabelecimentos recorrentes
- Calcula estatísticas (valor_medio, desvio_padrao, confiança)
- Classifica como alta/media/baixa confiança
- Sugestões de GRUPO/SUBGRUPO/TipoGasto

## 📂 Arquivos Modificados

1. **templates/transacoes.html** - Nova coluna Parcelado, switch simplificado
2. **templates/_macros/transacao_modal_edit.html** - Box de IDs, população de campos
3. **app/blueprints/admin/routes.py** - Filtros unificados
4. **app/blueprints/dashboard/routes.py** - IdParcela na API, forma_classificacao
5. **app/blueprints/dashboard/templates/dashboard.html** - Auto-toggle investimentos
6. **app/blueprints/upload/classifiers/auto_classifier.py** - Registra forma_classificacao
7. **app/blueprints/upload/processors/*.py** - Define forma_classificacao inicial
8. **app/blueprints/upload/routes.py** - Atualiza forma_classificacao em edições
9. **app/models.py** - Novo campo forma_classificacao
10. **app/utils/processors/preprocessors/extrato_btg.py** - Conversão brasileira

**Novo Arquivo:**
11. **scripts/migrate_add_classification_fields.py** - Migração do banco

## 🔧 Migração Necessária

```bash
# Adiciona colunas: banco, tipodocumento, forma_classificacao
python scripts/migrate_add_classification_fields.py
```

## 🧪 Testes Realizados

- ✅ Upload BTG com valores brasileiros (14.830,40)
- ✅ Validação BTG com tolerância ±0.10
- ✅ Filtros admin com múltiplos checkboxes
- ✅ Modal mostrando IdParcela corretamente
- ✅ Auto-toggle de investimentos funcionando
- ✅ Badge "Parcelado" aparecendo
- ✅ Switch simplificado com tooltip

## ⚠️ Breaking Changes

Nenhum. Mudanças são aditivas (novos campos, novas features).

## 📊 Estatísticas

- **Linhas adicionadas:** 331
- **Linhas removidas:** 61
- **Arquivos modificados:** 13
- **Arquivos novos:** 1

## 🔗 Relacionado

- Issue: Investimento YTD zerado
- Issue: Filtros admin não funcionando
- Issue: BTG com valores errados
- Feature: Rastreamento de origem de classificação

## 📝 Notas Técnicas

**Sobre regenerar_padroes():**
- É computacionalmente intensivo (analisa TODAS as transações)
- Roda em background após salvamento
- Não bloqueia UI do usuário
- Gera padrões segmentados por faixa de valor quando necessário

**Sobre forma_classificacao:**
- Permite análises futuras (quantas automáticas vs manuais)
- Facilita debug (saber de onde veio a classificação)
- Base para dashboard de qualidade da classificação automática

**Sobre BaseParcelas:**
- Essencial para vincular parcelas da mesma compra
- Permite calcular quanto falta pagar
- Usado pelo classifier para classificar parcelas futuras automaticamente
