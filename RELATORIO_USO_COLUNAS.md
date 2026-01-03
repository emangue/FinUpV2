# 🔍 RELATÓRIO DE USO - Colunas a Validar

**Data:** 03/01/2026  
**Objetivo:** Mapear uso de colunas antes de modificar/eliminar

---

## 1. `tipodocumento` - **✅ EM USO - NÃO ELIMINAR**

### Uso Crítico Identificado

#### **Deduplicador (`app/utils/deduplicator.py` linha 90)**
```python
elif 'Extrato' in tipodocumento and data and valor:
    # Checa Data + Valor (para extratos com variação de nome)
    # Aplica apenas para EXTRATOS (não para faturas)
```

**Função:** Distinguir lógica de duplicação entre Extrato vs Fatura
- **Extrato:** Usa Data+Valor para detectar duplicatas
- **Fatura:** Não usa essa lógica (tem lógica própria)

#### **Upload Routes (`app/blueprints/upload/routes.py`)**
- Linha 67, 76, 141, 150: Passa `tipodocumento` em metadados
- Linha 237: Usa para lógica de processamento

#### **Models (`app/models.py`)**
- Linha 143: Definição da coluna
- Comentário: "Extrato, Fatura Cartão de Crédito"

#### **Preprocessadores**
- `cartao_bb_ofx.py` linha 151, 277: Define como "Fatura Cartão de Crédito"

### Valores Atuais no Banco
- "Extrato": 129 registros (3.1%)
- NULL: 4.024 registros (96.9%)

### ⚠️ PROBLEMA IDENTIFICADO
**96.9% dos registros não têm `tipodocumento` preenchido!**

Isso significa que a lógica de deduplicação está **quebrada para a maioria das transações**.

### ✅ AÇÃO RECOMENDADA
1. **NÃO ELIMINAR** a coluna
2. **POPULAR valores históricos:**
   ```sql
   -- Popular baseado em origem
   UPDATE journal_entries SET tipodocumento = 'Extrato'
   WHERE origem IN ('XP', 'MP', 'Itaú Person', 'Itau Person', 'Santander', 'BTG')
     AND tipodocumento IS NULL;
   
   UPDATE journal_entries SET tipodocumento = 'Fatura'
   WHERE origem LIKE 'Fatura%' 
     AND tipodocumento IS NULL;
   
   UPDATE journal_entries SET tipodocumento = 'Cartão'
   WHERE origem IN ('Azul', 'Nubank')
     AND tipodocumento IS NULL;
   ```

3. **Tornar obrigatório** em novos uploads
4. **Atualizar processadores** para sempre preencher

---

## 2. `MarcacaoIA` - ✅ EM USO ATIVO

### Uso Identificado

#### **Auto Classifier (`app/blueprints/upload/classifiers/auto_classifier.py`)**
Valores definidos:
- `'Fatura Cartão'` (linha 74) - Detecta transações de fatura
- `'Base_Padroes'` (linha 219) - Classificado via base_padroes
- `'Journal Entries'` (linha 281) - Classificado via histórico
- `'Palavras-chave'` (linha 321) - Classificado por regex
- `'IdParcela'` (linha 402) - Vinculado a parcela
- `'Ignorar - Nome do Titular'` (linha 425) - Ignorado por ser nome
- `'Ignorar - Lista Admin'` (linha 452) - Ignorado por admin
- `'Não Encontrado'` (linha 494) - Não classificado

#### **Upload Routes (`app/blueprints/upload/routes.py`)**
- Linha 703: Define como `'Manual (Lote)'` quando usuário classifica em lote
- Linha 806: Salva valor no banco

#### **Processors**
- Fatura e Extrato inicializam como `None`

### Valores no Banco
- "Base_Padroes": 319 (7.7%)
- "Manual (Lote)": 92 (2.2%)
- "IdParcela": 88 (2.1%)
- "Palavras-chave": 7 (0.2%)
- "Fatura Cartão": 5 (0.1%)
- NULL: 3.639 (87.6%)

### Função
**Rastreabilidade:** Indica COMO a transação foi classificada (origem da classificação)

---

## 3. `forma_classificacao` - ✅ EM USO ATIVO

### Uso Identificado

#### **Dashboard Routes (`app/blueprints/dashboard/routes.py`)**
Linhas 733-736 e 824-829: **Lógica de atualização ao editar transação**

```python
# Se era automática mas foi editada → vira Semi-Automática
if forma_classificacao.startswith('Automática-'):
    forma_classificacao = 'Semi-Automática'

# Se não tinha classificação → vira Manual
elif not forma_classificacao or forma_classificacao == 'Não Classificada':
    forma_classificacao = 'Manual'
```

#### **Upload Routes (`app/blueprints/upload/routes.py`)**
- Linha 691: Lê valor atual para decidir nova forma
- Linha 705: Atualiza após classificação manual
- Linha 817: Salva no banco (default: 'Não Classificada')

### Valores Possíveis (definidos em models.py)
- "Automática-BasePadrao"
- "Automática-MarcacaoIA"
- "Semi-Automática"
- "Manual"
- "Não Classificada"

### Valores no Banco
- "Automática-BasePadrão": 98 (2.4%)
- "Semi-Automática": 21 (0.5%)
- "Manual": 10 (0.2%)
- "Automática-Histórico": 2 (0.0%)
- NULL: 4.022 (96.8%)

### Função
**Status da classificação:** Indica se foi automática, manual ou semi-automática

---

## 🔄 ANÁLISE DE MERGE: `MarcacaoIA` + `forma_classificacao`

### Diferenças Conceituais

| Aspecto | MarcacaoIA | forma_classificacao |
|---------|------------|---------------------|
| **Propósito** | ORIGEM da classificação | STATUS da classificação |
| **Valores** | Base_Padroes, IdParcela, Manual (Lote) | Automática, Semi-Automática, Manual |
| **Uso** | Rastreabilidade (QUEM classificou) | Lógica de edição (COMO foi classificado) |
| **Preenchimento** | 12.4% | 3.2% |

### ⚠️ CONCLUSÃO: **NÃO FAZER MERGE**

**Motivos:**
1. **Propósitos diferentes:**
   - `MarcacaoIA` = "Foi classificado por Base_Padroes"
   - `forma_classificacao` = "A classificação é Automática"
   
2. **Informações complementares, não redundantes:**
   - Uma transação pode ter `MarcacaoIA='Base_Padroes'` E `forma_classificacao='Semi-Automática'`
   - Exemplo: Foi classificada automaticamente mas depois editada

3. **Lógica de edição depende de `forma_classificacao`:**
   - Dashboard usa para decidir se mantém automática ou vira semi/manual
   - Merge quebraria essa lógica

4. **Baixo preenchimento atual indica falta de uso, não redundância:**
   - Ambos estão subpovoados
   - Solução: Popular valores, não eliminar

---

## ✅ AÇÕES RECOMENDADAS

### 1. `tipodocumento` - **MANTER E POPULAR**
```sql
UPDATE journal_entries SET tipodocumento = 'Extrato'
WHERE origem IN ('XP', 'MP', 'Itaú Person', 'Itau Person', 'Santander', 'BTG', 
                 'Extrato - extrato_itau.xls', 'BTG - extrato_btg.xls')
  AND tipodocumento IS NULL;

UPDATE journal_entries SET tipodocumento = 'Fatura'
WHERE (origem LIKE 'Fatura%' OR origem LIKE '%fatura%')
  AND tipodocumento IS NULL;

UPDATE journal_entries SET tipodocumento = 'Cartão'
WHERE origem IN ('Azul', 'Nubank', 'Mercado Pago')
  AND tipodocumento IS NULL;
```

### 2. `MarcacaoIA` - **MANTER E POPULAR**
```sql
-- Popular histórico como "Manual" ou "Histórico"
UPDATE journal_entries SET MarcacaoIA = 'Histórico'
WHERE MarcacaoIA IS NULL 
  AND created_at < '2025-12-01';  -- Antes de implementar sistema de marcação
```

### 3. `forma_classificacao` - **MANTER E POPULAR**
```sql
-- Popular baseado em MarcacaoIA
UPDATE journal_entries SET forma_classificacao = 'Automática-BasePadrão'
WHERE MarcacaoIA = 'Base_Padroes' 
  AND forma_classificacao IS NULL;

UPDATE journal_entries SET forma_classificacao = 'Automática-Histórico'
WHERE MarcacaoIA = 'Journal Entries'
  AND forma_classificacao IS NULL;

UPDATE journal_entries SET forma_classificacao = 'Manual'
WHERE (MarcacaoIA LIKE 'Manual%' OR MarcacaoIA = 'Histórico')
  AND forma_classificacao IS NULL;

UPDATE journal_entries SET forma_classificacao = 'Não Classificada'
WHERE forma_classificacao IS NULL;
```

### 4. **NÃO FAZER MERGE** de `MarcacaoIA` + `forma_classificacao`
- São campos complementares, não redundantes
- Ambos têm uso ativo no código
- Merge quebraria lógica de edição

---

## 📊 RESUMO FINAL

| Coluna | Status | Ação |
|--------|--------|------|
| `tipodocumento` | ✅ Crítica (deduplicador) | MANTER + Popular valores |
| `MarcacaoIA` | ✅ Em uso (rastreabilidade) | MANTER + Popular valores |
| `forma_classificacao` | ✅ Em uso (lógica de edição) | MANTER + Popular valores |
| **MERGE MarcacaoIA+forma** | ❌ NÃO RECOMENDADO | Propósitos diferentes |

---

## 🎯 NOVA PROPOSTA: Popular em vez de Eliminar

Em vez de eliminar colunas, **POPULAR valores históricos** para torná-las úteis:

1. ✅ **tipodocumento:** Popular baseado em `origem` (Extrato, Fatura, Cartão)
2. ✅ **MarcacaoIA:** Popular histórico como "Histórico" ou "Manual"
3. ✅ **forma_classificacao:** Popular baseado em `MarcacaoIA`
4. ✅ **Tornar campos obrigatórios** em novos uploads
5. ✅ **Documentar valores válidos** para cada campo

**Resultado:** Colunas úteis e bem preenchidas, sem perder funcionalidade! 🚀
