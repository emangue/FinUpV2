# Plano de Implementação — Performance V2
# Microações e Exemplos de Código

> Guia passo-a-passo para implementar cada melhoria. Cada item tem contexto, microações numeradas e exemplos de código prontos para uso.
>
> **Este arquivo é o documento de referência completo.**
> Para implementar, use os sub-planos por sprint abaixo — cada um é autocontido e focado.

---

## Status de Implementação

> Última atualização: 2026-03-08

| Sprint | Status | Itens | Commit |
|--------|--------|-------|--------|
| **Sprint 1** | ✅ Concluído | A3, F3, F4, F5 | `32a40c07` |
| **Sprint 2** | ✅ Concluído | B4, F2, G1, G2, G3 | `e8468157` |
| **Sprint 3** | ✅ Concluído | I1, E1, F1, F6 | `e238dd7a` |
| **Fix drift ProjecaoChart** | ✅ Concluído | G1↓, G3↓, curva laranja | `c1495221` |
| **Sprint 4** | ⬜ Pendente | A2, B2 | — |
| **Sprint 5** | ⬜ Pendente | A1 | — |
| **Sprint 6** | ⬜ Pendente | B1, B3, D, C1 | — |

### Sprint 1 — Detalhes (✅ Concluído)

| Item | Arquivo(s) | Resultado |
|------|-----------|-----------|
| **A3** — Fix scroll do mês | `page.tsx`, `month-scroll-picker.tsx` | ✅ Picker não aparece no mês errado. Skeleton durante null. Lista centrada em `selectedMonth`. Scroll `instant` no mount. |
| **F3** — Prefetch OrcamentoTab adjacentes | `page.tsx` | ✅ `fetchIncomeSources`, `fetchExpenseSources`, `fetchOrcamentoInvestimentos` disparados para prev/next no effect de meses adjacentes. |
| **F4** — Prefetch lastMonthWithData patrimônio | `page.tsx` | ✅ `_lastMonthPatrimonioPromise` inicia no mount em paralelo com transactions. Cache via `_inflight` dedup no `fetchLastMonthWithData`. |
| **F5** — Fallback parcial sliding window | `dashboard-api.ts` | ✅ Já estava implementado corretamente (sliding window com `_pointCache`). Sem alterações necessárias. |

### Sprint 2 — Detalhes (✅ Concluído)

| Item | Arquivo(s) | Resultado |
|------|-----------|-----------|
| **B4** — `in-memory-cache.ts` | `core/utils/in-memory-cache.ts` (novo) | ✅ Criado com `getCached`, `setCached`, `getInFlight`, `setInFlight`, `invalidateCache`. |
| **B4** — Cache `use-banks.ts` | `features/banks/hooks/use-banks.ts` | ✅ Cache 5min. `invalidateCache('banks:')` em create/update/delete. |
| **B4** — Cache `use-categories.ts` | `features/categories/hooks/use-categories.ts` | ✅ Cache 5min. `invalidateCache('categories:')` em mutações. |
| **F2** — Cache PatrimonioTab | `features/investimentos/services/investimentos-api.ts` | ✅ Cache 5min em `getPatrimonioTimeline` e `getDistribuicaoPorTipo`. Troca de tab sem re-fetch. |
| **G2** — Cache Plano | `features/plano/api.ts` | ✅ Cache 2min em `getResumoPlano`, `getOrcamento`, `getCashflow`. Cache 5min em `getProjecao`, `getImpactoLongoPrazo`. |
| **G1** — Debounce slider ProjecaoChart | `features/plano/components/ProjecaoChart.tsx` | ✅ `sliderValue` (UI imediata) + `debouncedPct` (debounce 400ms). ⚠️ `projCache` e fetch ao backend pelo slider foram **removidos** no fix de drift (commit `c1495221`) — ver seção abaixo. |
| **G3** — Effects separados ProjecaoChart | `features/plano/components/ProjecaoChart.tsx` | ✅ Effect 1 `[ano]` → base+cashflow permanece. ⚠️ Effect 2 `[debouncedPct, ano]` → **removido**: curva laranja é agora 100% frontend, sem chamada ao backend. |

### Sprint 3 — Detalhes (✅ Concluído)

| Item | Arquivo(s) | Resultado |
|------|-----------|-----------|
| **I1** — Índices compostos `journal_entries` | `transactions/models.py` + migration `b52feac5cd7f` | ✅ 3 índices: `idx_je_user_mesfatura`, `idx_je_user_mesfatura_cat_valor`, `idx_je_user_ignorar_mesfatura`. Index Scan confirmado. 5–20× speedup. |
| **E1** — Fix projeção de economia | `plano/service.py` (`get_projecao` else branch) | ✅ Fórmula corrigida: `renda - gastos_rec*fator + creditos_extras - debitos_extras`. Slider reduz só recorrentes. |
| **F6** — Renomear campos portfolio_resumo | `investimentos/repository.py`, `dashboard/repository.py` | ✅ Novos nomes canônicos (`total_ativos`, `total_passivos`, `patrimonio_liquido`) + deprecated mantidos por backward-compat. |
| **F1** — chart-data: 12 queries → 1 | `dashboard/repository.py` (`get_chart_data`) | ✅ Single query `IN + GROUP BY`. Cold start: ~600ms → ~50ms. Shape idêntico. |

---

### Fix ProjecaoChart — Drift Estrutural (✅ Concluído · `c1495221`)

**Contexto:** Descoberto após Sprint 3. O sprint E1 corrigiu o backend (`get_projecao`), mas a curva laranja no frontend ainda usava o retorno do backend como base, introduzindo um drift estrutural nos meses realizados.

**Problema raiz:** Duas curvas acumulam grandezas completamente diferentes:

| Curva | Fórmula para meses realizados |
|-------|------------------------------|
| 🟢 Verde | `patrimônio + Σ(investimentos_realizados)` — portfólio real |
| 🟠 Laranja (antes do fix) | `Σ(renda_real − gastos_real − invest_real)` — fluxo de caixa |

O drift acumulado Jan+Fev inflava o offset da curva laranja, tornando o FY com economia incorreto (241k exibido vs. ~204k correto com slider 10%, gastos_rec = 22.300).

**Fix (`ProjecaoChart.tsx`):**
- Removido `useEffect` que chamava `getProjecao(debouncedPct)` (Effect 2 do G3)
- Removido `projCache` ref e `data` state (não há mais fetch pelo slider)
- `serieRealMaisEconomia` calculado 100% no frontend ancorado na curva verde:
  ```
  laranja[i] = verde[i] + Σ gastos_recorrentes[j] × (pct / 100)
               para j = (lastRealIdx + 1) .. i
  ```
- `ganhoEconomia` = soma direta de `gastos_recorrentes × %` nos meses futuros do cashflow (já carregado)

**Resultado verificado com slider 10%:**
- `ganhoPorMes`: 22.300 × 10% = **2.230/mês** ✅
- `ganhoEconomia`: 2.230 × 11 = **24.530 no ano** ✅
- `fyRealMaisEconomiaFinal`: 179.1k + 24.5k = **~203.6k** ✅

**Bônus:** Eliminado 1 fetch ao backend por posição do slider — slider mais fluido.

---

| Sprint | Arquivo | Itens | Escopo | Dep. |
|--------|---------|-------|--------|------|
| **Sprint 1** ✅ | [sprint-1-frontend-quick-wins.md](sprint-1-frontend-quick-wins.md) | A3, F3, F4, F5 | Frontend only | — |
| **Sprint 2** ✅ | [sprint-2-frontend-cache-layer.md](sprint-2-frontend-cache-layer.md) | B4, F2, G1, G2, G3 | Frontend only | — |
| **Sprint 3** | [sprint-3-backend-bugs-e-queries.md](sprint-3-backend-bugs-e-queries.md) | I1, E1, F1, F6 | Backend only | — |
| **Sprint 4** | [sprint-4-endpoints-agregados.md](sprint-4-endpoints-agregados.md) | A2, B2 | Full-stack | Sprint 2 (B4) |
| **Sprint 5** | [sprint-5-tabela-materializada-cashflow.md](sprint-5-tabela-materializada-cashflow.md) | A1 | Backend + migration | — |
| **Sprint 6** | [sprint-6-goals-budget-skills.md](sprint-6-goals-budget-skills.md) | B1, B3, D, C1 | Full-stack | Sprint 5 (A1) para B3 |

> Sprints 1, 2 e 3 são independentes entre si — podem correr em paralelo.

---

## Índice completo (referência)

### Grupo A — Alta prioridade
- ✅ [A3 — Fix scroll do mês](#a3--fix-scroll-do-mês) → Sprint 1
- ⬜ [A1 — Tabela materializada cashflow](#a1--tabela-materializada-cashflow) → Sprint 5
- ⬜ [A2 — Endpoint agregado dashboard](#a2--endpoint-agregado-dashboard) → Sprint 4

### Grupo E — Bugs de lógica
- ⬜ [E1 — Fix projeção de economia (tela Plano)](#e1--fix-projeção-de-economia-tela-plano) → Sprint 3

### Grupo F — Dashboard: melhorias
- ✅ [F2 — Cache em PatrimonioTab](#f2--cache-em-patrimoniotab) → Sprint 2
- ✅ [F3 — Prefetch OrcamentoTab em meses adjacentes](#f3--prefetch-orcamentotab-em-meses-adjacentes) → Sprint 1
- ✅ [F4 — Prefetch lastMonthWithData patrimônio](#f4--prefetch-lastmonthwithdata-patrimônio) → Sprint 1
- ✅ [F5 — Fallback parcial no sliding window N4a](#f5--fallback-parcial-no-sliding-window-n4a) → Sprint 1 (já estava implementado)
- ⬜ [F1 — chart-data: 12 queries → 1](#f1--chart-data-12-queries--1) → Sprint 3
- ⬜ [F6 — Renomear campos confusos em get_portfolio_resumo](#f6--renomear-campos-confusos-em-get_portfolio_resumo) → Sprint 3

### Grupo G — Plano: melhorias
- ✅ [G1 — Debounce no slider da ProjecaoChart](#g1--debounce-no-slider-da-projecaochart) → Sprint 2
- ✅ [G2 — Cache para endpoints do Plano](#g2--cache-para-endpoints-do-plano) → Sprint 2
- ✅ [G3 — Separar effect de base e slider na ProjecaoChart](#g3--separar-effect-de-base-e-slider-na-projecaochart) → Sprint 2

### Grupo B — Média prioridade
- ✅ [B4 — Cache nos módulos descobertos](#b4--cache-nos-módulos-descobertos) → Sprint 2
- ✅ B5 — Deduplicação global: **resolvido automaticamente pelo B4**
- ⬜ [B1 — Optimistic updates em Goals](#b1--optimistic-updates-em-goals) → Sprint 6
- ⬜ [B2 — Endpoint agregado investimentos](#b2--endpoint-agregado-investimentos) → Sprint 4
- ⬜ [B3 — Batch range update goals](#b3--batch-range-update-goals) → Sprint 6

### Grupo C — Baixa prioridade
- ⬜ [C1 — Cursor pagination em transações](#c1--cursor-pagination-em-transações) → Sprint 6

### Grupo D — Skills de desenvolvimento
- ⬜ [D — Skills de desenvolvimento](#d--skills-de-desenvolvimento) → Sprint 6

---

## A1 — Tabela materializada cashflow

**Problema:** `GET /plano/cashflow?ano=Y` faz 48-60 queries por requisição. O endpoint `/cashflow/mes` computa os 12 meses e descarta 11.
**Impacto:** 300-800ms → 20-50ms por request.
**Escopo:** Backend only. Frontend zero mudanças.

---

### Microação 1 — Criar o model SQLAlchemy

**Arquivo:** `app_dev/backend/app/domains/plano/models.py`

Adicionar ao final do arquivo, após os models existentes:

```python
class PlanoCashflowMes(Base):
    __tablename__ = "plano_cashflow_mes"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ano             = Column(Integer, nullable=False)
    mes             = Column(Integer, nullable=False)        # 1 a 12
    mes_referencia  = Column(String(7), nullable=False)     # 'YYYY-MM'

    # Realizados (de journal_entries)
    renda_realizada           = Column(Float, nullable=True)
    gastos_realizados         = Column(Float, nullable=True)
    investimentos_realizados  = Column(Float, nullable=True)

    # Planejados (de budget_planning + expectativas)
    renda_esperada     = Column(Float, nullable=True)
    gastos_recorrentes = Column(Float, nullable=True)
    extras_creditos    = Column(Float, nullable=True)
    extras_debitos     = Column(Float, nullable=True)

    # Computados (resultado final da lógica de negócio)
    renda_usada      = Column(Float, nullable=True)
    total_gastos     = Column(Float, nullable=True)
    aporte_planejado = Column(Float, nullable=True)
    aporte_usado     = Column(Float, nullable=True)

    # Flags
    use_realizado = Column(Boolean, nullable=True)
    status_mes    = Column(String(20), nullable=True)   # 'ok', 'atencao', 'critico'

    # Controle
    computed_at  = Column(DateTime(timezone=True), nullable=False, default=func.now())
    invalidated  = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "ano", "mes", name="uq_plano_cashflow_mes"),
        Index("idx_plano_cashflow_mes_user_ano", "user_id", "ano"),
    )
```

---

### Microação 2 — Gerar a migration Alembic

```bash
docker exec finup_backend_dev alembic revision --autogenerate -m "Add plano_cashflow_mes table"
```

Revisar o arquivo gerado em `migrations/versions/`. Verificar que o `upgrade()` contém a criação da tabela e os índices, e que o `downgrade()` faz `op.drop_table("plano_cashflow_mes")`.

---

### Microação 3 — Aplicar em dev e verificar

```bash
docker exec finup_backend_dev alembic upgrade head
docker exec finup_backend_dev python -c "
from app.core.database import engine
from sqlalchemy import inspect
print(inspect(engine).get_columns('plano_cashflow_mes'))
"
```

---

### Microação 4 — Criar função de invalidação no service

**Arquivo:** `app_dev/backend/app/domains/plano/service.py`

Adicionar função utilitária de invalidação. Essa função é chamada por outros domínios após mutações:

```python
def invalidate_cashflow_cache(
    db: Session,
    user_id: int,
    mes_referencia: list[str] | None = None,   # ex: ['2026-02', '2026-03']
    ano_partir: int | None = None,              # invalida ano_partir em diante
):
    """
    Invalida entradas da tabela materializada.

    Casos de uso:
    - mes_referencia=['2026-02']: invalida meses específicos (após editar transação)
    - ano_partir=2026: invalida o ano inteiro e futuros (após mudar perfil financeiro)
    - ambos None: invalida tudo do usuário (uso excepcional)
    """
    query = db.query(PlanoCashflowMes).filter(
        PlanoCashflowMes.user_id == user_id
    )

    if mes_referencia:
        query = query.filter(PlanoCashflowMes.mes_referencia.in_(mes_referencia))
    elif ano_partir:
        query = query.filter(PlanoCashflowMes.ano >= ano_partir)

    query.update({"invalidated": True}, synchronize_session=False)
    db.commit()
```

---

### Microação 5 — Modificar `get_cashflow_mes` para lazy recompute

**Arquivo:** `app_dev/backend/app/domains/plano/service.py`

Localizar a função atual e envolvê-la com a lógica de cache:

```python
CASHFLOW_MES_TTL_HOURS = 6   # recomputa se mais velho que 6h

def get_cashflow_mes_cached(
    db: Session,
    user_id: int,
    ano: int,
    mes: int,
) -> dict:
    from datetime import datetime, timezone, timedelta

    cached = db.query(PlanoCashflowMes).filter_by(
        user_id=user_id, ano=ano, mes=mes, invalidated=False
    ).first()

    is_stale = (
        cached is None
        or (datetime.now(timezone.utc) - cached.computed_at) > timedelta(hours=CASHFLOW_MES_TTL_HOURS)
    )

    if not is_stale:
        # Retornar no mesmo formato que a função original
        return _cashflow_mes_to_dict(cached)

    # Recomputar usando a lógica existente
    computed = _compute_cashflow_mes(db, user_id, ano, mes)

    # Upsert na tabela materializada
    if cached:
        for key, value in computed.items():
            setattr(cached, key, value)
        cached.computed_at = datetime.now(timezone.utc)
        cached.invalidated = False
    else:
        db.add(PlanoCashflowMes(
            user_id=user_id, ano=ano, mes=mes,
            mes_referencia=f"{ano}-{mes:02d}",
            **computed,
        ))
    db.commit()

    return computed


def _cashflow_mes_to_dict(row: PlanoCashflowMes) -> dict:
    """Converte ORM para o formato de dict retornado pela função original."""
    return {
        "renda_realizada": row.renda_realizada,
        "gastos_realizados": row.gastos_realizados,
        "investimentos_realizados": row.investimentos_realizados,
        "renda_esperada": row.renda_esperada,
        "gastos_recorrentes": row.gastos_recorrentes,
        "extras_creditos": row.extras_creditos,
        "extras_debitos": row.extras_debitos,
        "renda_usada": row.renda_usada,
        "total_gastos": row.total_gastos,
        "aporte_planejado": row.aporte_planejado,
        "aporte_usado": row.aporte_usado,
        "use_realizado": row.use_realizado,
        "status_mes": row.status_mes,
    }
```

---

### Microação 6 — Plugar invalidações nos domínios que mutam dados

**Arquivo:** `app_dev/backend/app/domains/transactions/service.py`

Após importar transações (upload):

```python
from app.domains.plano.service import invalidate_cashflow_cache

# Dentro de after_import ou equivalente:
meses_afetados = list({
    t.MesFatura[:7]   # 'YYYYMM' → 'YYYY-MM'
    for t in transacoes_inseridas
    if t.MesFatura
})
invalidate_cashflow_cache(db, user_id, mes_referencia=meses_afetados)
```

**Arquivo:** `app_dev/backend/app/domains/budget/service.py`

Após criar/editar/deletar `budget_planning`:

```python
invalidate_cashflow_cache(db, user_id, mes_referencia=[item.mes_referencia])
```

**Arquivo:** `app_dev/backend/app/domains/plano/service.py`

Após atualizar `user_financial_profile` (renda, crescimento %):

```python
invalidate_cashflow_cache(db, user_id, ano_partir=ano_atual)
```

---

### Microação 7 — Substituir chamada no router pelo novo método

**Arquivo:** `app_dev/backend/app/domains/plano/router.py`

```python
# Antes (linha ~241-269)
@router.get("/cashflow/mes")
def cashflow_mes(ano: int, mes: int, ...):
    resultado = get_cashflow(db, user_id, ano)   # computa 12 meses
    return resultado[mes - 1]

# Depois
@router.get("/cashflow/mes")
def cashflow_mes(ano: int, mes: int, ...):
    return get_cashflow_mes_cached(db, user_id, ano, mes)
```

---

### Checklist A1

- [ ] Model `PlanoCashflowMes` criado e sem erros de import
- [ ] Migration gerada e aplicada em dev
- [ ] `get_cashflow_mes_cached` retorna o mesmo shape de dados que a função original
- [ ] Invalidação chamada após: import de transações, edição de transação, mudança em budget_planning, mudança em expectativas, atualização de perfil financeiro
- [ ] Teste manual: fazer upload → verificar que cache é invalidado → request seguinte recomputa → request posterior usa cache

---

## A2 — Endpoint agregado dashboard

**Problema:** 11 RTTs simultâneos no cold start do dashboard.
**Impacto:** ~60% de redução no tempo de carregamento.
**Escopo:** Backend (novo endpoint) + Frontend (refatorar `use-dashboard.ts`).

---

### Microação 1 — Criar endpoint `/dashboard/summary` no backend

**Arquivo:** `app_dev/backend/app/domains/dashboard/router.py`

```python
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.core.database import get_db
from app.shared.dependencies import get_current_user_id

@router.get("/summary")
def dashboard_summary(
    year: int,
    month: int,
    ytd_month: int,
    sections: Optional[str] = Query(
        default="metrics,chart,income-sources,budget-vs-actual,credit-cards,orcamento-investimentos,cashflow-mes,aporte-mes",
        description="Seções a incluir, separadas por vírgula"
    ),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Endpoint agregado que consolida múltiplos dados do dashboard em 1 request.
    Aceita ?sections= para retornar apenas o necessário.
    """
    requested = set(sections.split(",")) if sections else set()
    result = {}

    if "metrics" in requested:
        result["metrics"] = get_dashboard_metrics(db, user_id, year, month, ytd_month)

    if "chart" in requested:
        result["chart"] = get_chart_data(db, user_id, year, month)

    if "chart-yearly" in requested:
        years = [year - 2, year - 1, year]
        result["chart_yearly"] = get_chart_data_yearly(db, user_id, years, ytd_month)

    if "income-sources" in requested:
        result["income_sources"] = get_income_sources(db, user_id, year, month)

    if "budget-vs-actual" in requested:
        result["budget_vs_actual"] = get_budget_vs_actual(db, user_id, year, month)

    if "credit-cards" in requested:
        result["credit_cards"] = get_credit_cards(db, user_id, year, month)

    if "orcamento-investimentos" in requested:
        result["orcamento_investimentos"] = get_orcamento_investimentos(db, user_id, year, month, ytd_month)

    if "cashflow-mes" in requested:
        result["cashflow_mes"] = get_cashflow_mes_cached(db, user_id, year, month)

    if "aporte-mes" in requested:
        result["aporte_mes"] = get_aporte_mes(db, user_id, year, month)

    return result
```

---

### Microação 2 — Adicionar endpoint a `api.config.ts`

**Arquivo:** `src/core/config/api.config.ts`

```typescript
// Adicionar junto com os outros endpoints de dashboard
DASHBOARD_SUMMARY: `${API_BASE}/dashboard/summary`,
```

---

### Microação 3 — Criar função de fetch no service

**Arquivo:** `src/features/dashboard/services/dashboard-api.ts`

```typescript
export interface DashboardSummary {
  metrics?: DashboardMetrics
  chart?: ChartData
  chart_yearly?: ChartDataYearly
  income_sources?: IncomeSources
  budget_vs_actual?: BudgetVsActual
  credit_cards?: CreditCards
  orcamento_investimentos?: OrcamentoInvestimentos
  cashflow_mes?: CashflowMes
  aporte_mes?: AporteMes
}

export async function fetchDashboardSummary(
  year: number,
  month: number,
  ytdMonth: number,
  sections?: string,
): Promise<DashboardSummary> {
  const params = new URLSearchParams({
    year: String(year),
    month: String(month),
    ytd_month: String(ytdMonth),
  })
  if (sections) params.set('sections', sections)

  return apiGet<DashboardSummary>(`${ENDPOINTS.DASHBOARD_SUMMARY}?${params}`)
}
```

---

### Microação 4 — Refatorar `use-dashboard.ts` para usar o endpoint agregado

**Arquivo:** `src/features/dashboard/hooks/use-dashboard.ts`

```typescript
// Antes: 11 useEffect/hooks separados disparando em paralelo

// Depois: 1 fetch para dados principais + prefetch individual para meses adjacentes
useEffect(() => {
  if (!selectedMonth || !isAuth) return

  const year = selectedMonth.getFullYear()
  const month = selectedMonth.getMonth() + 1
  const ytdMonth = month

  setLoading(true)

  fetchDashboardSummary(year, month, ytdMonth)
    .then((summary) => {
      if (summary.metrics)               setMetrics(summary.metrics)
      if (summary.chart)                 setChartData(summary.chart)
      if (summary.income_sources)        setIncomeSources(summary.income_sources)
      if (summary.budget_vs_actual)      setBudgetVsActual(summary.budget_vs_actual)
      if (summary.credit_cards)          setCreditCards(summary.credit_cards)
      if (summary.orcamento_investimentos) setOrcamentoInvestimentos(summary.orcamento_investimentos)
      if (summary.cashflow_mes)          setCashflowMes(summary.cashflow_mes)
      if (summary.aporte_mes)            setAporteMes(summary.aporte_mes)
    })
    .catch(setError)
    .finally(() => setLoading(false))

  // Prefetch de meses adjacentes continua usando endpoints individuais
  prefetchAdjacentMonths(year, month)
}, [selectedMonth, isAuth])
```

---

### Checklist A2

- [ ] Endpoint `/dashboard/summary` retorna o mesmo shape de dados que os endpoints individuais
- [ ] `?sections=` funciona corretamente (omitir seção = campo ausente no response, não null)
- [ ] Frontend não quebra se uma seção estiver ausente no response
- [ ] Prefetch de meses adjacentes mantém os endpoints individuais (não o agregado)
- [ ] Tempo de carregamento do dashboard medido antes e depois

---

## A3 — Fix scroll do mês

**Problema:** `MonthScrollPicker` aparece no mês atual e faz scroll suave até o mês com dados.
**Escopo:** Frontend only — 2 arquivos.

---

### Microação 1 — Parte A: guardar Promise (não resultado) no ref

**Arquivo:** `src/app/mobile/dashboard/page.tsx`

```typescript
// Antes (linha ~37-116)
const [selectedMonth, setSelectedMonth] = useState<Date | null>(null)
const _pendingLastMonth = useRef<{ year: number; month: number } | null>(null)

useEffect(() => {
  fetchLastMonthWithData('transactions')
    .then((last) => { _pendingLastMonth.current = last })
    .catch(() => {})
}, [])

useEffect(() => {
  if (!isAuth) return
  const pending = _pendingLastMonth.current
  if (pending) {
    setSelectedMonth(new Date(pending.year, pending.month - 1, 1))
  } else {
    fetchLastMonthWithData('transactions').then((last) => {
      setSelectedMonth(new Date(last.year, last.month - 1, 1))
    })
  }
}, [isAuth])

// Depois
const [selectedMonth, setSelectedMonth] = useState<Date | null>(null)
const _lastMonthPromise = useRef<Promise<{ year: number; month: number }> | null>(null)

useEffect(() => {
  // Inicia o fetch imediatamente, sem esperar auth
  _lastMonthPromise.current = fetchLastMonthWithData('transactions')
}, [])

useEffect(() => {
  if (!isAuth) return

  // Reusa a promise que já está em andamento (ou inicia nova se necessário)
  const promise = _lastMonthPromise.current ?? fetchLastMonthWithData('transactions')

  promise
    .then((last) => {
      setSelectedMonth(new Date(last.year, last.month - 1, 1))
      setSelectedYear(last.year)
      setLastMonthWithData(last)
    })
    .catch(() => {
      // Fallback: usar mês atual apenas como último recurso
      const now = new Date()
      setSelectedMonth(new Date(now.getFullYear(), now.getMonth(), 1))
    })
}, [isAuth])
```

---

### Microação 2 — Parte B: skeleton em vez de `?? new Date()`

**Arquivo:** `src/app/mobile/dashboard/page.tsx` (linha ~148-155)

```tsx
// Antes
{period === 'month' ? (
  <MonthScrollPicker
    selectedMonth={selectedMonth ?? new Date()}
    onMonthChange={setSelectedMonth}
  />
) : (...)}

// Depois
{period === 'month' ? (
  selectedMonth ? (
    <MonthScrollPicker
      selectedMonth={selectedMonth}
      onMonthChange={setSelectedMonth}
    />
  ) : (
    <MonthScrollPickerSkeleton />
  )
) : (...)}
```

Adicionar o componente skeleton (pode ficar no mesmo arquivo ou em `month-scroll-picker.tsx`):

```tsx
function MonthScrollPickerSkeleton() {
  return (
    <div className="flex gap-2 px-5 py-2 overflow-hidden">
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className="shrink-0 min-w-[60px] min-h-[44px] rounded-lg bg-muted animate-pulse"
        />
      ))}
    </div>
  )
}
```

---

### Microação 3 — Parte C: lista de meses centrada em `selectedMonth`

**Arquivo:** `src/components/mobile/month-scroll-picker.tsx` (linha ~63-72)

```typescript
// Antes — centrado em hoje, recalcula nunca
const months = React.useMemo(() => {
  const result: Date[] = []
  const start = subMonths(startOfMonth(new Date()), monthsRange)
  for (let i = 0; i <= monthsRange * 2; i++) {
    result.push(addMonths(start, i))
  }
  return result
}, [monthsRange])

// Depois — centrado no mês selecionado
const months = React.useMemo(() => {
  const result: Date[] = []
  const center = startOfMonth(selectedMonth)   // usa a prop
  const start = subMonths(center, monthsRange)
  for (let i = 0; i <= monthsRange * 2; i++) {
    result.push(addMonths(start, i))
  }
  return result
}, [selectedMonth, monthsRange])
```

---

### Microação 4 — Parte D: scroll `instant` no mount, `smooth` nas interações

**Arquivo:** `src/components/mobile/month-scroll-picker.tsx` (linha ~74-93)

```typescript
// Antes — sempre smooth
React.useEffect(() => {
  if (selectedMonthRef.current && scrollContainerRef.current) {
    const container = scrollContainerRef.current
    const button = selectedMonthRef.current
    const containerWidth = container.offsetWidth
    const buttonLeft = button.offsetLeft
    const buttonWidth = button.offsetWidth
    const scrollPosition = buttonLeft - containerWidth / 2 + buttonWidth / 2
    container.scrollTo({ left: scrollPosition, behavior: 'smooth' })
  }
}, [selectedMonth])

// Depois — instant no mount, smooth nas mudanças do usuário
const isMountedRef = React.useRef(false)

React.useEffect(() => {
  if (selectedMonthRef.current && scrollContainerRef.current) {
    const container = scrollContainerRef.current
    const button = selectedMonthRef.current
    const containerWidth = container.offsetWidth
    const buttonLeft = button.offsetLeft
    const buttonWidth = button.offsetWidth
    const scrollPosition = buttonLeft - containerWidth / 2 + buttonWidth / 2

    container.scrollTo({
      left: scrollPosition,
      behavior: isMountedRef.current ? 'smooth' : 'instant',
    })
    isMountedRef.current = true
  }
}, [selectedMonth])
```

---

### Checklist A3

- [ ] Picker não aparece no mês atual antes de mover para o mês com dados
- [ ] Skeleton aparece no lugar do picker enquanto `selectedMonth` é null (deve ser < 100ms)
- [ ] Navegar para meses fora do range original funciona (lista se recalcula)
- [ ] Clicar em um mês ainda tem animação smooth
- [ ] Abrir o dashboard diretamente no mês correto sem nenhum scroll visível

---

## B1 — Optimistic updates em Goals

**Problema:** Toda mutação (criar, editar, excluir) dispara full refetch. Usuário espera 300-500ms por ação.
**Escopo:** Frontend only — `src/features/goals/hooks/use-goals.ts`.

---

### Microação 1 — Criar helper de goal optimista

**Arquivo:** `src/features/goals/hooks/use-goals.ts`

```typescript
import { v4 as uuid } from 'uuid'  // ou usar Date.now() como id temporário

function makeOptimisticGoal(data: CreateGoalInput): Goal {
  return {
    id: `temp-${Date.now()}`,    // id temporário, substituído após resposta do servidor
    ...data,
    ativo: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    _optimistic: true,           // flag para UI mostrar estado pendente se necessário
  }
}
```

---

### Microação 2 — Implementar createGoal com optimistic update

```typescript
// Antes
async function createGoal(data: CreateGoalInput) {
  await api.post('/budget/planning/bulk-upsert', [data])
  await loadGoals()  // full refetch
}

// Depois
async function createGoal(data: CreateGoalInput) {
  const optimistic = makeOptimisticGoal(data)
  setGoals(prev => [...prev, optimistic])   // UI atualiza imediatamente

  try {
    const [saved] = await api.post<Goal[]>('/budget/planning/bulk-upsert', [data])
    // Substitui o item optimista pelo item real do servidor
    setGoals(prev => prev.map(g => g.id === optimistic.id ? saved : g))
  } catch (err) {
    // Rollback: remove o item optimista
    setGoals(prev => prev.filter(g => g.id !== optimistic.id))
    throw err
  }
}
```

---

### Microação 3 — Implementar updateGoal com optimistic update

```typescript
// Antes
async function updateGoal(id: string, data: Partial<Goal>) {
  await api.patch(`/budget/planning/toggle/${id}`, data)
  await loadGoals()
}

// Depois
async function updateGoal(id: string, data: Partial<Goal>) {
  const previousGoals = goals   // snapshot para rollback

  // Atualização imediata na UI
  setGoals(prev => prev.map(g => g.id === id ? { ...g, ...data } : g))

  try {
    const updated = await api.patch<Goal>(`/budget/planning/toggle/${id}`, data)
    // Confirmar com dados reais do servidor
    setGoals(prev => prev.map(g => g.id === id ? updated : g))
  } catch (err) {
    // Rollback para estado anterior
    setGoals(previousGoals)
    throw err
  }
}
```

---

### Microação 4 — Implementar deleteGoal com optimistic update

```typescript
// Antes
async function deleteGoal(id: string) {
  await api.delete(`/budget/${id}`)
  await loadGoals()
}

// Depois
async function deleteGoal(id: string) {
  const previousGoals = goals

  // Remove imediatamente da UI
  setGoals(prev => prev.filter(g => g.id !== id))

  try {
    await api.delete(`/budget/${id}`)
    // Sucesso — UI já está correta
  } catch (err) {
    // Rollback
    setGoals(previousGoals)
    throw err
  }
}
```

---

### Checklist B1

- [ ] Criar meta: aparece na lista imediatamente, sem loading
- [ ] Editar meta: valor atualiza na UI antes da resposta do servidor
- [ ] Excluir meta: some da lista imediatamente
- [ ] Em caso de erro do servidor: UI volta ao estado anterior (rollback)
- [ ] Nenhum `loadGoals()` (full refetch) é chamado em fluxos normais de CRUD

---

## B2 — Endpoint agregado investimentos

**Problema:** 3 RTTs separados no mount (`lista + resumo + distribuição`).
**Escopo:** Backend (novo endpoint) + Frontend (refatorar `use-investimentos.ts`).

---

### Microação 1 — Criar endpoint `/investimentos/overview`

**Arquivo:** `app_dev/backend/app/domains/investimentos/router.py`

```python
@router.get("/overview")
def investimentos_overview(
    tipo: Optional[str] = None,
    ativo: int = 1,
    anomes: Optional[str] = None,
    classe_ativo: Optional[str] = None,
    include: str = Query(default="lista,resumo,distribuicao"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Endpoint agregado: retorna lista + resumo + distribuição em 1 request.
    ?include=lista,resumo,distribuicao (qualquer subconjunto)
    """
    requested = set(include.split(","))
    result = {}

    if "lista" in requested:
        result["lista"] = get_investimentos(
            db, user_id, tipo=tipo, ativo=ativo, anomes=anomes
        )

    if "resumo" in requested:
        result["resumo"] = get_portfolio_resumo(db, user_id)

    if "distribuicao" in requested:
        result["distribuicao"] = get_distribuicao_por_tipo(
            db, user_id, classe_ativo=classe_ativo
        )

    return result
```

---

### Microação 2 — Refatorar `use-investimentos.ts`

**Arquivo:** `src/features/investimentos/hooks/use-investimentos.ts`

```typescript
// Antes — 3 requests em paralelo
useEffect(() => {
  if (!isAuth) return
  Promise.all([
    getInvestimentos(),
    getPortfolioResumo(),
    getDistribuicaoPorTipo(),
  ]).then(([lista, resumo, distribuicao]) => {
    setInvestimentos(lista)
    setResumo(resumo)
    setDistribuicao(distribuicao)
  })
}, [isAuth])

// Depois — 1 request
useEffect(() => {
  if (!isAuth) return

  fetchInvestimentosOverview({ tipo, ativo, anomes })
    .then((overview) => {
      if (overview.lista)       setInvestimentos(overview.lista)
      if (overview.resumo)      setResumo(overview.resumo)
      if (overview.distribuicao) setDistribuicao(overview.distribuicao)
    })
    .catch(setError)
    .finally(() => setLoading(false))
}, [isAuth, tipo, ativo, anomes])
```

---

## B3 — Batch range update goals

**Problema:** `aplicarAteFinAno=true` faz 1 chamada por mês restante (até 12 chamadas).
**Escopo:** Backend (novo endpoint) + Frontend (`goals-api.ts`).

---

### Microação 1 — Criar endpoint `PUT /budget/planning/bulk-range`

**Arquivo:** `app_dev/backend/app/domains/budget/router.py`

```python
class BulkRangeInput(BaseModel):
    goal_categoria: str
    goal_grupo: str
    valor: float
    mes_inicio: str    # 'YYYY-MM'
    mes_fim: str       # 'YYYY-MM'

@router.put("/planning/bulk-range")
def bulk_range_update(
    data: BulkRangeInput,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Aplica o mesmo valor para todos os meses entre mes_inicio e mes_fim.
    Executa em 1 transação no backend.
    """
    from dateutil.relativedelta import relativedelta
    from datetime import datetime

    inicio = datetime.strptime(data.mes_inicio, "%Y-%m")
    fim = datetime.strptime(data.mes_fim, "%Y-%m")

    meses = []
    current = inicio
    while current <= fim:
        meses.append(current.strftime("%Y-%m"))
        current += relativedelta(months=1)

    # Upsert em batch dentro de 1 transação
    service.bulk_upsert_goals(
        db, user_id,
        categoria=data.goal_categoria,
        grupo=data.goal_grupo,
        valor=data.valor,
        meses=meses,
    )

    # Invalida cache de cashflow para os meses afetados
    invalidate_cashflow_cache(db, user_id, mes_referencia=meses)

    return {"updated": len(meses), "meses": meses}
```

---

### Microação 2 — Substituir loop de chamadas no frontend

**Arquivo:** `src/features/goals/services/goals-api.ts`

```typescript
// Antes (linhas 301-319) — 1 chamada por mês
async function updateGoalValor(goalId: string, valor: number, aplicarAteFinAno: boolean) {
  if (aplicarAteFinAno) {
    const mesesRestantes = getMesesRestantesDoAno()
    await Promise.all(
      mesesRestantes.map(mes => api.patch(`/budget/planning/${goalId}`, { valor, mes }))
    )
  } else {
    await api.patch(`/budget/planning/${goalId}`, { valor })
  }
}

// Depois — 1 chamada para o range inteiro
async function updateGoalValor(
  goalCategoria: string,
  goalGrupo: string,
  valor: number,
  mesInicio: string,
  aplicarAteFinAno: boolean,
) {
  if (aplicarAteFinAno) {
    const anoAtual = new Date().getFullYear()
    await api.put('/budget/planning/bulk-range', {
      goal_categoria: goalCategoria,
      goal_grupo: goalGrupo,
      valor,
      mes_inicio: mesInicio,
      mes_fim: `${anoAtual}-12`,
    })
  } else {
    await api.patch(`/budget/planning/bulk-upsert`, [{ categoria: goalCategoria, grupo: goalGrupo, valor, mes_referencia: mesInicio }])
  }
}
```

---

## B4 — Cache nos módulos descobertos

**Problema:** Investimentos, Plano, Bancos, Categorias e Transações fazem fetch sempre que renderizam.
**Escopo:** Frontend only — adaptar o padrão já usado no dashboard.

O utilitário de cache a copiar fica em `src/features/dashboard/services/dashboard-api.ts`. Extrair para um shared util:

---

### Microação 1 — Extrair utilitário de cache para local compartilhado

**Arquivo:** `src/core/utils/in-memory-cache.ts` (novo arquivo)

```typescript
interface CacheEntry<T> {
  data: T
  expiresAt: number
  inFlight?: Promise<T>
}

const store = new Map<string, CacheEntry<unknown>>()

export function getCached<T>(key: string): T | null {
  const entry = store.get(key) as CacheEntry<T> | undefined
  if (!entry) return null
  if (Date.now() > entry.expiresAt) {
    store.delete(key)
    return null
  }
  return entry.data
}

export function setCached<T>(key: string, data: T, ttlMs: number): void {
  store.set(key, { data, expiresAt: Date.now() + ttlMs })
}

export function getInFlight<T>(key: string): Promise<T> | null {
  const entry = store.get(key) as CacheEntry<T> | undefined
  return entry?.inFlight ?? null
}

export function setInFlight<T>(key: string, promise: Promise<T>): void {
  const existing = store.get(key) as CacheEntry<T> | undefined
  store.set(key, { ...(existing ?? { data: null as T, expiresAt: 0 }), inFlight: promise })
  promise.finally(() => {
    const e = store.get(key) as CacheEntry<T> | undefined
    if (e) store.set(key, { ...e, inFlight: undefined })
  })
}

export function invalidateCache(keyPrefix: string): void {
  for (const key of store.keys()) {
    if (key.startsWith(keyPrefix)) store.delete(key)
  }
}
```

---

### Microação 2 — Aplicar cache em `use-banks.ts`

**Arquivo:** `src/features/banks/hooks/use-banks.ts`

```typescript
import { getCached, setCached, getInFlight, setInFlight, invalidateCache } from '@/core/utils/in-memory-cache'

const CACHE_KEY = 'banks:list'
const TTL = 5 * 60 * 1000  // 5 minutos (bancos raramente mudam)

async function fetchBanksCached(): Promise<Bank[]> {
  // 1. Hit no cache
  const cached = getCached<Bank[]>(CACHE_KEY)
  if (cached) return cached

  // 2. Deduplicar in-flight
  const inFlight = getInFlight<Bank[]>(CACHE_KEY)
  if (inFlight) return inFlight

  // 3. Fetch real
  const promise = apiGet<Bank[]>(ENDPOINTS.BANKS)
    .then((data) => { setCached(CACHE_KEY, data, TTL); return data })

  setInFlight(CACHE_KEY, promise)
  return promise
}

// Após mutação: invalidar e recarregar
async function createBank(data: CreateBankInput) {
  await apiPost(ENDPOINTS.BANKS, data)
  invalidateCache('banks:')   // limpa todas as chaves que começam com 'banks:'
  await fetchBanksCached()    // recarrega com dado fresco
}
```

---

### Microação 3 — Aplicar o mesmo padrão em outros módulos

Repetir a estrutura acima com os TTLs sugeridos:

| Módulo | Cache key prefix | TTL sugerido |
|--------|-----------------|--------------|
| `use-banks.ts` | `banks:` | 5 min |
| `use-categories.ts` | `categories:` | 5 min |
| `use-investimentos.ts` | `investimentos:` | 2 min |
| `plano/api.ts` | `plano:` | 2 min |

---

## B5 — Deduplicação global de requests

**Problema:** Dois componentes chamando `fetchBanks()` ao mesmo tempo fazem 2 requests idênticos.

Esse problema é resolvido automaticamente pelo `getInFlight` e `setInFlight` do utilitário criado em B4. Não é necessária nenhuma ação adicional além de garantir que todos os hooks usam `fetchBanksCached()` (com dedup) em vez de `apiGet()` diretamente.

---

## C1 — Cursor pagination em transações

**Problema:** Paginação offset degrada linearmente com o volume de dados.
**Escopo:** Backend (novo parâmetro) + Frontend (atualizar lógica de paginação).

---

### Microação 1 — Adicionar suporte a cursor no backend

**Arquivo:** `app_dev/backend/app/domains/transactions/router.py`

```python
@router.get("/list")
def list_transactions(
    # Paginação atual (manter para compatibilidade)
    page: int = 1,
    limit: int = 10,
    # Cursor-based (novo — se informado, tem prioridade)
    cursor: Optional[str] = None,   # id da última transação vista
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    # ... filtros existentes
):
    if cursor:
        # Cursor-based: busca registros após o cursor
        items = service.get_transactions_after_cursor(db, user_id, cursor, limit)
    else:
        # Fallback: paginação offset (compatibilidade)
        items = service.get_transactions_paged(db, user_id, page, limit)

    next_cursor = items[-1].id if len(items) == limit else None

    return {
        "items": items,
        "next_cursor": next_cursor,
        "has_more": next_cursor is not None,
    }
```

**Arquivo:** `app_dev/backend/app/domains/transactions/service.py`

```python
def get_transactions_after_cursor(
    db: Session,
    user_id: int,
    cursor: str,    # id da última transação
    limit: int,
) -> list[Transaction]:
    return (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.id < int(cursor),   # assume id decrescente = mais recente primeiro
        )
        .order_by(Transaction.id.desc())
        .limit(limit)
        .all()
    )
```

---

## D — Skills de desenvolvimento

Os 6 skills propostos em `07-skills-processos-recorrentes.md`. Nenhum foi criado ainda.
**Escopo:** Criar arquivos em `.claude/commands/`.

---

### Microação 1 — Criar `/deploy`

**Arquivo:** `.claude/commands/deploy.md`

```markdown
# Skill: Deploy

## Contexto do projeto
- Host SSH: `minha-vps-hostinger`
- Path na VM: `/var/www/finup`
- Compose prod: `docker-compose.prod.yml`
- Containers: `finup_backend_prod` (:8000), `finup_frontend_app_prod` (:3003), `finup_frontend_admin_prod` (:3001)
- Scripts: `scripts/deploy/deploy_docker_build_local.sh` e `scripts/deploy/deploy_docker_vm.sh`

## Antes de executar, verifique
1. `git status -uno` → sem mudanças não commitadas
2. Branch atual está correta para o deploy
3. `ssh minha-vps-hostinger echo ok` → SSH acessível

## Passos

### 1. Push
```bash
git push origin $(git branch --show-current)
```

### 2. Escolha o script
- VM com memória suficiente (> 1GB livre): usar `deploy_docker_vm.sh` (build na VM)
- VM com risco de OOM: usar `deploy_docker_build_local.sh` (build local + SCP)

### 3. Execute
```bash
# Opção A — build na VM
bash scripts/deploy/deploy_docker_vm.sh

# Opção B — build local
bash scripts/deploy/deploy_docker_build_local.sh
```

### 4. Aguardar health checks
O script aguarda automaticamente. Se falhar manualmente:
```bash
ssh minha-vps-hostinger "curl -s http://localhost:8000/health"
```

### 5. Migrations
```bash
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic upgrade head"
```

### 6. Validar
```bash
bash scripts/deploy/validate_deploy.sh
```

## Regras
- NUNCA editar arquivos diretamente na VM
- Sempre push antes de pull na VM
- Em caso de falha: `ssh minha-vps-hostinger "cd /var/www/finup && docker compose -f docker-compose.prod.yml rollback"`
- Registrar o commit de rollback: `git log --oneline -1`
```

---

### Microação 2 — Criar `/migration`

**Arquivo:** `.claude/commands/migration.md`

```markdown
# Skill: Migration Alembic

## Contexto do projeto
- Container dev: `finup_backend_dev`
- Migrations: `app_dev/backend/migrations/versions/`
- Guard: `migrations/env.py` bloqueia SQLite (PostgreSQL only)

## Antes de executar, pergunte
1. Descrição da mudança (ex: "Add plano_cashflow_mes table")
2. Tabelas/campos afetados
3. Os models.py foram atualizados?

## Passos

### 1. Verificar models atualizados
Ler o `models.py` do domínio afetado e confirmar que a mudança está refletida.

### 2. Gerar migration
```bash
docker exec finup_backend_dev alembic revision --autogenerate -m "Descrição da mudança"
```

### 3. Revisar o arquivo gerado
Abrir o arquivo em `migrations/versions/`. Verificar:
- `upgrade()` contém a mudança esperada
- `downgrade()` reverte corretamente
- Campos NOT NULL sem default em tabelas com dados existentes têm `server_default`

### 4. Testar em dev
```bash
docker exec finup_backend_dev alembic upgrade head
docker exec finup_backend_dev alembic current
```

### 5. Testar rollback
```bash
docker exec finup_backend_dev alembic downgrade -1
docker exec finup_backend_dev alembic upgrade head
```

## Armadilhas
- Campo NOT NULL sem server_default em tabela com dados = falha em prod
- `alembic upgrade` fora do container pode rodar contra banco errado
- Nunca commitar migrations sem testar upgrade + downgrade em dev
```

---

### Microação 3 — Criar `/new-api-domain`

**Arquivo:** `.claude/commands/new-api-domain.md`

```markdown
# Skill: Novo Domínio FastAPI

## Contexto
Backend DDD com 5 arquivos por domínio. Path: `app_dev/backend/app/domains/{nome}/`

## Antes de criar, pergunte
1. Nome do domínio (snake_case)
2. Nome da tabela SQL
3. Campos principais (nome, tipo, nullable?)
4. Endpoints desejados (CRUD completo ou subset?)

## Estrutura a criar
```
app/domains/{nome}/
├── __init__.py
├── models.py        (SQLAlchemy)
├── schemas.py       (Pydantic)
├── repository.py    (queries)
├── service.py       (regras de negócio)
└── router.py        (endpoints HTTP)
```

## Regras obrigatórias
- `user_id = Column(Integer, ForeignKey("users.id"), nullable=False)` em todo model
- Todo repository filtra por `user_id` em todo WHERE
- Todo endpoint usa `Depends(get_current_user_id)`
- Dependências: `from app.core.database import get_db` e `from app.shared.dependencies import get_current_user_id`
- Registrar em `app/main.py`: `app.include_router({nome}_router, prefix="/api/v1")`

## Após criar os arquivos
Gerar migration:
```bash
docker exec finup_backend_dev alembic revision --autogenerate -m "Add {nome} table"
docker exec finup_backend_dev alembic upgrade head
```
```

---

### Microação 4 — Criar `/new-feature`

**Arquivo:** `.claude/commands/new-feature.md`

```markdown
# Skill: Nova Feature Frontend

## Contexto
Next.js 14 App Router. Features em `src/features/{nome}/`.

## Antes de criar, pergunte
1. Nome da feature (kebab-case)
2. Endpoints de backend que ela consome
3. Componentes necessários (listagem, formulário, modal?)
4. Precisa de página? (mobile / desktop / ambas / nenhuma)

## Estrutura a criar
```
src/features/{nome}/
├── index.ts
├── types/index.ts
├── services/{nome}-api.ts
├── hooks/use-{nome}.ts
└── components/
    ├── index.ts
    └── {NomeComponent}.tsx
```

## Regras
- URLs nunca hardcoded: sempre via `ENDPOINTS` de `src/core/config/api.config.ts`
- Sempre `fetchWithAuth` (nunca `fetch()` direto)
- Hooks com cancellation token via `AbortController` + cleanup no useEffect
- Cache in-memory com TTL se dados são lidos com frequência (usar `in-memory-cache.ts`)
- Não editar `/components/ui/` (gerenciado pelo shadcn)
- Mobile: `src/app/mobile/{nome}/page.tsx` | Desktop: `src/app/{nome}/page.tsx`

## Padrão de hook
```typescript
export function use{Nome}() {
  const [data, setData] = useState<Tipo[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    fetch{Nome}()
      .then((result) => { if (!cancelled) setData(result) })
      .catch((err) => { if (!cancelled) setError(err.message) })
      .finally(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [])

  return { data, loading, error }
}
```
```

---

### Microação 5 — Criar `/new-processor`

**Arquivo:** `.claude/commands/new-processor.md`

```markdown
# Skill: Novo Processador Raw

## Contexto
Processadores em `app_dev/backend/app/domains/upload/processors/raw/{formato}/`

## Antes de criar, pergunte
1. Nome do banco (ex: "Nubank", "C6 Bank")
2. Tipo: fatura ou extrato
3. Formato: excel (.xlsx), pdf (texto) ou pdf (OCR/imagem)

## Assinatura obrigatória
```python
def process_{banco}_{tipo}(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str = None,
    final_cartao: str = None,
) -> Tuple[List[RawTransaction], BalanceValidation]:
```

## Campos obrigatórios do RawTransaction
`banco`, `tipo_documento`, `nome_arquivo`, `data_criacao`, `data` (DD/MM/YYYY),
`lancamento`, `valor` (float, negativo=débito), `nome_cartao`, `final_cartao`, `mes_fatura` (AAAAMM)

## BalanceValidation
`saldo_inicial + soma_transacoes ≈ saldo_final` (tolerância 0.01)

## Após criar
1. Registrar em `registry.py`: `PROCESSORS[(_normalize_bank_name(banco), tipo, formato)] = funcao`
2. Testar com arquivo real: `balance_validation.is_valid == True`
3. Atualizar tabela de compatibilidade no banco
```

---

### Microação 6 — Criar `/branch`

**Arquivo:** `.claude/commands/branch.md`

```markdown
# Skill: Criação de Branch

## Workflow de fases do projeto
```
Phase 1: PRD     → docs/features/{nome}/01-PRD/PRD.md
Phase 2: TECH    → docs/features/{nome}/02-TECH_SPEC/TECH_SPEC.md
Phase 3: SPRINT  → docs/features/{nome}/03-SPRINT/SPRINTX_COMPLETE.md
Phase 4: DEPLOY  → docs/features/{nome}/04-DEPLOY/DEPLOY_CHECKLIST.md
Phase 5: POST    → docs/features/{nome}/05-POST/POST_MORTEM.md
```

## Antes de criar, pergunte
1. Nome da feature (kebab-case)
2. Fase atual (PRD / TECH / SPRINT / DEPLOY / POST)
3. Tipo de mudança: feat / fix / perf / chore / refactor

## Passos
```bash
# 1. Criar branch
git checkout -b {tipo}/{nome}

# 2. Criar estrutura de docs
mkdir -p docs/features/{nome}

# 3. Criar o arquivo da fase correspondente
```

## Regra crítica
NUNCA editar arquivos diretamente na VM. Todo código vai via git push + deploy.
```

---

---

## E1 — Fix projeção de economia (tela Plano)

**Problema:** A curva laranja ("Real + Economia") ignora completamente os valores extraordinários. A fórmula atual cancela créditos e débitos extraordinários algebricamente, resultando em uma linha suavizada sem sazonalidade.
**Escopo:** Backend only — 1 função, ~15 linhas.
**Referência:** `10-projecao-economia-extraordinarios.md` — diagnóstico completo e análise de impacto.

### Fórmula correta

```
saldo_mes = renda - gastos_rec × (1 - %economia) + aportes_extraordinarios - gastos_extraordinarios
```

Mapeado para campos do cashflow (todos já existem):
```
m["renda_esperada"] - m["gastos_recorrentes"] × fator + m["extras_creditos"] - m["extras_debitos"]
```

### Microação 1 — Substituir branch 2 de `get_projecao()`

**Arquivo:** `app_dev/backend/app/domains/plano/service.py` (linhas 511-528)

```python
# Substituir o bloco else (branch 2) por:
else:
    # Curva laranja — formula: renda - gastos_rec*(1-%eco) + Ce - De
    # Todos os campos estão disponíveis no cashflow output.
    for i, m in enumerate(cashflow["meses"][:meses]):
        if m.get("use_realizado"):
            # Meses passados: usar valores realizados diretamente
            renda_real  = m.get("renda_realizada") or 0.0
            gastos_real = m.get("gastos_realizados") or 0.0
            invest_real = m.get("investimentos_realizados") or 0.0
            saldo_mes   = renda_real - gastos_real - invest_real
        else:
            # Meses futuros: slider reduz APENAS gastos recorrentes
            renda_base      = m.get("renda_esperada") or 0.0
            gastos_rec      = m.get("gastos_recorrentes") or 0.0
            creditos_extras = m.get("extras_creditos") or 0.0
            debitos_extras  = m.get("extras_debitos") or 0.0
            saldo_mes = (
                renda_base
                - gastos_rec * fator
                + creditos_extras
                - debitos_extras
            )
        acumulado += saldo_mes
        serie.append({
            "mes": i + 1,
            "mes_referencia": m["mes_referencia"],
            "saldo_mes": round(saldo_mes, 2),
            "acumulado": round(acumulado, 2),
        })
```

### Checklist E1

- [ ] Curva laranja mostra dip nos meses com débitos extraordinários (IPVA, seguros)
- [ ] Curva laranja mostra spike nos meses com créditos extraordinários (13º, bônus)
- [ ] Slider em 0%: curva laranja coincide com a curva azul
- [ ] Débitos extras não são reduzidos pelo slider

---

## F1 — chart-data: 12 queries → 1

**Problema:** `GET /dashboard/chart-data` faz 12 queries SQL em loop (1 por mês). Mesmo com cache N4a, o cold start sempre executa 12 queries.
**Escopo:** Backend only — 1 função, mesma interface.
**Referência:** `11-dashboard-mapeamento.md` — D1.

### Microação 1 — Reescrever `get_chart_data()` com 1 query

**Arquivo:** `app_dev/backend/app/domains/dashboard/repository.py` — função `get_chart_data()` (linha 299)

```python
def get_chart_data(self, user_id: int, year: int, month: int) -> List[Dict]:
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    reference_date = datetime(year, month if month > 0 else 12, 1)

    # Montar lista dos 12 mes_fatura na ordem correta (mais antigo → mais novo)
    meses_fatura = []
    meses_meta = []  # para reconstruir date/year/month depois
    for i in range(11, -1, -1):
        d = reference_date - relativedelta(months=i)
        meses_fatura.append(f"{d.year}{d.month:02d}")
        meses_meta.append((d.year, d.month))

    # 1 query com IN + GROUP BY em vez de 12 queries separadas
    rows = self.db.query(
        JournalEntry.MesFatura,
        func.sum(case(
            (JournalEntry.CategoriaGeral == 'Receita', JournalEntry.Valor), else_=0
        )).label('receitas'),
        func.abs(func.sum(case(
            (JournalEntry.CategoriaGeral == 'Despesa', JournalEntry.Valor), else_=0
        ))).label('despesas')
    ).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.MesFatura.in_(meses_fatura),
        JournalEntry.IgnorarDashboard == 0
    ).group_by(JournalEntry.MesFatura).all()

    by_mes = {r.MesFatura: r for r in rows}

    return [
        {
            "date": f"{ano}-{mes:02d}-01",
            "receitas": float(by_mes[mf].receitas or 0) if mf in by_mes else 0.0,
            "despesas": float(by_mes[mf].despesas or 0) if mf in by_mes else 0.0,
            "year": ano,
            "month": mes,
        }
        for mf, (ano, mes) in zip(meses_fatura, meses_meta)
    ]
```

### Checklist F1

- [ ] Shape idêntico: cada item tem `date`, `receitas`, `despesas`, `year`, `month`
- [ ] Meses sem transações retornam `receitas: 0, despesas: 0` (não ficam ausentes)
- [ ] Cache N4a continua funcionando (usa `date` como key — não muda)
- [ ] Resultado numérico idêntico ao original para meses com dados

---

## F2 — Cache em PatrimonioTab

**Problema:** `getPatrimonioTimeline` e `getDistribuicaoPorTipo` não têm cache — re-fetch toda vez que o usuário alterna para a aba Patrimônio.
**Escopo:** Frontend — `src/features/investimentos/services/investimentos-api.ts`.
**Referência:** `11-dashboard-mapeamento.md` — D2.

### Microação 1 — Adicionar TTL cache nas funções de timeline e distribuição

```typescript
// src/features/investimentos/services/investimentos-api.ts
import { getCached, setCached, getInFlight, setInFlight } from '@/core/utils/in-memory-cache'

const TTL_5MIN = 5 * 60 * 1000

// Envolver getPatrimonioTimeline com cache:
export async function getPatrimonioTimeline(anoInicio: number, anoFim: number) {
  const key = `investimentos:timeline:patrimonio:${anoInicio}:${anoFim}`
  const cached = getCached(key)
  if (cached) return cached
  const inFlight = getInFlight(key)
  if (inFlight) return inFlight
  const promise = apiGet(`${BASE_URL}/investimentos/timeline/patrimonio?ano_inicio=${anoInicio}&ano_fim=${anoFim}`)
    .then(data => { setCached(key, data, TTL_5MIN); return data })
  setInFlight(key, promise)
  return promise
}

// Envolver getDistribuicaoPorTipo com cache:
export async function getDistribuicaoPorTipo(classeAtivo?: string) {
  const key = `investimentos:distribuicao:${classeAtivo ?? 'all'}`
  const cached = getCached(key)
  if (cached) return cached
  const inFlight = getInFlight(key)
  if (inFlight) return inFlight
  const qs = classeAtivo ? `?classe_ativo=${classeAtivo}` : ''
  const promise = apiGet(`${BASE_URL}/investimentos/distribuicao-tipo${qs}`)
    .then(data => { setCached(key, data, TTL_5MIN); return data })
  setInFlight(key, promise)
  return promise
}
```

**Pré-requisito:** B4 (criar `core/utils/in-memory-cache.ts`).

---

## F3 — Prefetch OrcamentoTab em meses adjacentes

**Problema:** Prefetch só cobre `chart-data`. Ao navegar para mês adjacente, OrcamentoTab (income-sources, credit-cards, orcamento-investimentos) faz requests novos.
**Escopo:** Frontend — `src/app/mobile/dashboard/page.tsx`.
**Referência:** `11-dashboard-mapeamento.md` — D3.

### Microação 1 — Adicionar endpoints do OrcamentoTab ao prefetch

**Arquivo:** `src/app/mobile/dashboard/page.tsx` — useEffect do prefetch adjacente

```typescript
useEffect(() => {
  if (!selectedMonth || period !== 'month') return
  const prev = subMonths(selectedMonth, 1)
  const next = addMonths(selectedMonth, 1)

  for (const m of [prev, next]) {
    const y = m.getFullYear()
    const mo = m.getMonth() + 1
    // Chart (já existia)
    prefetchChartData(y, mo)
    // OrcamentoTab — fire-and-forget (popula cache, ignora erro)
    fetchIncomeSources(y, mo).catch(() => {})
    fetchExpenseSources(y, mo).catch(() => {})
    fetchOrcamentoInvestimentos(y, mo, mo).catch(() => {})
  }
}, [selectedMonth, period])
```

---

## F4 — Prefetch lastMonthWithData patrimônio

**Problema:** `lastMonthWithData('patrimonio')` é buscado lazily quando PatrimonioTab abre. Prefetch junto com o de transactions elimina 1 RTT.
**Escopo:** Frontend — `src/app/mobile/dashboard/page.tsx`.
**Referência:** `11-dashboard-mapeamento.md` — D4.

### Microação 1 — Iniciar ambas as promises no mount

```typescript
// Antes: só transactions
const _lastMonthPromise = useRef(null)
useEffect(() => {
  _lastMonthPromise.current = fetchLastMonthWithData('transactions')
}, [])

// Depois: ambas em paralelo
const _lastMonthPromise = useRef(null)
const _lastMonthPatrimonioPromise = useRef(null)
useEffect(() => {
  _lastMonthPromise.current = fetchLastMonthWithData('transactions')
  _lastMonthPatrimonioPromise.current = fetchLastMonthWithData('patrimonio')
}, [])
```

---

## F5 — Fallback parcial no sliding window N4a

**Problema:** Se qualquer 1 dos 7 pontos do chart estiver ausente do `_pointCache`, o N4a cai no fetch completo (12 queries). Com fallback parcial, busca só os pontos faltantes.
**Escopo:** Frontend — `src/features/dashboard/services/dashboard-api.ts`.
**Referência:** `11-dashboard-mapeamento.md` — D5.

### Microação 1 — Implementar busca parcial dos pontos faltantes

```typescript
// Em fetchChartData(), após gerar as 7 keys:
const keys = _chartWindow(year, month)
const missingKeys = keys.filter(k => !_pointCache.has(k))

if (missingKeys.length === 0) {
  // Cache hit total — sem request
  return keys.map(k => _pointCache.get(k)!)
}

if (missingKeys.length <= 4) {
  // Busca parcial: apenas os meses faltantes via request completo
  // (o request retorna 12 meses, mas popula o pointCache para todos)
  await _fetchAndPopulatePointCache(year, month)
  return keys.map(k => _pointCache.get(k)!)
}

// Miss alto: request completo (comportamento atual)
return _fetchAndPopulatePointCache(year, month)
```

---

## F6 — Renomear campos confusos em get_portfolio_resumo

**Problema:** Os campos `total_investido`, `valor_atual` e `rendimento_total` em `get_portfolio_resumo()` têm nomes que não correspondem ao conteúdo real (são, respectivamente, total_ativos, total_passivos e patrimônio_líquido). Os valores exibidos estão corretos, mas o naming é uma armadilha para manutenção futura.
**Escopo:** Backend + 2 consumers.
**Referência:** `11-dashboard-mapeamento.md` — D6.

### Microação 1 — Renomear no retorno de `get_portfolio_resumo()`

**Arquivo:** `app_dev/backend/app/domains/investimentos/repository.py` (linha 462-464)

```python
# Antes (nomes confusos)
return {
    'total_investido': total_ativos,
    'valor_atual': total_passivos,
    'rendimento_total': patrimonio_liquido,
    ...
}

# Depois (nomes descritivos)
return {
    'total_ativos': total_ativos,
    'total_passivos': total_passivos,
    'patrimonio_liquido': patrimonio_liquido,
    # Manter backward-compat por 1 ciclo se houver outros consumers:
    'total_investido': total_ativos,       # deprecated — remover após atualizar todos os consumers
    'valor_atual': total_passivos,         # deprecated
    'rendimento_total': patrimonio_liquido, # deprecated
    ...
}
```

### Microação 2 — Atualizar os consumers

**Arquivo:** `app_dev/backend/app/domains/dashboard/repository.py` (linhas 230-232)

```python
# Antes
ativos_mes           = float(resumo.get("total_investido") or 0)
passivos_mes         = float(resumo.get("valor_atual") or 0)
patrimonio_liquido_mes = float(resumo.get("rendimento_total") or 0)

# Depois
ativos_mes           = float(resumo.get("total_ativos") or 0)
passivos_mes         = float(resumo.get("total_passivos") or 0)
patrimonio_liquido_mes = float(resumo.get("patrimonio_liquido") or 0)
```

Verificar se há outros consumers em `src/features/investimentos/` que leem esses campos e atualizar.

---

## G1 — Debounce no slider da ProjecaoChart

**Problema:** Cada posição do slider dispara 1 request a `GET /plano/projecao`. Arrastar de 0→30% = 6 requests.
**Escopo:** Frontend — `src/features/plano/components/ProjecaoChart.tsx`.
**Referência:** `10-projecao-economia-extraordinarios.md` — P-Plano-1.

### Microação 1 — Adicionar debounce de 400ms + cache por percentual

```typescript
// Separar estado visual do estado que dispara fetch
const [sliderValue, setSliderValue] = useState(0)       // atualiza a cada arraste (UI imediata)
const [debouncedPct, setDebouncedPct] = useState(0)     // atualiza só quando para de arrastar

useEffect(() => {
  const timer = setTimeout(() => setDebouncedPct(sliderValue), 400)
  return () => clearTimeout(timer)
}, [sliderValue])

// Cache por percentual — evita re-fetch do mesmo valor
const projCache = useRef<Map<number, ProjecaoResponse>>(new Map())

useEffect(() => {
  if (!debouncedPct) { setData(null); return }

  if (projCache.current.has(debouncedPct)) {
    setData(projCache.current.get(debouncedPct)!)
    return
  }
  getProjecao(ano, 12, debouncedPct, true).then((d) => {
    projCache.current.set(debouncedPct, d)
    setData(d)
  })
}, [debouncedPct, ano])

// Limpar cache quando o ano muda
useEffect(() => {
  projCache.current.clear()
}, [ano])
```

---

## G2 — Cache para endpoints do Plano

**Problema:** Nenhum endpoint consumido pela tela de Plano tem cache — toda navegação ou re-render faz novo request.
**Escopo:** Frontend — `src/features/plano/api.ts`.
**Referência:** `10-projecao-economia-extraordinarios.md` — P-Plano-2, P-Plano-3.

### Microação 1 — Adicionar cache em todas as funções de plano/api.ts

Usar o mesmo padrão do `in-memory-cache.ts` (B4):

```typescript
import { getCached, setCached, getInFlight, setInFlight } from '@/core/utils/in-memory-cache'

const TTL_2MIN = 2 * 60 * 1000
const TTL_5MIN = 5 * 60 * 1000

// Exemplo para getResumoPlano (replicar para todos):
export async function getResumoPlano(ano: number, mes: number) {
  const key = `plano:resumo:${ano}:${mes}`
  const cached = getCached(key)
  if (cached) return cached
  const inFlight = getInFlight(key)
  if (inFlight) return inFlight
  const promise = fetchWithAuth(`${BASE}/resumo?ano=${ano}&mes=${mes}`)
    .then(r => r.json())
    .then(data => { setCached(key, data, TTL_2MIN); return data })
  setInFlight(key, promise)
  return promise
}
```

| Função | TTL sugerido | Cache key |
|--------|-------------|-----------|
| `getResumoPlano` | 2 min | `plano:resumo:${ano}:${mes}` |
| `getOrcamento` | 2 min | `plano:orcamento:${ano}:${mes}` |
| `getCashflow` | 2 min | `plano:cashflow:${ano}` |
| `getProjecao` | 5 min | `plano:projecao:${ano}:${reducao_pct}:${sem_patrimonio}` |
| `getImpactoLongoPrazo` | 5 min | `plano:impacto:${ano}:${mes}` |

---

## G3 — Separar effect de base e slider na ProjecaoChart

**Problema:** A ProjecaoChart busca `getProjecao(..., reducao_pct=0)` em todo mount — inclusive quando só o slider muda.
**Escopo:** Frontend — `src/features/plano/components/ProjecaoChart.tsx`.
**Referência:** `10-projecao-economia-extraordinarios.md` — P-Plano-5.

### Microação 1 — Dois effects independentes

```typescript
// Effect 1: base + cashflow — só re-executa quando ANO muda
useEffect(() => {
  setLoadingBase(true)
  Promise.all([
    getProjecao(ano, 12, 0, true),
    getCashflow(ano),
  ]).then(([base, cf]) => {
    setBaseData(base)
    setCashflow(cf)
  }).finally(() => setLoadingBase(false))
}, [ano])  // ← só ano, não o slider

// Effect 2: curva laranja — só executa quando percentual muda
useEffect(() => {
  if (!debouncedPct) { setData(null); return }
  // (usa cache por percentual do G1)
  getProjecao(ano, 12, debouncedPct, true).then(setData)
}, [debouncedPct, ano])
```

---

## Resumo de Arquivos por Item

| Item | Arquivos a criar/modificar |
|------|--------------------------|
| A1 | `plano/models.py`, `plano/service.py`, `transactions/service.py`, `budget/service.py`, migration |
| A2 | `dashboard/router.py`, `api.config.ts`, `dashboard-api.ts`, `use-dashboard.ts` |
| A3 | `dashboard/page.tsx`, `month-scroll-picker.tsx` |
| E1 | `plano/service.py` (linhas 511-528) |
| F1 | `dashboard/repository.py` (função `get_chart_data`) |
| F2 | `investimentos/services/investimentos-api.ts` |
| F3 | `dashboard/page.tsx` (useEffect do prefetch) |
| F4 | `dashboard/page.tsx` (useEffect do mount) |
| F5 | `dashboard/services/dashboard-api.ts` (fetchChartData) |
| F6 | `investimentos/repository.py`, `dashboard/repository.py` |
| G1 | `plano/components/ProjecaoChart.tsx` |
| G2 | `plano/api.ts` |
| G3 | `plano/components/ProjecaoChart.tsx` |
| B1 | `use-goals.ts` |
| B2 | `investimentos/router.py`, `use-investimentos.ts` |
| B3 | `budget/router.py`, `budget/service.py`, `goals-api.ts` |
| B4 | `core/utils/in-memory-cache.ts` (novo), `use-banks.ts`, `use-categories.ts`, `use-investimentos.ts`, `plano/api.ts` |
| B5 | Resolvido automaticamente pelo B4 |
| C1 | `transactions/router.py`, `transactions/service.py` + frontend |
| D | `.claude/commands/deploy.md`, `migration.md`, `new-api-domain.md`, `new-feature.md`, `new-processor.md`, `branch.md` |
