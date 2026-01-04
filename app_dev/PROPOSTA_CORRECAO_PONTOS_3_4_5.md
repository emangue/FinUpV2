# 📋 PROPOSTA DE CORREÇÃO - PONTOS 3, 4 e 5

**Data:** 03/01/2026  
**Status Pontos 1 e 2:** ✅ Corrigidos com sucesso

---

## 🎯 PONTO 4: INCONSISTÊNCIA DATA/ANO/DT_FATURA

### Análise dos Exemplos

**Padrão identificado:**
- IDs 16, 23, 25, 26, 30, 32, 35, 36, 37, 38 (todos da origem "XP")
- Data real: Dezembro 2023 ou Outubro 2023
- Ano/DT_Fatura armazenados: 2024/202401

**Exemplo ID 16:**
```
Data: 16/12/2023        ← Data real da transação
Ano: 2024               ← ERRADO (deveria ser 2023)
DT_Fatura: 202401       ← ERRADO (deveria ser 202312)
Estabelecimento: MERCADOLIVRE*2PRODUTOS
Origem: XP
```

### Causa Raiz
Transações realizadas em **dez/2023 ou out/2023** foram marcadas com **Ano=2024** e **DT_Fatura=202401**.

Possíveis causas:
1. **Fatura de cartão:** Compras em dez/2023 aparecem na fatura de jan/2024
2. **Erro de processamento:** Processador usou mês da fatura em vez do mês da transação
3. **Importação tardia:** Arquivo importado em 2024 pegou ano/mês atual

### Proposta de Correção

**OPÇÃO A: Usar Data como fonte da verdade (RECOMENDADO)**
```sql
-- Recalcular Ano e DT_Fatura SEMPRE a partir de Data
UPDATE journal_entries
SET 
  Ano = CAST(substr(Data, 7, 4) AS INTEGER),
  DT_Fatura = substr(Data, 7, 4) || substr(Data, 4, 2)
WHERE Data LIKE '__/__/____';
```

**Justificativa:**
- `Data` é quando a transação REALMENTE aconteceu
- Para análise de gastos, importa quando gastou, não quando pagou
- Mantém consistência: Data ↔ Ano ↔ DT_Fatura

**OPÇÃO B: Usar DT_Fatura como fonte (NÃO recomendado)**
- Perderia informação da data real da compra
- Impossível reconstruir Data a partir de DT_Fatura (perderia dia)

### Decisão Necessária
❓ **Qual opção você prefere?**
- [ ] Opção A: Usar Data como verdade (corrige Ano/DT_Fatura)
- [ ] Opção B: Manter como está (usar DT_Fatura para agrupamento)
- [ ] Opção C: Criar campo adicional (Data vs DataFatura)

---

## 🎯 PONTOS 3 e 5: TIPOGASTO PARA TRANSAÇÕES NÃO-GASTO

### Problema Identificado

**Categorias que NÃO são gastos:**
1. **Transferências Entre Contas** (200 transações, R$ 1,09M)
   - Movimentação interna de dinheiro
   - Não reduz patrimônio líquido
   - TipoGasto atual: NULL, "Débito", "Ignorar" ou "nan"

2. **Salários** (56 transações, R$ 776K)
   - É RECEITA, não gasto
   - TipoGasto atual: "Salário", NULL ou "nan"

3. **Investimentos** (1.201 transações, R$ 760K)
   - É APLICAÇÃO de capital, não gasto
   - TipoGasto atual: "Investimentos - Ajustável", "Ajustável - Investimentos", NULL, "Débito", "Ajustado" ou "nan"

### Valores Não Padronizados (Ponto 5)

| Valor Atual | Qtd | Onde Aparece | Problema |
|---|---|---|---|
| `'Ajustável - Investimentos'` | 33 | Investimentos (Casa Nova, Flats, MP) | Ordem invertida |
| `'Ignorar'` | 16 | Transferências | Não é um TipoGasto válido |
| `'Fatura'` | 5 | Fatura / Cartão AZUL | Específico demais |
| `'Ajustado'` | 1 | Investimentos (Itaú Person) | Typo de "Ajustável" |
| `'nan'` | Vários | Vários | Valor vazio como string |
| `'Débito'` | Vários | Transferências, Investimentos | Não é TipoGasto |

---

## 💡 PROPOSTA: NOVA ESTRUTURA DE TIPOGASTO

### Conceito
**TipoGasto** deve indicar a **natureza da movimentação** e não apenas se é gasto ajustável/fixo.

### Categorias Propostas

#### 1. Para GASTOS (comportamento atual mantido)
- `'Fixo'` - Gastos fixos mensais
- `'Ajustável'` - Gastos variáveis
- `'Ajustável - Saídas'`
- `'Ajustável - Viagens'`
- `'Ajustável - Delivery'`
- `'Ajustável - Supermercado'`
- `'Ajustável - Carro'`
- `'Ajustável - Uber'`
- `'Ajustável - Assinaturas'`

#### 2. Para NÃO-GASTOS (NOVO)

##### **Transferências**
```
TipoGasto = 'Transferência'
```
- Movimentação interna entre contas
- **Ação:** Ignorar em dashboards de gastos
- **Campo:** Usar `IgnorarDashboard = 1`

##### **Receitas**
```
TipoGasto = 'Receita - Salário'
TipoGasto = 'Receita - Férias'
TipoGasto = 'Receita - Outras'
```
- Entrada de dinheiro
- **Ação:** Aparece em dashboard de receitas
- Sinal positivo em `Valor`

##### **Investimentos**
```
TipoGasto = 'Investimento - Fixo'        # Ex: Aluguel de flats, prestação casa
TipoGasto = 'Investimento - Ajustável'   # Ex: Aportes variáveis, empréstimos
```
- Aplicação de capital
- **Ação:** Dashboard específico de investimentos
- Não é gasto, mas saída de caixa

#### 3. Para ESPECIAIS

##### **Fatura de Cartão**
```
TipoGasto = 'Pagamento Fatura'
```
- Pagamento da fatura em si (não as compras)
- **Ação:** Sempre ignorar (evita duplicação)
- As compras já foram contabilizadas

---

## 🛠️ SCRIPT DE CORREÇÃO PROPOSTO

### Fase 1: Corrigir Valores Não Padronizados

```sql
BEGIN TRANSACTION;

-- 1. Corrigir ordem invertida: 'Ajustável - Investimentos' → 'Investimento - Ajustável'
UPDATE journal_entries 
SET TipoGasto = 'Investimento - Ajustável'
WHERE TipoGasto = 'Ajustável - Investimentos';

-- 2. Corrigir typo: 'Ajustado' → 'Investimento - Ajustável' (contexto: Investimentos)
UPDATE journal_entries 
SET TipoGasto = 'Investimento - Ajustável'
WHERE TipoGasto = 'Ajustado' AND GRUPO LIKE '%Investimento%';

-- 3. Corrigir 'nan' para NULL
UPDATE journal_entries 
SET TipoGasto = NULL
WHERE TipoGasto = 'nan' OR TipoGasto = 'NaN';

-- 4. Corrigir 'Débito' baseado no GRUPO
UPDATE journal_entries 
SET TipoGasto = 'Transferência'
WHERE TipoGasto = 'Débito' AND GRUPO LIKE '%Transferência%';

UPDATE journal_entries 
SET TipoGasto = 'Investimento - Ajustável'
WHERE TipoGasto = 'Débito' AND GRUPO LIKE '%Investimento%';

-- 5. Corrigir 'Ignorar' → 'Transferência'
UPDATE journal_entries 
SET TipoGasto = 'Transferência',
    IgnorarDashboard = 1
WHERE TipoGasto = 'Ignorar';

-- 6. Padronizar 'Fatura' → 'Pagamento Fatura'
UPDATE journal_entries 
SET TipoGasto = 'Pagamento Fatura',
    IgnorarDashboard = 1
WHERE TipoGasto = 'Fatura';

COMMIT;
```

### Fase 2: Preencher TipoGasto Missing

```sql
BEGIN TRANSACTION;

-- 1. Corrigir capitalização inconsistente
UPDATE journal_entries
SET GRUPO = 'Transferência Entre Contas'
WHERE GRUPO = 'Transferência entre contas';

-- 2. Preencher Transferências
UPDATE journal_entries
SET TipoGasto = 'Transferência',
    IgnorarDashboard = 1
WHERE (TipoGasto IS NULL OR TipoGasto = '')
  AND GRUPO LIKE '%Transferência%';

-- 3. Preencher Salários
UPDATE journal_entries
SET TipoGasto = 'Receita - Salário'
WHERE (TipoGasto IS NULL OR TipoGasto = '')
  AND GRUPO LIKE '%Salário%'
  AND SUBGRUPO = 'Salário';

UPDATE journal_entries
SET TipoGasto = 'Receita - Férias'
WHERE (TipoGasto IS NULL OR TipoGasto = '')
  AND GRUPO LIKE '%Salário%'
  AND SUBGRUPO = 'Férias';

-- 4. Preencher Investimentos
UPDATE journal_entries
SET TipoGasto = 'Investimento - Fixo'
WHERE (TipoGasto IS NULL OR TipoGasto = '')
  AND GRUPO = 'Investimentos'
  AND SUBGRUPO IN ('Flats', 'Casa Araraquara', 'Casa Nova');

UPDATE journal_entries
SET TipoGasto = 'Investimento - Ajustável'
WHERE (TipoGasto IS NULL OR TipoGasto = '')
  AND GRUPO = 'Investimentos';

-- 5. Backfill restante via base_marcacoes
UPDATE journal_entries
SET TipoGasto = (
    SELECT TipoGasto FROM base_marcacoes
    WHERE base_marcacoes.GRUPO = journal_entries.GRUPO
      AND base_marcacoes.SUBGRUPO = journal_entries.SUBGRUPO
)
WHERE (TipoGasto IS NULL OR TipoGasto = '')
  AND GRUPO IS NOT NULL 
  AND SUBGRUPO IS NOT NULL
  AND EXISTS (
      SELECT 1 FROM base_marcacoes
      WHERE base_marcacoes.GRUPO = journal_entries.GRUPO
        AND base_marcacoes.SUBGRUPO = journal_entries.SUBGRUPO
  );

COMMIT;
```

### Fase 3: Atualizar base_marcacoes

```sql
BEGIN TRANSACTION;

-- Adicionar novos TipoGasto em base_marcacoes
INSERT OR IGNORE INTO base_marcacoes (GRUPO, SUBGRUPO, TipoGasto)
VALUES 
  ('Transferência Entre Contas', 'XP', 'Transferência'),
  ('Transferência Entre Contas', 'MP', 'Transferência'),
  ('Transferência Entre Contas', 'Itaú Person', 'Transferência'),
  ('Transferência Entre Contas', 'Santander', 'Transferência'),
  ('Transferência Entre Contas', 'Mercado Pago', 'Transferência'),
  ('Salário', 'Salário', 'Receita - Salário'),
  ('Salário', 'Férias', 'Receita - Férias'),
  ('Investimentos', 'MP', 'Investimento - Ajustável'),
  ('Investimentos', 'XP', 'Investimento - Ajustável'),
  ('Investimentos', 'Itaú Person', 'Investimento - Ajustável'),
  ('Investimentos', 'Santander', 'Investimento - Ajustável'),
  ('Investimentos', 'Flats', 'Investimento - Fixo'),
  ('Investimentos', 'Casa Araraquara', 'Investimento - Fixo'),
  ('Investimentos', 'Casa Nova', 'Investimento - Fixo');

-- Atualizar TipoGasto em base_marcacoes existentes
UPDATE base_marcacoes
SET TipoGasto = 'Investimento - Ajustável'
WHERE TipoGasto = 'Investimentos - Ajustável';

COMMIT;
```

---

## 📊 IMPACTO ESPERADO

### Antes
```
TipoGasto NULL: 363 transações (8.74%)
TipoGasto inválidos: 55 transações (1.32%)
Total com problema: 418 transações (10.06%)
```

### Depois
```
TipoGasto NULL: 0 transações (0%)
TipoGasto padronizados: 4,153 transações (100%)
- Gastos (Fixo/Ajustável): ~2,896 transações
- Transferências: ~200 transações (ignoradas no dashboard)
- Receitas: ~56 transações
- Investimentos: ~1,001 transações
```

---

## ✅ DECISÕES NECESSÁRIAS

1. **Ponto 4 (Data/Ano/DT_Fatura):**
   - [ ] Opção A: Recalcular Ano/DT_Fatura a partir de Data
   - [ ] Opção B: Manter como está
   - [ ] Opção C: Criar campos separados (Data vs DataFatura)

2. **Ponto 3 (Estrutura TipoGasto):**
   - [ ] Aprovar nova estrutura proposta
   - [ ] Sugerir modificações
   - [ ] Manter estrutura atual

3. **Ponto 5 (Valores não padronizados):**
   - [ ] Aplicar script de correção
   - [ ] Revisar casos específicos antes

---

## 🎯 PRÓXIMOS PASSOS

1. **Você decide:** Revisar propostas acima
2. **Aprovar:** Quais correções aplicar
3. **Executar:** Scripts de correção
4. **Validar:** Rodar `python run_audits.py` novamente
5. **Integrar:** Atualizar validador de upload com novos TipoGasto

---

**Aguardando sua decisão para prosseguir!** 🚀
