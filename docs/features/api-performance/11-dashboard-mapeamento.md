# Dashboard — Mapeamento Completo, Bugs e Performance

> Tela: `localhost:3000/mobile/dashboard`
> Data: Março/2026
> Metodologia: mesma análise feita para a tela de Plano (doc 10).

---

## Mapa de APIs no Mount

### Sequência de inicialização

```
Page monta
  ├── prefetch fetchLastMonthWithData('transactions')  ← sem await, sem auth
  │   (guarda a Promise em _lastMonthPromise.current)
  └── fetch /auth/me (useRequireAuth)

auth resolve
  └── await _lastMonthPromise → setSelectedMonth(fev/2026)
      └── enabled = true → dispara hooks principais

selectedMonth resolvido
  ├── useDashboardMetrics   → GET /dashboard/metrics     (TTL 2min, dedup ✅)
  ├── useChartData          → GET /dashboard/chart-data  (TTL 5min + N4a, dedup ✅)  [só se period='month']
  └── useChartDataYearly    → GET /dashboard/chart-data-yearly  (TTL 5min, dedup ✅)  [só se period≠'month']

OrcamentoTab monta (Resultado — imediato)
  ├── fetchIncomeSources        → GET /dashboard/income-sources    (TTL 2min, dedup ✅)
  ├── fetchExpenseSources       → GET /dashboard/budget-vs-actual  (TTL 2min, dedup ✅)
  ├── fetchCreditCards          → GET /dashboard/credit-cards      (TTL 2min, dedup ✅)
  ├── fetchOrcamentoInvestimentos → GET /dashboard/orcamento-investimentos (TTL 2min, dedup ✅)
  └── fetchAporteInvestimentoDetalhado → GET /plano/aporte-investimento  (TTL 2min, dedup ✅)

PatrimonioTab (Patrimônio — lazy, só quando tab selecionada)
  ├── getPatrimonioTimeline → GET /investimentos/timeline/patrimonio
  └── getDistribuicaoPorTipo → GET /investimentos/distribuicao-tipo  (extra-lazy: onOpen do collapsible)
```

### Tabela de endpoints

| Endpoint | Hook/Função | TTL | In-Flight Dedup | Quando | SQL approx |
|----------|-------------|-----|-----------------|--------|------------|
| `GET /dashboard/last-month-with-data` | fetchLastMonthWithData | 5 min | ✅ | Pre-mount | 1 query |
| `GET /dashboard/metrics` | useDashboardMetrics | 2 min | ✅ | Mount (enabled) | 6–8 queries |
| `GET /dashboard/chart-data` | useChartData | 5 min + N4a | ✅ | Mount (period=month) | **12 queries em loop** |
| `GET /dashboard/chart-data-yearly` | useChartDataYearly | 5 min | ✅ | Mount (period≠month) | 1 query por ano |
| `GET /dashboard/income-sources` | fetchIncomeSources | 2 min | ✅ | OrcamentoTab mount | 1 query |
| `GET /dashboard/budget-vs-actual` | fetchExpenseSources | 2 min | ✅ | OrcamentoTab mount | 2 queries |
| `GET /dashboard/credit-cards` | fetchCreditCards | 2 min | ✅ | OrcamentoTab mount | 1 query |
| `GET /dashboard/orcamento-investimentos` | fetchOrcamentoInvestimentos | 2 min | ✅ | OrcamentoTab mount | 3 queries |
| `GET /plano/aporte-investimento` | fetchAporteInvestimentoDetalhado | 2 min | ✅ | OrcamentoTab mount | varia |
| `GET /investimentos/timeline/patrimonio` | getPatrimonioTimeline | ❌ sem cache | ❌ | PatrimonioTab (lazy) | varia |
| `GET /investimentos/distribuicao-tipo` | getDistribuicaoPorTipo | ❌ sem cache | ❌ | PatrimonioTab collapsible | 1 query |

---

## O que está bem implementado

| Mecanismo | Cobertura |
|-----------|-----------|
| Cache in-memory com TTL | Todos os endpoints do dashboard principal |
| In-flight deduplication | Todos os endpoints do dashboard principal |
| Sliding window N4a (chart-data) | Navegar entre meses adjacentes = 0 queries |
| Lazy loading de abas | PatrimonioTab só carrega quando selecionado |
| Prefetch de meses adjacentes | chartData do mês anterior e posterior |
| Pre-mount fetchLastMonthWithData | Elimina 1 RTT de cold start (N3) |

---

## Problemas Identificados

### D1 — `get_chart_data` faz 12 queries em loop (N+12)

**Arquivo:** `app_dev/backend/app/domains/dashboard/repository.py` — linha 316

```python
for i in range(11, -1, -1):   # 12 iterações
    result = self.db.query(
        func.sum(case(...)).label('receitas'),
        func.abs(func.sum(case(...))).label('despesas')
    ).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.MesFatura == mes_fatura,   # ← 1 query por mês
        JournalEntry.IgnorarDashboard == 0
    ).first()
```

**Impacto:** Cada request ao endpoint `GET /dashboard/chart-data` faz 12 queries. Com o cache N4a, a maioria dos acessos subsequentes é servida do `_pointCache` sem request. Mas no **cold start** (primeiro acesso ou cache expirado) são sempre 12 queries.

**Solução:** 1 única query com `IN` + agrupamento em Python:

```python
def get_chart_data(self, user_id: int, year: int, month: int) -> List[Dict]:
    reference_date = datetime(year, month if month > 0 else 12, 1)
    meses_fatura = [
        f"{(reference_date - relativedelta(months=i)).year}"
        f"{(reference_date - relativedelta(months=i)).month:02d}"
        for i in range(11, -1, -1)
    ]

    # 1 query com IN em vez de 12 queries separadas
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

    # Indexar por MesFatura para montar a resposta ordenada
    by_mes = {r.MesFatura: r for r in rows}
    months_data = []
    for mes_fatura in meses_fatura:
        r = by_mes.get(mes_fatura)
        ano = int(mes_fatura[:4])
        mes = int(mes_fatura[4:])
        months_data.append({
            "date": f"{ano}-{mes:02d}-01",
            "receitas": float(r.receitas or 0) if r else 0.0,
            "despesas": float(r.despesas or 0) if r else 0.0,
            "year": ano,
            "month": mes,
        })
    return months_data
```

**Impacto esperado:** 12 queries → 1 query. Redução de ~85% no tempo de resposta do endpoint.

**Atenção:** O shape de resposta é idêntico (`date`, `receitas`, `despesas`, `year`, `month`). Cache N4a e frontend não precisam de alteração.

---

### D2 — PatrimonioTab sem cache (timeline e distribuição)

**Endpoints sem cache:**
- `GET /investimentos/timeline/patrimonio`
- `GET /investimentos/distribuicao-tipo`

**Cenário problemático:**
1. Usuário abre o dashboard → aba Resultado (default)
2. Usuário clica em Patrimônio → CarregaPatrimonioTab (2 requests)
3. Usuário clica em Resultado e volta para Patrimônio → **2 requests novamente** (sem cache)

**Solução:** adicionar cache via `in-memory-cache.ts` (B4 do plano principal):

```typescript
// src/features/investimentos/services/investimentos-api.ts
import { getCached, setCached, getInFlight, setInFlight } from '@/core/utils/in-memory-cache'

const TTL_5MIN = 5 * 60 * 1000

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
```

---

### D3 — Prefetch de meses adjacentes não cobre OrcamentoTab

**Situação atual:** o prefetch de meses adjacentes só popula `_pointCache` do chart-data:

```typescript
// dashboard/page.tsx
useEffect(() => {
  if (!selectedMonth || period !== 'month') return
  prefetchChartData(prev.year, prev.month)
  prefetchChartData(next.year, next.month)
  // ← income-sources, credit-cards, orcamento-investimentos NÃO são prefetchados
}, [selectedMonth, period])
```

Quando o usuário navega para o mês anterior, o chart carrega do cache mas os dados do OrcamentoTab fazem request.

**Solução:** incluir os endpoints principais do OrcamentoTab no prefetch:

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
    // OrcamentoTab — fire-and-forget
    fetchIncomeSources(y, mo).catch(() => {})
    fetchExpenseSources(y, mo).catch(() => {})
    fetchOrcamentoInvestimentos(y, mo, mo).catch(() => {})
  }
}, [selectedMonth, period])
```

---

### D4 — `fetchLastMonthWithData('patrimonio')` não tem prefetch no mount

**Situação atual:** só `source='transactions'` é pré-buscado antes do auth:

```typescript
useEffect(() => {
  _lastMonthPromise.current = fetchLastMonthWithData('transactions')
}, [])
```

O `source='patrimonio'` é buscado lazily quando PatrimonioTab abre — representando 1 RTT extra para o usuário que vai direto para a aba Patrimônio.

**Solução:** iniciar os dois em paralelo no pre-mount:

```typescript
useEffect(() => {
  // Ambas as promises iniciam antes do auth
  _lastMonthPromise.current = fetchLastMonthWithData('transactions')
  _lastMonthPatrimonioPromise.current = fetchLastMonthWithData('patrimonio')
}, [])
```

---

### D5 — Fallback parcial ausente no sliding window N4a

**Situação atual:** se qualquer um dos 7 pontos do chart estiver ausente do `_pointCache`, o N4a falha e cai no fetch completo (12 queries):

```typescript
const keys = _chartWindow(year, month)  // 7 chaves
if (keys.every(k => _pointCache.has(k))) {
  return keys.map(k => _pointCache.get(k)!)  // rápido
}
// senão: request completo (lento)
```

**Cenário:** usuário navega mês a mês do dashboard, mas depois recarrega a página. O `_pointCache` tem 0 pontos → request completo. Se tivesse mantido apenas os últimos 3 meses no cache persistido, poderia servir 3 de 7 pontos do cache e buscar apenas 4.

**Solução de curto prazo** (sem persistência): buscar apenas os meses faltantes:

```typescript
const missingKeys = keys.filter(k => !_pointCache.has(k))

if (missingKeys.length === 0) {
  return keys.map(k => _pointCache.get(k)!)
}

if (missingKeys.length <= 3) {
  // Buscar apenas os meses faltantes individualmente
  const partialFetches = missingKeys.map(k => fetchChartDataPoint(k))
  await Promise.all(partialFetches)
  return keys.map(k => _pointCache.get(k)!)
}

// Se muitos faltando: request completo (comportamento atual)
return fetchChartData(year, month)
```

---

### D6 — Naming confuso em `get_portfolio_resumo` (não é bug, mas merece nota)

**Arquivo:** `app_dev/backend/app/domains/investimentos/repository.py` linha 462-464

```python
'total_investido': total_ativos,  # ← nome diz "investido" mas é ATIVOS
'valor_atual': total_passivos,    # ← nome diz "valor atual" mas é PASSIVOS (negativos)
'rendimento_total': patrimonio_liquido,  # ← nome diz "rendimento" mas é PL = ativos + passivos
```

O dashboard lê esses campos em `repository.py:230-232` e mapeia corretamente:

```python
ativos_mes           = resumo.get("total_investido")   # = total_ativos ✅
passivos_mes         = resumo.get("valor_atual")        # = total_passivos ✅
patrimonio_liquido_mes = resumo.get("rendimento_total") # = patrimônio líquido ✅
```

**Os valores exibidos estão corretos.** O problema é que o nome `rendimento_total` é enganoso — qualquer dev que leia o código de dashboard vai achar que está exibindo rendimento em vez de PL. Risco de introduzir bugs em código futuro.

**Sugestão:** renomear os campos no retorno de `get_portfolio_resumo()`:

```python
# Em vez de:
'total_investido': total_ativos,
'valor_atual': total_passivos,
'rendimento_total': patrimonio_liquido,

# Usar nomes descritivos:
'total_ativos': total_ativos,
'total_passivos': total_passivos,
'patrimonio_liquido': patrimonio_liquido,
```

E atualizar os 3 consumers que leem esses campos (dashboard/repository.py, investimentos page, plano service).

---

## Análise de Impacto — Nada Quebra

### D1 (chart-data: 12→1 query)

| Verificação | Status |
|-------------|--------|
| Shape do response idêntico (`date`, `receitas`, `despesas`, `year`, `month`) | ✅ |
| Cache N4a (`_pointCache`) usa `date` como key — não muda | ✅ |
| Frontend não precisa de alteração | ✅ |
| Resultado numérico idêntico (mesma lógica, só 1 query com GROUP BY) | ✅ |
| Ordem dos meses garantida (ordenando `meses_fatura` antes do loop) | ✅ |

### D6 (renomeação de campos)

| Consumer | Impacto |
|----------|---------|
| `dashboard/repository.py:230-232` | Atualizar 3 linhas |
| `investimentos/page.tsx` (se ler diretamente) | Verificar e atualizar |
| `plano/service.py:1098` (usa `get_expectativas`, não resumo) | ✅ não afetado |

---

## Resumo de Prioridade

| # | Item | Tipo | Esforço | Impacto |
|---|------|------|---------|---------|
| D1 | chart-data: 12→1 query | Backend | Baixo | Alto (cold start -85%) |
| D3 | Prefetch OrcamentoTab adjacentes | Frontend | Baixo | Médio (navegação fluida) |
| D2 | Cache em PatrimonioTab | Frontend | Baixo | Médio |
| D4 | Prefetch lastMonth patrimônio | Frontend | Muito baixo | Baixo |
| D5 | Fallback parcial N4a | Frontend | Médio | Baixo |
| D6 | Renomear campos portfolio_resumo | Refactor | Médio | Preventivo |

---

## Arquivos a Modificar

| Arquivo | Ação | Item |
|---------|------|------|
| `app_dev/backend/app/domains/dashboard/repository.py` | Reescrever `get_chart_data()` com 1 query IN + GROUP BY | D1 |
| `src/app/mobile/dashboard/page.tsx` | Adicionar prefetch de income-sources/credit-cards/orcamento para meses adjacentes | D3 |
| `src/app/mobile/dashboard/page.tsx` | Adicionar prefetch de lastMonthWithData('patrimonio') no mount | D4 |
| `src/features/investimentos/services/investimentos-api.ts` | Adicionar cache TTL para timeline e distribuição | D2 |
| `app_dev/backend/app/domains/investimentos/repository.py` | Renomear campos em `get_portfolio_resumo()` | D6 |
| `app_dev/backend/app/domains/dashboard/repository.py` | Atualizar leitura dos campos renomeados | D6 |
