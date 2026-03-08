# Sprint 4 — Full-stack: Endpoints Agregados

> **Escopo:** Backend (novos endpoints) + Frontend (refatorar hooks).
> **Itens:** A2 · B2
> **Pré-requisito:** Sprint 2 (B4 — in-memory-cache.ts para dedup no frontend)
> **Impacto:** ~60% de redução no número de RTTs no cold start do dashboard e investimentos.

---

## Índice

- [A2 — Endpoint agregado dashboard](#a2--endpoint-agregado-dashboard)
- [B2 — Endpoint agregado investimentos](#b2--endpoint-agregado-investimentos)

---

## A2 — Endpoint agregado dashboard

**Problema:** 11 RTTs simultâneos no cold start do dashboard. Cada seção faz seu próprio fetch.
**Impacto:** ~60% de redução no tempo de carregamento (11 RTTs → 1 RTT).
**Escopo:** Backend (novo endpoint `/dashboard/summary`) + Frontend (refatorar `use-dashboard.ts`).

---

### Microação 1 — Criar endpoint `/dashboard/summary` no backend

**Arquivo:** `app_dev/backend/app/domains/dashboard/router.py`

Adicionar ao final do router, após os endpoints existentes:

```python
from typing import Optional

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
    Omitir uma seção = campo ausente no response (não null).
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

> **Nota:** `get_cashflow_mes_cached` só existirá após Sprint 5 (A1). Até lá, usar a função atual `get_cashflow_mes`. O endpoint funciona sem A1.

---

### Microação 2 — Verificar imports das funções no router

Confirmar que todas as funções chamadas no endpoint já estão importadas em `dashboard/router.py`. Se não estiverem, adicionar:

```python
from app.domains.dashboard.service import (
    get_dashboard_metrics,
    get_chart_data,
    get_chart_data_yearly,
    get_income_sources,
    get_budget_vs_actual,
    get_credit_cards,
    get_orcamento_investimentos,
    get_aporte_mes,
)
from app.domains.plano.service import get_cashflow_mes  # ou get_cashflow_mes_cached após A1
```

---

### Microação 3 — Adicionar endpoint a `api.config.ts`

**Arquivo:** `app_dev/frontend/src/config/api.config.ts` (ou onde estiver `ENDPOINTS`)

```typescript
// Adicionar junto com os outros endpoints de dashboard
DASHBOARD_SUMMARY: `${API_BASE}/dashboard/summary`,
```

---

### Microação 4 — Criar função de fetch no service

**Arquivo:** `app_dev/frontend/src/features/dashboard/services/dashboard-api.ts`

```typescript
export interface DashboardSummary {
  metrics?: DashboardMetrics
  chart?: ChartDataPoint[]
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

  return fetchWithAuth(`${ENDPOINTS.DASHBOARD_SUMMARY}?${params}`).then(r => r.json())
}
```

---

### Microação 5 — Refatorar `use-dashboard.ts` para usar o endpoint agregado

**Arquivo:** `app_dev/frontend/src/features/dashboard/hooks/use-dashboard.ts`

> **Estratégia:** Substituir os N useEffects/hooks individuais por 1 fetch para o endpoint agregado. Prefetch de meses adjacentes continua usando endpoints individuais.

```typescript
// Antes: N useEffect/hooks separados disparando em paralelo

// Depois: 1 fetch para dados principais
useEffect(() => {
  if (!selectedMonth || !isAuth) return

  const year = selectedMonth.getFullYear()
  const month = selectedMonth.getMonth() + 1
  const ytdMonth = month

  setLoading(true)

  fetchDashboardSummary(year, month, ytdMonth)
    .then((summary) => {
      if (summary.metrics)                setMetrics(summary.metrics)
      if (summary.chart)                  setChartData(summary.chart)
      if (summary.income_sources)         setIncomeSources(summary.income_sources)
      if (summary.budget_vs_actual)       setBudgetVsActual(summary.budget_vs_actual)
      if (summary.credit_cards)           setCreditCards(summary.credit_cards)
      if (summary.orcamento_investimentos) setOrcamentoInvestimentos(summary.orcamento_investimentos)
      if (summary.cashflow_mes)           setCashflowMes(summary.cashflow_mes)
      if (summary.aporte_mes)             setAporteMes(summary.aporte_mes)
    })
    .catch(setError)
    .finally(() => setLoading(false))

  // Prefetch de meses adjacentes continua usando endpoints individuais
  prefetchAdjacentMonths(year, month)
}, [selectedMonth, isAuth])
```

---

### Checklist A2

- [ ] `GET /dashboard/summary` retorna o mesmo shape que os endpoints individuais
- [ ] `?sections=` funciona: campo ausente = campo omitido (não null)
- [ ] Frontend não quebra se uma seção estiver ausente (usar `if (summary.x)`)
- [ ] Prefetch de meses adjacentes mantém endpoints individuais
- [ ] DevTools: 1 request no cold start do dashboard (era 11)

---

## B2 — Endpoint agregado investimentos

**Problema:** 3 RTTs separados no mount do módulo de investimentos (lista + resumo + distribuição).
**Impacto:** 3 RTTs → 1 RTT no carregamento inicial.
**Escopo:** Backend (novo endpoint `/investimentos/overview`) + Frontend (refatorar `use-investimentos.ts`).

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

### Microação 2 — Adicionar endpoint a `api.config.ts`

```typescript
INVESTIMENTOS_OVERVIEW: `${API_BASE}/investimentos/overview`,
```

---

### Microação 3 — Criar função de fetch

**Arquivo:** `app_dev/frontend/src/features/investimentos/services/investimentos-api.ts`

```typescript
export interface InvestimentosOverview {
  lista?: Investimento[]
  resumo?: PortfolioResumo
  distribuicao?: DistribuicaoItem[]
}

export async function fetchInvestimentosOverview(params: {
  tipo?: string
  ativo?: number
  anomes?: string
  include?: string
}): Promise<InvestimentosOverview> {
  const qs = new URLSearchParams()
  if (params.tipo) qs.set('tipo', params.tipo)
  if (params.ativo !== undefined) qs.set('ativo', String(params.ativo))
  if (params.anomes) qs.set('anomes', params.anomes)
  if (params.include) qs.set('include', params.include)

  return fetchWithAuth(`${ENDPOINTS.INVESTIMENTOS_OVERVIEW}?${qs}`).then(r => r.json())
}
```

---

### Microação 4 — Refatorar `use-investimentos.ts`

**Arquivo:** `app_dev/frontend/src/features/investimentos/hooks/use-investimentos.ts`

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
  setLoading(true)

  fetchInvestimentosOverview({ tipo, ativo, anomes })
    .then((overview) => {
      if (overview.lista)        setInvestimentos(overview.lista)
      if (overview.resumo)       setResumo(overview.resumo)
      if (overview.distribuicao) setDistribuicao(overview.distribuicao)
    })
    .catch(setError)
    .finally(() => setLoading(false))
}, [isAuth, tipo, ativo, anomes])
```

---

### Checklist B2

- [ ] `GET /investimentos/overview` retorna o mesmo shape que os 3 endpoints individuais
- [ ] `?include=lista` retorna apenas lista (sem resumo e distribuição)
- [ ] Frontend não quebra se uma seção estiver ausente
- [ ] DevTools: 1 request no mount (era 3)

---

## Resumo do Sprint 4

| Item | Backend | Frontend | RTTs antes | RTTs depois |
|------|---------|----------|-----------|-------------|
| A2 | `dashboard/router.py` | `dashboard-api.ts`, `use-dashboard.ts` | 11 | 1 |
| B2 | `investimentos/router.py` | `investimentos-api.ts`, `use-investimentos.ts` | 3 | 1 |

**Ordem:** A2 e B2 podem ser desenvolvidos em paralelo (domínios independentes).
