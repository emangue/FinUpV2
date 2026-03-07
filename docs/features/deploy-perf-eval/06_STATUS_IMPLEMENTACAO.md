# Status de Implementação — Performance Dashboard Mobile

**Última atualização:** 07/03/2026  
**Branch:** `perf/performance-v2-n0-n4`

---

## O que foi implementado nesta sessão

### N1 + N2: Cache em memória + deduplicação (_inflight) ✅
**Commit:** dentro do histórico da branch  
Adicionados em sessão anterior. Cobrem `fetchLastMonthWithData`, `fetchDashboardMetrics`, `fetchIncomeSources`, `fetchChartData`, `fetchChartDataYearly`, `fetchPlanoCashflowMes`, `fetchAporteInvestimentoDetalhado`, `fetchCreditCards`.

### N3: Prefetch de lastMonth antes do auth ✅
**Commit:** dentro do histórico da branch  
`page.tsx` dispara `fetchLastMonthWithData` imediatamente (sem esperar `isAuth`), guarda resultado em `_pendingLastMonth`. Quando auth confirma, usa o resultado já pronto — elimina 1 RTT sequencial no cold start (~25ms).

### N4: Sliding window cache + prefetch de vizinhos ✅
**Commit:** `4db0ca5a` — 07/03/2026  
**Arquivos:** `dashboard-api.ts`, `month-scroll-picker.tsx`, `page.tsx`

**Como funciona:**
- `_pointCache`: `Map<string, ChartDataPoint>` — cada ponto do gráfico armazenado por chave `YYYY-MM-01`
- `_chartWindow(year, month)`: computa as 7 chaves que o `BarChart` vai buscar
- `fetchChartData`: antes do API call, verifica se todos os 7 pontos da janela já estão no `_pointCache` → se sim, monta localmente (0 requests)
- `prefetchChartData`: dispara fetch em background sem bloquear UI
- `page.tsx`: ao mudar de mês, prefetch automático de anterior + posterior
- `MonthScrollPicker`: `onMonthHover` → prefetch imediato ao fazer hover em qualquer mês

**Resultado validado com dados reais da API (07/03/2026):**

| Chamada | Pontos | Formato date | Resultado |
|---------|--------|-------------|-----------|
| `chart-data?year=2025&month=3` (cold) | 12 | `YYYY-MM-01` ✅ | `_pointCache` populado com 12 pontos |
| `_chartWindow(2025, 3)` | 7 chaves | — | Todas contidas nos 12 da API ✅ |
| `_chartWindow(2025, 4)` após prefetch | 7 chaves | — | Todas no `_pointCache` → **0 API calls** ✅ |

**Sem regressão visual:** `BarChart.generateLast7Months()` busca cada ponto por `data.find(d => d.date === key)` — funciona igual com 7 ou 12 pontos no array.

---

## Latências medidas (localhost, 07/03/2026)

| Endpoint | Latência | Tamanho resposta |
|----------|----------|-----------------|
| `dashboard/metrics` | 26ms | 446 bytes |
| `dashboard/income-sources` | 25ms | 115 bytes |
| `dashboard/chart-data` | 50ms | 841 bytes |
| `dashboard/budget-vs-actual` | 26ms | 1.785 bytes |
| `dashboard/credit-cards` | 21ms | 75 bytes |
| `plano/cashflow/mes` | **95ms** | 453 bytes |
| `plano/aporte-investimento` | 20ms | 334 bytes |

> Nota: latências locais são ~5–10x menores que na VM real (VM em SP, sem overhead de rede). Na VM, esperar 20–50ms por endpoint.

---

## Análise: o que mais vale prefetchar?

### Por que `chart-data` foi priorizado (N4)

O gráfico histórico é o único dado que **compartilha 6/7 pontos entre meses consecutivos**. Navegar de Março → Abril reaproveita Set–Mar. Nenhum outro dado tem essa propriedade — metrics, receitas, despesas, cartões são totalmente diferentes por mês.

### Os outros dados do OrcamentoTab

O `OrcamentoTab` dispara em paralelo (Promise.all) ao montar:
- `fetchIncomeSources` → cache N1 (TTL 2min) ✅
- `fetchCreditCards` → cache N1 (TTL 2min) ✅
- `fetchPlanoCashflowMes` → cache N1 (TTL 5min) ✅
- `fetchAporteInvestimentoDetalhado` → cache N1 (TTL 2min) ✅
- `fetchOrcamentoInvestimentos` → **sem cache** ⚠️
- `fetchGoals` → **sem cache, sem _inflight** ⚠️

### Prefetch de vizinhos para os outros dados: não vale

| Dado | Mudança entre meses | Prefetch vale? |
|------|-------------------|---------------|
| `chart-data` | 6/7 pontos em comum | ✅ **Muito** |
| `metrics` | 100% diferente | ❌ Desperdiça bandwidth |
| `income-sources` | 100% diferente | ❌ |
| `budget-vs-actual` | 100% diferente | ❌ |
| `credit-cards` | 100% diferente | ❌ |
| `plano/cashflow/mes` | 100% diferente | ❌ |
| `aporte-investimento` | 100% diferente, mas fixo no ano | 🟡 Marginal (20ms) |

### O que faz sentido: adicionar cache a `fetchOrcamentoInvestimentos`

É a única função que chama a API sem `_getCache` / `_withInFlight`. Com o padrão existente, seria:

```typescript
// fetchOrcamentoInvestimentos — adicionar cache
const key = `orcamentoInvestimentos:${params}`
const cached = _getCache<OrcamentoInvestimentosResponse>(key, TTL_2MIN)
if (cached) return cached
return _withInFlight(key, async () => {
  const response = await fetchWithAuth(...)
  return _setCache(key, await response.json())
})
```

Impacto: evita re-fetch ao trocar de tab (Resultado ↔ Patrimônio) no mesmo mês.

### `plano/cashflow/mes` tem latência alta (95ms)

Único endpoint com latência significativamente maior (~95ms vs 20–50ms dos outros). Já tem cache N1 (TTL 5min). **Não requer prefetch** — o cache já absorve re-renders e troca de tab.

---

## Próximas ações pendentes

| Prioridade | Ação | Impacto esperado |
|------------|------|-----------------|
| 🔴 Alta | Adicionar cache a `fetchOrcamentoInvestimentos` | Elimina re-fetch na troca de tab |
| 🟡 Média | Verificar `goals-api.ts` — sem cache, retorna 404 em `/goals/?month=` | Pode estar gerando erros silenciosos |
| 🟢 Baixa | Deploy do N4 na VM | Ganho real em produção |

