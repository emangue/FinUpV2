# Sprint 2 — Frontend: Cache Layer + Tela Plano

> **Escopo:** Frontend only. Sem novos endpoints, sem migrations.
> **Itens:** B4 · F2 · G1 · G2 · G3
> **Pré-requisito:** Nenhum. (Sprint 1 é independente — pode correr em paralelo)
> **Ordem obrigatória dentro do sprint:** B4 primeiro (outros dependem do `in-memory-cache.ts`)

---

## Índice

- [B4 — Criar utilitário `in-memory-cache.ts`](#b4--criar-utilitário-in-memory-cachets)
- [F2 — Cache em PatrimonioTab](#f2--cache-em-patrimoniotab)
- [G1 — Debounce no slider da ProjecaoChart](#g1--debounce-no-slider-da-projecaochart)
- [G2 — Cache para endpoints do Plano](#g2--cache-para-endpoints-do-plano)
- [G3 — Separar effects de base e slider na ProjecaoChart](#g3--separar-effects-de-base-e-slider-na-projecaochart)

---

## B4 — Criar utilitário `in-memory-cache.ts`

**Problema:** O padrão de cache (get/set/inFlight) está duplicado em `dashboard-api.ts` e precisa ser centralizado para todos os módulos.
**Impacto:** Pré-requisito de F2, G2, B4 (use-banks.ts, use-categories.ts).
**Arquivo:** `app_dev/frontend/src/core/utils/in-memory-cache.ts` **(novo)**

---

### Microação 1 — Criar o arquivo

```typescript
// app_dev/frontend/src/core/utils/in-memory-cache.ts

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

### Microação 2 — Aplicar o padrão em `use-banks.ts`

**Arquivo:** `app_dev/frontend/src/features/banks/hooks/use-banks.ts`

```typescript
import { getCached, setCached, getInFlight, setInFlight, invalidateCache } from '@/core/utils/in-memory-cache'

const CACHE_KEY = 'banks:list'
const TTL = 5 * 60 * 1000  // 5 min (bancos raramente mudam)

async function fetchBanksCached(): Promise<Bank[]> {
  const cached = getCached<Bank[]>(CACHE_KEY)
  if (cached) return cached

  const inFlight = getInFlight<Bank[]>(CACHE_KEY)
  if (inFlight) return inFlight

  const promise = apiGet<Bank[]>(ENDPOINTS.BANKS)
    .then((data) => { setCached(CACHE_KEY, data, TTL); return data })

  setInFlight(CACHE_KEY, promise)
  return promise
}

// Após mutação: invalidar e recarregar
async function createBank(data: CreateBankInput) {
  await apiPost(ENDPOINTS.BANKS, data)
  invalidateCache('banks:')
  await fetchBanksCached()
}
```

---

### Microação 3 — Aplicar o mesmo padrão em `use-categories.ts`

**Arquivo:** `app_dev/frontend/src/features/categories/hooks/use-categories.ts`

```typescript
import { getCached, setCached, getInFlight, setInFlight } from '@/core/utils/in-memory-cache'

const CACHE_KEY = 'categories:list'
const TTL = 5 * 60 * 1000

async function fetchCategoriesCached() {
  const cached = getCached(CACHE_KEY)
  if (cached) return cached
  const inFlight = getInFlight(CACHE_KEY)
  if (inFlight) return inFlight
  const promise = apiGet(ENDPOINTS.CATEGORIES)
    .then(data => { setCached(CACHE_KEY, data, TTL); return data })
  setInFlight(CACHE_KEY, promise)
  return promise
}
```

---

### Microação 4 — Adicionar cache a `fetchOrcamentoInvestimentos`

Esta função foi identificada no `06_STATUS_IMPLEMENTACAO.md` como sem cache. Adicionar usando o utilitário:

**Arquivo:** `app_dev/frontend/src/features/dashboard/services/dashboard-api.ts`

```typescript
import { getCached, setCached, getInFlight, setInFlight } from '@/core/utils/in-memory-cache'

const TTL_2MIN = 2 * 60 * 1000

export async function fetchOrcamentoInvestimentos(year: number, month: number, ytdMonth: number) {
  const key = `orcamentoInvestimentos:${year}:${month}:${ytdMonth}`
  const cached = getCached(key)
  if (cached) return cached
  const inFlight = getInFlight(key)
  if (inFlight) return inFlight
  const promise = fetchWithAuth(`${ENDPOINTS.ORCAMENTO_INVESTIMENTOS}?year=${year}&month=${month}&ytd_month=${ytdMonth}`)
    .then(r => r.json())
    .then(data => { setCached(key, data, TTL_2MIN); return data })
  setInFlight(key, promise)
  return promise
}
```

---

### Tabela de módulos e TTLs

| Módulo | Cache key prefix | TTL | Arquivo |
|--------|-----------------|-----|---------|
| `use-banks.ts` | `banks:` | 5 min | `features/banks/hooks/use-banks.ts` |
| `use-categories.ts` | `categories:` | 5 min | `features/categories/hooks/use-categories.ts` |
| `use-investimentos.ts` | `investimentos:` | 2 min | `features/investimentos/hooks/use-investimentos.ts` |
| `fetchOrcamentoInvestimentos` | `orcamentoInvestimentos:` | 2 min | `features/dashboard/services/dashboard-api.ts` |
| `plano/api.ts` | `plano:` | 2-5 min | `features/plano/api.ts` |

---

### Checklist B4

- [ ] Arquivo `core/utils/in-memory-cache.ts` criado e exportando as 5 funções
- [ ] `use-banks.ts` usando o cache — sem refetch em re-renders
- [ ] `use-categories.ts` usando o cache
- [ ] `fetchOrcamentoInvestimentos` com cache — sem re-fetch ao trocar de tab
- [ ] `invalidateCache` chamada após mutações (criação/edição/deleção de banco/categoria)

---

## F2 — Cache em PatrimonioTab

**Problema:** `getPatrimonioTimeline` e `getDistribuicaoPorTipo` re-fetcam toda vez que o usuário abre a tab Patrimônio.
**Impacto:** Elimina re-fetch na troca de tab (Resultado ↔ Patrimônio).
**Pré-requisito:** B4 (in-memory-cache.ts).
**Arquivo:** `app_dev/frontend/src/features/investimentos/services/investimentos-api.ts`

---

### Microação 1 — Adicionar TTL cache nas funções de timeline e distribuição

```typescript
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

---

### Checklist F2

- [ ] Abrir PatrimonioTab: 1 request por função (cold)
- [ ] Trocar para outra tab e voltar: 0 requests (cache hit)
- [ ] DevTools: nenhum request duplicado para `timeline/patrimonio` ou `distribuicao-tipo`

---

## G1 — Debounce no slider da ProjecaoChart

**Problema:** Cada posição do slider dispara 1 request a `GET /plano/projecao`. Arrastar de 0→30% = 6+ requests.
**Impacto:** Elimina requests intermediários — só o valor final é buscado.
**Arquivo:** `app_dev/frontend/src/features/plano/components/ProjecaoChart.tsx`

---

### Microação 1 — Separar estado visual do estado que dispara fetch + cache por percentual

```typescript
// Separar estado visual do estado que dispara fetch
const [sliderValue, setSliderValue] = useState(0)    // UI imediata
const [debouncedPct, setDebouncedPct] = useState(0)  // dispara fetch após parar

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

> **Detalhe de UX:** O slider deve usar `sliderValue` (não `debouncedPct`) para mover suavemente. Só o fetch é debouncado.

---

### Checklist G1

- [ ] Arrastar o slider de 0→50%: apenas 1 request (para o valor final)
- [ ] Voltar para um percentual já visitado: 0 requests (cache local)
- [ ] Mudar o ano limpa o cache de percentuais
- [ ] Slider continua se movendo suavemente (sem delay visual)

---

## G2 — Cache para endpoints do Plano

**Problema:** Toda navegação ou re-render na tela Plano faz novos requests — sem cache.
**Impacto:** Elimina re-fetches em re-renders e navegação entre abas.
**Pré-requisito:** B4 (in-memory-cache.ts).
**Arquivo:** `app_dev/frontend/src/features/plano/api.ts`

---

### Microação 1 — Envolver todas as funções com cache

```typescript
import { getCached, setCached, getInFlight, setInFlight } from '@/core/utils/in-memory-cache'

const TTL_2MIN = 2 * 60 * 1000
const TTL_5MIN = 5 * 60 * 1000

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

// Replicar para todas as funções com os TTLs abaixo:
```

| Função | TTL | Cache key |
|--------|-----|-----------|
| `getResumoPlano` | 2 min | `plano:resumo:${ano}:${mes}` |
| `getOrcamento` | 2 min | `plano:orcamento:${ano}:${mes}` |
| `getCashflow` | 2 min | `plano:cashflow:${ano}` |
| `getProjecao` | 5 min | `plano:projecao:${ano}:${reducao_pct}:${sem_patrimonio}` |
| `getImpactoLongoPrazo` | 5 min | `plano:impacto:${ano}:${mes}` |

---

### Checklist G2

- [ ] Abrir tela Plano: N requests (cold, N = número de endpoints)
- [ ] Navegar para outra tela e voltar: 0 requests (cache hit)
- [ ] `getProjecao` com mesmo percentual: 0 requests (cache hit)
- [ ] Cache não interfere com G1 (ProjecaoChart usa cache próprio de ref, G2 usa store global)

---

## G3 — Separar effects de base e slider na ProjecaoChart

**Problema:** A ProjecaoChart busca `getProjecao(..., reducao_pct=0)` em todo mount — inclusive quando só o slider muda. Causa re-fetch desnecessário.
**Impacto:** Elimina re-fetch da curva base ao interagir com o slider.
**Arquivo:** `app_dev/frontend/src/features/plano/components/ProjecaoChart.tsx`

---

### Microação 1 — Dois effects independentes

```typescript
// Effect 1: dados base + cashflow — só re-executa quando ANO muda
useEffect(() => {
  setLoadingBase(true)
  Promise.all([
    getProjecao(ano, 12, 0, true),
    getCashflow(ano),
  ]).then(([base, cf]) => {
    setBaseData(base)
    setCashflow(cf)
  }).finally(() => setLoadingBase(false))
}, [ano])  // ← só ano

// Effect 2: curva laranja — só executa quando percentual muda (usa G1 debounce)
useEffect(() => {
  if (!debouncedPct) { setSliderData(null); return }

  if (projCache.current.has(debouncedPct)) {
    setSliderData(projCache.current.get(debouncedPct)!)
    return
  }
  getProjecao(ano, 12, debouncedPct, true).then((d) => {
    projCache.current.set(debouncedPct, d)
    setSliderData(d)
  })
}, [debouncedPct, ano])
```

> **Nota:** G3 complementa G1. Implementar G1 antes de G3.

---

### Checklist G3

- [ ] Mover o slider NÃO re-fetcha os dados base (curva azul)
- [ ] Mudar o ano re-fetcha os dados base (curva azul)
- [ ] Slider e curva base têm estados de loading independentes

---

## Resumo do Sprint 2

| Item | Arquivo(s) | Dep. |
|------|-----------|------|
| B4 — in-memory-cache.ts | `core/utils/in-memory-cache.ts` (novo) | — |
| B4 — use-banks.ts cache | `features/banks/hooks/use-banks.ts` | B4 |
| B4 — use-categories.ts cache | `features/categories/hooks/use-categories.ts` | B4 |
| B4 — fetchOrcamentoInvestimentos cache | `features/dashboard/services/dashboard-api.ts` | B4 |
| F2 — Cache PatrimonioTab | `features/investimentos/services/investimentos-api.ts` | B4 |
| G1 — Debounce slider | `features/plano/components/ProjecaoChart.tsx` | — |
| G2 — Cache Plano | `features/plano/api.ts` | B4 |
| G3 — Separar effects | `features/plano/components/ProjecaoChart.tsx` | G1 |

**Ordem obrigatória:** B4 → (F2, G2 em paralelo) → G1 → G3
