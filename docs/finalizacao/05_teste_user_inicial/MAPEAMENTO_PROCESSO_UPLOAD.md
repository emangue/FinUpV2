# 📤 Mapeamento Completo: Processo de Upload

**Data:** 12/02/2026  
**Objetivo:** Documentar TODAS as tabelas atualizadas durante upload e em que momento

---

## 🎯 Visão Geral

**Fluxo de Upload:** 3 Endpoints, 6 Fases, 7 Tabelas Afetadas

**Endpoints:**
1. `POST /api/v1/upload/preview` - Processar arquivo e criar preview
2. `PATCH /api/v1/upload/preview/{session_id}/{preview_id}` - Editar classificação (opcional)
3. `POST /api/v1/upload/confirm/{session_id}` - Confirmar e salvar transações

**Fases do Pipeline:**
- **Fase 0:** Regenerar base_padroes (automático)
- **Fase 1:** Raw Processing (extração de dados do arquivo)
- **Fase 2:** ID Marking (geração de IdTransacao, IdParcela)
- **Fase 3:** Classification (classificar em grupo/subgrupo)
- **Fase 4:** Deduplication (verificar duplicatas)
- **Fase 5:** Update base_parcelas (atualizar parcelas) - **APÓS confirmação**
- **Fase 6:** ⚠️ **[TODO]** Sincronizar bases (grupos, marcações, tipos) - **APÓS Fase 5**

---

## 📊 Tabelas Afetadas (9 total)

| # | Tabela | Leitura | Escrita | Quando |
|---|--------|---------|---------|--------|
| 1 | **upload_history** | ✅ Busca | ✅ Create/Update | Preview + Confirm |
| 2 | **preview_transacoes** | ✅ Lista | ✅ Create/Update/Delete | Preview + Confirm |
| 3 | **base_padroes** | ✅ Lê | ✅ Create/Update | **ANTES** Preview (Fase 0) |
| 4 | **base_marcacoes** | ✅ Lê | ⚠️ **DEVERIA** Update | Preview (Fase 3) + Confirm (Fase 6) |
| 5 | **base_grupos_config** | ✅ Lê | ⚠️ **DEVERIA** Insert | Preview (Fase 3) + Edit + Confirm (Fase 6) |
| 6 | **journal_entries** | ✅ Check Duplicatas | ✅ Insert | Confirm |
| 7 | **base_parcelas** | ✅ Lê | ✅ Update/Insert | **APÓS** Confirm (Fase 5) |
| 8 | **base_tipos_gasto** | ✅ Lê | ⚠️ **DEVERIA** Insert | Confirm (Fase 6) - Se novo TipoGasto |
| 9 | **base_categorias** | ✅ Lê | ⚠️ **DEVERIA** Insert | Confirm (Fase 6) - Se nova CategoriaGeral |

**⚠️ ATENÇÃO:** Tabelas 4, 5, 8 e 9 atualmente **NÃO são atualizadas** automaticamente durante upload.  
**📝 TODO:** Implementar **Fase 6 - Sincronização de Bases** (após Fase 5)

---

## 🚀 FASE 0: Regenerar base_padroes (ANTES DO PREVIEW)

**Quando:** Automático no **início** do `POST /api/v1/upload/preview`

**Objetivo:** Atualizar padrões de classificação com base nas últimas transações

### 0.1. Leitura de Tabelas

**journal_entries (READ):**
```sql
SELECT 
    SUBGRUPO, 
    EstabelecimentoBase, 
    COUNT(*) as frequencia
FROM journal_entries
WHERE user_id = :user_id
  AND SUBGRUPO IS NOT NULL
  AND SUBGRUPO != ''
  AND origem_classificacao IS NOT NULL
GROUP BY SUBGRUPO, EstabelecimentoBase
HAVING COUNT(*) >= 2;
```

**Objetivo:** Identificar padrões repetidos (≥2 ocorrências)

### 0.2. Escrita em base_padroes

**base_padroes (WRITE):**
```sql
-- Inserir novo padrão
INSERT INTO base_padroes (user_id, GRUPO, SUBGRUPO, estabelecimento_padrao, frequencia, created_at, updated_at)
VALUES (:user_id, :grupo, :subgrupo, :estabelecimento_base, :frequencia, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (user_id, SUBGRUPO, estabelecimento_padrao) DO UPDATE
SET frequencia = :frequencia, updated_at = CURRENT_TIMESTAMP;
```

**Resultado:**
- ✅ Padrões criados/atualizados com frequências
- ✅ Classificação no Preview usará padrões atualizados
- ⚠️ Se falhar: Log warning, continua com padrões antigos

**🔄 Exemplo:**
```
Entrada (journal_entries):
- "Supermercado Pão de Açúcar" → SUBGRUPO: "Mercado/Hortifruti" (5 vezes)

Saída (base_padroes):
- id: 123
- user_id: 1
- SUBGRUPO: "Mercado/Hortifruti"
- estabelecimento_padrao: "SUPERMERCADO PAO"
- frequencia: 5
```

---

## 📝 FASE 1: POST /api/v1/upload/preview - RAW PROCESSING

**Endpoint:** `POST /api/v1/upload/preview`

**Parâmetros:**
- `file`: Arquivo (CSV, XLS, XLSX)
- `banco`: Nome do banco (ex: "itau", "btg")
- `tipo_documento`: "fatura" ou "extrato"
- `mes_fatura`: "YYYY-MM"
- `formato`: "csv", "xls", "xlsx"

### 1.1. Limpeza de Preview Anterior

**preview_transacoes (DELETE):**
```sql
DELETE FROM preview_transacoes WHERE user_id = :user_id;
```

**Quando:** **ANTES** de processar novo arquivo  
**Resultado:** Preview anterior deletado (se existir)

---

### 1.2. Criar Registro de Histórico

**upload_history (INSERT):**
```sql
INSERT INTO upload_history (
    user_id, session_id, banco, tipo_documento, 
    nome_arquivo, nome_cartao, final_cartao, mes_fatura,
    status, data_upload, created_at
) VALUES (
    :user_id, :session_id, :banco, :tipo_documento,
    :nome_arquivo, :nome_cartao, :final_cartao, :mes_fatura,
    'processing', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);
```

**Resultado:**
- ✅ Histórico criado com `status='processing'`
- ✅ `session_id` = `"session_YYYYMMDD_HHMMSS_{user_id}"`
- ✅ `id` retornado (ex: 42)

**🔄 Exemplo:**
```json
{
  "id": 42,
  "session_id": "session_20260212_103000_1",
  "banco": "itau",
  "tipo_documento": "extrato",
  "status": "processing",
  "data_upload": "2026-02-12T10:30:00"
}
```

---

### 1.3. Processar Arquivo (Raw Processing)

**Ação:** Ler arquivo e extrair transações brutas

**Dados Extraídos:**
- Data, Lançamento, Valor
- Banco, Tipo de Documento, Nome do Arquivo
- Nome do Cartão, Final do Cartão (se fatura)
- MesFatura (gerado ou input)

**🔄 Exemplo de Transação Bruta:**
```python
RawTransaction(
    banco="itau",
    tipo_documento="extrato",
    nome_arquivo="extrato_janeiro.csv",
    data="15/01/2026",
    lancamento="PIX TRANSF EMANUEL15/01",
    valor=-1000.50,
    mes_fatura="202601"  # Gerado: YYYYMM da Data
)
```

---

### 1.4. Salvar em preview_transacoes

**preview_transacoes (INSERT batch):**
```sql
INSERT INTO preview_transacoes (
    session_id, user_id, banco, tipo_documento, nome_arquivo,
    data, lancamento, valor, nome_cartao, cartao, mes_fatura,
    created_at,
    -- Campos das fases seguintes (NULL por enquanto)
    IdTransacao, IdParcela, EstabelecimentoBase,
    ParcelaAtual, TotalParcelas, ValorPositivo, TipoTransacao, Ano, Mes,
    GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral, origem_classificacao
) VALUES
    (...),  -- Transação 1
    (...),  -- Transação 2
    (...);  -- Transação N
```

**Resultado:**
- ✅ N transações salvas com dados brutos
- ✅ Classificação ainda NULL (preenchida nas fases seguintes)

**🔄 Exemplo de Registro Criado:**
```json
{
  "id": 1001,
  "session_id": "session_20260212_103000_1",
  "user_id": 1,
  "banco": "itau",
  "data": "15/01/2026",
  "lancamento": "PIX TRANSF EMANUEL15/01",
  "valor": -1000.50,
  "mes_fatura": "202601",
  "IdTransacao": null,  // ← Fase 2
  "GRUPO": null,         // ← Fase 3
  "SUBGRUPO": null       // ← Fase 3
}
```

---

### 1.5. Atualizar Histórico com Total

**upload_history (UPDATE):**
```sql
UPDATE upload_history
SET total_registros = :total_registros,
    balance_validation = :balance_validation_json,
    updated_at = CURRENT_TIMESTAMP
WHERE id = :history_id;
```

**Resultado:**
- ✅ `total_registros` = número de transações processadas
- ✅ `balance_validation` = validação de saldo (se houver)

**🔄 Exemplo:**
```json
{
  "id": 42,
  "total_registros": 150,
  "balance_validation": {
    "saldo_inicial": 5000.00,
    "saldo_final": 3200.50,
    "soma_transacoes": -1799.50,
    "is_valid": true
  }
}
```

---

## 🔖 FASE 2: ID MARKING

**Quando:** Automático após Fase 1 no `POST /api/v1/upload/preview`

**Objetivo:** Gerar IDs únicos (IdTransacao, IdParcela) e campos derivados

### 2.1. Leitura de preview_transacoes

**preview_transacoes (READ):**
```sql
SELECT * FROM preview_transacoes
WHERE session_id = :session_id
  AND user_id = :user_id;
```

### 2.2. Gerar IDs e Campos

**Campos Gerados:**
- `IdTransacao` - Hash único baseado em (Data + Estabelecimento + Valor + Sequência)
- `IdParcela` - Hash único para parcelas (inclui parcela_atual/total)
- `EstabelecimentoBase` - Nome limpo sem parcela (ex: "NETFLIX" de "NETFLIX (1/12)")
- `ValorPositivo` - Valor absoluto
- `ParcelaAtual` / `TotalParcelas` - Extraído do nome (ex: "NETFLIX (1/12)" → 1, 12)
- `TipoTransacao` - "Débito" ou "Crédito" (baseado em Valor)
- `Ano` - Ano da transação (integer)
- `Mes` - Mês da transação (integer 1-12)

**🔄 Exemplo:**
```python
# ANTES (Fase 1):
lancamento = "NETFLIX (1/12)"
valor = -49.90

# DEPOIS (Fase 2):
IdTransacao = hash("15/01/2026|NETFLIX|49.90|0")
IdParcela = hash("15/01/2026|NETFLIX|49.90|1|12")
EstabelecimentoBase = "NETFLIX"
ValorPositivo = 49.90
ParcelaAtual = 1
TotalParcelas = 12
TipoTransacao = "Débito"
Ano = 2026
Mes = 1
```

### 2.3. Atualizar preview_transacoes

**preview_transacoes (UPDATE batch):**
```sql
UPDATE preview_transacoes
SET IdTransacao = :id_transacao,
    IdParcela = :id_parcela,
    EstabelecimentoBase = :estabelecimento_base,
    ValorPositivo = :valor_positivo,
    ParcelaAtual = :parcela_atual,
    TotalParcelas = :total_parcelas,
    TipoTransacao = :tipo_transacao,
    Ano = :ano,
    Mes = :mes,
    updated_at = CURRENT_TIMESTAMP
WHERE id = :preview_id;
```

**Resultado:**
- ✅ IDs únicos gerados
- ✅ Campos derivados calculados
- ✅ Pronto para classificação

---

## 🎯 FASE 3: CLASSIFICATION

**Quando:** Automático após Fase 2 no `POST /api/v1/upload/preview`

**Objetivo:** Classificar transações em GRUPO/SUBGRUPO usando 5 níveis

### 3.1. Níveis de Classificação (Cascata)

**Ordem de tentativa:**
1. **base_parcelas** (READ) - Parcelas conhecidas (IdParcela match)
2. **base_padroes** (READ) - Padrões do usuário (estabelecimento_padrao match)
3. **journal_entries** (READ) - Histórico do usuário (EstabelecimentoBase match)
4. **generic_classification_rules** (READ) - Regras globais (keyword match)
5. **base_marcacoes** (READ) - Sugestão IA (estabelecimento match)

### 3.2. Tabelas Lidas (READ ONLY)

**3.2.1. base_parcelas:**
```sql
SELECT SUBGRUPO FROM base_parcelas
WHERE user_id = :user_id
  AND IdParcela = :id_parcela;
```

**3.2.2. base_padroes:**
```sql
SELECT GRUPO, SUBGRUPO FROM base_padroes
WHERE user_id = :user_id
  AND :estabelecimento_base_normalizado LIKE '%' || estabelecimento_padrao || '%'
ORDER BY frequencia DESC, LENGTH(estabelecimento_padrao) DESC
LIMIT 1;
```

**3.2.3. journal_entries:**
```sql
SELECT GRUPO, SUBGRUPO, COUNT(*) as freq
FROM journal_entries
WHERE user_id = :user_id
  AND EstabelecimentoBase = :estabelecimento_base
  AND SUBGRUPO IS NOT NULL
  AND SUBGRUPO != ''
GROUP BY GRUPO, SUBGRUPO
ORDER BY freq DESC
LIMIT 1;
```

**3.2.4. generic_classification_rules:**
```sql
SELECT grupo_destino, subgrupo_destino FROM generic_classification_rules
WHERE ativo = 1
  AND (:estabelecimento_base_normalizado LIKE '%' || LOWER(keyword) || '%')
ORDER BY prioridade ASC, LENGTH(keyword) DESC
LIMIT 1;
```

**3.2.5. base_marcacoes:**
```sql
SELECT GRUPO, SUBGRUPO FROM base_marcacoes
WHERE user_id = :user_id
  AND :estabelecimento_base_normalizado LIKE '%' || LOWER(SUBGRUPO) || '%'
ORDER BY LENGTH(SUBGRUPO) DESC
LIMIT 1;
```

### 3.3. Buscar TipoGasto e CategoriaGeral

**base_grupos_config (READ):**
```sql
SELECT tipo_gasto_padrao, categoria_geral
FROM base_grupos_config
WHERE user_id = :user_id
  AND nome_grupo = :grupo;
```

**Resultado:**
- ✅ GRUPO, SUBGRUPO classificados
- ✅ TipoGasto e CategoriaGeral preenchidos
- ✅ origem_classificacao registrada

### 3.4. Atualizar preview_transacoes

**preview_transacoes (UPDATE batch):**
```sql
UPDATE preview_transacoes
SET GRUPO = :grupo,
    SUBGRUPO = :subgrupo,
    TipoGasto = :tipo_gasto,
    CategoriaGeral = :categoria_geral,
    origem_classificacao = :origem,  -- 'base_parcelas', 'base_padroes', etc
    MarcacaoIA = :marcacao_ia,       -- Sugestão da base_marcacoes
    updated_at = CURRENT_TIMESTAMP
WHERE id = :preview_id;
```

**🔄 Exemplo de Classificação:**
```json
{
  "id": 1001,
  "lancamento": "IFOOD",
  "GRUPO": "Alimentação",
  "SUBGRUPO": "Delivery",
  "TipoGasto": "Variável",
  "CategoriaGeral": "Despesa",
  "origem_classificacao": "regras_genericas"
}
```

---

### 3.5. Atualizar Histórico com Stats

**upload_history (UPDATE):**
```sql
UPDATE upload_history
SET classification_stats = :stats_json,
    updated_at = CURRENT_TIMESTAMP
WHERE id = :history_id;
```

**Stats salvas:**
```json
{
  "total": 150,
  "base_parcelas": 12,
  "base_padroes": 25,
  "journal_entries": 48,
  "regras_genericas": 50,
  "nao_classificado": 15
}
```

---

## 🔍 FASE 4: DEDUPLICATION

**Quando:** Automático após Fase 3 no `POST /api/v1/upload/preview`

**Objetivo:** Identificar transações já importadas (duplicatas)

### 4.1. Verificar Duplicatas

**journal_entries (READ):**
```sql
SELECT id, Data FROM journal_entries
WHERE user_id = :user_id
  AND IdTransacao = :id_transacao;
```

**Se encontrado:**
- ✅ Transação já existe → Marcar como duplicata

### 4.2. Marcar Duplicatas em preview_transacoes

**preview_transacoes (UPDATE):**
```sql
UPDATE preview_transacoes
SET is_duplicate = TRUE,
    duplicate_reason = :reason,
    origem_classificacao = NULL,  -- Remove da contagem de classificados
    updated_at = CURRENT_TIMESTAMP
WHERE id = :preview_id;
```

**Resultado:**
- ✅ Duplicatas marcadas (`is_duplicate=True`)
- ✅ Não aparecerão em abas de classificação (apenas aba "Duplicadas")
- ✅ Não serão importadas no Confirm

**🔄 Exemplo:**
```json
{
  "id": 1050,
  "IdTransacao": "abc123...",
  "is_duplicate": true,
  "duplicate_reason": "IdTransacao já existe em journal_entries (ID: 3421, Data: 15/01/2026)"
}
```

---

## 📊 Response do POST /api/v1/upload/preview

**JSON retornado:**
```json
{
  "success": true,
  "sessionId": "session_20260212_103000_1",
  "totalRegistros": 150,
  "message": "Preview gerado com sucesso. 135 transações prontas para importar, 15 duplicatas encontradas."
}
```

**Front-end pode:**
- Listar preview: `GET /api/v1/upload/preview/{session_id}`
- Editar classificação: `PATCH /api/v1/upload/preview/{session_id}/{preview_id}`
- Confirmar: `POST /api/v1/upload/confirm/{session_id}`
- Cancelar: `DELETE /api/v1/upload/preview/{session_id}`

---

## ✏️ EDIÇÃO MANUAL (OPCIONAL)

**Endpoint:** `PATCH /api/v1/upload/preview/{session_id}/{preview_id}`

**Parâmetros:**
- `grupo`: Novo grupo (opcional)
- `subgrupo`: Novo subgrupo (opcional)
- `excluir`: 1 para marcar exclusão (opcional)

### Leitura de Tabelas

**base_grupos_config (READ):**
```sql
SELECT tipo_gasto_padrao, categoria_geral
FROM base_grupos_config
WHERE user_id = :user_id
  AND nome_grupo = :grupo;
```

**base_marcacoes (READ):**
```sql
SELECT GRUPO FROM base_marcacoes
WHERE user_id = :user_id
  AND SUBGRUPO = :subgrupo;
```

### Atualização

**preview_transacoes (UPDATE):**
```sql
UPDATE preview_transacoes
SET GRUPO = :grupo,
    SUBGRUPO = :subgrupo,
    TipoGasto = :tipo_gasto,
    CategoriaGeral = :categoria_geral,
    origem_classificacao = 'manual',
    excluir = :excluir,
    updated_at = CURRENT_TIMESTAMP
WHERE id = :preview_id
  AND session_id = :session_id
  AND user_id = :user_id;
```

**Resultado:**
- ✅ Classificação atualizada
- ✅ `origem_classificacao = 'manual'`
- ✅ Ou marcado para exclusão (`excluir=1`)

---

## ✅ CONFIRM: POST /api/v1/upload/confirm/{session_id}

**Quando:** Usuário clica em "Confirmar Upload" no front-end

**Objetivo:** Mover transações de `preview_transacoes` para `journal_entries`

### Fase 5.1: Filtrar Transações Válidas

**preview_transacoes (READ):**
```sql
SELECT * FROM preview_transacoes
WHERE session_id = :session_id
  AND user_id = :user_id
  AND is_duplicate = FALSE  -- Filtrar duplicatas
  AND excluir = 0;           -- Filtrar marcadas para exclusão
```

**Resultado:**
- ✅ Apenas transações válidas (não-duplicadas, não-excluídas)
- ✅ Exemplo: 150 total → 120 válidas (15 duplicatas + 15 excluídas)

---

### Fase 5.2: Inserir em journal_entries

**journal_entries (INSERT batch):**
```sql
INSERT INTO journal_entries (
    user_id, Data, Estabelecimento, EstabelecimentoBase, Valor, ValorPositivo,
    MesFatura, arquivo_origem, banco_origem, NomeCartao,
    IdTransacao, IdParcela, parcela_atual, TotalParcelas,
    GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral, origem_classificacao,
    tipodocumento, TipoTransacao, Ano, Mes,
    session_id, upload_history_id, created_at
) VALUES
    (...),  -- Transação 1
    (...),  -- Transação 2
    (...);  -- Transação N
```

**Dados copiados:**
- ✅ TODOS os campos do preview
- ✅ `session_id` - rastreamento
- ✅ `upload_history_id` - rastreamento

**🔄 Exemplo:**
```json
{
  "id": 5432,
  "user_id": 1,
  "Data": "15/01/2026",
  "Estabelecimento": "IFOOD",
  "EstabelecimentoBase": "IFOOD",
  "Valor": -35.90,
  "ValorPositivo": 35.90,
  "GRUPO": "Alimentação",
  "SUBGRUPO": "Delivery",
  "TipoGasto": "Variável",
  "CategoriaGeral": "Despesa",
  "IdTransacao": "abc123...",
  "origem_classificacao": "regras_genericas",
  "session_id": "session_20260212_103000_1",
  "upload_history_id": 42
}
```

**Resultado:**
- ✅ 120 transações criadas em `journal_entries`

---

### Fase 5.3: Atualizar upload_history

**upload_history (UPDATE):**
```sql
UPDATE upload_history
SET status = 'success',
    transacoes_importadas = :transacoes_criadas,
    transacoes_duplicadas = :total_duplicatas,
    data_confirmacao = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE id = :history_id;
```

**Resultado:**
- ✅ `status = 'success'`
- ✅ `transacoes_importadas = 120`
- ✅ `transacoes_duplicadas = 15`
- ✅ `data_confirmacao` registrada

---

## 🔄 FASE 5: UPDATE BASE_PARCELAS (APÓS CONFIRM)

**Quando:** Automático **APÓS** inserir em `journal_entries`

**Objetivo:** Atualizar tabela de parcelas com novas transações

### 5.1. Buscar Parcelas das Transações Importadas

**journal_entries (READ):**
```sql
SELECT 
    IdParcela, IdTransacao, Data, EstabelecimentoBase, Valor,
    parcela_atual, TotalParcelas, SUBGRUPO
FROM journal_entries
WHERE upload_history_id = :history_id
  AND TotalParcelas > 1;
```

**Filtro:** Apenas transações parceladas (`TotalParcelas > 1`)

---

### 5.2. Verificar se Parcela Já Existe

**base_parcelas (READ):**
```sql
SELECT * FROM base_parcelas
WHERE user_id = :user_id
  AND IdParcela = :id_parcela;
```

**Se não existe:**
- ✅ Criar nova parcela

**Se existe:**
- ✅ Atualizar parcela (incrementar contador)

---

### 5.3. Inserir/Atualizar base_parcelas

**base_parcelas (UPSERT):**
```sql
-- Se nova parcela:
INSERT INTO base_parcelas (
    user_id, IdParcela, IdTransacao, Data, Estabelecimento,
    Valor, parcela_atual, total_parcelas, SUBGRUPO,
    status, created_at, updated_at
) VALUES (
    :user_id, :id_parcela, :id_transacao, :data, :estabelecimento,
    :valor, :parcela_atual, :total_parcelas, :subgrupo,
    'ativa', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Se já existe:
UPDATE base_parcelas
SET parcelas_importadas = parcelas_importadas + 1,
    ultima_atualizacao = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE user_id = :user_id
  AND IdParcela = :id_parcela;

-- Se todas as parcelas foram importadas:
UPDATE base_parcelas
SET status = 'finalizada',
    data_finalizacao = CURRENT_TIMESTAMP
WHERE IdTransacao = :id_transacao
  AND parcelas_importadas = total_parcelas;
```

**🔄 Exemplo:**
```json
{
  "id": 234,
  "user_id": 1,
  "IdParcela": "def456...",
  "IdTransacao": "abc123...",
  "Estabelecimento": "NETFLIX",
  "Valor": -49.90,
  "parcela_atual": 1,
  "total_parcelas": 12,
  "parcelas_importadas": 1,
  "status": "ativa"
}

// Após importar 12/12:
{
  "parcelas_importadas": 12,
  "status": "finalizada",
  "data_finalizacao": "2026-12-15T10:30:00"
}
```

**Resultado:**
- ✅ Parcelas novas criadas
- ✅ Parcelas existentes atualizadas
- ✅ Parcelas finalizadas marcadas

**⚠️ Nota:** Se esta fase falhar, o confirm continua (não bloqueia). Apenas gera warning no log.

---

### 5.4. Limpar preview_transacoes

**preview_transacoes (DELETE):**
```sql
DELETE FROM preview_transacoes
WHERE session_id = :session_id
  AND user_id = :user_id;
```

**Resultado:**
- ✅ Preview limpo (liberado para novo upload)

---

## 📊 Response do POST /api/v1/upload/confirm

**JSON retornado:**
```json
{
  "success": true,
  "sessionId": "session_20260212_103000_1",
  "transacoesCriadas": 120,
  "total": 120
}
```

**Logs gerados:**
```
✅ 120 transações salvas no journal_entries
📝 Histórico atualizado: 120 importadas, 15 duplicadas
🔄 Fase 5: Atualização de Base Parcelas
  ✅ Parcelas processadas: 35 | Atualizadas: 10 | Novas: 25 | Finalizadas: 3
🗑️  150 registros de preview removidos
```

---

## 🗑️ CANCELAR: DELETE /api/v1/upload/preview/{session_id}

**Quando:** Usuário clica em "Cancelar" no front-end

### Atualizar Histórico

**upload_history (UPDATE):**
```sql
UPDATE upload_history
SET status = 'cancelled',
    updated_at = CURRENT_TIMESTAMP
WHERE session_id = :session_id
  AND user_id = :user_id
  AND status = 'processing';
```

### Deletar Preview

**preview_transacoes (DELETE):**
```sql
DELETE FROM preview_transacoes
WHERE session_id = :session_id
  AND user_id = :user_id;
```

**Response:**
```json
{
  "success": true,
  "sessionId": "session_20260212_103000_1",
  "deletedCount": 150
}
```

---

## 📊 Resumo: Ordem de Atualização das Bases

| Momento | Fase | Tabela | Operação | Quantidade |
|---------|------|--------|----------|------------|
| **ANTES Preview** | Fase 0 | base_padroes | UPDATE/INSERT | ~50 padrões |
| **Preview - Início** | - | preview_transacoes | DELETE | Preview anterior |
| **Preview - Início** | - | upload_history | INSERT | 1 registro |
| **Preview - Fase 1** | Raw | preview_transacoes | INSERT | N transações |
| **Preview - Fase 1** | Raw | upload_history | UPDATE | total_registros |
| **Preview - Fase 2** | Marking | preview_transacoes | UPDATE | IDs gerados |
| **Preview - Fase 3** | Classification | preview_transacoes | UPDATE | GRUPO/SUBGRUPO |
| **Preview - Fase 3** | Classification | upload_history | UPDATE | stats |
| **Preview - Fase 4** | Dedup | preview_transacoes | UPDATE | Duplicatas marcadas |
| **Edição (opcional)** | Manual | preview_transacoes | UPDATE | 1 por vez |
| **Confirm - Início** | - | journal_entries | INSERT | N válidas |
| **Confirm - Meio** | - | upload_history | UPDATE | status='success' |
| **Confirm - Fase 5** | Parcelas | base_parcelas | UPDATE/INSERT | M parcelas |
| **Confirm - Fase 6** | ⚠️ TODO | base_grupos_config | INSERT | Novos grupos |
| **Confirm - Fase 6** | ⚠️ TODO | base_marcacoes | INSERT | Novos SUBGRUPOS |
| **Confirm - Fase 6** | ⚠️ TODO | base_tipos_gasto | INSERT | Novos tipos |
| **Confirm - Fim** | - | preview_transacoes | DELETE | Preview limpo |

**Total de tabelas afetadas:** 9 (7 implementadas + 2 TODO)  
**Total de fases:** 7 (0 a 6, sendo Fase 6 não implementada)  
**Tempo médio atual:** ~2-5 segundos para 150 transações  
**Tempo estimado com Fase 6:** ~3-6 segundos (+1s para sincronização)

---

## 🎯 Checklist de Validação

Para cada upload, validar:

**Após Preview:**
- [ ] `upload_history`: 1 registro com `status='processing'`
- [ ] `preview_transacoes`: N transações com IDs gerados
- [ ] `preview_transacoes`: ~70% classificadas
- [ ] `base_padroes`: Padrões atualizados

**Após Confirm:**
- [ ] `journal_entries`: N transações inseridas
- [ ] `upload_history`: `status='success'`, contadores corretos
- [ ] `base_parcelas`: Parcelas atualizadas
- [ ] `preview_transacoes`: Vazio (limpo)

---
---

## 🚨 FASE 6: SINCRONIZAR BASES (TODO - NÃO IMPLEMENTADO)

**Status:** ⚠️ **NÃO IMPLEMENTADO** - Melhoria necessária

**Quando:** **APÓS** Fase 5 (update base_parcelas)

**Objetivo:** Sincronizar bases de configuração com novos grupos/subgrupos/tipos usados no upload

### 6.1. Problema Atual

**Cenário:**
1. Usuário edita transação no preview
2. Escolhe **GRUPO novo**: "Lazer" (não existe em `base_grupos_config`)
3. Escolhe **SUBGRUPO novo**: "Cinema" (não existe em `base_marcacoes`)
4. Confirma upload

**Resultado atual:**
- ❌ Transação salva em `journal_entries` com GRUPO="Lazer", SUBGRUPO="Cinema"
- ❌ `base_grupos_config` NÃO tem registro de "Lazer"
- ❌ `base_marcacoes` NÃO tem mapeamento "Lazer" → "Cinema"
- ❌ Próximas classificações não reconhecem "Cinema" como parte de "Lazer"
- ❌ Telas de configuração não mostram "Lazer" nas opções

---

### 6.2. Solução Proposta - UX com Botão "+"

**✅ ABORDAGEM RECOMENDADA:** Modal de criação explícita (melhor UX)

#### 6.2.1. Interface (Frontend)

**Tela de edição de transação no preview:**

```tsx
// Componente EditTransactionModal
<div className="form-group">
  <label>Grupo</label>
  <div className="flex gap-2">
    <Select 
      value={grupo} 
      onChange={setGrupo}
      options={gruposExistentes}
    />
    <Button 
      variant="outline" 
      size="icon"
      onClick={() => setShowModalNovoGrupo(true)}
    >
      <PlusIcon />
    </Button>
  </div>
</div>

<div className="form-group">
  <label>Subgrupo</label>
  <div className="flex gap-2">
    <Select 
      value={subgrupo} 
      onChange={setSubgrupo}
      options={subgruposFiltrados}  // Filtrado por grupo
    />
    <Button 
      variant="outline" 
      size="icon"
      onClick={() => setShowModalNovoSubgrupo(true)}
    >
      <PlusIcon />
    </Button>
  </div>
</div>
```

---

#### 6.2.2. Modal: Criar Novo SUBGRUPO

**Fluxo:**
1. Usuário clica no "+" ao lado do dropdown de Subgrupo
2. Modal abre com:
   - **GRUPO:** Dropdown com grupos existentes + botão "+" (aninhado)
   - **SUBGRUPO:** Input de texto (obrigatório)

**Exemplo de UI:**
```tsx
<Dialog open={showModalNovoSubgrupo}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Criar Novo Subgrupo</DialogTitle>
    </DialogHeader>
    
    <div className="space-y-4">
      <div className="form-group">
        <label>Grupo *</label>
        <div className="flex gap-2">
          <Select 
            value={novoSubGrupo.grupo}
            onChange={(val) => setNovoSubGrupo({...novoSubGrupo, grupo: val})}
            options={gruposExistentes}
            placeholder="Selecione o grupo"
          />
          <Button 
            variant="outline" 
            size="icon"
            onClick={() => setShowModalNovoGrupo(true)}
            title="Criar novo grupo"
          >
            <PlusIcon />
          </Button>
        </div>
      </div>
      
      <div className="form-group">
        <label>Nome do Subgrupo *</label>
        <Input 
          value={novoSubGrupo.nome}
          onChange={(e) => setNovoSubGrupo({...novoSubGrupo, nome: e.target.value})}
          placeholder="Ex: Cinema, Restaurante, etc"
        />
      </div>
      
      <div className="text-sm text-muted-foreground">
        Este subgrupo será adicionado ao grupo "{novoSubGrupo.grupo}"
      </div>
    </div>
    
    <DialogFooter>
      <Button variant="outline" onClick={() => setShowModalNovoSubgrupo(false)}>
        Cancelar
      </Button>
      <Button onClick={handleCriarSubgrupo}>
        Criar Subgrupo
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

---

#### 6.2.3. Modal: Criar Novo GRUPO

**Fluxo:**
1. Usuário clica no "+" ao lado do dropdown de Grupo
2. Modal abre com:
   - **GRUPO:** Input de texto (obrigatório)
   - **SUBGRUPO:** Input de texto (obrigatório - primeiro subgrupo)
   - **Tipo de Gasto:** Dropdown (Fixo, Variável, Investimento)
   - **Categoria Geral:** Dropdown (Receita, Despesa)

**Exemplo de UI:**
```tsx
<Dialog open={showModalNovoGrupo}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Criar Novo Grupo</DialogTitle>
    </DialogHeader>
    
    <div className="space-y-4">
      <div className="form-group">
        <label>Nome do Grupo *</label>
        <Input 
          value={novoGrupo.nome}
          onChange={(e) => setNovoGrupo({...novoGrupo, nome: e.target.value})}
          placeholder="Ex: Lazer, Educação, etc"
        />
      </div>
      
      <div className="form-group">
        <label>Primeiro Subgrupo *</label>
        <Input 
          value={novoGrupo.primeiroSubgrupo}
          onChange={(e) => setNovoGrupo({...novoGrupo, primeiroSubgrupo: e.target.value})}
          placeholder="Ex: Cinema, Cursos, etc"
        />
        <p className="text-xs text-muted-foreground mt-1">
          Você pode adicionar mais subgrupos depois
        </p>
      </div>
      
      <div className="form-group">
        <label>Tipo de Gasto *</label>
        <Select 
          value={novoGrupo.tipoGasto}
          onChange={(val) => setNovoGrupo({...novoGrupo, tipoGasto: val})}
          options={[
            { value: 'Fixo', label: 'Fixo' },
            { value: 'Variável', label: 'Variável' },
            { value: 'Investimento', label: 'Investimento' }
          ]}
        />
      </div>
      
      <div className="form-group">
        <label>Categoria Geral *</label>
        <Select 
          value={novoGrupo.categoriaGeral}
          onChange={(val) => setNovoGrupo({...novoGrupo, categoriaGeral: val})}
          options={[
            { value: 'Receita', label: 'Receita' },
            { value: 'Despesa', label: 'Despesa' }
          ]}
        />
      </div>
    </div>
    
    <DialogFooter>
      <Button variant="outline" onClick={() => setShowModalNovoGrupo(false)}>
        Cancelar
      </Button>
      <Button onClick={handleCriarGrupo}>
        Criar Grupo
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

---

#### 6.2.4. API: Criar Novo SUBGRUPO

**Endpoint:** `POST /api/v1/upload/classification/subgrupo`

**Request:**
```json
{
  "grupo": "Alimentação",
  "subgrupo": "Cafeteria"
}
```

**Backend:**
```python
@router.post("/classification/subgrupo")
def criar_subgrupo(
    data: CriarSubgrupoSchema,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Validar se grupo existe
    grupo_exists = db.query(BaseGruposConfig).filter(
        BaseGruposConfig.user_id == user_id,
        BaseGruposConfig.nome_grupo == data.grupo
    ).first()
    
    if not grupo_exists:
        raise HTTPException(400, f"Grupo '{data.grupo}' não existe. Crie o grupo primeiro.")
    
    # Validar se subgrupo já existe
    subgrupo_exists = db.query(BaseMarcacoes).filter(
        BaseMarcacoes.user_id == user_id,
        BaseMarcacoes.SUBGRUPO == data.subgrupo,
        BaseMarcacoes.GRUPO == data.grupo
    ).first()
    
    if subgrupo_exists:
        raise HTTPException(400, f"Subgrupo '{data.subgrupo}' já existe no grupo '{data.grupo}'")
    
    # Criar mapeamento
    nova_marcacao = BaseMarcacoes(
        user_id=user_id,
        GRUPO=data.grupo,
        SUBGRUPO=data.subgrupo,
        origem="manual_criacao",
        created_at=datetime.now()
    )
    db.add(nova_marcacao)
    db.commit()
    db.refresh(nova_marcacao)
    
    return {
        "success": True,
        "subgrupo": {
            "id": nova_marcacao.id,
            "grupo": nova_marcacao.GRUPO,
            "subgrupo": nova_marcacao.SUBGRUPO
        }
    }
```

**Response:**
```json
{
  "success": true,
  "subgrupo": {
    "id": 456,
    "grupo": "Alimentação",
    "subgrupo": "Cafeteria"
  }
}
```

---

#### 6.2.5. API: Criar Novo GRUPO (com primeiro subgrupo)

**Endpoint:** `POST /api/v1/upload/classification/grupo`

**Request:**
```json
{
  "grupo": "Lazer",
  "primeiro_subgrupo": "Cinema",
  "tipo_gasto": "Variável",
  "categoria_geral": "Despesa"
}
```

**Backend:**
```python
@router.post("/classification/grupo")
def criar_grupo(
    data: CriarGrupoSchema,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Validar se grupo já existe
    grupo_exists = db.query(BaseGruposConfig).filter(
        BaseGruposConfig.user_id == user_id,
        BaseGruposConfig.nome_grupo == data.grupo
    ).first()
    
    if grupo_exists:
        raise HTTPException(400, f"Grupo '{data.grupo}' já existe")
    
    # Criar grupo
    novo_grupo = BaseGruposConfig(
        user_id=user_id,
        nome_grupo=data.grupo,
        tipo_gasto_padrao=data.tipo_gasto,
        categoria_geral=data.categoria_geral,
        ativo=True,
        created_at=datetime.now()
    )
    db.add(novo_grupo)
    
    # Criar primeiro subgrupo
    primeira_marcacao = BaseMarcacoes(
        user_id=user_id,
        GRUPO=data.grupo,
        SUBGRUPO=data.primeiro_subgrupo,
        origem="manual_criacao",
        created_at=datetime.now()
    )
    db.add(primeira_marcacao)
    
    db.commit()
    db.refresh(novo_grupo)
    db.refresh(primeira_marcacao)
    
    return {
        "success": True,
        "grupo": {
            "id": novo_grupo.id,
            "nome": novo_grupo.nome_grupo,
            "tipo_gasto": novo_grupo.tipo_gasto_padrao,
            "categoria_geral": novo_grupo.categoria_geral
        },
        "subgrupo": {
            "id": primeira_marcacao.id,
            "subgrupo": primeira_marcacao.SUBGRUPO
        }
    }
```

**Response:**
```json
{
  "success": true,
  "grupo": {
    "id": 42,
    "nome": "Lazer",
    "tipo_gasto": "Variável",
    "categoria_geral": "Despesa"
  },
  "subgrupo": {
    "id": 456,
    "subgrupo": "Cinema"
  }
}
```

---

#### 6.2.6. Fluxo Completo no Frontend

**handleCriarSubgrupo:**
```typescript
const handleCriarSubgrupo = async () => {
  try {
    const response = await fetch('/api/v1/upload/classification/subgrupo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        grupo: novoSubGrupo.grupo,
        subgrupo: novoSubGrupo.nome
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Fechar modal
      setShowModalNovoSubgrupo(false);
      
      // PRÉ-PREENCHER no formulário principal
      setGrupo(data.subgrupo.grupo);
      setSubgrupo(data.subgrupo.subgrupo);
      
      // Atualizar lista de subgrupos
      await refetchSubgrupos();
      
      toast.success(`Subgrupo "${data.subgrupo.subgrupo}" criado com sucesso!`);
    }
  } catch (error) {
    toast.error("Erro ao criar subgrupo");
  }
}
```

**handleCriarGrupo:**
```typescript
const handleCriarGrupo = async () => {
  try {
    const response = await fetch('/api/v1/upload/classification/grupo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        grupo: novoGrupo.nome,
        primeiro_subgrupo: novoGrupo.primeiroSubgrupo,
        tipo_gasto: novoGrupo.tipoGasto,
        categoria_geral: novoGrupo.categoriaGeral
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Fechar modal de novo grupo
      setShowModalNovoGrupo(false);
      
      // Se foi chamado do modal de novo subgrupo, preencher lá
      if (showModalNovoSubgrupo) {
        setNovoSubGrupo({
          ...novoSubGrupo,
          grupo: data.grupo.nome
        });
      } else {
        // Senão, preencher no formulário principal
        setGrupo(data.grupo.nome);
        setSubgrupo(data.subgrupo.subgrupo);
      }
      
      // Atualizar listas
      await refetchGrupos();
      await refetchSubgrupos();
      
      toast.success(`Grupo "${data.grupo.nome}" criado com sucesso!`);
    }
  } catch (error) {
    toast.error("Erro ao criar grupo");
  }
}
```

---

### 6.3. Após CONFIRM (batch update)

**Objetivo:** Sincronizar TODAS as classificações usadas no upload

#### 6.3.1. Extrair Grupos/Subgrupos Únicos

**journal_entries (READ):**
```sql
SELECT DISTINCT GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral
FROM journal_entries
WHERE upload_history_id = :history_id
  AND GRUPO IS NOT NULL
  AND SUBGRUPO IS NOT NULL;
```

#### 6.3.2. Atualizar base_grupos_config

**Para cada GRUPO único:**
```python
for grupo_data in grupos_unicos:
    grupo_exists = db.query(BaseGruposConfig).filter(
        BaseGruposConfig.user_id == user_id,
        BaseGruposConfig.nome_grupo == grupo_data['GRUPO']
    ).first()
    
    if not grupo_exists:
        # Criar GRUPO
        novo_grupo = BaseGruposConfig(
            user_id=user_id,
            nome_grupo=grupo_data['GRUPO'],
            tipo_gasto_padrao=grupo_data['TipoGasto'],
            categoria_geral=grupo_data['CategoriaGeral'],
            ativo=True,
            created_at=datetime.now()
        )
        db.add(novo_grupo)

db.commit()
```

#### 6.3.3. Atualizar base_marcacoes

**Para cada GRUPO → SUBGRUPO único:**
```python
for marcacao in marcacoes_unicas:
    marcacao_exists = db.query(BaseMarcacoes).filter(
        BaseMarcacoes.user_id == user_id,
        BaseMarcacoes.SUBGRUPO == marcacao['SUBGRUPO'],
        BaseMarcacoes.GRUPO == marcacao['GRUPO']
    ).first()
    
    if not marcacao_exists:
        # Criar mapeamento
        nova_marcacao = BaseMarcacoes(
            user_id=user_id,
            GRUPO=marcacao['GRUPO'],
            SUBGRUPO=marcacao['SUBGRUPO'],
            origem="upload_sync",
            created_at=datetime.now()
        )
        db.add(nova_marcacao)

db.commit()
```

#### 6.3.4. Atualizar base_tipos_gasto (se novo)

**Para cada TipoGasto único:**
```python
for tipo in tipos_unicos:
    tipo_exists = db.query(BaseTiposGasto).filter(
        BaseTiposGasto.user_id == user_id,
        BaseTiposGasto.nome == tipo
    ).first()
    
    if not tipo_exists:
        novo_tipo = BaseTiposGasto(
            user_id=user_id,
            nome=tipo,
            ativo=True,
            created_at=datetime.now()
        )
        db.add(novo_tipo)

db.commit()
```

---

### 6.4. Logs Gerados (após implementação)

```
✅ 120 transações salvas no journal_entries
📝 Histórico atualizado: 120 importadas, 15 duplicadas
🔄 Fase 5: Atualização de Base Parcelas
  ✅ Parcelas processadas: 35 | Atualizadas: 10 | Novas: 25 | Finalizadas: 3
🔄 Fase 6: Sincronização de Bases
  ✅ Grupos novos criados: 2 (Lazer, Educação)
  ✅ Mapeamentos novos: 5 (Cinema, Teatro, Cursos, Livros, Material)
  ✅ Tipos novos: 0 (todos já existiam)
🗑️  150 registros de preview removidos
```

---

### 6.5. Benefícios da Abordagem com UI Explícita

**✅ Vantagens:**
1. **Controle total:** Usuário decide explicitamente quando criar grupo/subgrupo
2. **Validação imediata:** Erros mostrados no modal antes de salvar
3. **Campos completos:** Usuário preenche TipoGasto, CategoriaGeral no momento da criação
4. **UX intuitiva:** Botão "+" é padrão conhecido de interfaces modernas
5. **Sem surpresas:** Não cria grupos "por acidente" ao salvar transação
6. **Pré-preenchimento:** Após criar, já seleciona automaticamente no formulário
7. **Modal aninhado:** Pode criar grupo dentro do modal de criar subgrupo
8. **Telas sincronizadas:** Imediatamente disponível em todas as telas após criação

**🎯 Experiência do Usuário:**
```
1. Editando transação no preview
2. Precisa de novo subgrupo "Cafeteria" no grupo "Alimentação"
3. Clica no "+" ao lado do dropdown de Subgrupo
4. Modal abre → seleciona "Alimentação" → digita "Cafeteria"
5. Clica "Criar Subgrupo"
6. Modal fechcriar/modificar:**

**Backend:**
1. `app_dev/backend/app/domains/upload/router.py`
   - Adicionar `POST /classification/grupo` (criar grupo + primeiro subgrupo)
   - Adicionar `POST /classification/subgrupo` (criar subgrupo em grupo existente)

2. `app_dev/backend/app/domains/upload/schemas.py`
   - `CriarGrupoSchema` (grupo, primeiro_subgrupo, tipo_gasto, categoria_geral)
   - `CriarSubgrupoSchema` (grupo, subgrupo)

3. `app_dev/backend/app/domains/upload/service.py`
   - `criar_grupo()` - Inserir em base_grupos_config + base_marcacoes
   - `criar_subgrupo()` - Inserir em base_marcacoes com validações

**Frontend:**
1. `app_dev/frontend/src/features/upload/components/modals/`
   - `modal-novo-grupo.tsx` (formulário completo de criação)
   - `modal-novo-subgrupo.tsx` (formulário simplificado)

2. `app_dev/frontend/src/features/upload/components/edit-transaction-modal.tsx`
   - Adicionar botões "+" ao lado de dropdowns
   - Integrar modais aninhados
   - Lógica de pré-preenchimento após criação

**Tempo:** ~4-6 horas (2h backend + 3h frontend + 1h testes)  
**Complexidade:** Média-Alta (modais aninhados requerem atenção ao state)  
**Prioridade:** Alta (resolve problema real + melhora UX significativamente

---

### 6.6. Implementação Estimada

**Arquivos a modificar:**
1. `app_dev/backend/app/domains/upload/service.py`
   - Adicionar `_fase6_sync_bases()` após Fase 5
   - Adicionar validações em `edit_classification()` (PATCH endpoint)

2. `app_dev/backend/app/domains/upload/schemas.py`
   - Adicionar campo `novos_grupos_criados` no response

**Tempo:** ~2-3 horas  
**Complexidade:** Média  
**Prioridade:** Alta (resolve problema real de sincronização)

---

## 📚 Referências

- **Código backend:** `app_dev/backend/app/domains/upload/service.py`
- **Classificação:** `app_dev/backend/app/domains/upload/processors/classifier.py`
- **Marcação:** `app_dev/backend/app/domains/upload/processors/marker.py`
- **Regras genéricas:** [04_BASE_GENERICA.md](../04_base_generica/README.md)

---

**Criado em:** 12/02/2026  
**Atualizado:** 13/02/2026 - Adicionada Fase 6 (sincronização de bases)
**Atualizado:** Após cada mudança no pipeline de upload
