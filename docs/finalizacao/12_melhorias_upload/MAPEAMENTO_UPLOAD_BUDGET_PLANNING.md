# Mapeamento: Upload → budget_planning

**Data:** 16/02/2026  
**Objetivo:** Documentar se e como o upload atualiza a base `budget_planning`, e validar suporte a Investimentos

---

## 1. Fluxo de confirmação de upload

```
POST /api/v1/upload/confirm/{session_id}
  → UploadService.confirm_upload()
    → Fase 5: _fase5_update_base_parcelas()
    → Fase 6: _fase6_sync_budget_planning()  ← AQUI
```

**Arquivo:** `app_dev/backend/app/domains/upload/service.py`  
**Linhas:** ~886-894 (chamada), 1381-1432 (implementação)

---

## 2. O que a Fase 6 faz hoje

| Aspecto | Status | Detalhe |
|--------|--------|---------|
| **Quando executa** | ✅ Sim | Após Fase 5, no `confirm_upload` |
| **CategoriaGeral** | ⚠️ Parcial | Apenas `Despesa` |
| **Investimentos** | ❌ Não | Não inclui `CategoriaGeral == 'Investimentos'` |

### Query atual (apenas Despesa)

```python
rows = self.db.query(
    JournalEntry.GRUPO,
    JournalEntry.MesFatura
).filter(
    JournalEntry.user_id == user_id,
    JournalEntry.CategoriaGeral == 'Despesa',  # ← SÓ DESPESA
    JournalEntry.IgnorarDashboard == 0,
    ...
).distinct().all()
```

### O que é criado

Para cada `(grupo, mes_fatura)` retornado, se não existir em `budget_planning`:
- `valor_planejado = 0`
- `valor_medio_3_meses = 0`
- `ativo = 1`

---

## 3. Lacuna: Investimentos

Grupos com `CategoriaGeral == 'Investimentos'` em `journal_entries` **não** entram na sincronização.

Consequências:
- Tela Metas: grupos de investimento sem meta não aparecem em `budget_planning`
- Tab Orçamento: `valor_realizado` de investimentos depende de `budget/planning`, que usa `budget_planning` + `grupos_com_investimento` (adicionado no budget service)
- Mesmo assim, se não houver upload recente, `budget_planning` pode estar vazio para investimentos

---

## 4. Correção aplicada

A `_fase6_sync_budget_planning` foi ajustada para incluir **Despesa** e **Investimentos**:

```python
# Despesa
rows_desp = query(CategoriaGeral == 'Despesa')
# Investimentos
rows_inv = query(CategoriaGeral == 'Investimentos')
# Processar ambos
```

---

## 5. Como validar se está funcionando

### 5.1 Verificar se Fase 6 roda no upload

1. Fazer um upload e confirmar.
2. Conferir logs: `"🔄 Fase 6: Sincronização Budget Planning"` e `"✅ Budget: N linhas criadas"`.

### 5.2 Verificar `budget_planning` após upload

```sql
SELECT user_id, grupo, mes_referencia, valor_planejado
FROM budget_planning
WHERE user_id = :seu_user_id
ORDER BY mes_referencia DESC, grupo
LIMIT 50;
```

### 5.3 Conferir grupos de investimento

```sql
-- Grupos com investimentos em journal_entries
SELECT je.GRUPO, je.MesFatura, SUM(je.Valor) as total
FROM journal_entries je
JOIN base_grupos_config bgc ON bgc.nome_grupo = je.GRUPO
WHERE je.user_id = :user_id
  AND je.CategoriaGeral = 'Investimentos'
  AND je.IgnorarDashboard = 0
GROUP BY je.GRUPO, je.MesFatura;

-- Verificar se estão em budget_planning
SELECT bp.grupo, bp.mes_referencia
FROM budget_planning bp
WHERE bp.user_id = :user_id
  AND bp.grupo IN (SELECT DISTINCT nome_grupo FROM base_grupos_config WHERE categoria_geral = 'Investimentos');
```

---

## 6. Script de backfill (dados existentes)

Para popular `budget_planning` com dados já existentes em `journal_entries` (sem precisar de novo upload):

```bash
cd app_dev/backend
python scripts/sync_budget_planning_from_journal.py [--user-id USER_ID]
```

Se `--user-id` não for informado, processa todos os usuários.

---

## 7. Resumo

| Item | Antes | Depois |
|------|-------|--------|
| Fase 6 no fluxo | ✅ Sim | ✅ Sim |
| Despesa | ✅ Sim | ✅ Sim |
| Investimentos | ❌ Não | ✅ Sim |
| Receita | N/A | N/A (receitas não usam budget_planning) |

---

## 8. Valores zerados – possíveis causas

Se receitas, despesas ou investimentos continuam zerados:

1. **journal_entries vazia** – Não há transações para o mês/usuário.
2. **budget_planning vazio** – Fase 6 não rodou ou não havia upload após a correção. Rodar o script de backfill.
3. **MesFatura inconsistente** – Transações sem `MesFatura` válido (formato YYYYMM).
4. **CategoriaGeral incorreta** – Grupos com `CategoriaGeral` diferente de Receita/Despesa/Investimentos.
