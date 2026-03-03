# 🗺️ Mapeamento de APIs: Tela Plano vs Tela Dashboard (tab Orçamento)

> **Objetivo:** Documentar as diferenças entre as APIs e fontes de dados que alimentam a tela `/mobile/plano` vs o tab Orçamento de `/mobile/dashboard`, separando plano de despesas e plano de investimentos.

---

## 1. Visão Geral dos Componentes

| Tela | Rota | Componentes Relevantes |
|------|------|------------------------|
| **Plano** | `/mobile/plano` | `PlanoResumoCard`, `OrcamentoCategorias`, `TabelaReciboAnual`, `ProjecaoChart` |
| **Dashboard (tab Orçamento)** | `/mobile/dashboard` → tab Orçamento / Resultado | `OrcamentoTab` |

---

## 2. Plano de Despesas

### 2.1 Tela Plano

| Componente | Função | API | Endpoint Backend | Fonte de Dados (DB) |
|---|---|---|---|---|
| `PlanoResumoCard` | Renda declarada | `getResumoPlano()` | `GET /api/v1/plano/resumo?ano=&mes=` | `user_financial_profile.renda_mensal_liquida` |
| `PlanoResumoCard` | Total planejado (budget) | idem | idem | `budget_planning` (Despesa) + `expectativas_mes` (sazonais/debitadas) |
| `PlanoResumoCard` | Disponível (renda − budget) | idem | idem | calculado: renda − total_planejado |
| `PlanoResumoCard` | Total despesas realizadas | `fetchGoals()` | `GET /api/v1/budget/planning?mes_referencia=YYYY-MM` | `budget_planning.valor_realizado` ← calculado via `journal_entries` (CategoriaGeral='Despesa') |
| `OrcamentoCategorias` | Gasto real por grupo | `getOrcamento()` | `GET /api/v1/plano/orcamento?ano=&mes=` | `journal_entries` (SQL direto, SUM ABS(Valor) por GRUPO) |
| `OrcamentoCategorias` | Meta por grupo | idem | idem | `plano_meta_categoria` → fallback: `budget_planning` + `expectativas_mes` |
| `TabelaReciboAnual` | Cashflow 12 meses (gastos) | `getCashflow()` | `GET /api/v1/plano/cashflow?ano=` | `budget_planning` (planejado) + `journal_entries` (realizado); usa realizado quando disponível |

### 2.2 Dashboard (tab Orçamento) — componente `OrcamentoTab`

| Componente | Função | API | Endpoint Backend | Fonte de Dados (DB) |
|---|---|---|---|---|
| Resumo do Mês | Gastos realizados totais | `fetchGoals()` | `GET /api/v1/budget/planning?mes_referencia=YYYY-MM` | `budget_planning.valor_realizado` ← via `journal_entries` |
| Resumo do Mês | Gastos **planejados** para o Resumo | `fetchPlanoCashflowMes()` | `GET /api/v1/plano/cashflow?ano=&modo_plano=true` → campo `gastos_recorrentes + extras_debitos` | `budget_planning` (Despesa) + `expectativas_mes` (sazonais) |
| Despesas vs Plano (barra / lista) | Planejado por grupo | `fetchGoals()` | `GET /api/v1/budget/planning?mes_referencia=YYYY-MM` | `budget_planning.valor_planejado` **somente** (sem expectativas_mes) |
| Despesas vs Plano (barra / lista) | Realizado por grupo | idem | idem | `budget_planning.valor_realizado` ← via `journal_entries` |

### 2.3 Diferenças Críticas — Despesas

| Dimensão | Tela Plano | Tela Dashboard |
|---|---|---|
| **Endpoint principal** | `GET /plano/orcamento` | `GET /budget/planning` (via `fetchGoals`) |
| **Valor planejado (total resumo)** | `budget_planning` **+ `expectativas_mes`** (sazonais, parcelas) | `plano/cashflow?modo_plano=true` → `gastos_recorrentes + extras_debitos` (também inclui expectativas) |
| **Valor planejado (por grupo / barra)** | `budget_planning` + `expectativas_mes` via `get_planejado_por_grupo_mes()` | `budget_planning.valor_planejado` **apenas** — sem extras do mês |
| **Valor realizado por grupo** | `journal_entries` SQL direto (`SUM(ABS(Valor))`) | `budget_planning.valor_realizado` (calculado no backend) — mesma fonte, lógica idêntica |
| **Inclui sazonais no planejado por grupo** | ✅ Sim (`expectativas_mes`) | ❌ Não (só o budget base) |
| **Barras de progresso** | `OrcamentoCategorias` via `/plano/orcamento` | `OrcamentoTab` via `/budget/planning` |
| **Renda** | Exibe renda declarada (`user_financial_profile`) | Exibe receitas realizadas (`income-sources` → `journal_entries`) |

> **⚠️ Divergência de destaque:** O plano de despesas por grupo na barra da tela Dashboard **não inclui expectativas_mes** no valor planejado. Isso pode gerar inconsistência quando há sazonais cadastradas (ex: seguro anual em outubro). A tela Plano, via `/plano/orcamento`, reflete o total correto.

---

## 3. Plano de Investimentos

### 3.1 Tela Plano

| Componente | Função | API | Endpoint Backend | Fonte de Dados (DB) |
|---|---|---|---|---|
| `PlanoResumoCard` | Total investido (realizado) | `fetchGoals()` → filtra `categoria_geral === 'Investimentos'` | `GET /api/v1/budget/planning?mes_referencia=YYYY-MM` | `budget_planning.valor_realizado` ← via `journal_entries` (CategoriaGeral='Investimentos') |
| `PlanoResumoCard` | Aporte planejado | `fetchAportePrincipalPorMes()` | `GET /api/v1/investimentos/cenarios/principal/aporte-mes?year=&month=` | `CenarioProjecao` (cenário de aposentadoria — pode ter aportes extraordinários por mês) |
| `TabelaReciboAnual` | Aporte planejado (linha cashflow) | `getCashflow()` | `GET /api/v1/plano/cashflow?ano=` | `user_financial_profile.aporte_planejado` (campo fixo) |
| `TabelaReciboAnual` | Investimentos realizados (linha cashflow) | idem | idem | `journal_entries` (CategoriaGeral='Investimentos') |
| `ProjecaoChart` | Patrimônio projetado | `getProjecao()` | `GET /api/v1/plano/projecao?ano=&meses=` | `user_financial_profile` (aporte, patrimônio inicial, taxa) |

### 3.2 Dashboard (tab Orçamento) — componente `OrcamentoTab`

| Componente | Função | API | Endpoint Backend | Fonte de Dados (DB) |
|---|---|---|---|---|
| Investimentos vs Plano (mês) | Total investido realizado | `fetchGoals()` → filtra `categoria_geral === 'Investimentos'` | `GET /api/v1/budget/planning?mes_referencia=YYYY-MM` | `budget_planning.valor_realizado` ← `journal_entries` |
| Investimentos vs Plano (YTD/Ano) | Total investido realizado | `fetchOrcamentoInvestimentos()` | `GET /api/v1/dashboard/orcamento-investimentos?year=&ytd_month=` | `journal_entries` (CategoriaGeral='Investimentos', SUM por período) |
| Investimentos vs Plano (mês) | **Aporte planejado — fonte primária** | `fetchPlanoCashflowMes()` | `GET /api/v1/plano/cashflow?ano=&modo_plano=true` → campo `aporte_planejado` | `user_financial_profile.aporte_planejado` (wizard de plano) |
| Investimentos vs Plano (mês) | **Aporte planejado — fallback** | `fetchAportePrincipalPorMes()` | `GET /api/v1/investimentos/cenarios/principal/aporte-mes?year=&month=` | `CenarioProjecao` (cenário de aposentadoria) |
| Investimentos vs Plano (YTD) | Aporte planejado acumulado | `fetchAportePrincipalPeriodo()` | `GET /api/v1/investimentos/cenarios/principal/aporte-periodo?year=&ytd_month=` | `CenarioProjecao` (soma de aportes do cenário no período) |

### 3.3 Diferenças Críticas — Investimentos

| Dimensão | Tela Plano | Tela Dashboard |
|---|---|---|
| **Valor investido (realizado) — mês** | `budget/planning` → grupos Investimentos → `valor_realizado` | Idêntico: `budget/planning` → grupos Investimentos |
| **Valor investido (realizado) — YTD** | ❌ Não suporta modo YTD | ✅ `GET /dashboard/orcamento-investimentos?ytd_month=` (via `journal_entries` diretamente) |
| **Aporte planejado — fonte** | Sempre `CenarioProjecao` via `/cenarios/principal/aporte-mes` | **Primary:** `user_financial_profile.aporte_planejado` via `plano/cashflow?modo_plano=true`; **Fallback:** `CenarioProjecao` via `/cenarios/principal/aporte-mes` |
| **Aporte planejado — tabela** | `user_financial_profile.aporte_planejado` (campo fixo, sem sazonais) na linha do cashflow | `user_financial_profile.aporte_planejado` (mesmo campo) |
| **Extraordinários de investimentos** | ✅ `CenarioProjecao.aporte` **já inclui** regular + extra (via tabela `investimentos_aportes_extraordinarios`). `/cenarios/principal/aporte-mes` retorna esse valor combinado. | ⚠️ Atualmente usa `user_financial_profile.aporte_planejado` (fixo, sem extras). **Após I1:** passa a usar cenário → automaticamente inclui extraordinários |
| **Modo YTD aporte** | ❌ Não disponível | ✅ `/cenarios/principal/aporte-periodo` (soma do cenário Jan..N) |
| **CTA "sem plano"** | Exibe "sem plano" quando `aportePrincipal === 0` (cenário vazio) | Exibe CTA quando **ambos** cashflow e cenário retornam 0 |

> **⚠️ Divergência de destaque:** A fonte primária do aporte planejado no Dashboard é o **wizard de plano** (`user_financial_profile.aporte_planejado`), enquanto na tela Plano (`PlanoResumoCard`) é sempre o **cenário de aposentadoria** (`CenarioProjecao`). Se o usuário tiver um cenário com aportes extraordinários (ex: 13º salário em dezembro), o Dashboard pode exibir valor diferente da tela Plano para esses meses.

---

## 4. Resumo em Diagrama

```
┌─────────────────────────────────────────────────────────────────────┐
│  TELA PLANO (/mobile/plano)                                         │
│                                                                     │
│  Plano Despesas:                                                    │
│  ├── /plano/resumo          → renda + total_budget (c/ expectativas)│
│  ├── /plano/orcamento       → gasto real vs meta por grupo          │
│  │     └── realizado: journal_entries (SQL direto)                  │
│  │     └── planejado: budget_planning + expectativas_mes            │
│  └── /plano/cashflow        → 12 meses (realizado | planejado)      │
│                                                                     │
│  Plano Investimentos:                                               │
│  ├── /budget/planning       → valor_realizado grupos Investimentos  │
│  ├── /cenarios/principal/aporte-mes → aporte planejado (cenário)    │
│  └── /plano/cashflow        → aporte_planejado (perfil fixo)        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  TELA DASHBOARD (tab Orçamento)                                     │
│                                                                     │
│  Plano Despesas:                                                    │
│  ├── /budget/planning       → valor_planejado (SEM expectativas_mes)│
│  │     └── realizado: budget_planning.valor_realizado               │
│  │     └── planejado por grupo: budget_planning.valor_planejado     │
│  └── /plano/cashflow?modo_plano=true                                │
│        └── gastos_recorrentes + extras_debitos → Resumo do Mês     │
│                                                                     │
│  Plano Investimentos:                                               │
│  ├── /budget/planning       → valor_realizado grupos Investimentos  │
│  ├── /plano/cashflow?modo_plano=true → aporte_planejado (PRIMARY)   │
│  ├── /cenarios/principal/aporte-mes → fallback mês                  │
│  ├── /cenarios/principal/aporte-periodo → YTD                       │
│  └── /dashboard/orcamento-investimentos → realizado YTD             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Tabela de Endpoints por Contexto

| Endpoint | Tela Plano | Dashboard | O que entrega |
|---|:---:|:---:|---|
| `GET /plano/resumo` | ✅ | ❌ | renda + total_budget (com extras) + disponivel |
| `GET /plano/orcamento` | ✅ | ❌ | gasto real + meta por grupo (plano categ.) |
| `GET /plano/cashflow` (sem modo_plano) | ✅ | ❌ | 12 meses: realizado + planejado + saldo |
| `GET /plano/cashflow?modo_plano=true` | ❌ | ✅ | aporte_planejado + gastos recorrentes do mês |
| `GET /budget/planning` | ✅ (invest.) | ✅ (desp.+invest.) | metas por grupo: planejado + realizado |
| `GET /dashboard/income-sources` | ✅ (PlanoResumoCard) | ✅ | receitas realizadas por fonte |
| `GET /dashboard/orcamento-investimentos` | ❌ | ✅ (YTD) | investimentos realizados vs planejado (período) |
| `GET /investimentos/cenarios/principal/aporte-mes` | ✅ | ✅ (fallback) | aporte do cenário para o mês |
| `GET /investimentos/cenarios/principal/aporte-periodo` | ❌ | ✅ (YTD) | aporte acumulado do cenário Jan..N |
| `GET /dashboard/budget-vs-actual` | ❌ | ✅ (fetchExpenseSources) | comparação realizado vs planejado por grupo |

---

## 6. Fontes de Dados por Campo

### Campo: "Aporte Planejado"

```
user_financial_profile.aporte_planejado     ← wizard construir-plano (campo fixo)
   └── exposto por: GET /plano/cashflow → meses[n].aporte_planejado
   └── usado por: Dashboard (primary)

CenarioProjecao.aporte_mensal (por mês)     ← cenário de aposentadoria (pode variar por mês)
   └── exposto por: GET /cenarios/principal/aporte-mes?year=&month=
   └── usado por: Tela Plano (primary) | Dashboard (fallback)
```

### Campo: "Gastos Planejados (totais)"

```
budget_planning.valor_planejado             ← metas por grupo (tab Metas)
+ expectativas_mes.valor (tipo=debito)      ← gastos sazonais/parcelas
   └── exposto por: GET /plano/cashflow → meses[n].gastos_recorrentes + extras_debitos
   └── exposto por: GET /plano/resumo → total_budget
   └── exposto por: GET /plano/orcamento → por grupo (inclui extras)

budget_planning.valor_planejado             ← somente budget base, SEM expectativas
   └── exposto por: GET /budget/planning → budgets[n].valor_planejado
   └── usado por: Dashboard Despesas vs Plano (por grupo)
```

### Campo: "Gastos Realizados (por grupo)"

```
journal_entries                             ← transações importadas
  WHERE CategoriaGeral = 'Despesa'
  AND MesFatura = YYYYMM
  AND IgnorarDashboard = 0
  AND GRUPO IS NOT NULL
  → SUM(ABS(Valor)) por GRUPO

Exposto via:
  - GET /plano/orcamento   → campo gasto (SQL direto)
  - GET /budget/planning   → campo valor_realizado (calculado no service)
  - GET /dashboard/budget-vs-actual → campo realizado
```

---

## 7. Riscos de Inconsistência Identificados

| # | Cenário | Impacto | Severidade | Status |
|---|---|---|---|---|
| 1 | Usuário cadastra expectativa sazonal (ex: seguro anual R$ 3.000 em outubro) | Tela Plano mostra meta por grupo **com** o extra; Dashboard mostrava **sem** | 🟡 Médio | ✅ Corrigido (D1-D3, 02/03/2026) |
| 2 | Aporte planejado no Dashboard só exibe o recorrente, não inclui extraordinários | Ver análise detalhada abaixo (§7.1) | 🟠 Alto | 🔴 Aberto |
| 3 | Metas Investimentos no budget/planning com `valor_realizado` desatualizado | Ambas as telas usam a mesma fonte, então falham juntas | 🟢 Baixo | — |

### 7.1 Análise: Aporte Planejado mostra só recorrente (jan/26 e todos os meses)

**Observação:** "Investimentos vs Plano" no Dashboard exibe R$ 2.700/mês para jan/26, mesmo que o usuário tenha aportes extraordinários planejados naquele mês (ex: investimento de 13º, bônus, reserva extra).

**Causa raiz — backend (`app_dev/backend/app/domains/plano/service.py`, método `get_cashflow`):**

```python
# Linha executada UMA VEZ antes do loop de 12 meses:
aporte = float(profile.aporte_planejado or 0) if profile else 0.0

# Dentro do loop, cada mês recebe o MESMO valor fixo:
"aporte_planejado": aporte,   # ← invariante; nunca muda mês a mês
```

`profile.aporte_planejado` é o campo `user_financial_profile.aporte_planejado` — o aporte **recorrente mensal** configurado no wizard. É idêntico para todos os 12 meses.

Aportes extraordinários (ex: investir o 13º em dezembro) são criados como `base_expectativas` com `tipo_lancamento = "credito"` e materializados em `expectativas_mes`. No cashflow, esses valores aparecem no campo separado:

```python
"extras_creditos": round(exp_mes["creditos"], 2),  # ← aportes extras + quaisquer outros créditos
```

**Causa raiz — frontend (`dashboard-api.ts`, interface `PlanoCashflowMes`):**

```typescript
export interface PlanoCashflowMes {
  aporte_planejado: number   // só o recorrente (user_financial_profile.aporte_planejado)
  extras_creditos: number    // todos os créditos extraordinários (não filtrado por Investimentos)
  // ...
}

// OrcamentoTab lê apenas:
const totalPlanejadoInv = planoMes?.aporte_planejado ?? 0
// extras_creditos é ignorado
```

**Por que não basta somar `extras_creditos`:**

`extras_creditos` agrega **todos** os créditos de `expectativas_mes` sem filtrar por categoria. Inclui tanto aportes extras em Investimentos quanto rendas extras (ex: freelance pontual, restituição de IR) que o usuário pode não ter intenção de investir. Somar cegamente geraria falso planejamento.

**Solução proposta (não implementada):**

Duas opções:

1. **Backend (menor impacto):** No `get_cashflow`, adicionar campo `extras_creditos_investimentos` calculando só `expectativas_mes` onde `grupo` pertence a um grupo de categoria `Investimentos`:
   ```python
   from app.domains.grupos.models import BaseGruposConfig
   grupos_inv = {nome for nome, cat in grupos_config.items() if cat == "Investimentos"}
   extras_inv = sum(v for g, v in exp_items if g in grupos_inv and tipo == "credito")
   "aporte_planejado_total": aporte + extras_inv,  # recorrente + extraordinários de Investimentos
   ```

2. **Frontend (mais simples, aceita imprecisão):** Somar `extras_creditos` ao `aporte_planejado` assumindo que todos os créditos extras são destinados a Investimentos — válido se o usuário só usa expectativas-crédito para aportes extras.

**Impacto atual:** Para meses sem aportes extraordinários, o comportamento está correto. Para meses com aporte extra planejado (ex: jan/26 com aporte de R$ 5.000 extra), o Dashboard subestima o planejado — mostrando R$ 2.700 em vez de R$ 7.700.

---

## 8. Plano de Unificação (Tela Plano → Tela Dashboard)

> **Objetivo:** Fazer o Dashboard usar as mesmas fontes de dados da tela Plano para despesas e investimentos, eliminando as divergências listadas acima.
>
> **Regra preservada — 90% de receita:** A lógica que decide se um mês usa dados **realizados** ou dados do **plano** (`use_realizado = renda_realizada >= 0.9 * renda_esperada`) existe **exclusivamente** dentro de `GET /plano/cashflow` (sem `modo_plano=true`). Essa lógica **não deve ser tocada**. O Dashboard continuará chamando `/plano/cashflow?modo_plano=true` para o Resumo do Mês (que força valores planejados), e isso não muda.

---

### 8.1 Unificação do Plano de Despesas

**Problema:** A lista "Despesas vs Plano" no Dashboard mostra `budget_planning.valor_planejado` por grupo **sem** as expectativas_mes (gastos sazonais/parcelas). A tela Plano, via `/plano/orcamento`, inclui as expectativas_mes no planejado.

**Objetivo:** Dashboard exibir o mesmo `valor_planejado por grupo` que a tela Plano.

#### Passo D1 — Backend: adicionar campo `valor_planejado_com_extras` no `GET /budget/planning`

**Arquivo:** `app_dev/backend/app/domains/budget/service.py` → método `_get_budget_planning_impl`

Após calcular `resultado` (lista de budgets), somar os extras de `expectativas_mes` para cada grupo:

```python
# Adicionar ao final de _get_budget_planning_impl, antes do return

# Buscar expectativas_mes do mês (sazonais/parcelas, tipo=debito)
from app.domains.plano.models import ExpectativaMes
extras_rows = (
    self.db.query(ExpectativaMes.grupo, func.sum(ExpectativaMes.valor))
    .filter(
        ExpectativaMes.user_id == user_id,
        ExpectativaMes.mes_referencia == mes_referencia,
        ExpectativaMes.tipo == "debito",
        ExpectativaMes.grupo.isnot(None),
        ExpectativaMes.grupo != "",
    )
    .group_by(ExpectativaMes.grupo)
    .all()
)
extras_por_grupo = {r.grupo: float(r[1] or 0) for r in extras_rows}

# Adicionar campo valor_planejado_com_extras em cada item do resultado
for item in resultado:
    extra = extras_por_grupo.get(item["grupo"], 0.0)
    item["valor_planejado_com_extras"] = item["valor_planejado"] + extra
```

> ⚠️ Não alterar `valor_planejado` (campo existente). Adicionar apenas o novo campo `valor_planejado_com_extras` para não quebrar outros callers.

#### Passo D2 — Frontend: expor `valor_planejado_com_extras` na interface `Goal`

**Arquivo:** `app_dev/frontend/src/features/goals/types/index.ts` (ou onde `Goal` está definida)

```typescript
// Adicionar campo opcional (retro-compatível)
valor_planejado_com_extras?: number
```

**Arquivo:** `app_dev/frontend/src/features/goals/services/goals-api.ts` → função `fetchGoals`

```typescript
// No map de budgets → Goal, adicionar:
valor_planejado_com_extras: b.valor_planejado_com_extras ?? b.valor_planejado ?? 0,
```

#### Passo D3 — Frontend: `OrcamentoTab` usa `valor_planejado_com_extras`

**Arquivo:** `app_dev/frontend/src/features/dashboard/components/orcamento-tab.tsx`

Substituir o uso de `g.valor_planejado` pelo novo campo na seção de despesas:

```typescript
// Antes (linha do totalPlanejadoDesp):
const totalPlanejadoDesp = goalsDespesas.reduce((s, g) => s + (g.valor_planejado ?? 0), 0)

// Depois:
const totalPlanejadoDesp = goalsDespesas.reduce(
  (s, g) => s + (g.valor_planejado_com_extras ?? g.valor_planejado ?? 0), 0
)

// Na renderização por grupo (planejado e barra), substituir g.valor_planejado por:
const planejado = cat.valor_planejado_com_extras ?? cat.valor_planejado ?? 0
```

> ✅ O `resumoGastosPlanejados` (total do Resumo do Mês) já usa `/plano/cashflow?modo_plano=true → gastos_recorrentes + extras_debitos`, que inclui as expectativas. Esse campo **não muda**.

---

### 8.2 Unificação do Plano de Investimentos

**Problema:** A fonte primária do aporte planejado no Dashboard é `user_financial_profile.aporte_planejado` (via `plano/cashflow?modo_plano=true`), enquanto na tela Plano é `CenarioProjecao` via `/cenarios/principal/aporte-mes`. Para meses com aportes extraordinários no cenário (ex: 13º em dezembro), os valores divergem.

**Objetivo:** Dashboard usar `cenarios/principal/aporte-mes` como fonte primária (igual ao Plano), com fallback para `user_financial_profile.aporte_planejado`.

#### Passo I1 — Frontend: `OrcamentoTab` — inverter prioridade das fontes

**Arquivo:** `app_dev/frontend/src/features/dashboard/components/orcamento-tab.tsx`

```typescript
// Antes (lógica atual — wizard como primary, cenário como fallback):
const totalPlanejadoInv = (planoMes?.aporte_planejado ?? 0) > 0
  ? (planoMes?.aporte_planejado ?? 0)
  : aportePrincipal   // aportePrincipal = cenarios/principal/aporte-mes

// Depois (cenário como primary, wizard como fallback — igual ao PlanoResumoCard):
const totalPlanejadoInv = aportePrincipal > 0
  ? aportePrincipal                            // cenarios/principal/aporte-mes (primary)
  : (planoMes?.aporte_planejado ?? 0)          // user_financial_profile.aporte_planejado (fallback)
```

> ⚠️ **Atenção:** Se o usuário não tem cenário configurado, `aportePrincipal` será 0, e o fallback garantirá que ainda apareça o valor do wizard. Esse caso é tratado automaticamente pelo fallback.

#### Passo I2 — Frontend: `PlanoResumoCard` — verificar que permanece igual

**Arquivo:** `app_dev/frontend/src/features/plano/components/PlanoResumoCard.tsx`

A tela Plano já usa `fetchAportePrincipalPorMes()` como fonte única. **Nenhuma alteração necessária aqui.** Apenas confirmar que a lógica não foi alterada por outros PRs.

---

### 8.2.1 Extraordinários de Investimentos — Por Que I1 É Suficiente

> **Resposta direta à questão:** Sim, os valores extraordinários do plano de investimentos **já são considerados** no valor planejado — e o Passo I1 é a única mudança necessária para expô-los corretamente no Dashboard.

#### Como os extraordinários de investimentos funcionam

A tabela `investimentos_aportes_extraordinarios` (model `AporteExtraordinario`) armazena aportes extras planejados dentro de um cenário de aposentadoria (ex: 13º salário investido em dezembro, bônus anual, venda de ativo). Quando o cenário é calculado/atualizado, esses valores são incorporados na coluna `aporte` da tabela `investimentos_cenario_projecao`:

```python
# investimentos/models.py — CenarioProjecao
aporte = Column(Numeric(15, 2), nullable=True)
# Docstring: "Aporte planejado do mês (regular + extraordinário)"
```

O endpoint `/cenarios/principal/aporte-mes` (via `get_aporte_principal_mes()` no repository) retorna exatamente `CenarioProjecao.aporte` — já com regular + extraordinário combinados:

```python
# investimentos/repository.py — get_aporte_principal_mes()
if proj and proj.aporte is not None:
    return float(proj.aporte)          # ← regular + extraordinário já somados
return float(principal.aporte_mensal or 0)   # fallback: apenas o base
```

O mesmo vale para o YTD: `get_aporte_principal_periodo()` soma `CenarioProjecao.aporte` de cada mês — extraordinários incluídos.

**Conclusão:** ao implementar I1 (usar `aportePrincipal` do cenário como primário no Dashboard), o valor planejado exibido passa automaticamente a incluir aportes extraordinários, sem nenhum passo backend adicional.

#### Distinção crítica — `expectativas_mes.tipo='credito'` NÃO são aportes de investimento

Os registros `ExpectativaMes` com `tipo="credito"` representam **renda extraordinária prevista** (ex: 13º salário recebido na conta corrente, bônus de trabalho). Eles impactam `extras_creditos` no cashflow do plano (abatendo dos `gastos_extras`), mas **não são investimentos**. O quanto dessa renda extra vai para investimentos é configurado **no cenário** via `AporteExtraordinario` — de forma independente.

#### Tabela de Simetria: Extraordinários de Despesas vs Investimentos

| Dimensão | Despesas Extraordinárias | Investimentos Extraordinários |
|---|---|---|
| **Tabela fonte** | `expectativas_mes` (`tipo='debito'`) | `investimentos_aportes_extraordinarios` |
| **Agregado em** | `ExpectativaMes.valor` por grupo e mês | `CenarioProjecao.aporte` (regular + extra) |
| **Endpoint que expõe** | D1: novo campo `valor_planejado_com_extras` em `/budget/planning` | `/cenarios/principal/aporte-mes` **já inclui** (nenhuma mudança backend) |
| **Passos necessários** | D1 (backend) + D2 (tipos) + D3 (frontend) | **Zero** — I1 já é suficiente |
| **YTD** | — | `/cenarios/principal/aporte-periodo` também já soma extras |

---

### 8.3 Ordem de Implementação (DAG)

```
D1 (backend: campo com_extras) 
  └──► D2 (frontend: interface Goal)
         └──► D3 (frontend: OrcamentoTab usa com_extras)

I1 (frontend: OrcamentoTab inverte prioridade)   ← independente de D1/D2/D3
```

### 8.4 Como Validar Após Implementação

```bash
# 1. Testar mês com expectativa sazonal cadastrada (ex: outubro com seguro)
# Navegar para /mobile/plano?mes=YYYY-10 e verificar total planejado por grupo
# Navegar para /mobile/dashboard tab Orçamento para o mesmo mês
# Os valores planejados por grupo devem ser idênticos

# 2. Testar mês com aporte extraordinário no cenário (ex: 13º em dezembro)
# Verificar que a tabela investimentos_aportes_extraordinarios tem uma entrada para dezembro
# e que CenarioProjecao.aporte para esse mês inclui o valor extra.
# Navegar para /mobile/plano — PlanoResumoCard usa cenário (valor correto)
# Navegar para /mobile/dashboard tab Orçamento — após I1, também usa cenário
# Os aportes planejados devem ser idênticos (ambos = regular + extraordinário)

# 3. Testar usuário SEM cenário configurado
# /mobile/dashboard deve mostrar fallback (valor do wizard) quando aportePrincipal = 0
# /mobile/plano deve continuar mostrando "sem plano" quando cenário = 0

# 4. Garantir que o Resumo do Mês no Dashboard continua correto
# gastos_recorrentes + extras_debitos (via /plano/cashflow?modo_plano=true) não foi alterado
# A regra dos 90% só existe em /plano/cashflow SEM modo_plano — não é afetada
```

### 8.5 O que NÃO mudar (regra dos 90%)

A regra dos 90% está em `app_dev/backend/app/domains/plano/service.py`, método `get_cashflow`:

```python
# Esta lógica NÃO deve ser alterada
use_realizado = False if modo_plano_sempre else (
    renda_realizada is not None
    and renda is not None
    and renda > 0
    and renda_realizada >= 0.9 * renda   # ← NUNCA TOCAR
)
```

- **`GET /plano/cashflow` (sem `modo_plano`):** usado pela tela Plano (`TabelaReciboAnual`, `ProjecaoChart`) — aplica a regra dos 90% para decidir entre realizado e planejado. **Não mudar.**
- **`GET /plano/cashflow?modo_plano=true`:** usado pelo Dashboard para o Resumo do Mês (sempre retorna valores planejados). **Continua igual.**
- As mudanças D1–D3 e I1 não tocam nenhum desses endpoints nem na lógica de `use_realizado`.

---

*Documento gerado em: 02/03/2026 — baseado no código atual das features `plano` e `dashboard` do frontend e dos domínios `plano`, `budget`, `dashboard` e `investimentos` do backend.*
