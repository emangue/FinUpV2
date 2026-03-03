# 🚀 Plano de Implementação — Eficiência de APIs

**Data:** 2026-03  
**Escopo:** Eliminar chamadas desnecessárias e duplicadas em todo o app  
**Meta:** Reduzir ~16 chamadas por abertura do Dashboard para ~6–8  
**Dependência:** Leia `ANALISE_EFICIENCIA_APP.md` para o diagnóstico geral

---

## 📋 Sumário de Problemas

| ID | Prioridade | Arquivo principal | Calls wasted | Dificuldade |
|----|-----------|-------------------|-------------|-------------|
| [P0-1](#p0-1--wrong-initial-month--re-fire) | 🔴 P0 | `dashboard/page.tsx` L37 | −5 a −10 por abertura | Média |
| [P0-2](#p0-2--incomesources-duplicado-dashboard--orcamentotab) | 🔴 P0 | `page.tsx` L60 | −1 por abertura | Fácil |
| [P0-3](#p0-3--credit-cards-duplicado-orcamentotab--gastosmcartaobox) | 🔴 P0 | `orcamento-tab.tsx` L103 | −1 por abertura | Fácil |
| [P0-4](#p0-4--dois-hooks-de-chart-sempre-disparam) | 🔴 P0 | `page.tsx` L64–68 | −1 por abertura | Fácil |
| [P1-1](#p1-1--fetchlastmonthwithdata-6x-sem-cache) | 🟡 P1 | `dashboard-api.ts` | −2 a −4 por navegação | Fácil |
| [P1-2](#p1-2--getresumoplano-duplicado-planohubpage--planoresumocard) | 🟡 P1 | `plano/page.tsx` + `PlanoResumoCard.tsx` | −1 por abertura | Fácil |
| [P1-3](#p1-3--fetchplanocashflowmes-busca-12-meses-para-usar-1) | 🟡 P1 | `dashboard-api.ts` L246 | −91% payload | Média |
| [P1-4](#p1-4--transactions-3-fetches-sem-debounce-em-period-selects) | 🟡 P1 | `transactions/page.tsx` | −2 a −4 por interação | Fácil |
| [P2-1](#p2-1--zero-cache-client-side) | 🟢 P2 | App inteiro | Alto custo por navegação | Difícil |
| [P2-2](#p2-2--patrimoniotab-dispara-2-calls-prematuras) | 🟢 P2 | `patrimonio-tab.tsx` | −2 cold start | Fácil |
| [P2-3](#p2-3--hooks-de-loading-fantasmas-no-dashboard) | 🟢 P2 | `dashboard/page.tsx` L60–61 | Ruído | Trivial |

---

## Ordem de execução recomendada

```
P0-2 → P0-3 → P0-4 → P2-3   ← Quick wins, zero risco, isolar antes de P0-1
   ↓
P0-1                           ← Requer atenção (spinner global impacta UX)
   ↓
P1-1                           ← Cache singleton, baixo risco
P1-4                           ← Debounce, baixo risco
P2-2                           ← Lazy load, trivial
   ↓
P1-2                           ← Prop drilling simples
P1-3                           ← Backend change, precisam de migration review
   ↓
P2-1                           ← React Query (esforço alto, máximo ganho)
```

---

## P0-1 — Wrong initial month → re-fire

### Diagnóstico

**Arquivo:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx`

```typescript
// ❌ HOJE — L37: mês inicial errado (data atual)
const [selectedMonth, setSelectedMonth] = useState<Date>(new Date())

// ❌ L60-61: hooks disparam com mês errado
const { loading: loadingSources } = useIncomeSources(year, month)    // mês atual: errado
const { loading: loadingExpenses } = useExpenseSources(year, month)  // idem

// ❌ L81: fetchLastMonthWithData só resolve depois, então todos os hooks re-disparam
useEffect(() => {
  fetchLastMonthWithData('transactions')
    .then((last) => {
      setSelectedMonth(new Date(last.year, last.month - 1, 1))  // → re-render → re-fire
      ...
    })
}, [isAuth])
```

**Custo:** Cada hook dispara 2× (mês errado + mês correto). Com 5 hooks = **10 calls extras** por abertura.

### Solução

Iniciar `selectedMonth` como `null`. Bloquear os hooks enquanto o mês correto não foi resolvido.

**`app/mobile/dashboard/page.tsx`**

```typescript
// ✅ DEPOIS — L37: iniciar nulo
const [selectedMonth, setSelectedMonth] = useState<Date | null>(null)

// ✅ L46–50: derivar year/month apenas quando selectedMonth existe
const year  = selectedMonth
  ? (period === 'month' ? selectedMonth.getFullYear() : selectedYear)
  : new Date().getFullYear()
const month = selectedMonth
  ? (period === 'month' ? selectedMonth.getMonth() + 1 : undefined)
  : undefined

// ✅ Hooks recebem flag "enabled" — não disparam se selectedMonth === null
const { metrics, loading: loadingMetrics } = useDashboardMetrics(
  year, month, ytdMonth,
  { enabled: selectedMonth !== null }   // novo parâmetro
)
const { chartData: chartDataMonthly, loading: loadingChartMonthly } = useChartData(
  selectedMonth?.getFullYear() ?? new Date().getFullYear(),
  selectedMonth?.getMonth() !== undefined ? selectedMonth.getMonth() + 1 : undefined,
  { enabled: selectedMonth !== null }
)
const { chartData: chartDataYearly, loading: loadingChartYearly } = useChartDataYearly(
  yearsList,
  period === 'ytd' ? (lastMonthWithData?.month ?? undefined) : undefined,
  { enabled: selectedMonth !== null }
)

// ✅ Spinner global enquanto selectedMonth não resolveu
if (selectedMonth === null) {
  return <FullScreenSpinner />    // componente existente que você já tem
}
```

**`features/dashboard/hooks/use-dashboard.ts`** — adicionar `enabled` em todos os hooks:

```typescript
// ANTES
export function useDashboardMetrics(year: number, month?: number, ytdMonth?: number) {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function load() {
      ...
    }
    load()
    return () => { cancelled = true }
  }, [year, month, ytdMonth])

  return { metrics, loading, error }
}

// ✅ DEPOIS — aceitar { enabled }
interface HookOptions { enabled?: boolean }

export function useDashboardMetrics(
  year: number,
  month?: number,
  ytdMonth?: number,
  options: HookOptions = {}
) {
  const { enabled = true } = options
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(enabled)   // false se disabled

  useEffect(() => {
    if (!enabled) { setLoading(false); return }
    let cancelled = false
    async function load() {
      setLoading(true)
      try {
        const data = await fetchDashboardMetrics(year, month, ytdMonth)
        if (!cancelled) setMetrics(data)
      } catch (err) {
        if (!cancelled) setError(err as Error)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [year, month, ytdMonth, enabled])

  return { metrics, loading, error }
}
// Aplicar o mesmo padrão em: useIncomeSources, useExpenseSources, useChartData, useChartDataYearly
```

**Arquivos afetados:**
- `app/mobile/dashboard/page.tsx` — 3 blocos (state, hooks, guard)
- `features/dashboard/hooks/use-dashboard.ts` — 5 hooks (adicionar `enabled`)

**Como testar:** Abrir Dashboard. Network tab: antes = ~16 calls, depois = ~6–8 (sem calls duplicadas).

---

## P0-2 — IncomeSources duplicado (Dashboard + OrcamentoTab)

### Diagnóstico

**`dashboard/page.tsx` L60:**
```typescript
// ❌ Data é descartada — só usa `loading`
const { loading: loadingSources } = useIncomeSources(year, month)
```

**`orcamento-tab.tsx` L101:**
```typescript
// ❌ Mesma call, mesmos params — resultado independente
const results = await Promise.allSettled([
  fetchIncomeSources(year, month ?? undefined),   // ← duplicata!
  fetchGoals(selectedMonth),
  ...
])
```

**Custo:** 1 call a mais por abertura do dashboard. `OrcamentoTab` já tem os dados — o pai não precisa buscar.

### Solução

Remover `useIncomeSources` do pai. `OrcamentoTab` já busca e exibe corretamente.

**`dashboard/page.tsx`:**

```typescript
// ANTES
const { loading: loadingSources } = useIncomeSources(year, month)
const { loading: loadingExpenses } = useExpenseSources(year, month)
const isLoading = loadingMetrics || loadingSources || loadingExpenses || loadingChart

// ✅ DEPOIS — remover as duas linhas
// (ver P2-3 para remover loadingSources/loadingExpenses do isLoading também)
const isLoading = loadingMetrics || loadingChart
```

**Arquivos afetados:**
- `app/mobile/dashboard/page.tsx` — remover L60–61 e atualizar `isLoading`

**Como testar:** Network tab — `/dashboard/income-sources` deve aparecer 1× (vinda do OrcamentoTab), nunca 2×.

---

## P0-3 — Credit-cards duplicado (OrcamentoTab + GastosPorCartaoBox)

### Diagnóstico

**`orcamento-tab.tsx` L103:**
```typescript
fetchCreditCards(year, month ?? undefined),   // ← busca para calcular total
```

**`gastos-por-cartao-box.tsx` L56:**
```typescript
useEffect(() => {
  fetchCreditCards(year, month)               // ← mesma call para exibir detalhes
    .then(setCards)
}, [year, month])
```

**Custo:** 1 call duplicada. `OrcamentoTab` só usa `cards.reduce(sum + total)`, enquanto `GastosPorCartaoBox` precisa do array completo.

### Solução

`OrcamentoTab` passa os dados como prop para `GastosPorCartaoBox`. O componente filho para de fazer fetch próprio quando recebe a prop.

**`orcamento-tab.tsx`:**

```typescript
// ANTES — apenas cardsTotal (soma)
const cards = results[2].status === 'fulfilled' ? results[2].value : null
setCardsTotal(Array.isArray(cards) ? cards.reduce(...) : null)

// ✅ DEPOIS — guardar o array completo
const [cardsData, setCardsData] = useState<CreditCardExpense[]>([])
// ...
const cards = results[2].status === 'fulfilled' ? results[2].value : null
setCardsData(Array.isArray(cards) ? cards : [])
setCardsTotal(Array.isArray(cards) ? cards.reduce((s, c) => s + c.total, 0) : null)

// E no JSX — passar como prop
// (o prop gastosPorCartao já existe — usado pelo pai dashboard/page.tsx)
// dashboard/page.tsx renderiza <OrcamentoTab gastosPorCartao={<GastosPorCartaoBox .../>} />
// Mudar para: <OrcamentoTab gastosPorCartao={<GastosPorCartaoBox cards={cardsData} .../>} />
```

**`gastos-por-cartao-box.tsx`:**

```typescript
// ANTES
interface GastosPorCartaoBoxProps {
  year: number
  month?: number
  monthLabel?: string
}
export function GastosPorCartaoBox({ year, month, monthLabel }: GastosPorCartaoBoxProps) {
  const [cards, setCards] = useState<CreditCardExpense[]>([])
  useEffect(() => {
    fetchCreditCards(year, month).then(setCards)   // ← remover quando prop fornecida
  }, [year, month])
```

```typescript
// ✅ DEPOIS — aceitar cards como prop opcional
interface GastosPorCartaoBoxProps {
  year: number
  month?: number
  monthLabel?: string
  cards?: CreditCardExpense[]   // ← nova prop
}
export function GastosPorCartaoBox({ year, month, monthLabel, cards: cardsProp }: GastosPorCartaoBoxProps) {
  const [cards, setCards] = useState<CreditCardExpense[]>(cardsProp ?? [])
  const [loading, setLoading] = useState(!cardsProp)

  useEffect(() => {
    if (cardsProp !== undefined) {
      setCards(cardsProp)
      setLoading(false)
      return
    }
    setLoading(true)
    fetchCreditCards(year, month)
      .then(setCards)
      .catch(() => setCards([]))
      .finally(() => setLoading(false))
  }, [year, month, cardsProp])
```

**Arquivos afetados:**
- `features/dashboard/components/orcamento-tab.tsx` — guardar array, não só total
- `features/dashboard/components/gastos-por-cartao-box.tsx` — aceitar `cards` como prop
- `app/mobile/dashboard/page.tsx` — já usa `gastosPorCartao={<GastosPorCartaoBox/>}`, atualizar para passar `cards`

> ⚠️ O `OrcamentoTab` atualmente expõe `gastosPorCartao` como slot (ReactNode), então o controle do dado fica no `dashboard/page.tsx`. Ajustar o fluxo: `OrcamentoTab` expõe `cardsData` via callback ou memoiza estado e passa para baixo.

---

## P0-4 — Dois hooks de chart sempre disparam

### Diagnóstico

**`dashboard/page.tsx` L64–68:**
```typescript
// ❌ Sempre disparam — mesmo quando só um é usado
const { chartData: chartDataMonthly, loading: loadingChartMonthly } = useChartData(
  selectedMonth.getFullYear(),
  selectedMonth.getMonth() + 1
)
const { chartData: chartDataYearly, loading: loadingChartYearly } = useChartDataYearly(
  yearsList,
  period === 'ytd' ? (lastMonthWithData?.month ?? undefined) : undefined
)

const chartData = period === 'month' ? chartDataMonthly : chartDataYearly
const loadingChart = period === 'month' ? loadingChartMonthly : loadingChartYearly
```

**Custo:** 1 call desnecessária por abertura. Se período = `'month'`, o hook anual dispara mas resultado é descartado (e vice-versa).

### Solução

Passar `enabled` para desativar o hook não usado no momento:

```typescript
// ✅ DEPOIS
const { chartData: chartDataMonthly, loading: loadingChartMonthly } = useChartData(
  selectedMonth?.getFullYear() ?? new Date().getFullYear(),
  selectedMonth ? selectedMonth.getMonth() + 1 : undefined,
  { enabled: period === 'month' && selectedMonth !== null }   // ← só dispara no período correto
)
const { chartData: chartDataYearly, loading: loadingChartYearly } = useChartDataYearly(
  yearsList,
  period === 'ytd' ? (lastMonthWithData?.month ?? undefined) : undefined,
  { enabled: period !== 'month' && selectedMonth !== null }   // ← idem
)
```

> Requer o `enabled` implementado em P0-1 (`use-dashboard.ts`).

**Arquivos afetados:**
- `app/mobile/dashboard/page.tsx` — 2 linhas de hook call

---

## P1-1 — `fetchLastMonthWithData` 6× sem cache

### Diagnóstico

`fetchLastMonthWithData` é chamada em 6 arquivos diferentes:

| Arquivo | Source |
|---------|--------|
| `app/mobile/dashboard/page.tsx` | `'transactions'` |
| `app/mobile/carteira/page.tsx` | `'patrimonio'` |
| `app/mobile/budget/manage/page.tsx` | `'transactions'` |
| `app/mobile/investimentos/page.tsx` | `'patrimonio'` |
| `app/mobile/budget/page.tsx` | `'transactions'` |
| `app/mobile/transactions/page.tsx` *(via params)* | `'transactions'` |

Cada navegação entre páginas dispara 1 nova chamada — sem cache, sem TTL.

O backend (`dashboard/repository.py`) responde rápido (`ORDER BY Ano DESC, Mes DESC LIMIT 1`), mas acumula latência de round-trip quando o usuário navega entre telas.

### Solução

Cache em memória no módulo (singleton por process). TTL de 5 minutos.

**`features/dashboard/services/dashboard-api.ts`** — adicionar antes de `fetchLastMonthWithData`:

```typescript
// ─── CACHE: Last Month With Data ──────────────────────────────────────────────
interface CachedEntry<T> { value: T; ts: number }
const _lmwdCache = new Map<string, CachedEntry<{ year: number; month: number }>>()
const LMWD_TTL_MS = 5 * 60 * 1000   // 5 minutos

// ✅ Limpar cache manualmente após upload de novos dados
export function invalidateLastMonthCache(source?: LastMonthSource) {
  if (source) {
    _lmwdCache.delete(`lastMonth:${source}`)
  } else {
    _lmwdCache.clear()
  }
}
// ─────────────────────────────────────────────────────────────────────────────

export async function fetchLastMonthWithData(
  source: LastMonthSource = 'transactions'
): Promise<{ year: number; month: number }> {
  const key = `lastMonth:${source}`
  const hit = _lmwdCache.get(key)
  if (hit && Date.now() - hit.ts < LMWD_TTL_MS) {
    return hit.value      // ← cache hit, zero request
  }

  const response = await fetchWithAuth(
    `${BASE_URL}/dashboard/last-month-with-data?source=${source}`
  )
  if (!response.ok) throw new Error(`Failed to fetch last month: ${response.status}`)
  const value: { year: number; month: number } = await response.json()

  _lmwdCache.set(key, { value, ts: Date.now() })
  return value
}
```

**Chamar `invalidateLastMonthCache` após upload bem-sucedido:**

```typescript
// Em qualquer onSuccess de upload:
import { invalidateLastMonthCache } from '@/features/dashboard/services/dashboard-api'
// ...
onSuccess: () => {
  invalidateLastMonthCache('transactions')
  invalidateLastMonthCache('patrimonio')
  router.refresh()
}
```

**Arquivos afetados:**
- `features/dashboard/services/dashboard-api.ts` — cache + invalidate
- Arquivo de upload (onde o `onSuccess` existe)

**Como testar:** Navegar Dashboard → Carteira → Investimentos. Network: `last-month-with-data` deve aparecer 1× por 5 minutos, não 1× por página.

---

## P1-2 — `getResumoPlano` duplicado (PlanoHubPage + PlanoResumoCard)

### Diagnóstico

**`app/mobile/plano/page.tsx` L33:**
```typescript
// Para checar isEmpty
Promise.all([getResumoPlano(year, month), getOrcamento(year, month)])
  .then(([resumo, orcamento]) => {
    const semRenda = resumo?.renda == null
    setIsEmpty(semRenda && ...)
  })
```

**`features/plano/components/PlanoResumoCard.tsx` L43:**
```typescript
// Para exibir dados reais
Promise.all([
  getResumoPlano(year, month),    // ← mesma chamada, mesmos params
  fetchIncomeSources(year, month),
  ...
])
```

**Custo:** 1 call duplicada por abertura da tela Plano.

### Solução

`PlanoHubPage` faz a call e passa `resumo` como prop para `PlanoResumoCard`.

**`app/mobile/plano/page.tsx`:**

```typescript
// ANTES
const [isEmpty, setIsEmpty] = useState<boolean | null>(null)

useEffect(() => {
  Promise.all([getResumoPlano(year, month), getOrcamento(year, month)])
    .then(([resumo, orcamento]) => {
      setIsEmpty(resumo?.renda == null && (resumo?.total_budget ?? 0) === 0 && orcamento.length === 0)
    })
}, [year, month])

// ✅ DEPOIS — guardar o resumo
const [isEmpty, setIsEmpty] = useState<boolean | null>(null)
const [resumo, setResumo] = useState<ResumoPlano | null>(null)   // adicionar tipo

useEffect(() => {
  Promise.all([getResumoPlano(year, month), getOrcamento(year, month)])
    .then(([r, orcamento]) => {
      setResumo(r)
      setIsEmpty(r?.renda == null && (r?.total_budget ?? 0) === 0 && orcamento.length === 0)
    })
}, [year, month])

// No JSX — passar como prop
<PlanoResumoCard year={year} month={month} resumoExterno={resumo} />
```

**`features/plano/components/PlanoResumoCard.tsx`:**

```typescript
// ANTES
interface PlanoResumoCardProps {
  year: number
  month: number
}

export function PlanoResumoCard({ year, month }: PlanoResumoCardProps) {
  useEffect(() => {
    Promise.all([
      getResumoPlano(year, month),   // ← remover quando prop fornecida
      ...
    ])
  }, [year, month])

// ✅ DEPOIS
interface PlanoResumoCardProps {
  year: number
  month: number
  resumoExterno?: ResumoPlano | null   // ← nova prop opcional
}

export function PlanoResumoCard({ year, month, resumoExterno }: PlanoResumoCardProps) {
  useEffect(() => {
    const load = async () => {
      const r = resumoExterno ?? await getResumoPlano(year, month)   // só busca se não recebeu
      const [inc, g, aporteDetalhe] = await Promise.all([
        fetchIncomeSources(year, month),
        fetchGoals(new Date(year, month - 1, 1)),
        fetchAporteInvestimentoDetalhado(year, month),
      ])
      setResumo(r)
      ...
    }
    load()
  }, [year, month, resumoExterno])
```

**Arquivos afetados:**
- `app/mobile/plano/page.tsx` — guardar `resumo`, passar como prop
- `features/plano/components/PlanoResumoCard.tsx` — aceitar `resumoExterno`

---

## P1-3 — `fetchPlanoCashflowMes` busca 12 meses para usar 1

### Diagnóstico

**`features/dashboard/services/dashboard-api.ts` L246–268:**
```typescript
export async function fetchPlanoCashflowMes(year: number, month: number) {
  const response = await fetchWithAuth(
    `${BASE_URL}/plano/cashflow?ano=${year}&modo_plano=true`   // ← 12 meses!
  )
  const data = await response.json()
  const mes = (data.meses ?? []).find((m: any) => {
    const mm = parseInt((m.mes_referencia ?? '').split('-')[1] ?? '0', 10)
    return mm === month       // ← descarta 11 meses
  })
  ...
}
```

**Custo:** 91% do payload descartado. Em redes lentas (3G mobile), a diferença é visível.

### Solução

Opção A (recomendada — backend): Adicionar endpoint `/plano/cashflow/mes?ano=&mes=`.

**`app_dev/backend/app/domains/plano/router.py`** — adicionar após o endpoint `/cashflow/detalhe-mes` (L144):

```python
@router.get("/cashflow/mes")
def cashflow_mes_unico(
    ano: int = Query(..., ge=2020, le=2100),
    mes: int = Query(..., ge=1, le=12),
    modo_plano: bool = Query(False),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Retorna dados de cashflow para um único mês (subset do /cashflow anual)."""
    service = PlanoService(db)
    resultado = service.get_cashflow(user_id, ano, modo_plano_sempre=modo_plano)
    # get_cashflow retorna {"meses": [...], ...}
    meses = resultado.get("meses", []) if isinstance(resultado, dict) else []
    mes_ref = f"{ano}-{str(mes).zfill(2)}"
    mes_data = next((m for m in meses if m.get("mes_referencia") == mes_ref), None)
    if not mes_data:
        raise HTTPException(status_code=404, detail="Mês não encontrado no cashflow")
    return mes_data
```

**Frontend — `dashboard-api.ts`:**
```typescript
// ✅ DEPOIS
export async function fetchPlanoCashflowMes(
  year: number,
  month: number
): Promise<PlanoCashflowMes | null> {
  try {
    const response = await fetchWithAuth(
      `${BASE_URL}/plano/cashflow/mes?ano=${year}&mes=${month}&modo_plano=true`  // ← 1 mês!
    )
    if (!response.ok) return null
    const mes = await response.json()
    return {
      renda_esperada: mes.renda_esperada ?? 0,
      extras_creditos: mes.extras_creditos ?? 0,
      gastos_recorrentes: mes.gastos_recorrentes ?? 0,
      extras_debitos: mes.extras_debitos ?? 0,
      aporte_planejado: mes.aporte_planejado ?? 0,
    }
  } catch {
    return null
  }
}
```

> **Opção B (sem backend):** Memoizar o array completo por `ano` no módulo e reutilizar para diferentes meses do mesmo ano — evita repetir a call de 12 meses quando OrcamentoTab troca de mês dentro do mesmo ano.

**Arquivos afetados:**
- `app_dev/backend/app/domains/plano/router.py` — novo endpoint `/cashflow/mes`
- `features/dashboard/services/dashboard-api.ts` — atualizar URL

---

## P1-4 — Transactions: 3 fetches sem debounce em period selects

### Diagnóstico

**`transactions/page.tsx` — filtros de período:**
```typescript
// ✅ search já tem debounce de 300ms:
useEffect(() => {
  searchTimeoutRef.current = setTimeout(() => setSearchDebounced(searchQuery), 300)
}, [searchQuery])

// ❌ Mas yearInicio, monthInicio, yearFim, monthFim vão direto para `filters`:
const filters = useMemo(() => ({
  year_inicio: yearInicio,
  month_inicio: monthInicio,
  year_fim: yearFim,
  month_fim: monthFim,
  ...
}), [semFiltroPeriodo, yearInicio, monthInicio, yearFim, monthFim, ...])

// ❌ E `filters` dispara 2 fetches imediatamente:
useEffect(() => {
  fetchTransactions()
  fetchResumo()
}, [fetchTransactions, fetchResumo])
```

**Custo:** Cada mudança de `yearInicio` ou `monthInicio` (por scroll ou dropdown) dispara 3 calls (`fetchTransactions` + `fetchResumo` + `fetchGastosPorGrupo` se collapse aberto).

### Solução

Debounce de 400ms nos filtros de período, idêntico ao padrão já usado para `search`.

**`transactions/page.tsx`:**

```typescript
// ✅ ADICIONAR — debounce para filtros de período
const periodFilterRef = useRef<ReturnType<typeof setTimeout> | null>(null)
const [debouncedPeriod, setDebouncedPeriod] = useState({
  yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo
})

useEffect(() => {
  if (periodFilterRef.current) clearTimeout(periodFilterRef.current)
  periodFilterRef.current = setTimeout(() => {
    setDebouncedPeriod({ yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo })
  }, 400)
  return () => {
    if (periodFilterRef.current) clearTimeout(periodFilterRef.current)
  }
}, [yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo])

// ✅ filters usa debouncedPeriod em vez dos valores diretos
const filters = useMemo(() => {
  const base: Record<string, ...> = {
    search: searchDebounced || undefined,
    ...
  }
  if (!debouncedPeriod.semFiltroPeriodo) {
    const isSingleMonth = debouncedPeriod.yearInicio === debouncedPeriod.yearFim
      && debouncedPeriod.monthInicio === debouncedPeriod.monthFim
    if (isSingleMonth) {
      base.year = debouncedPeriod.yearInicio
      base.month = debouncedPeriod.monthInicio
    } else {
      base.year_inicio = debouncedPeriod.yearInicio
      base.month_inicio = debouncedPeriod.monthInicio
      base.year_fim = debouncedPeriod.yearFim
      base.month_fim = debouncedPeriod.monthFim
    }
  }
  return base
}, [debouncedPeriod, searchDebounced, categoriaGeral, grupoFilter, subgrupoFilter, estabelecimentoFilter])
```

**Arquivos afetados:**
- `app/mobile/transactions/page.tsx` — 1 bloco useEffect + alterar dependências do `filters` useMemo

---

## P2-1 — Zero cache client-side

### Diagnóstico

Toda navegação entre telas refaz 100% das chamadas. Não há React Query, SWR, nem cache manual.

**Impacto por navegação:**
- Dashboard → Carteira → Dashboard: `metrics`, `chart`, `income-sources`, `expense-sources` refazem do zero.
- Dashboard → Transações → Dashboard: idem.

### Solução

**Opção A — React Query (recomendada):**

```bash
# Instalar
npm install @tanstack/react-query
```

```typescript
// app/layout.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 3 * 60 * 1000,   // 3 minutos — dados frescos sem re-fetch
      gcTime:    10 * 60 * 1000,  // 10 minutos — manter em memória
      retry: 1,
    },
  },
})
export default function RootLayout({ children }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
```

```typescript
// features/dashboard/hooks/use-dashboard.ts — refatorar com useQuery
import { useQuery } from '@tanstack/react-query'

export function useDashboardMetrics(year: number, month?: number, ytdMonth?: number, options: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: ['dashboard', 'metrics', year, month, ytdMonth],
    queryFn: () => fetchDashboardMetrics(year, month, ytdMonth),
    enabled: options.enabled ?? true,
    staleTime: 3 * 60 * 1000,
  })
}
// Aplicar em todos os hooks
```

**Opção B — Cache manual simples (sem instalar libs):**

Mesma abordagem da `_lmwdCache` em P1-1, porém genérico:

```typescript
// core/utils/query-cache.ts
interface Entry<T> { data: T; ts: number }

export class QueryCache {
  private store = new Map<string, Entry<unknown>>()
  private ttl: number

  constructor(ttlMs = 3 * 60 * 1000) {
    this.ttl = ttlMs
  }

  get<T>(key: string): T | null {
    const entry = this.store.get(key) as Entry<T> | undefined
    if (!entry || Date.now() - entry.ts > this.ttl) return null
    return entry.data
  }

  set<T>(key: string, data: T) {
    this.store.set(key, { data, ts: Date.now() })
  }

  invalidate(prefix?: string) {
    if (!prefix) { this.store.clear(); return }
    for (const key of this.store.keys()) {
      if (key.startsWith(prefix)) this.store.delete(key)
    }
  }
}

export const dashboardCache = new QueryCache()
```

```typescript
// dashboard-api.ts
export async function fetchDashboardMetrics(year: number, month?: number, ytdMonth?: number) {
  const key = `metrics:${year}:${month}:${ytdMonth}`
  const cached = dashboardCache.get<DashboardMetrics>(key)
  if (cached) return cached

  const response = await fetchWithAuth(`${BASE_URL}/dashboard/metrics?...`)
  const data: DashboardMetrics = await response.json()
  dashboardCache.set(key, data)
  return data
}
```

**Esforço:** React Query = 2–3 dias de refatoração, máximo retorno. Cache manual = 1 dia, 60% do retorno.

---

## P2-2 — PatrimonioTab dispara 2 calls prematuras

### Diagnóstico

**`features/dashboard/components/patrimonio-tab.tsx` L95–98:**
```typescript
// ❌ Dispara ao montar o componente — mesmo com Collapsible fechado
useEffect(() => {
  fetchDistribuicao()
}, [fetchDistribuicao])

// Collapsible está fechado por padrão:
// (não há defaultOpen=true — logo o usuário não vê o conteúdo)
```

`fetchDistribuicao()` faz 2 calls paralelas:
- `getDistribuicaoPorTipo({ classe_ativo: 'Ativo' })`
- `getDistribuicaoPorTipo({ classe_ativo: 'Passivo' })`

### Solução

Lazy load: só buscar quando o Collapsible abrir.

**`patrimonio-tab.tsx`:**

```typescript
// ANTES
const [distribuicaoLoading, setDistribuicaoLoading] = useState(true)

useEffect(() => {
  fetchDistribuicao()   // ← sempre ao montar
}, [fetchDistribuicao])

// JSX
<Collapsible>
  <CollapsibleTrigger>Distribuição</CollapsibleTrigger>
  <CollapsibleContent>
    <DistribuicaoLista ... />
  </CollapsibleContent>
</Collapsible>

// ✅ DEPOIS
const [distribuicaoOpen, setDistribuicaoOpen] = useState(false)
const [distribuicaoFetched, setDistribuicaoFetched] = useState(false)

// Buscar apenas na primeira abertura
useEffect(() => {
  if (distribuicaoOpen && !distribuicaoFetched) {
    setDistribuicaoFetched(true)
    fetchDistribuicao()
  }
}, [distribuicaoOpen, distribuicaoFetched, fetchDistribuicao])

// JSX — controlar open state
<Collapsible open={distribuicaoOpen} onOpenChange={setDistribuicaoOpen}>
  <CollapsibleTrigger>Distribuição</CollapsibleTrigger>
  <CollapsibleContent>
    {distribuicaoOpen && <DistribuicaoLista ... />}
  </CollapsibleContent>
</Collapsible>
```

**Arquivos afetados:**
- `features/dashboard/components/patrimonio-tab.tsx` — 1 state + 1 useEffect + JSX

---

## P2-3 — Hooks de loading fantasmas no Dashboard

### Diagnóstico

```typescript
// dashboard/page.tsx L60–61 — data descartada, só loading usado:
const { loading: loadingSources } = useIncomeSources(year, month)   // ← data não usada
const { loading: loadingExpenses } = useExpenseSources(year, month) // ← data não usada

const isLoading = loadingMetrics || loadingSources || loadingExpenses || loadingChart
```

**Custo:** 2 calls desnecessárias + falso senso de precisão no `isLoading` (o spinner dura mais do que precisa).

### Solução

Remover ambos os hooks. `OrcamentoTab` cuida do seu próprio loading. O spinner global do Dashboard só precisa aguardar `metrics` e `chart`.

```typescript
// ✅ DEPOIS — remover as 2 linhas
// const { loading: loadingSources } = useIncomeSources(year, month)   ← REMOVER
// const { loading: loadingExpenses } = useExpenseSources(year, month) ← REMOVER

const isLoading = loadingMetrics || loadingChart   // ← simplificado
```

> Nota: `OrcamentoTab` tem seu próprio `loading` interno — o usuário verá skeleton dentro da tab enquanto os dados de income/expenses carregam, o que é UX correto (loading granular > spinner de página inteira).

**Arquivos afetados:**
- `app/mobile/dashboard/page.tsx` — remover L60–61, atualizar `isLoading`

---

## 📊 Resultado esperado após todas as correções

| Cenário | Calls antes | Calls depois | Redução |
|---------|------------|-------------|---------|
| Abrir Dashboard (1ª vez) | ~16 | ~6–8 | −50 a −63% |
| Abrir Dashboard (2ª vez, mesmo mês) | ~16 | ~2–4 (cache) | −75 a −88% |
| Trocar mês no scroll | ~5 | ~3 | −40% |
| Navegar Dash → Transações → Dash | ~21 | ~6 (cache) | −71% |
| Trocar filtro de período em Transações | ~3 calls/interação imediata | 1 call após 400ms | debounce |
| Abrir Aba Patrimônio | ~3 calls | ~1 call (timeline) + 2 lazy | −67% cold start |

---

## 🧪 Como validar

```
Chrome DevTools → Network → filtrar por "localhost:8000"
```

**Checklist pós-implementação:**

- [ ] Abrir Dashboard: total de calls ≤ 8 na 1ª abertura
- [ ] `/dashboard/income-sources` aparece apenas 1× (vindo do OrcamentoTab)
- [ ] `/dashboard/credit-cards` aparece apenas 1×
- [ ] Trocar period (Mês → YTD): apenas 1 chart call dispara, não 2
- [ ] Navegar para outra tela e voltar ao Dashboard: `last-month-with-data` não re-aparece no Network
- [ ] Digitar no search de Transações: calls aparecem após 300ms de pausa
- [ ] Mudar mês em Transações: calls aparecem após 400ms de pausa
- [ ] Abrir tab Patrimônio sem expandir Distribuição: apenas 1 call (`patrimonio/timeline`)
- [ ] Expandir Distribuição: 2 calls aparecem apenas neste momento

---

## 📁 Arquivos modificados (mapa completo)

```
Frontend (app_dev/frontend/src/)
├── app/mobile/dashboard/page.tsx              ← P0-1, P0-2, P0-3, P0-4, P2-3
├── app/mobile/plano/page.tsx                  ← P1-2
├── app/mobile/transactions/page.tsx           ← P1-4
├── features/dashboard/
│   ├── hooks/use-dashboard.ts                 ← P0-1 (enabled), P0-4
│   ├── services/dashboard-api.ts             ← P1-1 (cache), P1-3 (cashflow/mes)
│   └── components/
│       ├── orcamento-tab.tsx                  ← P0-2, P0-3
│       ├── gastos-por-cartao-box.tsx          ← P0-3
│       └── patrimonio-tab.tsx                 ← P2-2
└── features/plano/components/
    └── PlanoResumoCard.tsx                    ← P1-2

Backend (app_dev/backend/app/domains/)
└── plano/router.py                            ← P1-3 (novo endpoint /cashflow/mes)
```

---

*Gerado em: 2026-03 | Relacionado: `ANALISE_EFICIENCIA_APP.md` | Metodologia: `docs/WOW.md`*
