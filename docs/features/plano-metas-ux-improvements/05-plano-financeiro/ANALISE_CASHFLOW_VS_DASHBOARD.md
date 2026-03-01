# Análise: Por que os números do Cashflow diferem do Dashboard

**Data:** 28/02/2026  
**Objetivo:** Entender por que Receitas, Despesas e Investimentos no "Resumo do Mês" (dashboard) não batem com Renda, Gastos e Aporte na tabela "Cashflow anual".

---

## Resumo executivo

| Métrica | Dashboard (Resumo do Mês) | Cashflow (tabela anual) | Diferença provável |
|---------|---------------------------|-------------------------|---------------------|
| Receitas/Renda | 87.049 | 87k | ≈ igual |
| Despesas/Gastos | 25.016 | 26,3k | ~1.300 a mais no cashflow |
| Investidos/Aporte | 54.391 | 66,7k | ~12.300 a mais no cashflow |

**Causas identificadas:** fontes de dados diferentes, regras de filtro distintas e **soma com valores absolutos vs valores reais** (principal causa para Investimentos).

---

## 1. Fontes de dados

### Dashboard "Resumo do Mês" (OrcamentoTab)

Quando o usuário está no modo **Mês** (scroll de meses):

| Métrica | API | Endpoint |
|---------|-----|----------|
| Receitas | `fetchIncomeSources` | `GET /dashboard/income-sources?year=X&month=Y` |
| Despesas | `fetchGoals` | `GET /budget/planning?mes_referencia=YYYY-MM` |
| Investidos | `fetchGoals` | `GET /budget/planning?mes_referencia=YYYY-MM` |

Quando está em **YTD** ou **Ano**:

| Métrica | API | Endpoint |
|---------|-----|----------|
| Receitas | `metrics` | `GET /dashboard/metrics?year=X&ytd_month=Y` |
| Despesas | `metrics` | `GET /dashboard/metrics?year=X&ytd_month=Y` |
| Investidos | `fetchOrcamentoInvestimentos` | `GET /dashboard/orcamento-investimentos` |

### Cashflow (TabelaReciboAnual)

| Métrica | API | Endpoint |
|---------|-----|----------|
| Renda | `get_cashflow` | `GET /plano/cashflow?ano=X` |
| Gastos | `get_cashflow` | `GET /plano/cashflow?ano=X` |
| Aporte | `get_cashflow` | `GET /plano/cashflow?ano=X` |

---

## 2. Lógica de cálculo — Receitas/Renda

### Dashboard (income-sources)

**Arquivo:** `dashboard/repository.py` → `get_income_sources`

```
Filtros:
- user_id, MesFatura (ou date_filter)
- IgnorarDashboard = 0
- CategoriaGeral = 'Receita'
- GRUPO.isnot(None)   ← exclui transações sem grupo
- GRUPO != ''

Query: agrupa por GRUPO, soma(Valor)
Total = soma dos totais por grupo
```

### Cashflow (plano/service.py)

```
Filtros (quando use_realizado):
- user_id, MesFatura, IgnorarDashboard = 0
- GRUPO.isnot(None), GRUPO != ''   ← alinhado
- CategoriaGeral = 'Receita'

Query: agrupa por GRUPO, soma(Valor) por grupo
Total = soma dos totais por grupo
```

**Conclusão:** Receitas/Renda tendem a bater, pois ambos usam GRUPO not null e CategoriaGeral = Receita.

---

## 3. Lógica de cálculo — Despesas/Gastos

### Dashboard (budget/planning → goalsDespesas)

**Arquivo:** `budget/service.py` → `_get_budget_planning_impl`

1. Grupos em `budget_planning` com `categoria_geral = 'Despesa'` (via BaseGruposConfig)
2. Grupos com gastos no mês que **não** estão em budget_planning (`grupos_com_gasto`)

Para `grupos_com_gasto`:
```
Filtros:
- MesFatura, user_id, IgnorarDashboard = 0
- CategoriaGeral = 'Despesa'
- GRUPO.isnot(None), GRUPO != ''   ← só transações com grupo

Query: agrupa por GRUPO, soma(Valor)   ← valores REAIS (com sinal)
valor_realizado = abs(total) por grupo ← neta estornos dentro do grupo
```

Total despesas = soma de `valor_realizado` de todos os grupos Despesa.

### Cashflow (plano/service.py)

```
gastos_realizados = sum(ABS(Valor))   ← soma de VALORES ABSOLUTOS
Filtros:
- user_id, MesFatura, IgnorarDashboard = 0
- CategoriaGeral = 'Despesa'
- SEM filtro GRUPO   ← inclui transações com GRUPO null ou vazio
```

**Diferença 1 (GRUPO):** O cashflow inclui transações com GRUPO null/vazio. O dashboard não.

**Diferença 2 (soma abs vs real):** O dashboard usa `sum(Valor)` por grupo e depois `abs()` — ou seja, **neta** estornos/reembolsos dentro do grupo. O cashflow usa `sum(abs(Valor))` — soma os módulos, sem netar. Ex.: grupo com -1000 (gasto) e +500 (estorno): dashboard = 500, cashflow = 1500.

**Evidência (DB local):** Grupos como Carro, Alimentação, Compras e Tecnologia têm diferenças de R$ 0,02 a R$ 75 quando há sinais mistos no mês.

---

## 4. Lógica de cálculo — Investimentos/Aporte

### Dashboard (budget/planning → goalsInvestimentos)

O budget usa a `categoria_geral` do grupo em **BaseGruposConfig** para decidir se o grupo é Despesa ou Investimentos.

- Grupos em `budget_planning` com `categoria_geral = 'Investimentos'` em BaseGruposConfig
- Grupos com investimentos no mês que não estão em budget_planning (`grupos_com_investimento`)

Para cada grupo em budget_planning:
```
valor_realizado = _calcular_valor_realizado_grupo(grupo, categoria_geral)
  → filtra JournalEntry por GRUPO = grupo E CategoriaGeral = categoria_geral do grupo
```

Ou seja: o valor realizado de um grupo é calculado usando a **categoria_geral do grupo** (Despesa ou Investimentos), não a CategoriaGeral da transação.

### Cashflow (plano/service.py)

O cashflow usa `sum(Valor)` por grupo e depois `abs()` — mesma lógica do budget para investimentos. Porém, em versões anteriores ou em trechos diferentes do código, pode ter sido usado `sum(abs(Valor))`.

**Diferença principal (soma abs vs real):** Investimentos têm aplicações (negativas) e resgates (positivos). O dashboard usa `sum(Valor)` por grupo → **neta** aplicações e resgates → depois `abs()`. O cashflow, se usar `sum(abs(Valor))`, soma os módulos sem netar.

**Exemplo:** Grupo com -50k (aplicação) e +10k (resgate): dashboard = abs(-40k) = 40k; cashflow com sum(abs) = 60k.

**Evidência (DB local):** O grupo "Investimentos" em vários meses tem diferenças enormes:
- 202501: sum(Valor) = -14.712, sum(abs) = 38.604 → diff 23.892
- 202504: sum(Valor) = -89.604, sum(abs) = 121.646 → diff 32.041
- 202510: sum(Valor) = +2.898, sum(abs) = 115.423 → diff 112.524

**Conclusão:** A principal causa da diferença em Investimentos é **sum(abs(Valor))** vs **abs(sum(Valor))** por grupo. O dashboard neta; o cashflow (se usar sum(abs)) não neta.

---

## 5. Regra dos 90% (cashflow)

O cashflow tem a regra `use_realizado`:

- Se `renda_realizada >= 0.9 * renda_esperada` → usa valores realizados (receita, despesas, investimentos)
- Caso contrário → usa valores planejados (renda do perfil, gastos_recorrentes do budget, aporte planejado)

O dashboard sempre mostra realizados quando há mês selecionado. A regra dos 90% só afeta o cashflow e pode mudar o que é exibido em meses com receita abaixo do esperado.

---

## 6. Resumo das causas

| Causa | Onde | Efeito |
|------|------|--------|
| **sum(abs) vs abs(sum)** | Cashflow usa `sum(abs(Valor))`; dashboard usa `abs(sum(Valor))` por grupo | **Principal causa.** Com sinais mistos (estornos, resgates), cashflow mostra valor maior. Investimentos: diferenças de dezenas de milhares. Despesas: diferenças menores (estornos). |
| **GRUPO null em despesas** | Cashflow não filtra GRUPO em gastos_realizados | Gastos no cashflow > Despesas no dashboard (se houver despesas sem grupo) |
| **Categoria do grupo vs transação** | Dashboard usa categoria_geral do grupo (BaseGruposConfig); cashflow usa CategoriaGeral da transação | Investimentos no cashflow podem ser maiores se houver transações Investimentos em grupos Despesa |
| **Regra 90%** | Só no cashflow | Em meses com receita < 90% do esperado, cashflow usa planejado em vez de realizado |

---

## 7. Recomendações (para futura implementação)

1. **Gastos:** Usar `sum(Valor)` por grupo e depois `abs()` (como o budget), em vez de `sum(abs(Valor))`. Incluir filtro GRUPO not null.
2. **Investimentos:** Garantir que o cashflow use `abs(sum(Valor))` por grupo (já faz em `inv_por_grupo`), **não** `sum(abs(Valor))`. Verificar se há outro trecho usando sum(abs).
3. **Fonte única:** Avaliar reutilizar os mesmos endpoints ou funções do dashboard no cashflow para garantir consistência.

---

## Referências de código

| Componente | Arquivo |
|------------|---------|
| Dashboard Resumo | `frontend/.../orcamento-tab.tsx` |
| income-sources | `backend/.../dashboard/repository.py` → `get_income_sources` |
| budget/planning | `backend/.../budget/service.py` → `_get_budget_planning_impl` |
| valor_realizado por grupo | `backend/.../budget/service.py` → `_calcular_valor_realizado_grupo` |
| Cashflow | `backend/.../plano/service.py` → `get_cashflow` |
| Tabela cashflow | `frontend/.../TabelaReciboAnual.tsx` |
