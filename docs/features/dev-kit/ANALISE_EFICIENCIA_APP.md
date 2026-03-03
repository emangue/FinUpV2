# Mapeamento de Eficiência — App Mobile FinUp

**Data:** 2026-03-02  
**Escopo:** Frontend completo (`app_dev/frontend/src/`) + padrões de API  
**Referência anterior:** `ANALISE_MONTH_SCROLL_INIT.md` (problema do mês inicial — P0 isolado)

---

## Resumo Executivo

Foram encontrados **11 problemas de eficiência** classificados em 3 prioridades. Os mais críticos causam **chamadas de API duplicadas na mesma tela** ou **chamadas com dados descartados** a cada abertura de página.

| Prioridade | Qtde | Impacto resumido |
|---|---|---|
| **P0 — Crítico** | 4 | Chamadas duplicadas / descartadas em toda abertura do app |
| **P1 — Alto** | 4 | Re-fetches desnecessários e dados buscados em excesso |
| **P2 — Médio** | 3 | Ausência de cache, cold start, padrões sub-ótimos |

---

## P0 — Crítico (chamadas desperdiçadas em toda abertura)

---

### P0-1 · Dashboard: mês inicial errado → 10 chamadas viram 5 (documentado)

> **Referência:** `ANALISE_MONTH_SCROLL_INIT.md`

**Problema:** 5 hooks de dados disparam com o mês atual antes de `fetchLastMonthWithData` resolver. Quando o resultado chega (`~80 ms`), todos os 5 disparam novamente com o mês correto.

**Custo atual (pior caso — início de mês):**
```
t=0ms  → 5 chamadas com mês errado (ex: mar/2026)
t=80ms → 5 chamadas canceladas, 5 novas com mês certo (jan/2026)
         + animação dupla no MonthScrollPicker
```

**Arquivos:**  
- [app/mobile/dashboard/page.tsx](app_dev/frontend/src/app/mobile/dashboard/page.tsx#L37)  
- [features/dashboard/hooks/use-dashboard.ts](app_dev/frontend/src/features/dashboard/hooks/use-dashboard.ts)

---

### P0-2 · Dashboard: `income-sources` buscado duas vezes na mesma tela

**Problema:** O dado de receitas por fonte é buscado **duas vezes independentemente** para o mesmo `year/month`:

```
dashboard/page.tsx
├─ useIncomeSources(year, month)          → GET /income-sources ①
│   (só o loading é usado — .sources nunca é lido no page.tsx)
│
└─ <OrcamentoTab year={year} month={month}>
       └─ fetchIncomeSources(year, month) → GET /income-sources ②  ← DUPLICATA
```

**Evidência:**
```typescript
// dashboard/page.tsx linha 60 — usa apenas "loading", descarta "sources":
const { loading: loadingSources } = useIncomeSources(year, month)

// orcamento-tab.tsx linha 101 — busca o mesmo dado:
fetchIncomeSources(year, month ?? undefined),
```

**Custo:** 1 chamada extra por abertura da aba Resultado (sempre visível).

**Arquivos:**  
- [app/mobile/dashboard/page.tsx](app_dev/frontend/src/app/mobile/dashboard/page.tsx#L60)  
- [features/dashboard/components/orcamento-tab.tsx](app_dev/frontend/src/features/dashboard/components/orcamento-tab.tsx#L101)

---

### P0-3 · Dashboard: `credit-cards` buscado duas vezes na mesma tela

**Problema:** O dado de gastos por cartão é buscado em **dois níveis da árvore** para o mesmo `year/month`:

```
OrcamentoTab (nível 1)
├─ fetchCreditCards(year, month)          → GET /credit-cards ①
│   (usa só o total — .reduce para cardsTotal)
│
└─ <GastosPorCartaoBox year={year} month={month}>
       └─ fetchCreditCards(year, month)   → GET /credit-cards ②  ← DUPLICATA
```

**Evidência:**
```typescript
// orcamento-tab.tsx linha 103:
fetchCreditCards(year, month ?? undefined),

// gastos-por-cartao-box.tsx linha 56:
fetchCreditCards(year, month)
  .then(setCards)
```

**Custo:** 1 chamada extra sempre que o collapse "Gastos por Cartão" é exibido (acontece por padrão na aba Resultado).

**Arquivos:**  
- [features/dashboard/components/orcamento-tab.tsx](app_dev/frontend/src/features/dashboard/components/orcamento-tab.tsx#L103)  
- [features/dashboard/components/gastos-por-cartao-box.tsx](app_dev/frontend/src/features/dashboard/components/gastos-por-cartao-box.tsx#L56)

---

### P0-4 · Dashboard: ambos `chart-data` e `chart-data-yearly` disparam sempre

**Problema:** O dashboard sempre executa **ambos** os hooks de gráfico, mas só **um** é exibido dependendo do período (`month`, `ytd`, `year`):

```typescript
// dashboard/page.tsx — ambos sempre executam:
const { chartData: chartDataMonthly }  = useChartData(...)       // GET /chart-data
const { chartData: chartDataYearly }   = useChartDataYearly(...) // GET /chart-data-yearly

// Apenas um é usado:
const chartData = period === 'month' ? chartDataMonthly : chartDataYearly
```

**Custo:** 1 chamada de gráfico sempre descartada. No modo `month` (padrão): `chart-data-yearly` nunca é exibido mas sempre busca dados. No modo `ytd`/`year`: `chart-data` nunca é exibido mas sempre busca dados.

**Nota:** `useChartDataYearly` aguarda `yearsList` (que depende de `lastMonthWithData`), então em geral resolve depois — mas a chamada ainda é feita desnecessariamente.

**Arquivos:**  
- [app/mobile/dashboard/page.tsx](app_dev/frontend/src/app/mobile/dashboard/page.tsx#L64)

---

## P1 — Alto (re-fetches e excessos evitáveis)

---

### P1-1 · `fetchLastMonthWithData` chamado em 6 lugares sem nenhum cache

**Problema:** O endpoint `GET /dashboard/last-month-with-data` é chamado de forma independente em **6 páginas distintas**, sem qualquer compartilhamento de estado ou cache:

| Página/componente | Source | Arquivo |
|---|---|---|
| `/mobile/dashboard` | `transactions` | [dashboard/page.tsx](app_dev/frontend/src/app/mobile/dashboard/page.tsx#L81) |
| `/mobile/budget` | `transactions` | [budget/page.tsx](app_dev/frontend/src/app/mobile/budget/page.tsx#L67) |
| `/mobile/budget/manage` | `transactions` | [budget/manage/page.tsx](app_dev/frontend/src/app/mobile/budget/manage/page.tsx#L19) |
| `/mobile/carteira` | `patrimonio` | [carteira/page.tsx](app_dev/frontend/src/app/mobile/carteira/page.tsx#L255) |
| `/mobile/investimentos` | `patrimonio` | [investimentos/page.tsx](app_dev/frontend/src/app/mobile/investimentos/page.tsx#L64) |
| `PersonalizarPlanoLayout` | `patrimonio` | [PersonalizarPlanoLayout.tsx](app_dev/frontend/src/features/plano-aposentadoria/components/PersonalizarPlanoLayout.tsx#L1151) |

**Custo:** Cada vez que o usuário navega entre dashboard → budget → manage, **3 chamadas idênticas** são feitas ao mesmo endpoint. Dado que `last-month-with-data` é estático por sessão (o dado raramente muda durante uso), essas chamadas poderiam ser cacheadas por no mínimo 5 minutos.

---

### P1-2 · `/mobile/plano`: `getResumoPlano` chamado duas vezes

**Problema:** A página `/mobile/plano` chama `getResumoPlano` para o check de isEmpty, e em seguida `PlanoResumoCard` (filho) chama de novo para exibir:

```
PlanoHubPage (parent)
├─ getResumoPlano(year, month)   → GET /plano/resumo ①  (só para isEmpty check)
├─ getOrcamento(year, month)     → GET /plano/orcamento ①
│
└─ <PlanoResumoCard year={year} month={month}>
       ├─ getResumoPlano(year, month)              → GET /plano/resumo ②  ← DUPLICATA
       ├─ fetchIncomeSources(year, month)          → GET /income-sources
       ├─ fetchGoals(selectedMonth)                → GET /budget/planning
       └─ fetchAporteInvestimentoDetalhado(year, month) → GET /plano/aporte-investimento
```

**Custo:** 1 chamada extra de `/plano/resumo` a cada abertura de `/mobile/plano`.

**Arquivos:**  
- [app/mobile/plano/page.tsx](app_dev/frontend/src/app/mobile/plano/page.tsx#L30)  
- [features/plano/components/PlanoResumoCard.tsx](app_dev/frontend/src/features/plano/components/PlanoResumoCard.tsx#L41)

---

### P1-3 · `fetchPlanoCashflowMes` busca ano inteiro para extrair 1 mês

**Problema:** A função `fetchPlanoCashflowMes(year, mesRef)` em `dashboard-api.ts` chama o endpoint do **cashflow do ano inteiro** e depois filtra localmente para extrair apenas um mês:

```typescript
// dashboard-api.ts (fetchPlanoCashflowMes)
const response = await fetchWithAuth(`${BASE_URL}/plano/cashflow?ano=${year}&modo_plano=true`)
// retorna 12 meses...
const mes = (data.meses ?? []).find((m: any) => { ... mm === month })
// usa apenas 1 dos 12 meses
```

**Custo:**  
- Payload de rede: ~12x maior do que o necessário  
- Backend: processa 12 meses de dados quando só 1 é necessário  
- Isso é chamado em `OrcamentoTab` para cada abertura do dashboard

**Solução simples:** Adicionar `?mes=MM` ao endpoint `/plano/cashflow` (ou criar `/plano/cashflow/mes?ano=YYYY&mes=MM`).

**Arquivos:**  
- [features/dashboard/services/dashboard-api.ts](app_dev/frontend/src/features/dashboard/services/dashboard-api.ts#L122)

---

### P1-4 · Transactions: 3 chamadas simultâneas em todo filter change, sem debounce em período

**Problema:** A tela de transações tem 3 fetches separados que disparam **juntos** a cada mudança de filtro:

```typescript
// transactions/page.tsx — 3 useEffects que dependem de filters:
useEffect(() => {
  fetchTransactions()   // GET /transactions/list?...   ①
  fetchResumo()         // GET /transactions/resumo?... ②
}, [fetchTransactions, fetchResumo])

useEffect(() => {
  if (gastosOpen) fetchGastosPorGrupo()  // GET /transactions/gastos-por-grupo?... ③
}, [gastosOpen, fetchGastosPorGrupo])
```

**O debounce de 300 ms existe apenas para `searchQuery`** (campo de texto). Mudanças nos selects de período (`yearInicio`, `monthInicio`, etc.) disparam imediatamente — o que pode gerar 3 chamadas a cada clique de select.

**Custo por mudança de período:** 3 chamadas de rede simultâneas. Se o usuário mudar mês + ano (2 interações), pode disparar 6 chamadas em 500ms.

**Arquivos:**  
- [app/mobile/transactions/page.tsx](app_dev/frontend/src/app/mobile/transactions/page.tsx#L175)

---

## P2 — Médio (arquitetura e cold starts)

---

### P2-1 · Ausência total de cache client-side

**Problema:** Não há nenhuma camada de cache entre o React e a API. Cada navegação entre telas refaz todas as chamadas do zero:

- Sem `React Query` / `SWR` com TTL
- Sem `localStorage` como cache de curta duração (exceto a sugestão do `ANALISE_MONTH_SCROLL_INIT.md` para lastMonth)
- Sem `sessionStorage` para dados da sessão (lastMonthWithData, grupos, etc.)

**Exemplo concreto:**  
Dashboard → Budget → Dashboard: o dashboard refaz **todas** as chamadas novamente, incluindo `last-month-with-data`, `metrics`, `income-sources`, `budget-vs-actual`, `chart-data`, `chart-data-yearly`.

**Impacto:**
- Usuário percebe loading em toda navegação de volta
- Backend recebe carga desnecessária (dados raramente mudam em segundos)
- `fetchLastMonthWithData` é o caso mais óbvio: é imutável por sessão

**Quick win sem React Query:** Cache de módulo singleton para `lastMonthWithData`:

```typescript
// dashboard-api.ts
const _cache = new Map<string, { value: any; ts: number }>()
const TTL_MS = 5 * 60 * 1000 // 5 minutos

export async function fetchLastMonthWithData(source: LastMonthSource) {
  const key = `lastMonth:${source}`
  const hit = _cache.get(key)
  if (hit && Date.now() - hit.ts < TTL_MS) return hit.value
  const response = await fetchWithAuth(...)
  const value = await response.json()
  _cache.set(key, { value, ts: Date.now() })
  return value
}
```

---

### P2-2 · PatrimonioTab: 3 chamadas cold start ao clicar na aba

**Problema:** `PatrimonioTab` está condicionalmente renderizado (`{activeTab === 'patrimonio' && <PatrimonioTab />}`), o que é correto. Porém, ao clicar em "Patrimônio" pela primeira vez, 3 chamadas disparam **simultaneamente** antes do usuário ver qualquer conteúdo:

```
click "Patrimônio"
    ├─ getPatrimonioTimeline({ano_inicio, ano_fim})  → GET /investimentos/timeline
    ├─ getDistribuicaoPorTipo({ classe_ativo: 'Ativo' })   → GET /investimentos/distribuicao
    └─ getDistribuicaoPorTipo({ classe_ativo: 'Passivo' }) → GET /investimentos/distribuicao
```

Sendo que o gráfico (`PatrimonioChart`) não pode renderizar até `getPatrimonioTimeline` resolver, e a distribuição ativo/passivo fica em um Collapsible fechado por padrão — ou seja, as 2 últimas chamadas podem ser adiadas.

**Melhoria:** Buscar `getPatrimonioTimeline` imediatamente; buscar `getDistribuicaoPorTipo` apenas quando o Collapsible for aberto (já é `defaultOpen={false}`).

**Arquivos:**  
- [features/dashboard/components/patrimonio-tab.tsx](app_dev/frontend/src/features/dashboard/components/patrimonio-tab.tsx#L67)

---

### P2-3 · `useIncomeSources` e `useExpenseSources` no dashboard só usam loading

**Problema:** O dashboard/page.tsx mantém hooks completos de `income-sources` e `expense-sources` apenas para rastrear `loading`, mas **não usa os dados retornados** (as fontes vêm de dentro de `OrcamentoTab`):

```typescript
// dashboard/page.tsx — dados descartados, só loading usado:
const { loading: loadingSources } = useIncomeSources(year, month)  // 🗑️ sources descartado
const { loading: loadingExpenses } = useExpenseSources(year, month) // 🗑️ sources descartado
```

Isso faz duas chamadas desnecessárias cujos dados são descartados — o loading poderia ser rastreado de outra forma (por exemplo, o próprio `OrcamentoTab` expor um callback de pronto, ou o `isLoading` do dashboard basear-se apenas em `metrics` + `chart`).

**Arquivos:**  
- [app/mobile/dashboard/page.tsx](app_dev/frontend/src/app/mobile/dashboard/page.tsx#L60)

---

## Mapa Completo de Chamadas por Tela

### `/mobile/dashboard` (abertura — pior caso, início de mês)

```
t=0ms
 ├─ GET /dashboard/last-month-with-data?source=transactions
 ├─ GET /dashboard/metrics?year=2026&month=3          ← MÊS ERRADO (descartado)
 ├─ GET /dashboard/income-sources?year=2026&month=3   ← MÊS ERRADO (descartado) [P0-1]
 ├─ GET /dashboard/budget-vs-actual?year=2026&month=3 ← MÊS ERRADO (descartado) [P0-1]
 ├─ GET /dashboard/chart-data?year=2026&month=3       ← MÊS ERRADO (descartado) [P0-1]
 └─ GET /dashboard/chart-data-yearly?years=...        ← pode ou não ser descartado [P0-4]

t=80ms (last-month-with-data resolve → jan/2026)
 ├─ GET /dashboard/metrics?year=2026&month=1          ← correto
 ├─ GET /dashboard/income-sources?year=2026&month=1   ← correto [mas duplicado abaixo]
 ├─ GET /dashboard/budget-vs-actual?year=2026&month=1 ← correto
 ├─ GET /dashboard/chart-data?year=2026&month=1       ← correto
 └─ GET /dashboard/chart-data-yearly?years=...        ← correto [mas não usado no modo 'month']

t=80ms (OrcamentoTab monta com year/month corretos)
 ├─ GET /dashboard/income-sources?year=2026&month=1   ← DUPLICATA [P0-2]
 ├─ GET /budget/planning?mes_referencia=2026-01       ← metas/goals
 ├─ GET /dashboard/credit-cards?year=2026&month=1     ← correto [mas duplicado abaixo]
 ├─ GET /plano/cashflow?ano=2026&modo_plano=true       ← 12 meses para extrair 1 [P1-3]
 └─ GET /plano/aporte-investimento?ano=2026&mes=1

t=80ms (GastosPorCartaoBox monta)
 └─ GET /dashboard/credit-cards?year=2026&month=1     ← DUPLICATA [P0-3]

TOTAL PIOR CASO: ~16 chamadas (6 descartadas + 2 duplicadas + 1 superdimensionada)
TOTAL IDEAL:      8 chamadas
```

---

### `/mobile/transactions` (mudança de filtro)

```
Usuário clica em "Fev/2026" no select:
 ├─ GET /transactions/list?year=2026&month=2&limit=500
 ├─ GET /transactions/resumo?year=2026&month=2
 └─ GET /transactions/gastos-por-grupo?year=2026&month=2  (se collapse aberto)

Usuário clica em "2025" no select de ano (500ms depois):
 ├─ GET /transactions/list?year=2025&month=2&limit=500
 ├─ GET /transactions/resumo?year=2025&month=2
 └─ GET /transactions/gastos-por-grupo?year=2025&month=2  (se collapse aberto)

TOTAL: 6 chamadas para 2 mudanças de select, sem debounce [P1-4]
```

---

### `/mobile/plano` (abertura)

```
 ├─ GET /plano/resumo?ano=2026&mes=3     ← isEmpty check
 ├─ GET /plano/orcamento?ano=2026&mes=3  ← isEmpty check
 │
 └─ PlanoResumoCard monta:
     ├─ GET /plano/resumo?ano=2026&mes=3     ← DUPLICATA [P1-2]
     ├─ GET /dashboard/income-sources?...
     ├─ GET /budget/planning?...
     └─ GET /plano/aporte-investimento?...
 │
 ├─ TabelaReciboAnual: GET /plano/cashflow?ano=2026   ← 12 meses
 ├─ ProjecaoChart: GET /plano/projecao?...
 ├─ AnosPerdidasCard: GET /plano/impacto-longo-prazo?...
 └─ OrcamentoCategorias: GET /plano/orcamento?...     ← já buscado acima
```

---

## Plano de Ação Priorizado

### Fase 1 — Quick Wins (P0, baixo risco, alto impacto)

| # | Ação | Esforço | Impacto |
|---|---|---|---|
| 1 | **P0-1:** Implementar `selectedMonth = null` + guard nos hooks | Médio | -5 a -10 chamadas por abertura do dashboard |
| 2 | **P0-2:** Remover `useIncomeSources` do dashboard/page.tsx; deixar só em OrcamentoTab | Baixo | -1 chamada por abertura |
| 3 | **P0-3:** Passar `cards` como prop de `OrcamentoTab` para `GastosPorCartaoBox` | Baixo | -1 chamada por abertura |
| 4 | **P0-4:** Usar hook condicional: `useChartData` só quando `period === 'month'`; `useChartDataYearly` só quando `period !== 'month'` | Baixo | -1 chamada por abertura |

### Fase 2 — Cache de sessão (P1-1)

| # | Ação | Esforço | Impacto |
|---|---|---|---|
| 5 | **P1-1:** Cache de módulo singleton (5 min TTL) para `fetchLastMonthWithData` | Baixo | -1 a -3 chamadas por navegação entre telas |
| 6 | **P1-4:** Debounce de 300ms nos selects de período em transactions | Baixo | -2 a -4 chamadas por interação |

### Fase 3 — Refatoração de componentes (P1, médio prazo)

| # | Ação | Esforço | Impacto |
|---|---|---|---|
| 7 | **P1-2:** Passar `resumo` como prop para `PlanoResumoCard` (não buscar novamente) | Médio | -1 chamada por abertura de /plano |
| 8 | **P1-3:** Endpoint `/plano/cashflow/mes` ou parâmetro `?mes=MM` para buscar 1 mês | Médio | Payload -91% quando só 1 mês é necessário |
| 9 | **P2-3:** Remover `useIncomeSources`/`useExpenseSources` do dashboard; rastrear loading de dentro do OrcamentoTab via callback | Médio | -2 chamadas desnecessárias + 1 chamada poupada (redundante com OrcamentoTab) |
| 10 | **P2-2:** Lazy load das distribuições de PatrimonioTab (só buscar ao abrir Collapsible) | Baixo | -2 chamadas no cold start da aba Patrimônio |

### Fase 4 — Cache global (P2-1, maior prazo)

| # | Ação | Esforço | Impacto |
|---|---|---|---|
| 11 | **P2-1:** Instalar `React Query` ou `SWR`; adicionar TTL de 2-5 min para todas as rotas de leitura do dashboard | Alto | Elimina re-fetches na navegação entre telas |

---

## Ganho estimado por fase

| Estado | Chamadas na abertura do dashboard (pior caso) | Chamadas na troca de filtro (transactions) |
|---|---|---|
| **Hoje** | ~16 | 3–6 por interação (sem debounce) |
| **Após Fase 1** | ~8–9 | 3 por interação |
| **Após Fase 2** | ~7–8 | 1–2 por interação (com debounce) |
| **Após Fase 3** | ~6 | 1–2 por interação |
| **Após Fase 4** | ~2–3 (dados cacheados) | 0 (cache) |

---

## O que NÃO mudar

- `fetchGoals` em `OrcamentoTab` é correto — `budget_planning` é a fonte de orçamento, diferente de `budget-vs-actual`
- `PatrimonioTab` renderizado condicionalmente está certo — não pré-renderizar
- Os hooks de dashboard com cleanup (`cancelled = true`) estão corretos e previnem race conditions
- A lógica de period (`month` / `ytd` / `year`) no dashboard é necessária — só o lazy loading precisa ser adicionado
- `fetchOrcamentoInvestimentos` chamado por `OrcamentoTab` apenas no modo ano/ytd está correto — sem duplicação nesses modos
