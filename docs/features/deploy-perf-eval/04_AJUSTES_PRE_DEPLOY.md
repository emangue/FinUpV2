# Ajustes Pré-Deploy — 07/03/2026

Resumo de todas as alterações realizadas nesta sessão antes do próximo deploy em produção.

---

## 1. Fix: Cache Stampede em `dashboard-api.ts`

**Arquivo:** `app_dev/frontend/src/features/dashboard/services/dashboard-api.ts`

**Problema confirmado:** Dois componentes React montando simultaneamente chamavam a mesma função de fetch. Ambos erravam o cache (ainda não populado) e disparavam requests duplicados ao backend — comprovado pelos logs do nginx mostrando o mesmo endpoint chamado 2× no mesmo segundo.

**Solução:** In-flight Promise deduplication via `_inflight` Map.

```typescript
const _inflight = new Map<string, Promise<unknown>>()

function _withInFlight<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  if (_inflight.has(key)) return _inflight.get(key) as Promise<T>
  const p = fetcher().finally(() => _inflight.delete(key))
  _inflight.set(key, p)
  return p
}
```

**Onde foi aplicado:** Todas as 8 funções cacheadas:
- `fetchLastMonthWithData`
- `fetchDashboardMetrics`
- `fetchIncomeSources`
- `fetchChartData`
- `fetchChartDataYearly`
- `fetchPlanoCashflowMes`
- `fetchAporteInvestimentoDetalhado`
- `fetchCreditCards`

**Também atualizado:** `invalidateDashboardCache()` e `invalidateLastMonthCache()` passaram a limpar `_inflight` além do `_cache`.

**Impacto esperado:** -200 a -600ms por troca de tela/filtro (elimina o request duplicado que estava sendo descartado, mas ainda consumia RTT + CPU no backend).

---

## 2. N3: Pre-fetch Paralelo de `lastMonthWithData`

**Arquivo:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx`

**Problema:** No cold start, o fetch de `lastMonthWithData` só iniciava após `auth/me` resolver — dois RTTs sequenciais.

**Solução (N3 do PLANO_PERFORMANCE_V2):** Iniciar o fetch imediatamente (sem esperar autenticação), guardar o resultado num `useRef`, e consumi-lo no `useEffect` de `isAuth` se já estiver disponível.

```typescript
const _pendingLastMonth = useRef<{ year: number; month: number } | null>(null)

// Inicia imediatamente — sem esperar auth
useEffect(() => {
  fetchLastMonthWithData('transactions')
    .then((last) => { _pendingLastMonth.current = last })
    .catch(() => {})
}, [])

// Quando auth resolver, usa o resultado pré-buscado se disponível
useEffect(() => {
  if (!isAuth) return
  const pending = _pendingLastMonth.current
  if (pending) {
    _pendingLastMonth.current = null
    setSelectedMonth(new Date(pending.year, pending.month - 1, 1))
    setSelectedYear(pending.year)
    setLastMonthWithData(pending)
  } else {
    fetchLastMonthWithData('transactions').then(...).catch(...)
  }
}, [isAuth])
```

**Impacto esperado:** -200ms no cold start (elimina 1 RTT sequencial).

---

## 3. Reorganização de Scripts de Deploy

**Problema:** 46 scripts de deploy acumulados — risco operacional alto, impossível saber qual usar.

**Ação:** Criado `scripts/deploy/archive/` e movidos 43 scripts obsoletos.

**Scripts mantidos em `scripts/deploy/`:**
| Script | Função |
|--------|--------|
| `deploy_docker_build_local.sh` | Deploy padrão (build local → SCP → VM) |
| `deploy_docker_vm.sh` | Deploy alternativo (build na VM, com rollback) |
| `validate_deploy.sh` | Validação pós-deploy |
| `README.md` | Documentação dos scripts (atualizado) |

---

## 4. Reorganização de Docs de Deploy

**Problema:** 37+ documentos históricos em `docs/deploy/` — maioria obsoleta, referenciando scripts e fluxos extintos.

**Ação:** Criado `docs/deploy/archive/` e movidos todos os docs históricos.

**Docs mantidos em `docs/deploy/`:**
| Arquivo | Conteúdo |
|---------|----------|
| `GUIA_DEPLOY.md` | Fluxo padrão, containers em produção, migrations, rollback |
| `TROUBLESHOOTING.md` | Erros conhecidos e soluções |

---

## 5. Remoção de `docker-compose.vm.yml`

**Arquivo removido:** `docker-compose.vm.yml` (raiz do projeto)

**Motivo:** O arquivo era destinado a uma VM com PostgreSQL no host OS (sem container). A VM atual usa PostgreSQL em container Docker (`docker-compose.prod.yml`), tornando este arquivo errado e fonte de confusão operacional.

**Compose file ativo:** `docker-compose.prod.yml` (projeto `finup`)

---

## Status dos itens do PLANO_PERFORMANCE_V2

| Item | Descrição | Status |
|------|-----------|--------|
| N0 | Cache simples em dashboard-api.ts | ✅ Já estava feito |
| N1 | Cache com TTL | ✅ Já estava feito (mas com stampede — corrigido agora) |
| N2 | Mostrar estrutura antes dos dados | ✅ Já estava feito |
| N3 | Pre-fetch lastMonth em paralelo com auth | ✅ **Implementado nesta sessão** |
| N4 | Prefetch no hover dos meses | Não verificado |
| Cache Stampede | In-flight deduplication | ✅ **Implementado nesta sessão** |

---

## Próximo passo

Rodar o deploy:

```bash
./scripts/deploy/deploy_docker_build_local.sh
```
