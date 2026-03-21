# Sprint 1 — Frontend: Quick Wins

> **Escopo:** Frontend only. Sem novos endpoints, sem migrations.
> **Itens:** A3 · F3 · F4 · F5
> **Arquivos:** `page.tsx` · `month-scroll-picker.tsx` · `dashboard-api.ts`
> **Pré-requisito:** Nenhum (pode iniciar imediatamente)

---

## Índice

- [A3 — Fix scroll do mês](#a3--fix-scroll-do-mês)
- [F3 — Prefetch OrcamentoTab em meses adjacentes](#f3--prefetch-orcamentotab-em-meses-adjacentes)
- [F4 — Prefetch lastMonthWithData patrimônio](#f4--prefetch-lastmonthwithdata-patrimônio)
- [F5 — Fallback parcial no sliding window](#f5--fallback-parcial-no-sliding-window)

---

## A3 — Fix scroll do mês

**Problema:** O `MonthScrollPicker` aparece no mês atual e faz scroll suave até o mês com dados — o usuário vê o scroll acontecendo.
**Impacto:** UX — elimina scroll visível no carregamento.
**Arquivos:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx` · `app_dev/frontend/src/components/mobile/month-scroll-picker.tsx`

---

### Microação 1 — Guardar Promise (não resultado) no ref

**Arquivo:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx`

```typescript
// Antes
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
      const now = new Date()
      setSelectedMonth(new Date(now.getFullYear(), now.getMonth(), 1))
    })
}, [isAuth])
```

---

### Microação 2 — Skeleton em vez de `?? new Date()`

**Arquivo:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx`

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

Adicionar o componente skeleton no mesmo arquivo ou em `month-scroll-picker.tsx`:

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

### Microação 3 — Lista de meses centrada em `selectedMonth`

**Arquivo:** `app_dev/frontend/src/components/mobile/month-scroll-picker.tsx`

```typescript
// Antes — centrado em hoje, nunca recalcula
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

### Microação 4 — Scroll `instant` no mount, `smooth` nas interações

**Arquivo:** `app_dev/frontend/src/components/mobile/month-scroll-picker.tsx`

```typescript
// Antes — sempre smooth
React.useEffect(() => {
  if (selectedMonthRef.current && scrollContainerRef.current) {
    const container = scrollContainerRef.current
    const button = selectedMonthRef.current
    const scrollPosition = button.offsetLeft - container.offsetWidth / 2 + button.offsetWidth / 2
    container.scrollTo({ left: scrollPosition, behavior: 'smooth' })
  }
}, [selectedMonth])

// Depois — instant no mount, smooth nas mudanças do usuário
const isMountedRef = React.useRef(false)

React.useEffect(() => {
  if (selectedMonthRef.current && scrollContainerRef.current) {
    const container = scrollContainerRef.current
    const button = selectedMonthRef.current
    const scrollPosition = button.offsetLeft - container.offsetWidth / 2 + button.offsetWidth / 2
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

- [ ] Picker NÃO aparece no mês atual antes de mover para o mês com dados
- [ ] Skeleton aparece enquanto `selectedMonth` é null (deve durar < 100ms)
- [ ] Navegar para meses fora do range original funciona (lista se recalcula)
- [ ] Clicar em um mês tem animação smooth
- [ ] Abrir o dashboard direto no mês correto sem nenhum scroll visível

---

## F3 — Prefetch OrcamentoTab em meses adjacentes

**Problema:** Prefetch atual cobre apenas `chart-data`. Ao navegar para mês adjacente, `OrcamentoTab` ainda faz requests novos para income-sources, credit-cards e orcamento-investimentos.
**Impacto:** Elimina 3 RTTs na navegação entre meses.
**Arquivo:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx`

---

### Microação 1 — Adicionar endpoints do OrcamentoTab ao prefetch de vizinhos

```typescript
// No useEffect do prefetch adjacente (já existente em page.tsx)
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

> **Nota:** Esse prefetch só faz sentido se `fetchIncomeSources`, `fetchExpenseSources` e `fetchOrcamentoInvestimentos` tiverem cache em memória. `fetchIncomeSources` já tem (N1). `fetchOrcamentoInvestimentos` e `fetchExpenseSources` precisam (ver Sprint 2 — B4).

---

### Checklist F3

- [ ] Navegar para mês anterior/próximo não dispara novos requests no OrcamentoTab
- [ ] Erro de prefetch não quebra a UI (`.catch(() => {})`)
- [ ] Prefetch dispara no change do `selectedMonth`, não no mount

---

## F4 — Prefetch lastMonthWithData patrimônio

**Problema:** `lastMonthWithData('patrimonio')` é buscado lazily quando PatrimonioTab abre. Um prefetch junto com o de `transactions` elimina 1 RTT.
**Impacto:** ~20–50ms de redução no primeiro carregamento da PatrimonioTab.
**Arquivo:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx`

---

### Microação 1 — Iniciar ambas as promises no mount

```typescript
// Antes: só transactions
const _lastMonthPromise = useRef<Promise<{ year: number; month: number }> | null>(null)
useEffect(() => {
  _lastMonthPromise.current = fetchLastMonthWithData('transactions')
}, [])

// Depois: ambas em paralelo
const _lastMonthPromise = useRef<Promise<{ year: number; month: number }> | null>(null)
const _lastMonthPatrimonioPromise = useRef<Promise<{ year: number; month: number }> | null>(null)

useEffect(() => {
  _lastMonthPromise.current = fetchLastMonthWithData('transactions')
  _lastMonthPatrimonioPromise.current = fetchLastMonthWithData('patrimonio')
}, [])
```

---

### Microação 2 — Passar a promise para PatrimonioTab (se aplicável)

Se `PatrimonioTab` busca `lastMonthWithData('patrimonio')` internamente, repassar a promise via prop ou context para evitar fetch duplicado:

```typescript
// Em page.tsx — passar ref como prop para PatrimonioTab
<PatrimonioTab
  lastMonthPatrimonioPromise={_lastMonthPatrimonioPromise.current}
/>

// Em PatrimonioTab — consumir se disponível
useEffect(() => {
  const promise = lastMonthPatrimonioPromise ?? fetchLastMonthWithData('patrimonio')
  promise.then(setLastMonth)
}, [])
```

---

### Checklist F4

- [ ] `fetchLastMonthWithData('patrimonio')` dispara no mount (antes do auth, igual ao de transactions)
- [ ] PatrimonioTab usa a promise já em andamento, não inicia nova
- [ ] DevTools: apenas 1 request para `last-month?type=patrimonio` no load

---

## F5 — Fallback parcial no sliding window (N4a)

**Problema:** Se qualquer 1 dos 7 pontos do chart estiver ausente do `_pointCache`, o N4a faz fetch completo (12 queries SQL). Com fallback parcial, busca apenas os pontos faltantes.
**Impacto:** Reduz fetches desnecessários após navegação não-linear entre meses.
**Arquivo:** `app_dev/frontend/src/features/dashboard/services/dashboard-api.ts`

---

### Microação 1 — Implementar busca diferenciada por número de misses

```typescript
// Em fetchChartData(), após gerar as 7 keys:
const keys = _chartWindow(year, month)
const missingKeys = keys.filter(k => !_pointCache.has(k))

if (missingKeys.length === 0) {
  // Cache hit total — 0 requests
  return keys.map(k => _pointCache.get(k)!)
}

// Miss parcial ou total — busca a janela completa (popula mais pontos no cache)
await _fetchAndPopulatePointCache(year, month)
return keys.map(k => _pointCache.get(k)!)
```

> **Nota:** A simplificação acima é suficiente e mais robusta que tentar buscar apenas os pontos faltantes (o endpoint retorna 12 meses de uma vez, então buscar a janela completa é o comportamento correto).

---

### Checklist F5

- [ ] `_pointCache` com 7/7 pontos: 0 requests (invariante do N4, não deve quebrar)
- [ ] `_pointCache` com 3/7 pontos: 1 request completo (igual ao comportamento atual)
- [ ] `_pointCache` com 0/7 pontos: 1 request completo
- [ ] Navegação não-linear (pular vários meses) não gera múltiplos requests simultâneos

---

## Resumo do Sprint 1

| Item | Arquivo(s) | Risco |
|------|-----------|-------|
| A3 — Fix scroll do mês | `page.tsx`, `month-scroll-picker.tsx` | Baixo |
| F3 — Prefetch OrcamentoTab | `page.tsx` | Baixo |
| F4 — Prefetch lastMonth patrimônio | `page.tsx` | Baixo |
| F5 — Fallback parcial sliding window | `dashboard-api.ts` | Baixo |

**Ordem sugerida:** F5 → F4 → A3 → F3
(F5 é isolada em `dashboard-api.ts`; F4 é 2 linhas; A3 é o mais complexo; F3 depende de cache do Sprint 2 para funcionar bem)
