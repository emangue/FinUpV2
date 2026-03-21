# Plano: Sliding Window Cache + Prefetch de Meses (N4)

**Data:** 07/03/2026

## Contexto

Ao trocar de mês no dashboard, `fetchChartData(year, month)` sempre dispara um novo request ao backend mesmo que 6 dos 7 pontos do gráfico histórico já tenham sido retornados em chamadas anteriores. O cache atual funciona por chave completa (`chartData:year=2025&month=3`), então trocar para Abril gera um cache miss mesmo com 6 meses em comum.

A solução combina duas técnicas:

**A. Sliding window cache (individual point cache)**
Cada `ChartDataPoint` é armazenado individualmente por data (`YYYY-MM-01`). Na próxima chamada, se todos os 7 meses necessários já estiverem no cache individual → monta o array localmente sem nenhum request.

**B. Prefetch de vizinhos (N4)**
Quando o usuário seleciona um mês, dispara imediatamente em background os fetches do mês anterior e posterior. Quando navegar, a resposta já está no cache. Combinado com A: o prefetch popula o ponto "faltante" no sliding window, tornando a próxima navegação 100% local.

**Fluxo resultante (sequencial):**
- Usuário abre Março → 1 API call → caches Set24–Mar25 individualmente → prefetch faz Feb + Apr
- Clica em Abril → todos os 7 meses (Out24–Abr25) já no _pointCache → 0 API calls
- _pointCache de Abril já está completo → prefetch dispara Mar + Maio
- Clica em Maio → 0 API calls. E assim por diante.

---

## Validação do caminho escolhido (pesquisa web)

| Padrão | Status | Referência |
|--------|--------|------------|
| Sliding window cache | ✅ Comprovado | Patent US9141723, implementações ativas no GitHub |
| Prefetch de vizinhos | ✅ Conceito validado | Next.js prefetching, Relay bidirectional pagination |
| SWR / React Query | ✅ Alternativa mais robusta | Stripe usa SWR + ISR em dashboards financeiros |

**Por que não migrar para SWR/React Query agora?**
O projeto já tem um cache próprio bem estruturado (`_cache`, `_inflight`, TTL). A migração exigiria refatorar todos os hooks — escopo amplo demais para este momento. As técnicas planejadas são exatamente o que SWR/React Query fariam internamente — mesma lógica, sem a dependência.

---

## Arquivos a modificar

| Arquivo | Mudança |
|---------|---------|
| `app_dev/frontend/src/features/dashboard/services/dashboard-api.ts` | Adicionar `_pointCache`, montar sliding window em `fetchChartData`, adicionar `prefetchChartData` |
| `app_dev/frontend/src/components/mobile/month-scroll-picker.tsx` | Adicionar prop `onMonthHover?: (month: Date) => void` |
| `app_dev/frontend/src/app/mobile/dashboard/page.tsx` | Prefetch no change de selectedMonth + wiring de onMonthHover |

---

## Passo 1 — `dashboard-api.ts`: _pointCache + sliding window

### 1a. Adicionar `_pointCache`

Após os Maps existentes (`_cache`, `_inflight`):

```typescript
// Cache por ponto individual — chave: "YYYY-MM-01"
// Permite montar janelas de 7 meses sem nova request quando todos os pontos já foram vistos.
const _pointCache = new Map<string, ChartDataPoint>()
```

### 1b. Helper: computar janela de 7 meses

```typescript
function _chartWindow(year: number, month: number): string[] {
  const keys: string[] = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(year, month - 1 - i, 1)
    keys.push(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`)
  }
  return keys
}
```

### 1c. Modificar `fetchChartData`

```typescript
export async function fetchChartData(year: number, month?: number): Promise<ChartDataPoint[]> {
  // 1. Tenta montar da janela individual (só aplica ao modo mensal)
  if (month) {
    const keys = _chartWindow(year, month)
    if (keys.every(k => _pointCache.has(k))) {
      return keys.map(k => _pointCache.get(k)!)
    }
  }

  // 2. Cache da resposta completa (chave por parâmetros)
  const params = new URLSearchParams({ year: year.toString() })
  if (month) params.append('month', month.toString())
  const key = `chartData:${params}`
  const cached = _getCache<ChartDataPoint[]>(key, TTL_5MIN)
  if (cached) return cached

  // 3. API call com deduplicação
  return _withInFlight(key, async () => {
    const response = await fetchWithAuth(`${BASE_URL}/dashboard/chart-data?${params}`)
    if (!response.ok) throw new Error(`Failed to fetch chart data: ${response.status}`)
    const result = await response.json()
    const data: ChartDataPoint[] = result.data || []
    // Popula _pointCache com cada ponto retornado
    for (const point of data) {
      _pointCache.set(point.date, point)
    }
    return _setCache(key, data)
  })
}
```

### 1d. Adicionar `prefetchChartData`

```typescript
export function prefetchChartData(year: number, month: number): void {
  fetchChartData(year, month).catch(() => {})
}
```

### 1e. Limpar `_pointCache` em `invalidateDashboardCache`

```typescript
export function invalidateDashboardCache() {
  _cache.clear()
  _inflight.clear()
  _pointCache.clear()  // ← adicionar
}
```

---

## Passo 2 — `month-scroll-picker.tsx`: prop onMonthHover

```typescript
interface MonthScrollPickerProps {
  selectedMonth: Date
  onMonthChange: (month: Date) => void
  onMonthHover?: (month: Date) => void  // ← novo
  monthsRange?: number
  className?: string
}
```

Adicionar `onMouseEnter` em cada botão de mês:

```typescript
<button
  onMouseEnter={() => onMonthHover?.(month)}
  onClick={() => onMonthChange(month)}
  ...
>
```

---

## Passo 3 — `page.tsx`: prefetch de vizinhos

### 3a. Importar `prefetchChartData`

```typescript
import { fetchLastMonthWithData, prefetchChartData } from '@/features/dashboard/services/dashboard-api'
```

### 3b. useEffect: prefetch ao mudar de mês

```typescript
// N4: pré-busca mês anterior e posterior (popula _pointCache para navegação instantânea)
useEffect(() => {
  if (!selectedMonth || period !== 'month') return
  const prev = new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() - 1, 1)
  const next = new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() + 1, 1)
  prefetchChartData(prev.getFullYear(), prev.getMonth() + 1)
  prefetchChartData(next.getFullYear(), next.getMonth() + 1)
}, [selectedMonth, period])
```

### 3c. onMonthHover no MonthScrollPicker

```tsx
<MonthScrollPicker
  selectedMonth={selectedMonth ?? new Date()}
  onMonthChange={setSelectedMonth}
  onMonthHover={(month) => {
    if (period === 'month') prefetchChartData(month.getFullYear(), month.getMonth() + 1)
  }}
/>
```

---

## O que NÃO muda

- Nenhuma mudança no backend
- `fetchChartDataYearly` não precisa de sliding window (modo anual — não é scroll rápido)
- `fetchDashboardMetrics`, `OrcamentoTab`, etc. não são prefetchados (dados específicos do mês, não histórico)
- TTL e `_inflight` existentes continuam sem alteração

---

## Verificação

1. Abrir dashboard mobile → selecionar Março
2. Verificar no DevTools Network que Fevereiro e Abril são prefetchados em background
3. Clicar em Abril → verificar que **não há** nova request de `chart-data` (servido do _pointCache)
4. Hover em um mês visível → verificar que prefetch dispara imediatamente
5. `invalidateDashboardCache()` (chamado no upload) → verificar que `_pointCache` também é limpo
