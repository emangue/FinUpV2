# Plano de Ação — Performance de APIs

---

## Alta Prioridade

### [P2] Criar tabela materializada `plano_cashflow_mes`

**Problema:** Cashflow computa 48-60 queries por requisição dinamicamente. Não existe tabela de plano por mês.

**Solução:** Criar tabela `plano_cashflow_mes` no banco e popular via background task. Ver detalhes em [`04-cashflow-tabela-materializada.md`](./04-cashflow-tabela-materializada.md).

**Impacto esperado:** 48-60 queries → 1 query por requisição. Redução de ~80-90% no tempo de resposta do cashflow.

**Escopo:**
- Backend: migration + model + service de refresh
- Backend: lógica de invalidação por evento
- Backend: modificar `get_cashflow()` para ler da tabela quando disponível
- Frontend: nenhuma mudança necessária (endpoint mantém contrato)

---

### [P1] Criar endpoint agregado para o dashboard

**Problema:** 11 chamadas simultâneas no mount do dashboard.

**Solução:** Endpoint `GET /dashboard/summary` que retorna todos os dados necessários em uma única chamada, com campos selecionáveis via query param (`?sections=metrics,chart,income-sources,...`).

**Impacto esperado:** 11 RTTs → 1 RTT no cold start. Redução de ~60% no tempo de carregamento do dashboard.

**Escopo:**
- Backend: novo endpoint `/dashboard/summary` que chama os serviços existentes internamente
- Frontend: refatorar `use-dashboard.ts` para usar o endpoint agregado
- Frontend: manter endpoints individuais para prefetch de meses adjacentes

---

### [P4] Optimistic updates em Goals/Orçamento

**Problema:** Toda mutação faz full refetch. Usuário espera ~300-500ms após cada ação.

**Solução:** Atualizar estado local imediatamente após a mutação, sem aguardar refetch.

```typescript
// Antes
async function createGoal(data) {
  await api.post('/budget/planning/bulk-upsert', data)
  await loadGoals() // full refetch
}

// Depois
async function createGoal(data) {
  const newGoal = optimisticGoal(data)
  setGoals(prev => [...prev, newGoal]) // atualização imediata
  try {
    const saved = await api.post('/budget/planning/bulk-upsert', data)
    setGoals(prev => prev.map(g => g.id === newGoal.id ? saved : g))
  } catch {
    setGoals(prev => prev.filter(g => g.id !== newGoal.id)) // rollback
  }
}
```

**Impacto esperado:** UX imediata para o usuário. Elimina 1 request por mutação.

**Escopo:** Apenas frontend — `src/features/goals/hooks/use-goals.ts`

---

## Média Prioridade

### [P3] Endpoint agregado para investimentos

**Problema:** 3 RTTs separados no mount (`getInvestimentos + resumo + distribuicao`).

**Solução:** Endpoint `GET /investimentos/overview?include=resumo,distribuicao` que retorna lista + resumo + distribuição em uma chamada.

**Escopo:** Backend (novo endpoint) + frontend (refatorar `use-investimentos.ts`)

---

### [P5] Endpoint batch para range update de goals

**Problema:** `aplicarAteFinAno=true` faz 1 chamada por mês restante (até 12 chamadas).

**Solução:** Endpoint `PUT /budget/planning/bulk-range` que aceita `{ goalId, valor, mes_inicio, mes_fim }` e aplica no backend em uma transação.

**Escopo:** Backend (novo endpoint) + frontend (goals-api.ts)

---

### [P6] Cache para módulos sem cobertura

**Problema:** Investimentos, Plano, Bancos, Categorias, Transações não têm cache.

**Solução curto prazo:** Implementar o mesmo padrão de cache in-memory com TTL já usado no dashboard (copiar o utilitário de cache de `dashboard-api.ts`).

**Solução ideal:** Adotar **React Query** ou **SWR** globalmente para eliminar cache ad-hoc e ter deduplicação, revalidação e invalidação padronizadas.

**Módulos afetados:**
- `use-investimentos.ts` — TTL sugerido: 2 min
- `use-banks.ts` — TTL sugerido: 5 min (dados raramente mudam)
- `use-categories.ts` — TTL sugerido: 5 min
- `plano/api.ts` — TTL sugerido: 2 min

---

### [P7] Deduplicação global de requests

**Problema:** Dois componentes chamando `fetchBanks()` ao mesmo tempo fazem 2 requests.

**Solução:** Implementar in-flight deduplication global (igual ao `dashboard-api.ts`) ou adotar React Query.

---

## Baixa Prioridade

### [P9] Cursor-based pagination em transações

**Problema:** Paginação offset degrada com datasets grandes.

**Solução:** Implementar cursor pagination no backend (`GET /transactions/list?cursor=X&limit=10`) e atualizar o frontend.

---

### [P10] Paginação real em investimentos

**Problema:** `limit=200` hardcoded — sem paginação para portfólios grandes.

**Solução:** Cursor-based pagination + virtualização da lista no frontend.

---

### [P11] Skeleton progressivo por seção

**Problema:** Páginas mostram loading até tudo estar pronto.

**Solução:** Renderizar seções assim que seus dados chegarem, com skeleton placeholder nas demais. Usar Suspense boundaries por seção do dashboard.

---

## Resumo por Impacto

| # | Problema | Esforço | Impacto | Tipo |
|---|----------|---------|---------|------|
| P2 | Tabela materializada cashflow | Alto | Alto | Backend |
| P1 | Endpoint agregado dashboard | Médio | Alto | Full-stack |
| P4 | Optimistic updates goals | Baixo | Médio | Frontend |
| P3 | Endpoint agregado investimentos | Médio | Médio | Full-stack |
| P5 | Batch range update goals | Médio | Médio | Full-stack |
| P6 | Cache nos módulos sem cobertura | Baixo | Médio | Frontend |
| P7 | Deduplicação global | Baixo | Médio | Frontend |
| P9 | Cursor pagination transações | Médio | Baixo | Full-stack |
| P10 | Paginação real investimentos | Médio | Baixo | Full-stack |
| P11 | Skeleton progressivo | Médio | Baixo | Frontend |
