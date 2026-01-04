# 📊 RELATÓRIO DE AUDITORIA COMPLETA DO BANCO DE DADOS

**Data:** 03/01/2026  
**Banco:** `app/financas.db`  
**Total de Transações:** 4,153  

---

## 🎯 RESUMO EXECUTIVO

### Status Geral
- **Health Score:** 80/100 ⚠️
- **Data Quality Score:** 64.2/100 🔶
- **Status:** Dados com problemas moderados - correção recomendada

###Principais Problemas Identificados

#### 🚨 CRÍTICOS (Ação Imediata Necessária)
1. **1,220 transações (29.38%) com formato de Data incorreto** 
   - Formato encontrado: `'2024-01-01 00:00:00'` (DateTime string)
   - Formato esperado: `'01/01/2024'` (DD/MM/AAAA)
   - **Impacto:** Ordenação incorreta, queries complexas, impossível usar funções SQL de data

2. **7 transações com inconsistência Valor vs ValorPositivo**
   - Exemplo: ID 2358: Valor=0.16, ValorPositivo=-0.16 (ValorPositivo deveria ser sempre positivo)
   - **Impacto:** Cálculos de totais incorretos

#### ⚠️ IMPORTANTES (Correção Recomendada)
3. **363 transações (8.74%) sem TipoGasto**
   - 356 têm GRUPO/SUBGRUPO mas não TipoGasto
   - 7 completamente sem classificação
   - **Solução:** 348 podem ser preenchidos via base_marcacoes

4. **234 transações (5.63%) com inconsistência Data/Ano/DT_Fatura**
   - Exemplo: Data=2023, Ano=2024, MesAnoRef=202401
   - **Impacto:** Filtros por mês/ano podem estar incorretos

5. **55 transações (1.32%) com TipoGasto não padronizado**
   - 'Ajustável - Investimentos': 33 registros
   - 'Ignorar': 16 registros
   - 'Fatura': 5 registros
   - Estes valores não existem em base_marcacoes

#### ℹ️ INFO (Manutenção)
6. **169 padrões de classificação com baixa confiança** (< 3 ocorrências)
7. **101 contratos de parcelas** (22 ativos, 79 finalizados) - OK
8. **3 usuários** (3 ativos, 1 admin + 2 users) - OK

---

## 📋 DETALHAMENTO DOS PROBLEMAS

### 1. Formato de Data Incorreto (29.38% dos dados)

#### Problema
```sql
-- Formato ERRADO encontrado no banco:
Data = '2024-01-01 00:00:00'  -- String com timestamp

-- Formato CORRETO esperado:
Data = '01/01/2024'  -- String DD/MM/AAAA
```

#### Impacto
- **Ordenação alfabética incorreta:**
  ```sql
  SELECT * FROM journal_entries ORDER BY Data DESC;
  -- Retorna: '2024-01-01', '2023-12-31', '2023-11-30'
  -- Deveria: '31/12/2023', '30/11/2023', '01/01/2024'
  ```

- **Queries de range complexas demais:**
  ```sql
  -- Query atual (RUIM):
  WHERE substr(Data, 7, 4) || substr(Data, 4, 2) || substr(Data, 1, 2) >= '20240101'
  
  -- Query ideal (se Data fosse Date):
  WHERE Data >= '2024-01-01'
  ```

#### Solução Proposta
**Opção A: Migração de Dados (Recomendado)**
```sql
-- Script de correção
UPDATE journal_entries
SET Data = 
  substr(Data, 9, 2) || '/' ||  -- Dia
  substr(Data, 6, 2) || '/' ||  -- Mês
  substr(Data, 1, 4)            -- Ano
WHERE Data LIKE '____-__-__ __:__:__';
```

**Opção B: Migração de Schema (Ideal - Longo Prazo)**
- Alterar coluna `Data` de `String(10)` para `Date`
- Exige mudanças em todos os preprocessadores
- Requer versão MAJOR (breaking change)

---

### 2. Inconsistência Valor vs ValorPositivo

#### Problema
```python
# Casos encontrados:
ID 790:  Valor=0.02,  ValorPositivo=0.00   # ValorPositivo deveria ser 0.02
ID 2288: Valor=0.07,  ValorPositivo=0.20   # Valores completamente diferentes
ID 2358: Valor=0.16,  ValorPositivo=-0.16  # ValorPositivo está NEGATIVO!
```

#### Solução
```sql
-- Correção automática:
UPDATE journal_entries
SET ValorPositivo = ABS(Valor)
WHERE ABS(ABS(Valor) - ValorPositivo) > 0.01;
```

---

### 3. TipoGasto Missing (8.74% dos dados)

#### Análise Detalhada

**Grupo 1: Podem ser preenchidos via base_marcacoes (348 transações)**
| GRUPO | SUBGRUPO | QTD | EXISTE em base_marcacoes? |
|---|---|---|---|
| Investimentos | MP | 204 | ✅ Sim |
| Transferência Entre Contas | XP | 37 | ✅ Sim |
| Salário | Salário | 14 | ✅ Sim |
| Transferência entre contas | MP | 4 | ❌ **NÃO** |
| Casa | TV Sala | 1 | ❌ **NÃO** |

**Grupo 2: Não existem em base_marcacoes (8 transações)**
- `Transferência entre contas` + `MP` (4 transações)
- `Transferência entre contas` + `Itaú Person` (3 transações)
- `Casa` + `TV Sala` (1 transação)

**Nota:** Repare na inconsistência de capitalização:
- "Transferência Entre Contas" (existe)
- "Transferência entre contas" (não existe)

#### Solução SQL Automática
```sql
-- Backfill de TipoGasto via base_marcacoes
UPDATE journal_entries
SET TipoGasto = (
    SELECT TipoGasto 
    FROM base_marcacoes
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
```

#### Ações Manuais Necessárias
1. **Corrigir capitalização inconsistente:**
   ```sql
   UPDATE journal_entries
   SET GRUPO = 'Transferência Entre Contas'
   WHERE GRUPO = 'Transferência entre contas';
   ```

2. **Adicionar combinações faltantes em base_marcacoes:**
   ```sql
   INSERT INTO base_marcacoes (GRUPO, SUBGRUPO, TipoGasto)
   VALUES ('Casa', 'TV Sala', 'Fixo');
   ```

---

### 4. TipoGasto Não Padronizado (55 transações)

#### Valores Inválidos Encontrados
| Valor | Qtd | Status | Ação |
|---|---|---|---|
| 'Ajustável - Investimentos' | 33 | ❌ Não existe em base_marcacoes | Mudar para 'Investimentos - Ajustável' ou criar nova categoria |
| 'Ignorar' | 16 | ❌ Não é um TipoGasto válido | Usar campo `IgnorarDashboard` em vez disso |
| 'Fatura' | 5 | ⚠️ Existe mas é específico | Validar se uso está correto |
| 'Ajustado' | 1 | ❌ Typo de 'Ajustável' | Corrigir |

#### Solução
```sql
-- Corrigir valores inválidos
UPDATE journal_entries 
SET TipoGasto = 'Investimentos - Ajustável'
WHERE TipoGasto = 'Ajustável - Investimentos';

UPDATE journal_entries 
SET TipoGasto = NULL, IgnorarDashboard = 1
WHERE TipoGasto = 'Ignorar';

UPDATE journal_entries 
SET TipoGasto = 'Ajustável'
WHERE TipoGasto = 'Ajustado';
```

---

### 5. Inconsistência Data/Ano/DT_Fatura (234 transações)

#### Exemplos
```
ID 16:  Data='10/10/2023', Ano=2024, DT_Fatura='202401'
        ❌ Ano extraído da Data (2023) ≠ Ano armazenado (2024)

ID 23:  Data='10/10/2023', Ano=2024, DT_Fatura='202401'
        ❌ Diferença de 3 meses entre Data e DT_Fatura
```

#### Solução
```sql
-- Recalcular Ano e DT_Fatura a partir de Data
UPDATE journal_entries
SET 
  Ano = CAST(substr(Data, 7, 4) AS INTEGER),
  DT_Fatura = substr(Data, 7, 4) || substr(Data, 4, 2)
WHERE Data LIKE '__/__/____';
```

---

## 🛠️ PLANO DE AÇÃO RECOMENDADO

### Fase 1: Correções Críticas (Executar Imediatamente)

#### 1.1. Backup do Banco
```bash
cp app/financas.db app/financas.db.backup_$(date +%Y%m%d_%H%M%S)
```

#### 1.2. Corrigir Formato de Data (1,220 transações)
```sql
-- Script: scripts/fix_data_format.sql
UPDATE journal_entries
SET Data = 
  substr(Data, 9, 2) || '/' ||
  substr(Data, 6, 2) || '/' ||
  substr(Data, 1, 4)
WHERE Data LIKE '____-__-__ __:__:__';
```

#### 1.3. Corrigir ValorPositivo (7 transações)
```sql
UPDATE journal_entries
SET ValorPositivo = ABS(Valor)
WHERE ABS(ABS(Valor) - ValorPositivo) > 0.01;
```

#### 1.4. Recalcular Ano e DT_Fatura (234 transações)
```sql
UPDATE journal_entries
SET 
  Ano = CAST(substr(Data, 7, 4) AS INTEGER),
  DT_Fatura = substr(Data, 7, 4) || substr(Data, 4, 2)
WHERE Data LIKE '__/__/____';
```

### Fase 2: Preenchimento de TipoGasto (363 transações)

#### 2.1. Corrigir Capitalização
```sql
UPDATE journal_entries
SET GRUPO = 'Transferência Entre Contas'
WHERE GRUPO = 'Transferência entre contas';
```

#### 2.2. Backfill via base_marcacoes
```sql
UPDATE journal_entries
SET TipoGasto = (
    SELECT TipoGasto FROM base_marcacoes
    WHERE base_marcacoes.GRUPO = journal_entries.GRUPO
      AND base_marcacoes.SUBGRUPO = journal_entries.SUBGRUPO
)
WHERE (TipoGasto IS NULL OR TipoGasto = '')
  AND GRUPO IS NOT NULL AND SUBGRUPO IS NOT NULL;
```

#### 2.3. Adicionar Combinações Faltantes
```sql
INSERT INTO base_marcacoes (GRUPO, SUBGRUPO, TipoGasto)
VALUES ('Casa', 'TV Sala', 'Fixo');
```

#### 2.4. Corrigir Valores Inválidos
```sql
UPDATE journal_entries 
SET TipoGasto = 'Investimentos - Ajustável'
WHERE TipoGasto = 'Ajustável - Investimentos';

UPDATE journal_entries 
SET TipoGasto = NULL, IgnorarDashboard = 1
WHERE TipoGasto = 'Ignorar';
```

### Fase 3: Validação e Verificação

```bash
# Executar novamente as auditorias
python run_audits.py

# Verificar que erros foram corrigidos
# Novo Data Quality Score esperado: >90/100
```

---

## 📝 PREVENÇÃO DE PROBLEMAS FUTUROS

### 1. Adicionar Validações no Upload (routes.py)

Criar função de validação obrigatória ANTES de inserir no banco:

```python
# app/blueprints/upload/validators.py

import re
from datetime import datetime

def validate_transaction_data(trans_dict):
    """
    Valida transação ANTES de inserir no banco
    Retorna: (is_valid, error_message)
    """
    errors = []
    
    # 1. Validar Data (formato DD/MM/AAAA)
    data = trans_dict.get('Data')
    if not data:
        errors.append("Campo 'Data' é obrigatório")
    elif not re.match(r'^\d{2}/\d{2}/\d{4}$', data):
        errors.append(f"Data em formato inválido: '{data}' (esperado DD/MM/AAAA)")
    else:
        try:
            day, month, year = data.split('/')
            datetime(int(year), int(month), int(day))
        except ValueError:
            errors.append(f"Data inválida: '{data}'")
    
    # 2. Validar Valor e ValorPositivo
    valor = trans_dict.get('Valor')
    valor_pos = trans_dict.get('ValorPositivo')
    
    if valor is None:
        errors.append("Campo 'Valor' é obrigatório")
    if valor_pos is None:
        errors.append("Campo 'ValorPositivo' é obrigatório")
    elif abs(valor_pos) != abs(valor):
        errors.append(f"ValorPositivo ({valor_pos}) deve ser abs(Valor) ({abs(valor)})")
    elif valor_pos < 0:
        errors.append(f"ValorPositivo não pode ser negativo: {valor_pos}")
    
    # 3. Validar campos obrigatórios
    required = ['IdTransacao', 'Estabelecimento', 'origem']
    for field in required:
        if not trans_dict.get(field):
            errors.append(f"Campo '{field}' é obrigatório")
    
    # 4. Validar DT_Fatura (formato AAAAMM)
    dt_fatura = trans_dict.get('DT_Fatura')
    if dt_fatura and not re.match(r'^\d{6}$', dt_fatura):
        errors.append(f"DT_Fatura em formato inválido: '{dt_fatura}' (esperado AAAAMM)")
    
    # 5. Validar TipoGasto se GRUPO/SUBGRUPO estão preenchidos
    grupo = trans_dict.get('GRUPO')
    subgrupo = trans_dict.get('SUBGRUPO')
    tipogasto = trans_dict.get('TipoGasto')
    
    if grupo and subgrupo and not tipogasto:
        # Buscar em base_marcacoes
        from app.models import BaseMarcacao, get_db_session
        db = get_db_session()
        marcacao = db.query(BaseMarcacao).filter_by(GRUPO=grupo, SUBGRUPO=subgrupo).first()
        
        if marcacao:
            trans_dict['TipoGasto'] = marcacao.TipoGasto  # Auto-preencher
        else:
            errors.append(f"Combinação GRUPO='{grupo}' + SUBGRUPO='{subgrupo}' não existe em base_marcacoes")
    
    if errors:
        return False, '; '.join(errors)
    
    return True, None
```

**Integração em routes.py:**
```python
# app/blueprints/upload/routes.py (linha ~785)

from app.blueprints.upload.validators import validate_transaction_data

# Dentro do loop de salvamento:
for trans in transacoes_novas:
    # VALIDAR ANTES DE CRIAR ENTRY
    is_valid, error_msg = validate_transaction_data(trans)
    
    if not is_valid:
        flash(f"❌ Transação inválida (ID: {trans.get('IdTransacao')}): {error_msg}", 'error')
        continue  # Pula esta transação
    
    entry = JournalEntry(...)  # Resto do código
```

### 2. Adicionar Constraint no Banco

```sql
-- Garantir que ValorPositivo seja sempre positivo
ALTER TABLE journal_entries 
ADD CONSTRAINT check_valor_positivo 
CHECK (ValorPositivo >= 0);

-- Garantir formato de Data (básico)
ALTER TABLE journal_entries 
ADD CONSTRAINT check_data_format 
CHECK (Data LIKE '__/__/____');
```

### 3. Criar Job de Validação Periódica

```bash
# Adicionar ao crontab (rodar toda segunda 9h)
0 9 * * 1 /path/to/venv/bin/python /path/to/run_audits.py
```

---

## 📊 MÉTRICAS DE SUCESSO

### Antes da Correção
- Health Score: 80/100
- Data Quality Score: 64.2/100
- Erros Críticos: 1,227
- Avisos: 289

### Meta Após Correção
- Health Score: >95/100
- Data Quality Score: >90/100
- Erros Críticos: 0
- Avisos: <50

---

## 🔗 ARQUIVOS GERADOS

1. `database_health_report_20260103_113511.txt` - Relatório de saúde geral
2. `data_validation_report_20260103_113511.txt` - Validação de formatos
3. `tipogasto_analysis_20260103_113511.txt` - Análise de TipoGasto missing
4. `run_audits.py` - Script para executar todas as auditorias

---

## 📞 PRÓXIMOS PASSOS

1. ✅ **Revisar este relatório** e decidir quais correções executar
2. ⬜ **Fazer backup do banco** antes de qualquer alteração
3. ⬜ **Executar Fase 1** (correções críticas)
4. ⬜ **Validar** que correções foram aplicadas (rodar `run_audits.py` novamente)
5. ⬜ **Executar Fase 2** (preenchimento de TipoGasto)
6. ⬜ **Implementar validações** no upload para prevenir problemas futuros
7. ⬜ **Planejar migração** de Data para tipo Date (longo prazo)

---

**Relatório gerado por:** Sistema de Auditoria  
**Próxima auditoria:** Após aplicação das correções  
**Contato:** Revisar com equipe de desenvolvimento
