# Plano de Performance — FinUp Mobile V2

**Data:** 2026-03-06
**Base:** Auditoria de código local + inspeção ao vivo da VM (meufinup.com.br)
**Referência anterior:** `ANALISE_EFICIENCIA_APP.md` (P0–P2, todos implementados)

---

## Resumo Executivo

O problema de **5 segundos no dashboard** foi investigado ao vivo na VM. O código de otimização (P0–P2) está **100% deployado**. A causa raiz era um **rate limit de nginx absurdamente baixo** (`30r/m burst=20`) que causava `503` silencioso no `fetchLastMonthWithData` — o app ficava preso no spinner para sempre.

**Corrigido em produção:** rate limit atualizado para `120r/m` na sessão atual.

> **Débito de segurança introduzido:** ao elevar o rate limit geral da API, o endpoint `/api/v1/auth/login` ficou com proteção insuficiente contra brute force. Requer correção imediata (ver **S0** abaixo).

Este documento mapeia o que falta para chegar a uma navegação fluida e sem loading perceptível.

---

## Parte 1 — O Que Já Está Feito

### Otimizações de Código (ANALISE_EFICIENCIA_APP.md — todos deployados)

| Item | Descrição | Arquivo |
|------|-----------|---------|
| P0-1 | `selectedMonth = null` + guard `enabled` nos hooks | `dashboard/page.tsx:63` |
| P0-2 | Removido `useIncomeSources` duplicado do dashboard | `dashboard/page.tsx:83` |
| P0-3 | `cards` passado como prop para `GastosPorCartaoBox` | `gastos-por-cartao-box.tsx:48` |
| P0-4 | `useChartData`/`useChartDataYearly` condicionais por `period` | `dashboard/page.tsx:69` |
| P1-1 | Cache de módulo 5 min para `fetchLastMonthWithData` | `dashboard-api.ts:19` |
| P1-2 | `resumoExterno` como prop para `PlanoResumoCard` | `plano/page.tsx:126` |
| P1-3 | Endpoint `/plano/cashflow/mes` — 1 mês em vez de 12 | `dashboard-api.ts:270` |
| P1-4 | Debounce 400 ms nos selects de período em Transactions | `transactions/page.tsx:129` |
| P2-2 | Lazy load das distribuições em `PatrimonioTab` | `patrimonio-tab.tsx:99` |
| P2-3 | Removidos `useIncomeSources`/`useExpenseSources` do dashboard | `dashboard/page.tsx:83` |

### Correção de Infraestrutura (feita hoje)

| Item | Antes | Depois | Arquivo |
|------|-------|--------|---------|
| nginx rate limit API | `30r/m burst=20` — causava 503 após 20 calls | `120r/m burst=20` | `/var/www/infra/nginx/nginx.conf` |
| nginx rate limit frontend | `60r/m burst=30` | `240r/m burst=30` | idem |

**Evidência:** log de 21:23h confirmava `503` em `/api/v1/plano/aporte-investimento` de um usuário móvel no dashboard.

> **Atenção:** o rate limit de `120r/m` é adequado para endpoints autenticados (JWT inválido = rejeição imediata sem acesso a dados). Porém, o endpoint `/api/v1/auth/login` **não exige token** e ficou com a mesma cota elevada — ver **S0**.

---

## Parte 2 — Mapeamento de Novos Problemas

---

### S0 — SEGURANÇA CRÍTICA: Login sem rate limit dedicado

**Problema:** O rate limit geral da API foi elevado de `30r/m` para `120r/m` para corrigir os 503s no dashboard. Com isso, o endpoint `/api/v1/auth/login` — que não exige token — passou a aceitar **120 tentativas de senha por minuto** por IP. Antes aceitava 30. Ambos são ruins para brute force, mas o novo valor é pior.

Endpoints autenticados não têm esse problema: sem JWT válido, o backend rejeita antes de acessar qualquer dado. O login é o único endpoint onde o volume de requests importa para segurança.

**Solução:** Criar uma `limit_req_zone` dedicada para o login no nginx, com taxa baixa:

```nginx
# nginx.conf — adicionar no bloco http:
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=10r/m;

# meufinup.com.br.conf — adicionar ANTES do location /api/ genérico:
location = /api/v1/auth/login {
    limit_req zone=login_limit burst=5 nodelay;
    proxy_pass         http://finup_backend_prod:8000;
    proxy_http_version 1.1;
    proxy_set_header   Host              $host;
    proxy_set_header   X-Real-IP         $remote_addr;
    proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto https;
}
```

Com isso: login = 10r/m burst=5 (10 tentativas/min por IP), demais APIs autenticadas = 120r/m.

**Observação:** O `location =` (match exato) tem prioridade sobre o `location /api/` (prefixo), então não é necessário remover nem alterar o bloco existente.

**Esforço:** Muito baixo | **Impacto:** Proteção de brute force restaurada para o login

---

### Contexto: por que ainda demora ~5s

Mesmo com todos os itens anteriores implementados, o carregamento do dashboard tem **3 estágios sequenciais obrigatórios** antes de mostrar conteúdo:

```
[usuário abre app]
  ↓ Estágio 0: AuthContext.loadUser() → GET /auth/me           ~200ms API + latência
  ↓ isAuth=true → dashboard pode iniciar

  ↓ Estágio 1: fetchLastMonthWithData()                        ~200ms API + latência
  ↓ selectedMonth resolve → enabled=true → hooks disparam

  ↓ Estágio 2 (paralelo): metrics + chart-data                 ~300ms API + latência
  ↓ isLoading=false → OrcamentoTab monta

  ↓ Estágio 3: 6 APIs do OrcamentoTab em paralelo              ~300ms API + latência
  ↓ loading=false → conteúdo visível
─────────────────────────────────────────────────────
Mínimo teórico:  ~1.0s de APIs
Com latência BR (200ms/RTT × 4 estágios): ~1.8s
Na prática (JS bundle + hidratação + cold start): 3–5s
```

---

### N0 — Crítico: `.catch(() => {})` vazio em rotas críticas

**Problema:** Se `fetchLastMonthWithData` recebe qualquer erro (503, timeout, rede), a Promise cai num `.catch(() => {})` vazio. `setSelectedMonth` nunca é chamado. `enabled` fica `false`. O dashboard fica num **spinner eterno sem possibilidade de retry**.

**Locais afetados:**

| Arquivo | Linha | Impacto |
|---------|-------|---------|
| `dashboard/page.tsx` | L95 | App preso para sempre se `lastMonth` falha |
| `investimentos/page.tsx` | L68 | Scroll preso no mês atual |
| `carteira/page.tsx` | L257 e L291 | Scroll preso |
| `budget/manage/page.tsx` | L23 | Scroll preso |

**Solução:** No dashboard (o mais crítico), fallback para o mês atual se a chamada falhar:

```typescript
// dashboard/page.tsx — substituir o .catch vazio:
.catch(() => {
  const now = new Date()
  setSelectedMonth(new Date(now.getFullYear(), now.getMonth(), 1))
  setSelectedMonth(now)
  setLastMonthWithData({ year: now.getFullYear(), month: now.getMonth() + 1 })
})
```

**Esforço:** Baixo | **Impacto:** Elimina o caso de spinner eterno

---

### N1 — Alto: Sem cache para as demais APIs do dashboard

**Problema:** Só `fetchLastMonthWithData` tem cache. As outras 7 APIs do dashboard refazem fetch completo a cada troca de mês ou volta de navegação. O padrão do cache já existe no código — basta replicar.

**APIs sem cache:**

| Função | Endpoint | TTL sugerido |
|--------|----------|-------------|
| `fetchDashboardMetrics` | `/dashboard/metrics` | 2 min |
| `fetchChartData` | `/dashboard/chart-data` | 5 min |
| `fetchChartDataYearly` | `/dashboard/chart-data-yearly` | 5 min |
| `fetchIncomeSources` | `/dashboard/income-sources` | 2 min |
| `fetchCreditCards` | `/dashboard/credit-cards` | 2 min |
| `fetchAporteInvestimentoDetalhado` | `/plano/aporte-investimento` | 2 min |
| `fetchPlanoCashflowMes` | `/plano/cashflow/mes` | 5 min |

**Solução:** Mesma estrutura do `_lmwdCache` já em `dashboard-api.ts`:

```typescript
// dashboard-api.ts — padrão a replicar para cada função:
const _metricsCache = new Map<string, { value: DashboardMetrics; ts: number }>()
const METRICS_TTL = 2 * 60 * 1000

export async function fetchDashboardMetrics(year, month?, ytdMonth?): Promise<DashboardMetrics> {
  const key = `metrics:${year}:${month ?? 'all'}:${ytdMonth ?? ''}`
  const hit = _metricsCache.get(key)
  if (hit && Date.now() - hit.ts < METRICS_TTL) return hit.value
  // ... fetch normal ...
  _metricsCache.set(key, { value, ts: Date.now() })
  return value
}
```

**Invalidação:** Chamar `invalidateCache()` após upload bem-sucedido (já existe `invalidateLastMonthCache` como exemplo).

**Restrição de segurança:** O cache de módulo vive na memória do browser (JavaScript do cliente), portanto é isolado por usuário — não há risco de dados cruzados entre sessões. Porém, as funções cacheadas **não podem ser chamadas de Server Components ou rotas de API do Next.js** (contexto SSR), onde o módulo seria compartilhado entre requisições de diferentes usuários. Todas as funções afetadas são chamadas de hooks com `useEffect` em componentes `'use client'` — manter essa restrição ao implementar.

**Esforço:** Baixo (~80 linhas) | **Impacto:** Troca de mês passa de ~700ms para **0ms** se mês já foi visitado

---

### N2 — Alto: Dashboard renderiza OrcamentoTab em série (3 estágios → 2)

**Problema:** O `isLoading` do dashboard bloqueia a renderização do `OrcamentoTab` até `metrics` E `chart` carregarem. Isso cria o Estágio 3 sequencial (após Estágio 2). OrcamentoTab poderia montar imediatamente com seu próprio skeleton.

```typescript
// ATUAL — OrcamentoTab só monta após isLoading=false:
const isLoading = !enabled || loadingMetrics || loadingChart

{isLoading ? <Spinner /> : (
  <OrcamentoTab ... />  // só aparece aqui
)}

// PROPOSTA — OrcamentoTab monta junto com stage 2:
const isContentReady = enabled  // só espera selectedMonth resolver

{!isContentReady ? <Spinner /> : (
  <>
    {/* Métricas e gráfico com seu próprio loading inline */}
    {loadingMetrics || loadingChart ? <ChartSkeleton /> : <BarChart ... />}
    {/* OrcamentoTab monta imediatamente — tem seu próprio loading */}
    <OrcamentoTab ... />
  </>
)}
```

**Ganho:** Estágio 2 e Estágio 3 passam a ser paralelos. Reduz o tempo total percebido em ~300–400ms.

**Esforço:** Médio | **Impacto:** Estágios 2+3 em paralelo → -300ms percebidos

---

### N3 — Médio: AuthContext: `auth/me` sem cache entre rotas

**Problema:** `AuthContext` chama `loadUser()` → `GET /auth/me` no mount do provider. O provider persiste entre navegações (correto), mas em cold start (abre app do zero) esse call é o **Estágio 0** antes de tudo. Não há como paralelizá-lo com `lastMonthWithData` porque o dashboard aguarda `isAuth=true` antes de iniciar.

**Solução:** Iniciar `fetchLastMonthWithData` logo que o componente monta, **sem esperar autenticação** — e usar o resultado se a auth confirmar:

```typescript
// dashboard/page.tsx — pré-buscar lastMonth em paralelo com auth:
useEffect(() => {
  // Começa a buscar imediatamente, mesmo sem saber se está autenticado
  // Se auth falhar, o redirect vai acontecer de qualquer forma
  fetchLastMonthWithData('transactions')
    .then((last) => { pendingLastMonth.current = last })
    .catch(() => {})
}, [])  // sem dependência de isAuth

useEffect(() => {
  if (!isAuth) return
  const last = pendingLastMonth.current
  if (last) {
    setSelectedMonth(new Date(last.year, last.month - 1, 1))
    setLastMonthWithData(last)
    pendingLastMonth.current = null
  } else {
    fetchLastMonthWithData('transactions').then(...)
  }
}, [isAuth])
```

**Ganho:** Estágio 0 e Estágio 1 se tornam paralelos → -200ms no cold start.

**Esforço:** Médio | **Impacto:** -200ms no cold start do app

---

### N4 — Médio: Transactions — 500 itens no DOM sem virtualização

**Problema:** A query usa `limit: 500` e renderiza todos os resultados de uma vez no DOM. Com 500 transações, a lista pode ter 2.000–3.000 nós DOM, causando lentidão no scroll, especialmente em celulares mid-range.

**Evidência:** `fetchTransactions` em `transactions/page.tsx:L169` — `limit: 500, page: 1`.

**Solução A (simples):** Reduzir limit para 100 com botão "Carregar mais".

**Solução B (ideal):** Virtualização com `react-window` ou `react-virtual` — renderiza só os itens visíveis.

**Solução C (rápida):** Paginação por data (lazy load ao scrollar para baixo).

**Esforço:** Médio (A) / Alto (B) | **Impacto:** Scroll fluido em listas grandes

---

### N5 — Médio: Backend — Redis rodando mas não usado para cache de queries

**Problema:** O container `finup_redis_prod` está rodando e saudável, mas as APIs pesadas do backend (metrics, income-sources, chart-data) consultam PostgreSQL a cada requisição, sem aproveitar o Redis.

**Candidatos ao cache Redis no backend:**

| Endpoint | TTL sugerido | Motivo |
|----------|-------------|--------|
| `GET /dashboard/metrics` | 2 min | Cálculo agregado de journal_entries |
| `GET /dashboard/income-sources` | 2 min | GROUP BY em journal_entries |
| `GET /dashboard/chart-data` | 5 min | 7 meses de dados agregados |
| `GET /dashboard/last-month-with-data` | 5 min | MAX(date) query simples |
| `GET /budget/planning` | 1 min | Raramente muda durante a sessão |

**Chave de cache — requisito de segurança obrigatório:** A chave DEVE incluir o `user_id`. Uma chave sem user_id (`metrics:2026:1`) retornaria dados de um usuário para outro.

```python
# ERRADO — dados de um usuário vazam para outro:
key = f"metrics:{year}:{month}"

# CORRETO — isolado por usuário:
key = f"metrics:{user_id}:{year}:{month}"
```

A chave completa recomendada: `finup:{user_id}:{endpoint}:{params_hash}`

**Invalidação:** Ao fazer upload, invalidar todas as chaves do `user_id` no Redis: `DEL finup:{user_id}:*`

**Esforço:** Médio | **Impacto:** Backend passa de ~100–300ms para ~5–20ms (leitura de cache)

---

### N6 — Baixo: Endpoint agregado de dashboard (`/dashboard/summary`)

**Problema:** O dashboard faz 8 chamadas HTTP separadas (após as otimizações P0–P2). Cada chamada tem overhead de: TLS resume + proxy nginx + FastAPI routing + query PostgreSQL + serialização JSON. Um endpoint único reduziria esse overhead.

**Proposta:**

```
GET /api/v1/dashboard/summary?year=2026&month=1

Response:
{
  "metrics": { ... },
  "income_sources": { ... },
  "chart_data": [ ... ],
  "credit_cards": [ ... ],
  "budget_planning": [ ... ],
  "plano_cashflow_mes": { ... },
  "aporte_investimento": { ... }
}
```

**Compatibilidade:** Pode ser implementado em paralelo — o frontend continuaria chamando os endpoints individuais até a migração estar pronta.

**Esforço:** Alto | **Impacto:** 8 calls → 1 call por abertura do dashboard

---

### N7 — Baixo: Ausência de `loading.tsx` por rota

**Problema:** Next.js 13+ suporta `loading.tsx` por rota para exibir um skeleton imediatamente enquanto o JS do componente carrega (antes mesmo de qualquer `useEffect`). Atualmente, o usuário vê tela em branco ou spinner genérico.

**Solução:** Criar `app/mobile/dashboard/loading.tsx` com um skeleton visual que corresponda ao layout do dashboard.

**Esforço:** Baixo | **Impacto:** Elimina flash de tela branca na navegação inicial

---

## Parte 3 — Plano de Ação Priorizado

### Fase 0 — Segurança (executar antes de qualquer outra coisa)

| # | Item | Esforço | Impacto |
|---|------|---------|---------|
| 0 | **S0:** Rate limit dedicado para `/auth/login` (`10r/m burst=5`) no nginx | Muito baixo | Restaura proteção brute force |

### Fase 1 — Correções de bug (baixo risco, alto impacto)

| # | Item | Esforço | Impacto |
|---|------|---------|---------|
| 1 | **N0:** `.catch` vazio → fallback para mês atual em todas as rotas | Baixo | Elimina spinner eterno |

### Fase 2 — Cache client-side (risco zero, altíssimo impacto)

| # | Item | Esforço | Impacto |
|---|------|---------|---------|
| 2 | **N1:** Cache de módulo TTL para 7 APIs do dashboard | Baixo | Troca de mês = 0ms (mês já visitado) |

### Fase 3 — Paralelização do dashboard (médio esforço)

| # | Item | Esforço | Impacto |
|---|------|---------|---------|
| 3 | **N2:** Renderizar OrcamentoTab junto com Estágio 2 | Médio | -300ms percebidos no carregamento |
| 4 | **N3:** Pré-buscar `lastMonth` em paralelo com `auth/me` | Médio | -200ms no cold start |

### Fase 4 — Backend e listas (médio prazo)

| # | Item | Esforço | Impacto |
|---|------|---------|---------|
| 5 | **N5:** Redis cache no backend para queries pesadas | Médio | Backend: 300ms → 20ms |
| 6 | **N4:** Transactions: limit 100 + "carregar mais" | Médio | Scroll fluido |

### Fase 5 — Arquitetura (longo prazo)

| # | Item | Esforço | Impacto |
|---|------|---------|---------|
| 7 | **N6:** Endpoint `/dashboard/summary` agregado | Alto | 8 calls → 1 call |
| 8 | **N7:** `loading.tsx` por rota | Baixo | Elimina flash branco |

---

## Parte 4 — Ganho Estimado por Fase

| Estado | Cold start (abre app) | Troca de mês | Volta ao dashboard |
|--------|----------------------|--------------|-------------------|
| **Hoje (após rate limit fix)** | ~3–5s | ~1.5s | ~1.5s |
| **Após Fase 0 (S0)** | ~3–5s | ~1.5s | ~1.5s (login protegido) |
| **Após Fase 1 (N0)** | ~3–5s | ~1.5s | ~1.5s (nunca trava) |
| **Após Fase 2 (N1)** | ~3–5s | **0ms** (cache) | **0ms** (cache) |
| **Após Fase 3 (N2+N3)** | **~2–3s** | 0ms | 0ms |
| **Após Fase 4 (N4+N5)** | **~1.5–2s** | 0ms | 0ms |
| **Após Fase 5 (N6)** | **~1s** | 0ms | 0ms |

---

## Parte 5 — Mapa de Chamadas Esperado (Após Fase 2)

### Abertura do dashboard (cold start)

```
t=0ms   AuthContext.loadUser() → GET /auth/me
t=0ms   (paralelo) fetchLastMonthWithData → GET /last-month-with-data  ← N3

t=200ms selectedMonth resolve → enabled=true

t=200ms (paralelo) GET /dashboard/metrics
t=200ms (paralelo) GET /dashboard/chart-data
t=200ms (paralelo — N2) OrcamentoTab monta:
          GET /dashboard/income-sources
          GET /dashboard/credit-cards
          GET /budget/planning
          GET /plano/cashflow/mes
          GET /plano/aporte-investimento

t=500ms  Tela completa visível

TOTAL: ~500ms (vs ~3–5s atual)
```

### Troca de mês (após cache N1)

```
Cache HIT para metrics, chart, income-sources, credit-cards, budget, cashflow, aporte
→ Conteúdo atualizado instantaneamente (0ms de API)
```

### Volta para o dashboard (navegou para outra tela)

```
Cache HIT para tudo (dentro do TTL de 2–5 min)
→ Dashboard renderiza sem nenhuma chamada de rede
```

---

## Parte 6 — Restrições de Segurança por Item

| Item | Restrição | Consequência se ignorada |
|------|-----------|--------------------------|
| **S0** (rate limit login) | Criar `login_limit` separado com `10r/m burst=5` | Brute force no login com 120 tentativas/min por IP |
| **N1** (cache client-side) | Chamar apenas de componentes `'use client'` — nunca de Server Components | Cache compartilhado entre usuários diferentes no processo Node.js do servidor |
| **N5** (Redis backend) | Chave de cache DEVE ser `finup:{user_id}:{endpoint}:{params}` | Dados financeiros de um usuário retornados para outro |
| **N3** (pré-fetch antes de auth) | Aplicar resultado apenas quando `isAuth === true` | Nenhum — endpoint exige auth no backend; request não-autenticado retorna 401 |
| **N6** (endpoint summary) | Validar que o response retorna apenas dados do `user_id` autenticado | Exposição de dados de outro usuário no endpoint agregado |

---

## Observações

- **O que NÃO mudar:** A lógica `enabled = selectedMonth !== null` (P0-1) é crítica — não remover.
- **Invalidação de cache:** Sempre chamar `invalidateCache()` após upload de extrato bem-sucedido. O padrão já existe em `invalidateLastMonthCache` — seguir o mesmo.
- **TTL conservador:** Usar 2 min para dados que mudam com uploads (metrics, sources) e 5 min para dados estruturais (chart, cashflow do plano).
- **Redis no backend:** Independente do cache client-side — ambos se complementam. O Redis beneficia todos os usuários; o cache de módulo beneficia apenas a sessão atual do usuário.
- **Ordem obrigatória:** S0 antes de N1 e N5. As otimizações de cache só devem ir para produção depois que as restrições de segurança de cada uma estiverem garantidas.
