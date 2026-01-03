# 📊 PROPOSTA DE OTIMIZAÇÃO - Colunas journal_entries

**Data:** 03/01/2026  
**Versão:** 1.0.0  
**Status:** Aguardando aprovação

---

## 🎯 OBJETIVO

Revisar todas as 30 colunas da tabela `journal_entries` para:
1. Validar necessidade e utilidade de cada coluna
2. Propor eliminação de colunas desnecessárias
3. Propor padronizações e merges
4. Reduzir redundância e complexidade

---

## 📋 ANÁLISE POR CATEGORIA

### 🟢 COLUNAS ESSENCIAIS (Manter)

#### **1. id** (INTEGER, PK)
- **Necessidade:** CRÍTICA
- **Uso:** Chave primária, identificador único
- **Decisão:** ✅ MANTER

#### **2. IdTransacao** (VARCHAR(64), UNIQUE)
- **Necessidade:** CRÍTICA
- **Uso:** Hash único para detectar duplicatas
- **Preenchimento:** 100% (4.153)
- **Valores únicos:** 4.153 (cada transação tem hash único)
- **Decisão:** ✅ MANTER

#### **3. Data** (VARCHAR(10), DD/MM/AAAA)
- **Necessidade:** CRÍTICA
- **Uso:** Data da transação
- **Preenchimento:** 100% (4.153)
- **Valores únicos:** 702 datas diferentes
- **Decisão:** ✅ MANTER

#### **4. Estabelecimento** (TEXT)
- **Necessidade:** CRÍTICA
- **Uso:** Nome do estabelecimento/descrição
- **Preenchimento:** 100% (4.153)
- **Valores únicos:** 1.691 estabelecimentos
- **Decisão:** ✅ MANTER

#### **5. Valor** (FLOAT)
- **Necessidade:** CRÍTICA
- **Uso:** Valor da transação (negativo = gasto, positivo = receita)
- **Preenchimento:** 100% (4.153)
- **Decisão:** ✅ MANTER

#### **6. ValorPositivo** (FLOAT)
- **Necessidade:** ALTA
- **Uso:** ABS(Valor) para cálculos e visualizações
- **Preenchimento:** 100% (4.153)
- **Decisão:** ✅ MANTER (facilita queries e dashboards)

#### **7. TipoGasto** (VARCHAR(100))
- **Necessidade:** CRÍTICA
- **Uso:** Classificação Fixo/Ajustável/Receita/Investimento
- **Preenchimento:** 100% (4.153) - recém corrigido!
- **Valores únicos:** 23 categorias
- **Decisão:** ✅ MANTER

#### **8. GRUPO** (VARCHAR(100))
- **Necessidade:** CRÍTICA
- **Uso:** Categoria principal (Alimentação, Carro, etc)
- **Preenchimento:** 99.8% (4.146)
- **Valores únicos:** 21 grupos
- **Decisão:** ✅ MANTER

#### **9. SUBGRUPO** (VARCHAR(100))
- **Necessidade:** CRÍTICA
- **Uso:** Subcategoria detalhada
- **Preenchimento:** 99.8% (4.146)
- **Valores únicos:** 213 subgrupos
- **Decisão:** ✅ MANTER

#### **10. created_at** (DATETIME)
- **Necessidade:** ALTA
- **Uso:** Timestamp de criação do registro
- **Preenchimento:** 100% (4.153)
- **Decisão:** ✅ MANTER (auditoria)

#### **11. user_id** (INTEGER)
- **Necessidade:** ALTA
- **Uso:** Relacionamento com tabela users (multi-usuário)
- **Preenchimento:** 100% (todos user_id=1)
- **Decisão:** ✅ MANTER (suporte multi-usuário futuro)

---

### 🟡 COLUNAS COM PROBLEMAS (Ajustar)

#### **12. origem** (VARCHAR(50), OBRIGATÓRIO)
- **Problema:** Mistura BANCO + TIPO + ARQUIVO
- **Exemplos:**
  - "MP" (banco)
  - "Azul" (cartão)
  - "Itau Person" vs "Itaú Person" (inconsistente)
  - "Fatura - fatura_itau-202510.csv" (redundante)
- **Preenchimento:** 100% (4.153)
- **Valores únicos:** 15
- **Proposta:** 
  ```
  PADRONIZAR valores:
  - "Itau Person" → "Itaú"
  - "Itaú Person" → "Itaú"
  - "Fatura - fatura_itau-*.csv" → "Itaú"
  - "Extrato - extrato_itau.xls" → "Itaú"
  - "Mercado Pago - mp_agosto.xlsx" → "Mercado Pago"
  - "BTG - extrato_btg.xls" → "BTG"
  
  RENOMEAR coluna: origem → banco_origem
  ```

#### **13. banco** (TEXT)
- **Problema:** Quase vazio (96.9% NULL), redundante com origem
- **Preenchimento:** 3.1% (129)
- **Valores:** "Mercado Pago" (119), "BTG" (10)
- **Proposta:** 
  ```
  ELIMINAR coluna banco
  PREENCHER origem padronizada para todos
  CRIAR nova coluna arquivo_origem (rastreabilidade)
  ```

#### **13b. arquivo_origem** (TEXT) - **NOVA COLUNA**
- **Necessidade:** ALTA (rastreabilidade)
- **Uso:** Nome do arquivo original usado no upload
- **Proposta:**
  ```
  CRIAR coluna arquivo_origem
  POPULAR com origem atual onde aplicável
  Histórico: "dado_historico"
  Novos uploads: preencher automaticamente
  ```

#### **14. Ano** (INTEGER)
- **Problema:** Derivado de Data, redundante
- **Uso:** Facilita agrupamento por ano
- **Preenchimento:** 100% (4.153)
- **Valores:** 2024, 2025
- **Proposta:** 
  ```
  OPÇÃO A: ELIMINAR (calcular via substr(Data, 7, 4))
  OPÇÃO B: MANTER (otimização de queries)
  
  RECOMENDADO: Manter (performance em dashboards)
  ```

#### **15. DT_Fatura** (VARCHAR(6), AAAAMM)
- **Problema:** Nem sempre alinhado com Data (compra ≠ fatura)
- **Uso:** Mês de faturamento do cartão
- **Preenchimento:** 100% (4.153)
- **Valores únicos:** 24 meses
- **Proposta:** 
  ```
  RENOMEAR: DT_Fatura → MesFatura
  MANTER como está (útil para análise de faturas)
  ```

#### **16. NomeTitular** (VARCHAR(200))
- **Problema:** Inconsistente e pouco usado
- **Preenchimento:** 15.7% (650)
- **Valores:**
  - "EMANUEL GUERRA" (332)
  - "Emanuel Guerra Leandro" (292)
  - "EMANUEL GUERRA LEANDRO" (22)
  - "0" (4)
- **Proposta:** 
  ```
  OPÇÃO A: ELIMINAR (usar user_id → users.nome)
  OPÇÃO B: PADRONIZAR valores
  
  RECOMENDADO: ELIMINAR (redundante com user_id)
  ```

#### **17. DataPostagem** (VARCHAR(10), DD/MM/AAAA)
- **Problema:** Pouco usado (8.6%)
- **Uso:** Data de postagem no extrato (diferente de Data transação)
- **Preenchimento:** 8.6% (356)
- **Proposta:** 
  ```
  OPÇÃO A: ELIMINAR (pouco usado)
  OPÇÃO B: MANTER (pode ser útil para reconciliação)
  
  RECOMENDADO: MANTER mas renomear → DataExtrato
  ```

---

### 🔴 COLUNAS VAZIAS/DESNECESSÁRIAS (Eliminar)

#### **18. ValidarIA** (VARCHAR(10))
- **Preenchimento:** 0% (0)
- **Decisão:** ❌ ELIMINAR

#### **19. CartaoCodigo8** (VARCHAR(20))
- **Preenchimento:** 0% (0)
- **Decisão:** ❌ ELIMINAR

#### **20. FinalCartao** (VARCHAR(4))
- **Preenchimento:** 0% (0)
- **Decisão:** ❌ ELIMINAR

#### **21. IdOperacao** (VARCHAR(20))
- **Preenchimento:** 0% (0)
- **Decisão:** ❌ ELIMINAR

#### **22. TipoLancamento** (VARCHAR(20))
- **Preenchimento:** 8.6% (356)
- **Valor único:** "Nacional"
- **Utilidade:** Baixa (todos são "Nacional")
- **Decisão:** ❌ ELIMINAR

#### **23. TransacaoFutura** (VARCHAR(3))
- **Preenchimento:** 12.4% (514)
- **Valor único:** "NÃO"
- **Utilidade:** Baixa (todos são "NÃO")
- **Decisão:** ❌ ELIMINAR

#### **24. tipodocumento** (TEXT) - **⚠️ CRÍTICO - MANTER**
- **Preenchimento:** 3.1% (129) - **PROBLEMA!**
- **Valor único:** "Extrato"
- **Uso CRÍTICO:** Deduplicador usa para distinguir Extrato vs Fatura
- **Código:** `app/utils/deduplicator.py` linha 90
- **Decisão:** ✅ **MANTER E POPULAR** (usando TipoTransacao)
- **Proposta:**
  ```
  MANTER coluna tipodocumento
  POPULAR usando TipoTransacao:
  - Se TipoTransacao = 'Cartão de Crédito' → tipodocumento = 'Cartão'
  - Se TipoTransacao = 'Receitas' ou 'Despesas' → tipodocumento = 'Extrato'
  TORNAR obrigatório em novos uploads
  ```

---

### 🟠 COLUNAS ESPECÍFICAS (Avaliar)

#### **25. TipoTransacao** (VARCHAR(50))
- **Uso:** "Cartão de Crédito" (45.5%), "Despesas" (32.2%), "Receitas" (22.3%)
- **Preenchimento:** 100% (4.153)
- **Utilidade:** Média (pode ser derivado de TipoGasto)
- **Proposta:** 
  ```
  OPÇÃO A: ELIMINAR (derivar de TipoGasto)
  OPDecisão:** ❌ **ELIMINAR** (aprovado pelo usuário)
- **Proposta:** 
  ```
  ELIMINAR TipoTransacaoAjuste
  MANTER apenas TipoTransacaocódigo
  Se não for usado em dashboards críticos → ELIMINAR
  ```

#### **26. TipoTransacaoAjuste** (VARCHAR(50))
- **Uso:** Similar a TipoTransacao mas com leve diferença
- **Preenchimento:** 100% (4.153)
- **Problema:** Redundante com TipoTransacao
- **Proposta:** 
  ```
  MERGE com TipoTransacao ou ELIMINAR
  ```
 (ORIGEM da classificação)
- **Valores:** "Base_Padroes" (7.7%), "Manual (Lote)" (2.2%), "IdParcela" (2.1%)
- **Preenchimento:** 12.4% (514)
- **Uso no código:** `auto_classifier.py` define valores, `upload/routes.py` usa
- **Decisão:** ✅ **MANTER E POPULAR**
- **Proposta:** 
  ```
  MANTER MarcacaoIA (NÃO fazer merge com forma_classificacao)
  POPULAR histórico: MarcacaoIA = 'Histórico' para antigos
  RENOMEAR → origem_classificacao
  POPULAR com valores padrão (ex: "Manual" para antigos)
  ```

#### **28. IgnorarDashboard** (BOOLEAN)
- **Uso:** Flag para ignorar transações (Transferências, Fatura)
- **Preenchimento:** 33.7% são "1" (ignorar)
- **Utilidade:** ALTA (evita duplicação)
- **Decisão:** ✅ MANTER

#### **29. IdParcela** (TEXT)
- **Uso:** Relacionamento com contratos parcelados
- **Preenchimento:** 9.1% (378)
- **ValoresStatus da classificação (Automática, Semi-Automática, Manual)
- **Preenchimento:** 3.2% (131)
- **Valores:** "Automática-BasePadrão" (98), "Semi-Automática" (21), etc
- **Uso CRÍTICO:** Dashboard usa para lógica de edição (linhas 733-736, 824-829)
- **Decisão:** ✅ **MANTER E POPULAR**
- **NÃO fazer merge com MarcacaoIA (propósitos diferentes!)**
- **Proposta:** 
  ```
  MANTER forma_classificacao separada
  POPULAR baseado em MarcacaoIA:
  - Base_Padroes → Automática-BasePadrão
  - Manual/Histórico → Manual
  - NULL → Não Classificada"Semi-Automática" (21), etc
- **Problema:** Muito similar a MarcacaoIA
- **Proposta:** 
### ❌ ELIMINAR (11 colunas)
1. ✅ **ValidarIA** - 0% preenchimento
2. ✅ **CartaoCodigo8** - 0% preenchimento
3. ✅ **FinalCartao** - 0% preenchimento
4. ✅ **IdOperacao** - 0% preenchimento
5. ✅ **TipoLancamento** - Valor único "Nacional"
6. ✅ **TransacaoFutura** - Valor único "NÃO"
7. ✅ **banco** - Redundante com origem (após criar arquivo_origem)
8. ✅ **NomeTitular** - Redundante com user_id
9. ✅ **TipoTransacaoAjuste** - Redundante com TipoTransacao
10. 🔗 **MarcacaoIA** - Mesclada em origem_classificacao
11. 🔗 **forma_classificacao** - Mesclada em origem_classificacao
2. ✅ **CartaoCodigo8** - 0% preenchimento
3. ✅ **FinalCarta2 colunas)
1. **origem** → **banco_origem**
2. **DT_Fatura** → **MesFatura**

### ➕ CRIAR (1 nova coluna)
1. **arquivo_origem** (TEXT) - Nome do arquivo de upload original

### 📝 POPULAR (3 colunas subpovoadas)
1. **tipodocumento** - Popular 96.9% NULL com valores corretos
2. **MarcacaoIA** - Popular histórico como "Histórico"
3. **forma_classificacao** - Popular baseado em MarcacaoIA
### 🔄 RENOMEAR (3 colunas)
1. **origem** → **banco_origem**
2. **DT_Fatura** → **MesFatura**
3. **DataPostagem** → **DataExtrato** (opcional)

### 🔗 MERGE (2 pares)
1. **MarcacaoIA** + **forma_classificacao** → **origem_classificacao**
2. **TipoTransacao** + **TipoTransacaoAjuste** → Avaliar necessidade

### 🔧 PADRONIZAR (origem/banco_origem)

```sql
-- Padronizar Itaú
UPDATE journal_entries SET origem = 'Itaú' 
WHERE origem IN ('Itau Person', 'Itaú Person', 'Extrato - extrato_itau.xls')
   OR origem LIKE 'Fatura - fatura_itau%';

-- Padronizar Mercado Pago
UPDATE journal_entries SET origem = 'Mercado Pago' 
WHERE origem = 'Mercado Pago - mp_agosto.xlsx';

-- Padronizar BTG
UPDATE journal_entries SET origem = 'BTG' 
WHERE origem = 'BTG - extrato_btg.xls';

-- Padronizar Fatura Itaú genérica
UPDATE journal_entries SET origem = 'Itaú' 
WHERE origem LIKE 'Fatura - fatura-%';
```

---

## 📊 IMPACTO

### Antes
- **30 colunas** na tabela
- **4.024 registros** com banco NULL
- **535 registros** com origem inconsistente (Itaú)
- **8 colunas** 100% vazias ou com valor único
- **4.022 registros** (96.8%) sem tipodocumento (quebra deduplicador!)
- **2 colunas** redundantes (MarcacaoIA + forma_classificacao)

### Depois
- **21 colunas** (redução de 30% - eliminadas 11, criadas 2 novas)
- **0 registros** com banco_origem NULL
- **Valores padronizados** e consistentes
- **100% tipodocumento preenchido** (deduplicador funcional)
- **Nova coluna arquivo_origem** (rastreabilidade completa)
- **Nova coluna origem_classificacao** (merge inteligente)
- **Schema mais limpo** e bem documentado

---

## 🛠️ SCRIPT DE MIGRAÇÃO - **ATUALIZADO**

```sql
BEGIN TRANSACTION;

-- ========================================
-- FASE 1: CRIAR NOVA COLUNA arquivo_origem
-- ========================================
ALTER TABLE journal_entries ADD COLUMN arquivo_origem TEXT;

-- Migrar dados onde origem contém nome de arquivo
UPDATE journal_entries SET arquivo_origem = origem 
WHERE origem LIKE '%-%' OR origem LIKE '%.%';

-- Popular histórico
UPDATE journal_entries SET arquivo_origem = 'dado_historico'
WHERE arquivo_origem IS NULL;

-- ========================================
-- FASE 2: PADRONIZAR origem → banco_origem
-- ========================================

-- Padronizar Itaú
UPDATE journal_entries SET origem = 'Itaú' 
WHERE origem IN ('Itau Person', 'Itaú Person', 'Extrato - extrato_itau.xls')
   OR origem LIKE 'Fatura - fatura_itau%'
   OR origem LIKE 'Fatura - fatura-%';

-- Padronizar Mercado Pago
UPDATE journal_entries SET origem = 'Mercado Pago' 
WHERE origem = 'Mercado Pago - mp_agosto.xlsx';

-- Padronizar BTG
UPDATE journal_entries SET origem = 'BTG' 
WHERE origem = 'BTG - extrato_btg.xls';

-- Renomear coluna
ALTER TABLE journal_entries RENAME COLUMN origem TO banco_origem;
ALTER TABLE journal_entries RENAME COLUMN DT_Fatura TO MesFatura;

-- ========================================
-- FASE 3: POPULAR tipodocumento (CRÍTICO!)
-- ========================================

UPDATE journal_entries SET tipodocumento = 'Extrato'
WHERE banco_origem IN ('XP', 'MP', 'Itaú', 'Santander', 'BTG')
  AND tipodocumento IS NULL;

UPDATE journal_entries SET tipodocumento = 'Cartão'
WHERE banco_origem IN ('Azul', 'Nubank', 'Mercado Pago')
  AND tipodocumento IS NULL;

UPDATE journal_entries SET tipodocumento = 'Fatura'
WHERE tipodocumento IS NULL;  -- Resto assume fatura

-- ========================================
-- FASE 4: POPULAR MarcacaoIA e forma_classificacao
-- ======================== - **ATUALIZADO**

**ELIMINAR COLUNAS:**
- [ ] ValidarIA
- [ ] CartaoCodigo8
- [ ] FinalCartao
- [ ] IdOperacao
- [ ] TipoLancamento
- [ ] TransacaoFutura
- [ ] banco
- [ ] NomeTitular
- [ ] TipoTransacaoAjuste

**CRIAR NOVA COLUNA:**
- [ ] arquivo_origem (TEXT) - Rastreabilidade do arquivo de upload

**RENOMEAR:**
- [ ] origem → banco_origem
- [ ] DT_Fatura → MesFatura

**PADRONIZAR banco_origem:**
- [ ] Itaú (todas variações)
- [ ] Mercado Pago
- [ ] BTG

**POPULAR VALORES:**
- [ ] tipodocumento (Extrato, Cartão, Fatura) - **CRÍTICO para deduplicador!**
- [ ] MarcacaoIA ('Histórico' para antigos)
- [ ] forma_classificacao (baseado em MarcacaoIA)
- [ ] arquivo_origem ('dado_historico' para antigos)

**NÃO FAZER (CANCELADO):**
- [x] ~~Merge MarcacaoIA + forma_classificacao~~ - Propósitos diferentes!
- [x] ~~Eliminar tipodocumento~~ - Usado pelo deduplicador!
- [x] ~~Eliminar DataPostagem~~ - Manter como está

**AGUARDANDO VALIDAÇÃO (ver BACKLOG):**
- [ ] Lógica do campo Ano (Extrato vs Fatura)
- [ ] Relacionamento Ano / MesFatura / DataOLUMN IdOperacao;
ALTER TABLE journal_entries DROP COLUMN TipoLancamento;
ALTER TABLE journal_entries DROP COLUMN TransacaoFutura;
ALTER TABLE journal_entries DROP COLUMN banco;
ALTER TABLE journal_entries DROP COLUMN NomeTitular;
ALTER TABLE journal_entries DROP COLUMN TipoTransacaoAjuste;

COMMIT;
```

---

## ⚠️ ATENÇÃO: Questão do Campo `Ano`

**NÃO incluído no script acima** - requer validação:

O campo `Ano` tem lógica complexa:
- Se origem = Extrato → Ano vem de Data
- Se origem = Fatura → Ano vem de DT_Fatura (MesFatura)

Ver arquivo [BACKLOG_VALIDACOES.md](BACKLOG_VALIDACOES.md) para detalhes.

**Ação:** Validar lógica antes de qualquer mudança.

---

## ✅ CHECKLIST DE APROVAÇÃO

**ELIMINAR COLUNAS:**
- [ ] ValidarIA
- [ ] CartaoCodigo8
- [ ] FinalCartao
- [ ] IdOperacao
- [ ] TipoLancamento
- [ ] TransacaoFutura
- [ ] tipodocumento
- [ ] banco
- [ ] NomeTitular

**RENOMEAR:**
- [ ] origem → banco_origem
- [ ] DT_Fatura → MesFatura
- [ ] DataPostagem → DataExtrato

**PADRONIZAR:**
- [ ] Itaú (todas variações)
- [ ] Mercado Pago
- [ ] BTG
- [ ] Fatura genérica

**MERGE:**
- [ ] MarcacaoIA + forma_classificacao → origem_classificacao
- [ ] Avaliar TipoTransacao + TipoTransacaoAjuste

**MANTER COMO ESTÁ:**
- [ ] Ano (performance)
- [ ] IgnorarDashboard (essencial)

---

## 🚨 ATENÇÃO: ANTES DE APLICAR

1. ✅ **Fazer backup completo do banco**
2. ✅ **Testar script em ambiente de dev**
3. ✅ **Validar uso de TipoTransacao/TipoTransacaoAjuste no código**
4. ✅ **Atualizar models.py** após mudanças no schema
5. ✅ **Atualizar validadores e processadores**
6. ✅ **Atualizar dashboards e queries**

---

**Aguardando sua aprovação para prosseguir!** 🚀
