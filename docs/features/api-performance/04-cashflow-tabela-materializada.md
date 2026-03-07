# Proposta: Tabela Materializada `plano_cashflow_mes`

> Este é o problema de maior impacto isolado no app. O cashflow é computado dinamicamente com ~48-60 queries por requisição. Criar uma tabela materializada reduz isso para 1 query.

---

## Diagnóstico Atual

### Por que é lento

O endpoint `GET /plano/cashflow?ano=Y` entra em um loop de 12 meses e, para cada mês, faz:

1. `SELECT SUM(Valor) FROM journal_entries WHERE user_id=X AND MesFatura=YYYYMM AND CategoriaGeral='Receita'`
2. `SELECT SUM(Valor) FROM journal_entries WHERE user_id=X AND MesFatura=YYYYMM AND CategoriaGeral='Despesa'`
3. `SELECT SUM(valor_planejado) FROM budget_planning WHERE user_id=X AND mes_referencia='YYYY-MM' AND ativo=True`
4. `SELECT * FROM expectativas_mes WHERE user_id=X AND mes_referencia='YYYY-MM'`
5. Lógica Python: crescimento, reajuste, decisão `use_realizado`, cálculo de aporte

**Total: ~48-60 queries + lógica Python para cada ano consultado.**

### Por que `/cashflow/mes` não resolve

O endpoint de mês único (`GET /plano/cashflow/mes?ano=Y&mes=M`) chama internamente `get_cashflow(ano)` e filtra o resultado. Ou seja, **ainda computa os 12 meses** e descarta 11.

**Localização do problema:**
- `app_dev/backend/app/domains/plano/router.py` — linhas 241-269
- `app_dev/backend/app/domains/plano/service.py` — linhas 268-464

---

## Proposta de Solução

### Nova tabela: `plano_cashflow_mes`

```sql
CREATE TABLE plano_cashflow_mes (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ano             INTEGER NOT NULL,
    mes             INTEGER NOT NULL,  -- 1 a 12
    mes_referencia  VARCHAR(7) NOT NULL,  -- formato: 'YYYY-MM'

    -- Valores realizados (de journal_entries)
    renda_realizada             FLOAT,
    gastos_realizados           FLOAT,
    investimentos_realizados    FLOAT,

    -- Valores planejados (de budget_planning + expectativas)
    renda_esperada              FLOAT,
    gastos_recorrentes          FLOAT,
    extras_creditos             FLOAT,
    extras_debitos              FLOAT,

    -- Valores computados (resultado final da lógica de negócio)
    renda_usada                 FLOAT,
    total_gastos                FLOAT,
    aporte_planejado            FLOAT,
    aporte_usado                FLOAT,

    -- Flags
    use_realizado               BOOLEAN,
    status_mes                  VARCHAR(20),  -- 'ok', 'atencao', 'critico'

    -- Controle
    computed_at                 TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    invalidated                 BOOLEAN DEFAULT FALSE,

    UNIQUE(user_id, ano, mes)
);

CREATE INDEX idx_plano_cashflow_mes_user_ano ON plano_cashflow_mes(user_id, ano);
```

---

## Quando Invalidar o Cache

| Evento | Meses afetados | Ação |
|--------|---------------|------|
| Upload de extrato (novas transações) | Meses das transações inseridas | Recomputar meses afetados |
| Edição de transação | Mês da transação editada | Recomputar mês |
| Mudança em `budget_planning` | Mês do orçamento alterado | Recomputar mês |
| Criar/editar/excluir expectativa | Todos os meses futuros afetados | Recomputar a partir do mês da expectativa |
| Atualizar `user_financial_profile` (renda, crescimento%) | Ano todo (e futuros) | Recomputar ano inteiro |

---

## Estratégia de Implementação

### Opção A: Lazy recompute (recomendado para começar)

```python
async def get_cashflow_mes(user_id, ano, mes):
    # 1. Busca na tabela materializada
    cached = db.query(PlanoCashflowMes).filter_by(
        user_id=user_id, ano=ano, mes=mes, invalidated=False
    ).first()

    if cached and not is_stale(cached.computed_at):
        return cached

    # 2. Se não tem ou está stale, computa e salva
    computed = compute_cashflow_mes(user_id, ano, mes)
    upsert(PlanoCashflowMes, computed)
    return computed
```

### Opção B: Background task (ideal a longo prazo)

Celery/APScheduler que roda à meia-noite:
1. Para cada usuário ativo, recomputa os meses que tiveram eventos no dia.
2. Marca como válidos os demais meses sem alteração.

### Invalidação por evento (para ambas opções)

```python
# Após import de transações
def after_import_transactions(user_id, meses_afetados):
    db.query(PlanoCashflowMes).filter(
        PlanoCashflowMes.user_id == user_id,
        PlanoCashflowMes.mes_referencia.in_(meses_afetados)
    ).update({"invalidated": True})

# Após mudança no perfil financeiro
def after_update_profile(user_id, ano):
    db.query(PlanoCashflowMes).filter(
        PlanoCashflowMes.user_id == user_id,
        PlanoCashflowMes.ano >= ano
    ).update({"invalidated": True})
```

---

## Impacto Esperado

| Métrica | Atual | Com tabela materializada |
|---------|-------|--------------------------|
| Queries por requisição de cashflow anual | ~48-60 | 1 (SELECT por user_id + ano) |
| Queries por requisição de cashflow mensal | ~48-60 (computa 12) | 1 (SELECT por user_id + ano + mes) |
| Tempo de resposta estimado | 300-800ms | 20-50ms |
| Impacto no dashboard | Alto (1 das 11 chamadas) | Baixo |
| Impacto na tela de Plano | Muito alto | Baixo |

---

## Arquivos a Criar/Modificar

### Backend

| Arquivo | Ação |
|---------|------|
| `migrations/versions/XXXX_add_plano_cashflow_mes.py` | Nova migration |
| `app/domains/plano/models.py` | Adicionar model `PlanoCashflowMes` |
| `app/domains/plano/service.py` | Modificar `get_cashflow()` e `get_cashflow_mes()` para ler/escrever na tabela |
| `app/domains/plano/service.py` | Adicionar `invalidate_cashflow_cache(user_id, ...)` |
| `app/domains/transactions/service.py` | Chamar invalidação após import |
| `app/domains/budget/service.py` | Chamar invalidação após mudança em budget_planning |
| `app/domains/plano/service.py` | Chamar invalidação após mudança em expectativas ou perfil |

### Frontend

Nenhuma mudança necessária. O contrato dos endpoints se mantém.
