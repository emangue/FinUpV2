# Problemas de Performance Identificados

---

## Problemas Críticos

### P1 — Dashboard: 11 chamadas no mount (N+11)

**Impacto:** Alto — afeta diretamente o tempo de carregamento da tela principal.

O dashboard dispara 11 hooks simultâneos ao montar. Mesmo com deduplicação in-flight e cache por TTL, no **cold start** (primeira abertura ou após expirar cache) são feitas 11 requisições reais ao backend.

Cada requisição tem latência de 50-200ms. O usuário percebe o loading de cada seção carregando separadamente.

**Localização:**
- `src/app/mobile/dashboard/page.tsx` (linhas 69-81)
- `src/features/dashboard/services/dashboard-api.ts`

**Agravante:** Cada aba (Resultado, Patrimônio, Orçamento) pode disparar chamadas adicionais fora do bloco principal.

---

### P2 — Cashflow: ausência de tabela materializada por mês

**Impacto:** Alto — afeta dashboard e tela de plano.

O endpoint `GET /plano/cashflow?ano=Y` é **100% dinâmico**: computa os 12 meses do ano do zero a cada requisição.

**Fluxo por mês (×12):**
```
1. query em journal_entries (transações realizadas)
2. query em budget_planning (orçamento planejado)
3. query em expectativas_mes (sazonais, parcelas, extras)
4. lógica de crescimento, reajuste, decisão realizado vs planejado
```

**Total: ~48 a 60 queries por requisição.**

O endpoint `/cashflow/mes` (mês único) **não resolve**: internamente ainda computa os 12 meses e filtra 1 — é só uma máscara no response.

**Localização:**
- `app_dev/backend/app/domains/plano/router.py` (linhas 241-269)
- `app_dev/backend/app/domains/plano/service.py` (linhas 268-464)

**Tabelas envolvidas:** `journal_entries`, `budget_planning`, `base_expectativas`, `expectativas_mes`, `user_financial_profile`

**Não existe** uma tabela `plano_cashflow_mes` ou equivalente no banco.

---

### P3 — Investimentos: 3 RTTs separados no mount

**Impacto:** Médio-Alto — atraso perceptível na tela de investimentos.

```python
# use-investimentos.ts
Promise.all([
  getInvestimentos(),        # GET /investimentos?limit=200
  getPortfolioResumo(),      # GET /investimentos/resumo
  getDistribuicaoPorTipo()   # GET /investimentos/distribuicao-tipo
])
```

Apesar do `Promise.all`, são 3 RTTs simultâneos que poderiam ser 1. Sem cache, qualquer filtro recarrega tudo.

**Localização:** `src/features/investimentos/hooks/use-investimentos.ts` (linhas 40-44)

---

### P4 — Goals: full refetch após toda mutação

**Impacto:** Médio — UX lenta em telas de orçamento.

Toda mutação (criar, editar, excluir meta) dispara um `loadGoals()` completo:
```
createGoal()  → POST → loadGoals() → GET /budget/planning?mes=...
updateGoal()  → PATCH → loadGoals() → GET /budget/planning?mes=...
deleteGoal()  → DELETE → loadGoals() → GET /budget/planning?mes=...
```

Não há optimistic updates. O usuário espera a resposta do servidor antes de ver qualquer mudança na UI.

**Localização:** `src/features/goals/hooks/use-goals.ts` (linhas 47-60)

---

### P5 — Goals: range update = N chamadas ao backend

**Impacto:** Médio — afeta usuários que aplicam orçamento para o restante do ano.

`updateGoalValor(..., aplicarAteFinAno=true)` faz **1 chamada por mês restante**:
- Se o usuário está em Agosto → 5 chamadas (Ago, Set, Out, Nov, Dez)
- Se está em Janeiro → 12 chamadas

**Localização:** `src/features/goals/services/goals-api.ts` (linhas 301-319)

**Não existe** endpoint batch para esse caso.

---

## Problemas Moderados

### P6 — Módulos sem cache algum

Os seguintes módulos fazem fetch sempre que renderizam, sem nenhuma camada de cache:

| Módulo | Arquivo do hook |
|--------|----------------|
| Investimentos | `use-investimentos.ts` |
| Plano/Cashflow | chamadas diretas em `plano/api.ts` |
| Bancos | `use-banks.ts` |
| Categorias | `use-categories.ts` |
| Transações | `transactions/page.tsx` |
| Upload (compat. matrix) | `upload-api.ts` |

**Impacto:** Cada navegação ou re-render resulta em requests desnecessários.

---

### P7 — Banks e Categorias: full refetch após mutação + sem deduplicação

Similar ao P4, mas mais grave: não há cache algum. Se dois componentes chamam `fetchBanks()` ao mesmo tempo, são feitas 2 requests idênticas.

**Localização:**
- `src/features/banks/hooks/use-banks.ts` (linhas 31, 53)
- `src/features/categories/hooks/use-categories.ts`

---

### P8 — Inconsistência de estratégia de cache

Dashboard e Goals têm cache in-memory com TTL. Os demais módulos não têm nada. Não há camada de cache global compartilhada.

Consequência: se Dashboard e Upload ambos precisam dos bancos (`/compatibility/`), fazem fetches independentes sem compartilhar o resultado.

---

## Problemas Menores

### P9 — Paginação offset em transações

`limit=10` e `page=X` hardcoded. Sem cursor-based pagination. Problemático para datasets grandes (degradação linear com tamanho).

### P10 — `limit=200` hardcoded em investimentos

Sem paginação real. Para usuários com muitos ativos, retorna tudo de uma vez sem cursor.

### P11 — Anti-pattern: sem Suspense ou Streaming

Páginas aguardam todos os hooks completarem antes de renderizar qualquer coisa. Não há skeleton progressivo por seção.
