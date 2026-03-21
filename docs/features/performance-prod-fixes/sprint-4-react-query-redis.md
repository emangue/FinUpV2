# Sprint 4 — React Query + Redis: Deduplicação Arquitetural

> **Esforço total:** ~6–7 horas  
> **Itens:** P3 · P6 · P9  
> **Pré-requisito:** Sprints 1, 2 e 3 concluídos  
> **Impacto:** Elimina duplicatas residuais, UX fluída na navegação, backend < 5ms por request

---

## 🔗 Rastreamento de Erros — O Que Ainda Sobra Após S1 + S2 + S3

> Estes são problemas **arquiteturais** que os sprints anteriores não resolvem completamente. S4 é a camada de dedução e cache permanente.

### P3 — Chamada Dupla de `/plano/cashflow` (race condition)

| Dimensão | Detalhe |
|---|---|
| **Sintoma** | Mesmo após S3 (cache backend < 50ms), o Budget/Plano ainda dispara `/plano/cashflow` 2× por page load. |
| **Medido** | Network mostra 2 chamadas para `/plano/cashflow?ano=` com offset de ~10–50ms (ambas simúltaneas). |
| **Arquivo** | `app_dev/frontend/src/features/plano/api.ts` — cache manual com `Map` in-flight |
| **Causa raiz** | Dois componentes montam ao mesmo tempo. Antes de qualquer um registrar o in-flight request, ambos iniciam `fetch()` independentemente. O `Map` de in-flight do cache manual não protege esse window de milissegundos. |
| **O fix** | React Query: mesma `queryKey` → deduplicado automaticamente em nível de framework, independente de quando os componentes montam. |

### P6 — Backend Ainda Executa 5 Queries para `/onboarding/progress`

| Dimensão | Detalhe |
|---|---|
| **Sintoma** | Após S2, usuários com cache no localStorage não fazem fetch. Mas quando o fazem (nova sessão, novo usuário), o backend executa ~80–100ms de queries. |
| **Verificar** | `docker exec finup_redis_prod redis-cli info memory` → `used_memory_human: ~3.3MB` — Redis ativo mas não usado por nenhuma lógica de negócio. |
| **Arquivo** | `app_dev/backend/app/domains/onboarding/service.py` — função `get_progress()` |
| **Causa raiz** | Redis está configurado no Docker Compose mas não é usado. Cada request de `/onboarding/progress` executa 5 queries ao PostgreSQL. |
| **O fix** | Cache Redis com TTL=5min em `get_progress()`. 1ª chamada: 5 queries (~100ms). 2ª+ chamada: `redis.get()` (<5ms). |

### P9 — Investimentos Usa Endpoint de Lista em Vez do `/overview` Agregado

| Dimensão | Detalhe |
|---|---|
| **Sintoma** | Se `investimentos/page.tsx` precisar de resumo ou distribuição, disparará 2 requests extras além do de lista. |
| **Arquivo exato** | `app_dev/frontend/src/app/mobile/investimentos/page.tsx` linhas **87–100** — `loadInvestimentos` chama `getInvestimentos()` diretamente |
| **Causa raiz** | O endpoint `/investimentos/overview` já existe (retorna lista+resumo+distribuição em 1 request), mas a página usa o endpoint de lista individual. |
| **O fix** | Migrar `loadInvestimentos` para `fetchInvestimentosOverview()` → 1 request retorna tudo. |

---

## Contexto — O Que Ainda Sobra Após S1 + S2 + S3

Após os 3 primeiros sprints (~90 minutos de código), as maiores fontes de latência estão resolvidas. O Sprint 4 ataca os problemas **arquiteturais** que permanecem:

| Problema residual | Causa | Item |
|------------------|-------|------|
| `/plano/cashflow` ainda chamado 2× por page load | Dois componentes montam antes do in-flight deduplication funcionar (race condition) | P3 |
| `/onboarding/progress` ainda faz 1 request por sessão | Cache está no client (localStorage), backend ainda processa 5 queries | P6 |
| Investimentos usa endpoint de lista em vez do `/overview` (B2 agregado) | `investimentos/page.tsx` chama `getInvestimentos()` diretamente | P9 |

---

## Índice

- [P3 — React Query para cashflow (deduplicação de in-flight)](#p3--react-query-para-cashflow)
- [P6 — Redis cache para `/onboarding/progress`](#p6--redis-cache-para-onboardingprogress)
- [P9 — Migrar investimentos/page.tsx para endpoint `/overview`](#p9--migrar-investimentospagetsx-para-overview)
- [Checklist final e validação](#checklist-final-sprint-4)

---

## P3 — React Query para cashflow (3–4 horas)

### Problema

`GET /plano/cashflow?ano=2026` é chamado **2×** por carregamento de Budget/Plano. O `features/plano/api.ts` já tem cache manual com `Map` e in-flight deduplication, mas quando dois componentes montam **ao mesmo tempo** (antes do primeiro request ser registrado como in-flight), ambos disparam o fetch independentemente.

Após Sprint 3 (cache no backend), a 2ª chamada responderá em <50ms — imperceptível. Mas React Query resolve o problema de forma nativa e permanente.

### Pré-requisito: instalar React Query (se não instalado)

```bash
# Verificar se já está instalado:
docker exec finup_frontend_app_dev cat /app/package.json | grep -E "react-query|tanstack"

# Se não estiver:
docker exec finup_frontend_app_dev npm install @tanstack/react-query
# Depois: commitar package.json + package-lock.json
```

### Subitem P3.1 — Criar `QueryProvider` no app

**Arquivo:** `app_dev/frontend/src/app/layout.tsx` (ou onde está o provider raiz)

```typescript
// Adicionar ao layout raiz:
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () => new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 2 * 60 * 1000,      // 2 minutos — dados "frescos"
          gcTime: 5 * 60 * 1000,          // 5 minutos — mantém em cache após unmount
          retry: 1,                        // 1 retry em erro
          refetchOnWindowFocus: false,     // não refetch ao focar janela
        },
      },
    })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && (
        // Opcional: React Query Devtools (apenas dev)
        // import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
        // <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  )
}
```

> **Nota:** Verificar se já existe um `QueryClientProvider` no projeto antes de adicionar um novo. Buscar por `QueryClientProvider` em todo o frontend.

### Subitem P3.2 — Criar hook `useCashflowAnual`

**Arquivo novo:** `app_dev/frontend/src/features/plano/hooks/use-cashflow-anual.ts`

```typescript
import { useQuery } from '@tanstack/react-query'
import { fetchWithAuth } from '@/core/api'

export interface CashflowMesItem {
  mes: number
  renda_realizada: number
  gastos_recorrentes: number
  gastos_reais: number
  investimentos: number
  saldo_projetado: number
  // ... outros campos que o backend retorna
}

export interface CashflowAnual {
  ano: number
  nudge_acumulado: number
  meses: CashflowMesItem[]
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function fetchCashflowAnual(ano: number): Promise<CashflowAnual> {
  const res = await fetchWithAuth(
    `${API_BASE}/api/v1/plano/cashflow?ano=${ano}`
  )
  if (!res.ok) throw new Error(`cashflow anual ${res.status}`)
  return res.json()
}

export function useCashflowAnual(ano: number) {
  return useQuery({
    queryKey: ['plano', 'cashflow', 'anual', ano],
    queryFn: () => fetchCashflowAnual(ano),
    staleTime: 2 * 60 * 1000,   // 2 minutos (mesmo TTL atual do cache manual)
    enabled: !!ano,              // só executa se ano for válido
  })
}
```

**Benefício nativo do React Query:**  
Se dois componentes chamam `useCashflowAnual(2026)` ao mesmo tempo:
- O React Query registra a query key `['plano', 'cashflow', 'anual', 2026]`
- Apenas **1 request HTTP** é disparado (deduplicação automática)
- Ambos os componentes recebem o mesmo dado quando a promise resolve
- Nenhum cache manual necessário

### Subitem P3.3 — Substituir chamadas manuais pelo hook

**Localizar componentes** que chamam `getCashflow()` ou `fetchCashflow()` diretamente:

```bash
# Dentro do container ou localmente:
grep -r "getCashflow\|fetchCashflow\|cashflow.*ano" \
  app_dev/frontend/src/features/plano/ \
  app_dev/frontend/src/app/mobile/budget/ \
  --include="*.ts" --include="*.tsx" -l
```

**Para cada arquivo encontrado**, substituir o padrão:

```typescript
// ANTES — fetch manual com cache:
const [cashflow, setCashflow] = useState<CashflowAnual | null>(null)
const [loading, setLoading] = useState(true)

useEffect(() => {
  getCashflow(ano)
    .then(setCashflow)
    .finally(() => setLoading(false))
}, [ano])

// DEPOIS — hook React Query:
import { useCashflowAnual } from '@/features/plano/hooks/use-cashflow-anual'

const { data: cashflow, isLoading: loading } = useCashflowAnual(ano)
```

### Subitem P3.4 — Invalidação quando dados mudam

React Query invalida a query automaticamente se você chamar `queryClient.invalidateQueries`:

```typescript
// Em qualquer lugar onde expectativas/budget mudam (ex: ao salvar um plano):
import { useQueryClient } from '@tanstack/react-query'

const queryClient = useQueryClient()

// Após salvar expectativa ou budget:
queryClient.invalidateQueries({ queryKey: ['plano', 'cashflow', 'anual'] })
// Isso invalida o cashflow de TODOS os anos (útil quando ano muda não é certo)

// Ou invalidar apenas o ano afetado:
queryClient.invalidateQueries({ queryKey: ['plano', 'cashflow', 'anual', ano] })
```

### Subitem P3.5 — Remover cache manual de `features/plano/api.ts`

Após o React Query estar funcionando, o cache manual (Map de in-flight + getCached) em `api.ts` pode ser removido para simplificar:

```typescript
// features/plano/api.ts — REMOVER depois de P3 estar funcionando:
const _cashflowCache = new Map<string, CashflowAnual>()
const _cashflowInFlight = new Map<string, Promise<CashflowAnual>>()

export async function getCashflow(ano: number): Promise<CashflowAnual> {
  const key = String(ano)
  const cached = _cashflowCache.get(key)
  if (cached) return cached
  // ...
}
```

> **Estratégia de migração:** implementar React Query em paralelo com o cache manual, verificar que funciona, depois remover o manual. Não remover antes de validar.

---

## P6 — Redis cache para `/onboarding/progress` (2 horas)

### Contexto

Após Sprint 2 (localStorage cache), a maioria dos usuários não faz o fetch de `/onboarding/progress`. Mas quando **fazem** (primeira visita pós-login ou novo usuário), o backend ainda executa 5 queries no PostgreSQL. Com Redis, o backend responderia em **<5ms** (em vez de ~100ms de queries).

**Benefício imediato:** para novos usuários (onboarding não completo), cada check será instantâneo do ponto de vista do backend.

### Pré-requisito: Redis já está configurado

```bash
# Verificar que Redis está ativo:
docker exec finup_redis_prod redis-cli ping
# → PONG

# Verificar que `redis_client` está disponível no backend:
grep -r "redis_client\|from.*redis" app_dev/backend/app/ --include="*.py" | head -5
```

### Subitem P6.1 — Verificar dependências Redis no backend

```bash
# No container:
docker exec finup_backend_dev python3 -c "import redis; print(redis.__version__)"
# ou
docker exec finup_backend_dev python3 -c "from redis.asyncio import Redis; print('ok')"

# Se não instalado:
# Adicionar ao requirements.txt: redis>=5.0.0
# Rebuild: docker-compose build backend
```

### Subitem P6.2 — Adicionar cliente Redis ao app

**Arquivo:** `app_dev/backend/app/core/redis_client.py` (criar se não existir)

```python
import json
import os
from typing import Any, Optional

import redis

# Conexão com pool (thread-safe para uso com FastAPI sync workers)
_pool = redis.ConnectionPool.from_url(
    os.getenv("REDIS_URL", "redis://redis:6379/0"),
    decode_responses=True,
    max_connections=10,
)

def get_redis() -> redis.Redis:
    """Retorna cliente Redis com pool compartilhado."""
    return redis.Redis(connection_pool=_pool)


def redis_get(key: str) -> Optional[Any]:
    """Lê e desserializa valor do Redis. Retorna None se não existir."""
    try:
        client = get_redis()
        raw = client.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None  # Redis indisponível não deve quebrar o app


def redis_set(key: str, value: Any, ex: int = 300) -> bool:
    """Serializa e grava valor no Redis com TTL em segundos."""
    try:
        client = get_redis()
        client.set(key, json.dumps(value), ex=ex)
        return True
    except Exception:
        return False


def redis_delete(key: str) -> None:
    """Remove chave do Redis (para invalidação de cache)."""
    try:
        get_redis().delete(key)
    except Exception:
        pass
```

### Subitem P6.3 — Adicionar cache Redis em `get_progress()`

**Arquivo:** `app_dev/backend/app/domains/onboarding/service.py`

Localizar a função `get_progress()` (ou equivalente que calcula onboarding status):

```python
# ANTES:
def get_progress(db: Session, user_id: int) -> dict:
    # 5 queries ao PostgreSQL:
    tem_upload = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.fonte != 'demo'
    ).first() is not None

    tem_plano = db.query(BudgetPlanning).filter(
        BudgetPlanning.user_id == user_id
    ).first() is not None

    # ... mais 3 queries
    
    return {
        "onboarding_completo": all([tem_upload, tem_plano, ...]),
        "tem_demo": ...,
        # ... outros campos
    }

# DEPOIS — com cache Redis:
from app.core.redis_client import redis_get, redis_set

ONBOARDING_CACHE_TTL = 5 * 60  # 5 minutos

def get_progress(db: Session, user_id: int) -> dict:
    cache_key = f"onboarding:progress:{user_id}"
    
    # Tentar cache Redis primeiro
    cached = redis_get(cache_key)
    if cached is not None:
        return cached  # ← <5ms (vs ~100ms das 5 queries)
    
    # Cache miss — computar normalmente
    tem_upload = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.fonte != 'demo'
    ).first() is not None

    tem_plano = db.query(BudgetPlanning).filter(
        BudgetPlanning.user_id == user_id
    ).first() is not None

    # ... resto das queries existentes

    result = {
        "onboarding_completo": all([tem_upload, tem_plano, ...]),
        "tem_demo": ...,
    }
    
    # Salvar no cache Redis
    redis_set(cache_key, result, ex=ONBOARDING_CACHE_TTL)
    
    return result
```

### Subitem P6.4 — Invalidar cache quando arquivo é uploadado

```python
# Em: app_dev/backend/app/domains/upload/service.py
# Após processar upload com sucesso:

from app.core.redis_client import redis_delete

def process_upload(db: Session, user_id: int, file_data):
    # ... lógica existente de processamento ...
    
    # Invalidar cache de onboarding após upload
    redis_delete(f"onboarding:progress:{user_id}")
    
    return resultado
```

### Subitem P6.5 — Invalidar cache quando budget/plano é criado

```python
# Em: app_dev/backend/app/domains/plano/service.py ou budget/service.py
# Após criar primeira expectativa/budget:

from app.core.redis_client import redis_delete

def create_budget_planning(db: Session, user_id: int, data):
    # ... lógica existente ...
    
    redis_delete(f"onboarding:progress:{user_id}")
    
    return resultado
```

### Comportamento do cache Redis

```
request: GET /api/v1/onboarding/progress  (user_id=42)
→ redis.get("onboarding:progress:42") → miss
→ 5 queries PostgreSQL: ~80–100ms
→ redis.set("onboarding:progress:42", resultado, ex=300)
→ response: ~100ms

request 2 (< 5 min depois): GET /api/v1/onboarding/progress
→ redis.get("onboarding:progress:42") → HIT
→ response: <5ms  ← 20x mais rápido
```

---

## P9 — Migrar Investimentos para endpoint `/overview` (1 hora)

### Contexto

Após Sprint 4 dos api-performance (B2 concluído), o endpoint `/api/v1/investimentos/overview` existe e retorna `lista + resumo + distribuição` em 1 request. Mas `app/mobile/investimentos/page.tsx` ainda chama `getInvestimentos()` diretamente — o endpoint de lista individual.

| Consumidor atual | API usada | Requests |
|-----------------|-----------|----------|
| `investimentos/page.tsx` | `getInvestimentos()` → `/investimentos` | 1 request (lista) |
| `use-investimentos.ts` | `fetchInvestimentosOverview()` → `/investimentos/overview` | 1 request (lista+resumo+dist) |

A página usa apenas a lista, mas se futuramente precisar do resumo ou distribuição, fará 2 requests adicionais. Migrar agora unifica.

### Subitem P9.1 — Atualizar `investimentos/page.tsx`

**Arquivo:** `app_dev/frontend/src/app/mobile/investimentos/page.tsx`

```typescript
// ANTES — após o fix P7 (selectedMonth = null):
React.useEffect(() => {
  if (!isAuth || !selectedMonth) return
  
  // Chamadas separadas:
  getInvestimentos({ ativo: 1, anomes: String(anomes) })
    .then(setInvestimentos)
    .catch(setError)
}, [isAuth, anomes, selectedMonth])

// DEPOIS — usar endpoint overview:
import { fetchInvestimentosOverview } from '@/features/investimentos/services/investimentos-api'

React.useEffect(() => {
  if (!isAuth || !selectedMonth) return
  
  setLoading(true)
  fetchInvestimentosOverview({
    ativo: 1,
    anomes: String(anomes),
    include: 'lista,resumo,distribuicao',
  })
    .then((overview) => {
      if (overview.lista)        setInvestimentos(overview.lista)
      if (overview.resumo)       setResumo(overview.resumo)
      if (overview.distribuicao) setDistribuicao(overview.distribuicao)
    })
    .catch(setError)
    .finally(() => setLoading(false))
}, [isAuth, anomes, selectedMonth])
```

### Subitem P9.2 — Remover chamadas redundantes em `carteira/page.tsx`

Verificar se `carteira/page.tsx` também chama `getInvestimentos()` separadamente. Se sim, migrar para o hook `useInvestimentos()` que já usa o endpoint `/overview`:

```typescript
// Buscar em carteira/page.tsx:
grep -n "getInvestimentos\|investimentos" app_dev/frontend/src/app/mobile/carteira/page.tsx
```

---

## Ordem de Execução Recomendada

```
P6 (2h)  →  P3 (3-4h)  →  P9 (1h)
Redis       React Query    Overview
```

**Justificativa:**
- P6 é mais simples — apenas backend, sem refatoração de componentes React
- P3 requer instalação de dependência e mudança em múltiplos componentes
- P9 é simples mas depende de P7 (já feito no Sprint 1) estar funcionando

---

## Playwright — Validação Final (Após Todos os 4 Sprints)

### Executar bateria completa de performance

```bash
# Executar a bateria completa de Playwright (mede todas as telas + APIs):
python3 scripts/testing/perf_measure.py --url https://meufinup.com.br \
  2>&1 | tee deploy/history/perf_resultado_s4_final.txt

# Comparar com o baseline original (antes de qualquer sprint):
diff deploy/history/perf_baseline_pre_s1.txt \
     deploy/history/perf_resultado_s4_final.txt \
  | grep -E "ms|\+|\-" | head -30
```

### Validação específica de P3 (deduplication React Query)

```bash
# Verificar que apenas 1 request de cashflow é disparado por page load:
# 1. Abrir DevTools > Network > filtrar por "cashflow"
# 2. Navegar para /mobile/plano (Budget)
# Antes do S4: 2 requests de /plano/cashflow?ano=
# Após S4: 1 request apenas

# Verificar deduplication via logs do backend:
docker exec finup_backend_dev grep -c "cashflow" /var/log/app/access.log
# Em uma visita: deve aparecer 1 vez (não 2)
```

### Validação específica de P6 (Redis cache)

```bash
# Verificar que o Redis está sendo preenchido:
docker exec finup_redis_prod redis-cli keys "onboarding:*"
# Após 1 visita: deve mostrar "onboarding:progress:1" (ou o user_id do usuário)

# Medir tempo da 2ª chamada ao endpoint:
time curl -s \
  "http://localhost:8000/api/v1/onboarding/progress" \
  -H "Authorization: Bearer $TOKEN"
# 1ª chamada: ~100ms (5 queries PostgreSQL)
# 2ª chamada: < 10ms (Redis hit)

# TTL do cache:
docker exec finup_redis_prod redis-cli ttl "onboarding:progress:1"
# Deve mostrar ~300 (5 minutos em segundos)
```

### Metas de aprovação — Estado final

| Cenário | S0 (baseline) | Meta pós-S4 | Critério de falha |
|---|---|---|---|
| Dashboard 1ª visita | ~7s | **< 1.5s** | > 3s → verificar S2 (onboarding cache) |
| Dashboard 2ª+ visita | ~7s | **< 0.5s** | > 1s → verificar S2 |
| Budget/Plano | 5.8s | **< 0.5s** | > 1.5s → verificar S3 (cashflow cache) |
| Transações | ~800ms | **< 400ms** | > 700ms → verificar S1/P8 |
| Carteira/Investimentos | ~1500ms | **< 600ms** | > 1000ms → verificar S1/P7 |
| `/onboarding/progress` (2ª call) | ~100ms | **< 10ms** | > 50ms → Redis não está sendo usado |
| `/plano/cashflow` requests por page | 2× | **1×** | 2× → React Query não deduplicando |

### Script de verificação consolidado

```bash
# Executar verificação de todos os sprints:
python3 scripts/testing/perf_s1_verify.py --url https://meufinup.com.br  # S1: P7+P8
python3 scripts/testing/perf_s2_verify.py --url https://meufinup.com.br  # S2: P1

# Para P3 (React Query), P6 (Redis), P9 (overview):
# Usar perf_measure.py + análise manual da aba Network (scripts não embutidos ainda)
```

### Resultado esperado pós todos os 4 sprints

```
╔═════════════════════════════════════════════════════════════╗
║        ⏱️  FinUp — Medição de Performance (Pós-S4)      ║
╚═════════════════════════════════════════════════════════════╝

  Tela                         Tempo    Barra
  ─────────────────────────── ───────  ────────────────────
  Dashboard (mobile)            420ms  ████░░░░░░░░░░░░░░░░
  Transações                   380ms  ███░░░░░░░░░░░░░░░░░░
  Budget/Plano                  290ms  ██░░░░░░░░░░░░░░░░░░░
  Investimentos                 510ms  ████░░░░░░░░░░░░░░░░░
  Upload                        210ms  ██░░░░░░░░░░░░░░░░░░░
```

---

## Checklist Final Sprint 4

### P3 — React Query
- [ ] `@tanstack/react-query` instalado e em `package.json`
- [ ] `QueryClientProvider` no layout raiz
- [ ] Hook `useCashflowAnual` criado em `features/plano/hooks/`
- [ ] Todos os componentes que chamavam `getCashflow` migrados para `useCashflowAnual`
- [ ] DevTools Network: apenas 1 request de `/plano/cashflow` por page load
- [ ] Invalidação funciona: editar budget → cashflow atualiza na tela
- [ ] Cache manual de `api.ts` removido após validação

### P6 — Redis
- [ ] `redis_client.py` criado em `app/core/`
- [ ] `get_progress()` usa Redis com TTL de 5 minutos
- [ ] Upload de arquivo invalida cache Redis de onboarding
- [ ] Criação de budget invalida cache Redis de onboarding
- [ ] `docker exec finup_redis_prod redis-cli keys "onboarding:*"` mostra chaves após 1 acesso
- [ ] Segunda requisição ao `/onboarding/progress`: tempo < 10ms nos logs do backend

### P9 — Overview
- [ ] `investimentos/page.tsx` usa `fetchInvestimentosOverview`
- [ ] Tela de Investimentos carrega lista + resumo + distribuição em 1 request
- [ ] TypeScript sem erros: `tsc --noEmit`
- [ ] Tela renderiza corretamente

### Git e Deploy
- [ ] Commit: `feat(perf): React Query + Redis cache + investimentos overview (P3/P6/P9)`
- [ ] `docker-compose build frontend-app` (nova dependência npm)
- [ ] Deploy via `./deploy/scripts/deploy_docker_build_local.sh`
- [ ] Playwright: `python3 deploy/validations/ui_tests.py --headed` para validar UX

---

## Impacto Consolidado (Após Todos os 4 Sprints)

| Cenário | S0 (hoje) | Após S1 | Após S2 | Após S3 | Após S4 |
|---------|-----------|---------|---------|---------|---------|
| Dashboard 1ª visita | ~7s | ~5s | **~2s** | ~2s | ~1s |
| Dashboard 2ª+ visita | ~7s | ~5s | **~0.5s** | ~0.5s | ~0.3s |
| Bottom nav (toda troca) | 6–8s | ~4s | **~0.5s** | ~0.5s | ~0.3s |
| Budget/Plano | 5.8s | 5.8s | 5.8s | **~0.3s** | ~0.1s |
| Transações abertura | ~3s | **~1.5s** | ~1.5s | ~1.5s | ~0.8s |
| Carteira (fria) | ~1.5s (dupla) | **~0.8s** | ~0.8s | ~0.8s | ~0.5s |
| Investimentos (fria) | ~1.5s (dupla) | **~0.8s** | ~0.8s | ~0.8s | ~0.4s |
| `/onboarding/progress` backend | ~100ms | ~100ms | ~100ms | ~100ms | **<5ms** |

---

## Dívida Técnica Identificada (Fora do Escopo)

| Item | Esforço | Prioridade |
|------|---------|-----------|
| Adicionar índice em `investimento_historicos(investimento_id, ano, anomes)` | 5 min | 🟡 Baixa (queries já <700ms) |
| Migrar demais hooks de Dashboard para React Query | 4-6h | 🟢 Futura |
| Playwright: adicionar teste de performance (budget < 500ms) | 1h | 🟡 Média |
| Alertas de Redis (slot cheio, memory > 80%) | 1h | 🟡 Média |

---

**Documentação da análise base:** [`ANALISE_PERFORMANCE_VM.md`](ANALISE_PERFORMANCE_VM.md)
