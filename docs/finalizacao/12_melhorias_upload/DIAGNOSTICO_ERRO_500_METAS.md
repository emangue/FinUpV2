# Diagnóstico: Erro 500 na Tela de Metas

**Data:** 16/02/2026  
**Endpoint afetado:** `GET /api/v1/budget/planning?mes_referencia=YYYY-MM`  
**Tela:** `/mobile/budget` (Metas)

---

## ✅ CAUSA RAIZ IDENTIFICADA E CORRIGIDA (16/02/2026)

**Erro real (logs do servidor):**
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) column budget_planning.cor does not exist
```

**Causa:** A coluna `cor` foi adicionada ao modelo `BudgetPlanning` e existe migration `a1b2c3d4e5f6_add_cor_to_budget_planning`, mas **a migration não havia sido executada em produção**.

**Correção aplicada:** Executadas migrations pendentes no servidor:
```bash
alembic upgrade head
# 599d728bc4da -> 1376b5bda14c (fix_base_marcacoes)
# 1376b5bda14c -> a1b2c3d4e5f6 (add_cor_to_budget_planning)
```

**Validação:** `base_grupos_config` existe e tem 22 registros. O problema era exclusivamente a coluna `cor` ausente.

---

## Resumo (análise inicial)

O endpoint `/budget/planning` retornava **500 Internal Server Error** para os meses Dez/2025, Jan/2026 e Fev/2026. O frontend trata o erro retornando lista vazia, exibindo "Nenhuma meta de gastos".

---

## Análise de Modularidade

### Endpoints que FUNCIONAM (mesma tela / contexto)

| Endpoint | Módulo | Status |
|----------|--------|--------|
| `GET /dashboard/budget-vs-actual?year=&month=` | Dashboard | ✅ OK |
| `useExpenseSources` (chama budget-vs-actual) | Dashboard | ✅ OK |

### Endpoint que FALHA

| Endpoint | Módulo | Status |
|----------|--------|--------|
| `GET /budget/planning?mes_referencia=` | Budget | ❌ 500 |

### Conclusão de modularidade

- **Dashboard** e **Budget** são módulos distintos.
- O Dashboard usa `DashboardRepository.get_budget_vs_actual()` que:
  - Usa `BudgetPlanning` + `JournalEntry` diretamente
  - **NÃO** usa `BaseGruposConfig`
- O Budget usa `BudgetService.get_budget_planning()` que:
  - Usa `BudgetPlanning` + `JournalEntry` + **`BaseGruposConfig`**
  - A tabela `base_grupos_config` é a principal diferença

**Hipótese:** O erro está na dependência exclusiva do Budget: **`BaseGruposConfig`** (tabela `base_grupos_config`).

---

## Fluxo do `get_budget_planning`

```
Router (budget/router.py:186)
  → BudgetService.get_budget_planning(user_id, mes_referencia)
    → 1. Query BudgetPlanning (budget_planning)
    → 2. Query BaseGruposConfig (base_grupos_config)  ← PONTO CRÍTICO
    → 3. Query JournalEntry (journal_entries) - grupos com gasto
    → 4. Para cada budget: _calcular_valor_realizado_grupo()
    → 5. Para grupos com gasto sem meta: adicionar ao resultado
```

---

## Causas prováveis (por ordem de probabilidade)

### 1. Tabela `base_grupos_config` ausente ou com schema diferente em produção

O `get_budget_planning` faz:

```python
grupos_rows = self.db.query(BaseGruposConfig.nome_grupo, BaseGruposConfig.categoria_geral).all()
```

Se a tabela não existir em PostgreSQL (produção), a query falha com erro de banco.

**Validação em produção:**
```sql
-- Verificar se a tabela existe
SELECT EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_name = 'base_grupos_config');

-- Verificar estrutura
\d base_grupos_config
```

### 2. Colunas `Ano` e `Mes` em `journal_entries` (PostgreSQL)

O Dashboard usa `JournalEntry.Ano` e `JournalEntry.Mes` em algumas queries. O Budget usa `JournalEntry.MesFatura`. Se houver inconsistência de dados (Ano/Mes NULL ou incorretos), o Dashboard pode funcionar em alguns cenários e o Budget em outros.

**Nota:** O `get_budget_planning` usa apenas `MesFatura`, então isso é menos provável.

### 3. Exceção não tratada no service

O `BudgetService.get_budget_planning` não tem `try/except`. Qualquer exceção (AttributeError, KeyError, etc.) propaga como 500.

### 4. Diferença SQLite (local) vs PostgreSQL (produção)

- Local: SQLite, case-insensitive em identificadores
- Produção: PostgreSQL, case-sensitive em identificadores entre aspas
- Colunas como `GRUPO`, `Valor`, `MesFatura` no modelo podem ter comportamento diferente

---

## O que foi alterado recentemente (impacto em metas)

Com base no DIAGNOSTICO_BASE_PARCELAS e no contexto:

| Área | Alteração | Impacto em Metas? |
|------|-----------|-------------------|
| Upload / base_parcelas | Marker, Classifier, Fase 5 | ❌ Não – Metas não usam base_parcelas |
| Dashboard | budget-vs-actual | ❌ Não – endpoint diferente |
| Budget | get_budget_planning usa BaseGruposConfig | ✅ Sim – única dependência extra |
| Grupos | base_grupos_config | ✅ Possível – se migrations não rodaram |

**Conclusão:** Nenhuma alteração recente no fluxo de upload deveria impactar a tela de metas. O problema parece estar na infraestrutura (tabela/schema) ou em uma exceção não mapeada.

---

## Próximos passos recomendados

### 1. Adicionar logging no backend (para capturar o erro real)

Envolver `get_budget_planning` em try/except e registrar a exceção:

```python
# Em budget/service.py - get_budget_planning
import logging
logger = logging.getLogger(__name__)

def get_budget_planning(self, user_id: int, mes_referencia: str) -> dict:
    try:
        # ... código atual ...
    except Exception as e:
        logger.exception("Erro em get_budget_planning: user_id=%s mes=%s", user_id, mes_referencia)
        raise
```

Depois, verificar os logs do servidor em produção ao reproduzir o erro.

### 2. Validar tabelas em produção

```bash
# No servidor de produção
psql $DATABASE_URL -c "\dt base_grupos_config"
psql $DATABASE_URL -c "\d base_grupos_config"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM base_grupos_config"
```

### 3. Testar endpoint localmente

```bash
cd app_dev/backend
source venv/bin/activate
# Com token válido
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/budget/planning?mes_referencia=2026-01"
```

### 4. Tornar BaseGruposConfig opcional (mitigação)

Se `base_grupos_config` estiver vazia ou inacessível, usar fallback:

```python
try:
    grupos_rows = self.db.query(BaseGruposConfig.nome_grupo, BaseGruposConfig.categoria_geral).all()
except Exception:
    grupos_rows = []
grupos_config = {nome: cat for nome, cat in grupos_rows}
```

---

## Referências de código

- `app_dev/backend/app/domains/budget/service.py` – `get_budget_planning` (linhas 107–185)
- `app_dev/backend/app/domains/budget/router.py` – rota GET `/budget/planning` (linhas 186–218)
- `app_dev/frontend/src/features/goals/services/goals-api.ts` – `fetchGoals` (linha 64)
- `app_dev/frontend/src/app/mobile/budget/page.tsx` – tela de metas
