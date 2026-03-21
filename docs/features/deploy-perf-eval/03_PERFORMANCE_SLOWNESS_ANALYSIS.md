# Análise de Lentidão do App na VM — 07/03/2026

**Sintoma:** App funciona perfeitamente local. Na VM, há demora perceptível ao mudar de tela ou de filtro (mês, período).

---

## TL;DR

A lentidão **não é** infra da VM (RAM abundante, CPU baixo, VM em SP). É causada por dois bugs de código que só ficam visíveis quando a API tem latência (>0ms), ou seja, sempre que o app está na VM.

| Causa | Impacto | Status |
|-------|---------|--------|
| **Cache stampede** | Cada troca de tela ou filtro faz chamadas duplicadas ao backend | Bug ativo |
| **N3 não implementado** | Auth e lastMonth são sequenciais (+1 RTT no cold start) | Pendente |

---

## Dados da VM (eliminando hipóteses)

| Métrica | Valor | Conclusão |
|---------|-------|-----------|
| RAM livre | 7.8 GB + 6.8 GB cache | OOM descartado |
| CPU load avg | 0.22 / 0.54 / 0.88 | CPU descartado |
| TTFB frontend (localhost) | 4ms | Next.js standalone OK |
| Localização VM | São Paulo, BR | RTT baixo para usuários BR |
| Backend health | healthy | Backend OK |

---

## Causa 1: Cache Stampede (confirmado pelos logs)

### O que é

O cache em `dashboard-api.ts` armazena o **valor resolvido** após o fetch completar:

```typescript
// Atual: armazena valor (não a Promise em voo)
function _setCache<T>(key: string, value: T): T {
  _cache.set(key, { value, ts: Date.now() })
  return value
}
```

Quando dois componentes montam **ao mesmo tempo** e chamam a mesma função:
1. Componente A chama `fetchBudgetPlanning(2026, 1)` → cache miss → HTTP request iniciado
2. Componente B chama `fetchBudgetPlanning(2026, 1)` → cache miss (fetch A ainda não terminou) → segundo HTTP request
3. Ambos terminam, ambos setam o cache → desperdício: 2 requests, 2× latência

### Prova nos logs nginx

```log
02:25:38 GET /api/v1/plano/orcamento?ano=2026&mes=1        → 200  ← 1ª chamada
02:25:38 GET /api/v1/plano/orcamento?ano=2026&mes=1        → 200  ← DUPLICADA (mesmo segundo)

02:25:38 GET /api/v1/dashboard/income-sources?year=2026    → 200  ← 1ª chamada
02:25:39 GET /api/v1/dashboard/income-sources?year=2026    → 200  ← DUPLICADA

02:25:38 GET /api/v1/plano/aporte-investimento?ano=2026    → 200  ← 1ª chamada
02:25:39 GET /api/v1/plano/aporte-investimento?ano=2026    → 200  ← DUPLICADA

02:25:38 GET /api/v1/budget/planning?mes_referencia=2026-01 → 200 ← 1ª chamada
02:25:39 GET /api/v1/budget/planning?mes_referencia=2026-01 → 200 ← DUPLICADA
```

**4 endpoints duplicados na mesma abertura da tela `/mobile/plano`.**

### Por que local não aparece

- Local: cada API call ~1ms → duplicata = 2ms → imperceptível
- VM: cada API call ~100-300ms → duplicata = 200-600ms → claramente percebido

### Fix

Mudar o cache para guardar a **Promise em voo**. Chamadas concorrentes para a mesma key retornam a mesma Promise, eliminando o segundo request:

```typescript
// Proposta: deduplicação de requests em voo
const _inflightCache = new Map<string, Promise<unknown>>()

async function _withCache<T>(key: string, ttl: number, fetcher: () => Promise<T>): Promise<T> {
  // 1. Verifica cache de valor (resolvido)
  const hit = _cache.get(key)
  if (hit && Date.now() - hit.ts < ttl) return hit.value as T

  // 2. Verifica se já tem request em voo para essa key
  if (_inflightCache.has(key)) return _inflightCache.get(key) as Promise<T>

  // 3. Inicia request, registra como em voo
  const promise = fetcher().then((value) => {
    _setCache(key, value)
    _inflightCache.delete(key)
    return value
  }).catch((err) => {
    _inflightCache.delete(key)
    throw err
  })

  _inflightCache.set(key, promise)
  return promise
}
```

**Impacto estimado:** elimina 50-100% dos requests duplicados → reduz latência percebida em 200-600ms por troca de tela.

---

## Causa 2: N3 não implementado — auth e lastMonth sequenciais

### Status atual

```typescript
// dashboard/page.tsx — linha 86-98
useEffect(() => {
  if (!isAuth) return  // ← espera auth/me completar ANTES de chamar lastMonth
  fetchLastMonthWithData('transactions')
    .then(...)
}, [isAuth])
```

Sequência atual:
```
t=0ms    GET /auth/me  ──────────────────────────►  t=200ms  isAuth=true
                                                              ↓
t=200ms  GET /last-month-with-data  ─────────────►  t=400ms  selectedMonth resolve
                                                              ↓
t=400ms  todos os hooks disparam (paralelo)
```

### Proposta N3

```typescript
// Paralelo: inicia lastMonth imediatamente, usa o resultado quando isAuth=true
const pendingLastMonth = useRef<{ year: number; month: number } | null>(null)

useEffect(() => {
  fetchLastMonthWithData('transactions')
    .then((last) => { pendingLastMonth.current = last })
    .catch(() => {})
}, [])  // ← sem dependência de isAuth

useEffect(() => {
  if (!isAuth) return
  const last = pendingLastMonth.current
  if (last) {
    setSelectedMonth(new Date(last.year, last.month - 1, 1))
    pendingLastMonth.current = null
  } else {
    fetchLastMonthWithData('transactions').then(...)
  }
}, [isAuth])
```

**Impacto estimado:** -200ms no cold start (um RTT a menos antes de qualquer conteúdo aparecer).

---

## Status de implementação N0–N4

| Item | Descrição | Status |
|------|-----------|--------|
| **N0** | `.catch` vazio → fallback para mês atual | ✅ Implementado |
| **N1** | Cache de módulo TTL para APIs do dashboard | ✅ Implementado (mas tem cache stampede) |
| **N2** | `isLoading = !enabled` → OrcamentoTab monta junto | ✅ Implementado |
| **N3** | Pré-fetch `lastMonth` em paralelo com `auth/me` | ❌ Pendente |
| **N4** | Transactions: limit 500 → 100 + "carregar mais" | Verificar |

---

## Problema adicional: Rate limiting por servidor

O Docker NAT (masquerade) faz todos os clientes externos aparecerem como `172.20.0.1` no nginx. O rate limit `$binary_remote_addr` aplica-se por servidor inteiro, não por usuário.

| Zona | Taxa real | Impacto |
|------|-----------|---------|
| `api_limit` 120r/m | 120 requests/min para TODOS os usuários somados | Rate limit compartilhado |
| `login_limit` 10r/m | 10 tentativas/min de qualquer IP → proteção brute force ineficaz | Segurança comprometida |

**Fix:** Configurar `proxy_protocol` ou usar `$http_x_forwarded_for` para o IP real. O infra_nginx já passa `X-Real-IP` para o backend, mas o próprio nginx não usa esse header para rate limit (não pode, pois o header vem de si mesmo).

A solução correta é usar `network_mode: host` para o `infra_nginx` (elimina a camada NAT) ou configurar PROXY protocol entre o Load Balancer da Hostinger e o nginx.

---

## Resumo: Prioridades

| # | Ação | Esforço | Impacto |
|---|------|---------|---------|
| 1 | **Fix cache stampede** em `dashboard-api.ts` | Baixo (~30 linhas) | -200 a -600ms por troca de tela |
| 2 | **Implementar N3** no `dashboard/page.tsx` | Baixo (~15 linhas) | -200ms no cold start |
| 3 | **Verificar N4** (transactions limit) | Mínimo | Scroll fluido com muitas transações |
| 4 | Fix rate limiting (X-Forwarded-For ou host networking) | Médio | Segurança e fairness |
