# 🔗 PROPOSTA DE MERGE - MarcacaoIA + forma_classificacao

**Data:** 03/01/2026  
**Objetivo:** Unificar informações de classificação em uma única coluna

---

## 🎯 CONCEITO

Criar coluna única `origem_classificacao` que contém:
- **Tipo:** Automática, Semi-Automática, Manual
- **Origem:** De onde veio a classificação automática
- **Lote:** Se foi marcação em lote

---

## 📊 ESTRUTURA DA NOVA COLUNA `origem_classificacao`

### Valores Possíveis (formato limpo)

#### **1. Automáticas**
- `Automática - Base Padrões` (classificado via base_marcacoes)
- `Automática - Histórico` (classificado via journal_entries antigos)
- `Automática - Parcela` (vinculado a IdParcela)
- `Automática - Palavras-chave` (regex/keywords)
- `Automática - Fatura` (detectado como pagamento de fatura)

#### **2. Semi-Automática**
- `Semi-Automática` (foi automática mas foi editada depois)

#### **3. Manuais**
- `Manual` (classificação manual individual)
- `Manual - Lote` (várias marcações manuais ao mesmo tempo)

#### **4. Especiais**
- `Ignorada` (ignorada por ser nome titular ou admin)
- `Não Classificada` (não foi classificada ainda)

---

## 🔄 MAPEAMENTO: Valores Antigos → Novos

### De `MarcacaoIA` → `origem_classificacao`

| MarcacaoIA (antigo) | forma_classificacao (antigo) | origem_classificacao (NOVO) |
|---------------------|------------------------------|----------------------------|
| `Base_Padroes` | `Automática-*` | `Automática - Base Padrões` |
| `Base_Padroes` | `Semi-Automática` | `Semi-Automática` |
| `Base_Padroes` | NULL/Manual | `Manual` (foi editada) |
| `Journal Entries` | `Automática-*` | `Automática - Histórico` |
| `IdParcela` | `Automática-*` | `Automática - Parcela` |
| `Palavras-chave` | `Automática-*` | `Automática - Palavras-chave` |
| `Fatura Cartão` | `Automática-*` | `Automática - Fatura` |
| `Manual (Lote)` | ANY | `Manual - Lote` |
| `Ignorar - *` | ANY | `Ignorada` |
| `Não Encontrado` | ANY | `Não Classificada` |
| `Histórico` | ANY | `Manual` |
| NULL | `Manual` | `Manual` |
| NULL | `Semi-Automática` | `Semi-Automática` |
| NULL | NULL | `Não Classificada` |

---

## 🛠️ SCRIPT DE MIGRAÇÃO

```sql
BEGIN TRANSACTION;

-- =========================================
-- FASE 1: CRIAR NOVA COLUNA
-- =========================================
ALTER TABLE journal_entries ADD COLUMN origem_classificacao VARCHAR(50);
CREATE INDEX idx_origem_classificacao ON journal_entries(origem_classificacao);

-- =========================================
-- FASE 2: POPULAR origem_classificacao
-- =========================================

-- 1. Automática - Base Padrões
UPDATE journal_entries 
SET origem_classificacao = 'Automática - Base Padrões'
WHERE MarcacaoIA = 'Base_Padroes' 
  AND (forma_classificacao IS NULL 
       OR forma_classificacao LIKE 'Automática%');

-- 2. Automática - Histórico
UPDATE journal_entries 
SET origem_classificacao = 'Automática - Histórico'
WHERE MarcacaoIA = 'Journal Entries'
  AND (forma_classificacao IS NULL 
       OR forma_classificacao LIKE 'Automática%');

-- 3. Automática - Parcela
UPDATE journal_entries 
SET origem_classificacao = 'Automática - Parcela'
WHERE MarcacaoIA = 'IdParcela'
  AND (forma_classificacao IS NULL 
       OR forma_classificacao LIKE 'Automática%');

-- 4. Automática - Palavras-chave
UPDATE journal_entries 
SET origem_classificacao = 'Automática - Palavras-chave'
WHERE MarcacaoIA = 'Palavras-chave'
  AND (forma_classificacao IS NULL 
       OR forma_classificacao LIKE 'Automática%');

-- 5. Automática - Fatura
UPDATE journal_entries 
SET origem_classificacao = 'Automática - Fatura'
WHERE MarcacaoIA = 'Fatura Cartão'
  AND (forma_classificacao IS NULL 
       OR forma_classificacao LIKE 'Automática%');

-- 6. Semi-Automática (foi automática mas editada)
UPDATE journal_entries 
SET origem_classificacao = 'Semi-Automática'
WHERE forma_classificacao = 'Semi-Automática'
  OR (MarcacaoIA IN ('Base_Padroes', 'Journal Entries', 'IdParcela', 'Palavras-chave')
      AND forma_classificacao = 'Manual');

-- 7. Manual - Lote
UPDATE journal_entries 
SET origem_classificacao = 'Manual - Lote'
WHERE MarcacaoIA = 'Manual (Lote)';

-- 8. Ignorada
UPDATE journal_entries 
SET origem_classificacao = 'Ignorada'
WHERE MarcacaoIA LIKE 'Ignorar%';

-- 9. Manual (histórico ou manual puro)
UPDATE journal_entries 
SET origem_classificacao = 'Manual'
WHERE (MarcacaoIA = 'Histórico' OR forma_classificacao = 'Manual')
  AND origem_classificacao IS NULL;

-- 10. Não Classificada (resto)
UPDATE journal_entries 
SET origem_classificacao = 'Não Classificada'
WHERE origem_classificacao IS NULL;

-- =========================================
-- FASE 3: ATUALIZAR CÓDIGO QUE USA AS COLUNAS ANTIGAS
-- =========================================
-- (Será feito após aprovação - requer mudanças em múltiplos arquivos)

-- =========================================
-- FASE 4: ELIMINAR COLUNAS ANTIGAS (APÓS TESTES)
-- =========================================
-- ALTER TABLE journal_entries DROP COLUMN MarcacaoIA;
-- ALTER TABLE journal_entries DROP COLUMN forma_classificacao;

COMMIT;
```

---

## 📝 LÓGICA DE USO NO CÓDIGO

### Dashboard - Ao editar transação

**ANTES:**
```python
if transacao.forma_classificacao.startswith('Automática-'):
    transacao.forma_classificacao = 'Semi-Automática'
```

**DEPOIS:**
```python
if transacao.origem_classificacao.startswith('Automática -'):
    transacao.origem_classificacao = 'Semi-Automática'
```

### Auto Classifier - Ao classificar automaticamente

**ANTES:**
```python
trans['MarcacaoIA'] = 'Base_Padroes'
trans['forma_classificacao'] = 'Automática-BasePadrão'
```

**DEPOIS:**
```python
trans['origem_classificacao'] = 'Automática - Base Padrões'
```

### Upload Routes - Classificação manual em lote

**ANTES:**
```python
transacoes[idx]['MarcacaoIA'] = 'Manual (Lote)'
transacoes[idx]['forma_classificacao'] = nova_forma
```

**DEPOIS:**
```python
transacoes[idx]['origem_classificacao'] = 'Manual - Lote'
```

---

## 🎯 VANTAGENS DO MERGE

### ✅ Simplicidade
- 1 coluna em vez de 2
- Valores auto-explicativos
- Fácil de entender e filtrar

### ✅ Completude
- Mantém TODA a informação (origem + status)
- Formato: `[Tipo] - [Origem]`
- Exemplo: `Automática - Base Padrões` = tipo + origem

### ✅ Manutenibilidade
- Menos código para atualizar
- Um único ponto de verdade
- Índice único

### ✅ Performance
- 1 índice em vez de 2
- Queries mais simples
- Menos JOINs/checks

---

## 📊 IMPACTO

### Distribuição Esperada (4.153 transações)

| origem_classificacao | Estimativa |
|---------------------|------------|
| `Automática - Base Padrões` | ~319 (7.7%) |
| `Manual - Lote` | ~92 (2.2%) |
| `Automática - Parcela` | ~88 (2.1%) |
| `Semi-Automática` | ~31 (0.7%) |
| `Manual` | ~10 (0.2%) |
| `Automática - Histórico` | ~2 (0.0%) |
| `Automática - Palavras-chave` | ~7 (0.2%) |
| `Automática - Fatura` | ~5 (0.1%) |
| `Ignorada` | ~2 (0.0%) |
| `Não Classificada` | ~3.597 (86.6%) |

**Nota:** 86.6% ainda não classificadas (valores históricos NULL)

---

## 🔄 ARQUIVOS QUE PRECISAM SER ATUALIZADOS

### 1. Models (`app/models.py`)
- Adicionar coluna `origem_classificacao`
- Remover `MarcacaoIA` e `forma_classificacao` (após testes)

### 2. Dashboard Routes (`app/blueprints/dashboard/routes.py`)
- Linha 733-736: Lógica de edição
- Linha 824-829: Lógica de edição
- Substituir `forma_classificacao` por `origem_classificacao`

### 3. Upload Routes (`app/blueprints/upload/routes.py`)
- Linha 691: Leitura de valor
- Linha 703: Define `Manual - Lote`
- Linha 705: Atualização
- Linha 806: Salva no banco
- Linha 817: Default value

### 4. Auto Classifier (`app/blueprints/upload/classifiers/auto_classifier.py`)
- Todas as linhas que definem `MarcacaoIA`
- Substituir por `origem_classificacao` com novos valores

### 5. Processors
- `fatura_cartao.py`: Inicializar com NULL ou 'Não Classificada'
- `extrato_conta.py`: Inicializar com NULL ou 'Não Classificada'

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

**FASE 1: PREPARAÇÃO**
- [ ] Backup completo do banco
- [ ] Criar branch git para mudanças
- [ ] Documentar valores antigos vs novos

**FASE 2: MIGRAÇÃO DE DADOS**
- [ ] Executar script SQL de criação e população
- [ ] Validar que todos registros foram migrados
- [ ] Conferir distribuição de valores

**FASE 3: ATUALIZAÇÃO DE CÓDIGO**
- [ ] Atualizar models.py
- [ ] Atualizar dashboard/routes.py
- [ ] Atualizar upload/routes.py
- [ ] Atualizar auto_classifier.py
- [ ] Atualizar processors

**FASE 4: TESTES**
- [ ] Testar edição de transação no dashboard
- [ ] Testar upload com classificação automática
- [ ] Testar classificação manual em lote
- [ ] Validar que lógica Semi-Automática funciona

**FASE 5: CLEANUP**
- [ ] Eliminar colunas antigas (`MarcacaoIA`, `forma_classificacao`)
- [ ] Remover código legacy
- [ ] Atualizar documentação

---

## 🚀 BENEFÍCIO FINAL

**De 2 colunas confusas para 1 coluna clara:**

```
ANTES:
├─ MarcacaoIA: "Base_Padroes"
└─ forma_classificacao: "Automática-BasePadrão"
   (Redundante e confuso)

DEPOIS:
└─ origem_classificacao: "Automática - Base Padrões"
   (Claro, conciso, completo)
```

---

**Aguardando aprovação para implementar!** 🚀
