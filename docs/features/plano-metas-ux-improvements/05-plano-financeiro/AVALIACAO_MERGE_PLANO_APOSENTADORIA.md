# Avaliação: Merge Plano Financeiro + Plano de Aposentadoria

**Data:** 01/03/2026
**Atualizado:** 01/03/2026 (decisões finais consolidadas)
**Status:** DECISÕES TOMADAS — pronto para implementação

---

## 1. Situação Atual — Onde os Dados Vivem

### 1.1 Plano de Aposentadoria (`/mobile/personalizar-plano`)

| Dado | Tabela | Observação |
|------|--------|------------|
| Renda, aporte, idade, aposentadoria, retorno, inflação, patrimônio | `investimentos_cenarios` | Por cenário (usuário pode ter vários) |
| Ganhos extraordinários (13º, bônus, etc.) | `investimentos_cenarios.extras_json` | JSON com recorrência, evolução anual |
| Projeção mês a mês | `investimentos_cenario_projecao` | Patrimônio por mês |

**extras_json** contém:
```json
[
  {
    "mesAno": 12,
    "valor": 15000,
    "descricao": "13º salário",
    "recorrencia": "anual",
    "evoluir": true,
    "evolucaoValor": 5,
    "evolucaoTipo": "percentual"
  }
]
```

### 1.2 Plano Financeiro (Construtor + Cashflow)

| Dado | Tabela | Observação |
|------|--------|------------|
| Renda, aporte, idade, aposentadoria, patrimônio, taxa | `user_financial_profile` | Um por usuário |
| Sazonais, ganhos extras, parcelas | `base_expectativas` | tipo: sazonal_plano, renda_plano, parcela_futura |
| Metas por grupo | `budget_planning` | Por mês/grupo |

**base_expectativas** (por registro):
- descricao, valor, grupo, tipo_lancamento, mes_referencia (YYYY-MM), tipo_expectativa
- **Não tem:** recorrência, evolução anual

### 1.3 Sobreposição

| Conceito | Aposentadoria | Plano Financeiro |
|----------|---------------|------------------|
| Renda | `investimentos_cenarios.renda_mensal_alvo` | `user_financial_profile.renda_mensal_liquida` |
| Aporte | `investimentos_cenarios.aporte_mensal` | `user_financial_profile.aporte_planejado` |
| Idade, aposentadoria, retorno, inflação | `investimentos_cenarios` | `user_financial_profile` |
| Ganhos extraordinários | `extras_json` (rico: recorrência, evolução) | `base_expectativas` (simples: 1 registro = 1 mês) |

### 1.4 Como a projeção funciona hoje

Existem **dois sistemas de projeção completamente separados**:

| Sistema | Onde roda | Horizonte | Fonte de dados |
|---------|-----------|-----------|----------------|
| `get_projecao` (plano service) | Backend | 12 meses | `budget_planning` + `base_expectativas` |
| Projeção de aposentadoria | **Frontend** (`PersonalizarPlanoLayout.tsx`) | 30+ anos | `investimentos_cenarios` + `extras_json` |

A projeção longa **não usa `budget_planning`**. Para anos futuros sem dados na base, extrapola o aporte fixo com juros compostos. Isso significa que `investimentos_cenario_projecao` é apenas um cache de algo matematicamente trivial — 360 iterações de juros compostos custam próximo de zero.

---

## 2. Decisão: Matar o Plano de Aposentadoria como Feature Separada

**Decisão tomada:** A tela `/mobile/personalizar-plano` (Plano de Aposentadoria) é extinta. Tudo que ela faz bem passa a viver dentro do **Plano**.

### O que morre

| Item | Destino |
|------|---------|
| Tela `/mobile/personalizar-plano` | Extinta |
| `investimentos_cenarios` | Depreciada — parâmetros migram para `user_financial_profile` |
| `investimentos_cenario_projecao` | Extinta — cálculo passa para o backend do plano, on-demand |
| Múltiplos cenários | Nunca implementado de fato — um único cenário por usuário |
| `extras_json` | Depreciado — dados migram para `base_expectativas` |

### O que sobrevive e migra para o Plano

| Item | Como entra no Plano |
|------|---------------------|
| Gráfico de linha do tempo (patrimônio até aposentadoria) | Vira o gráfico longo do hub do plano |
| Parâmetros: taxa, inflação, idade aposentadoria, patrimônio | Já estão em `user_financial_profile` |
| Ganhos extraordinários com recorrência/evolução | Migram para `base_expectativas` com `metadata_json` |
| Cálculo da regra dos 4% | Movido para o backend do plano service |
| Slider de sensibilidade (economizar X% a mais) | Vive na Tela 4 do novo wizard |

---

## 3. Novo Wizard — 4 Telas

O Construtor de Plano (`/mobile/construir-plano`) absorve os parâmetros de aposentadoria e se torna a **única entrada do plano real**.

### Tela 1 — Renda
- Salário/renda mensal líquida
- Ganhos extraordinários de **renda** (13º, bônus, PLR)
- Recorrência disponível: bimestral, trimestral, semestral, anual (**não existe mensal**)

### Tela 2 — Gastos recorrentes por grupo
- Input de valor por grupo (Moradia, Transporte, Alimentação…)
- **Média dos últimos 3 meses visível** ao lado de cada grupo — âncora de realidade
- Aviso claro na tela: *"Tem gasto que não acontece todo mês? Adicione na próxima tela"*

### Tela 3 — Gastos extraordinários
- Grupo + subgrupo **obrigatórios**
- Recorrência mínima: **bimestral** — se é todo mês, pertence à Tela 2
- Valor, mês de início, evolução anual (opcional)
- Ao salvar: atualiza `budget_planning` e materializa em `expectativas_mes` (ver seção 5)

### Tela 4 — Plano de aposentadoria + projeção
- Inputs: taxa de retorno esperada, inflação, idade de aposentadoria, patrimônio atual
- Resumo consolidado: renda → gastos recorrentes → gastos extraordinários (médio mensal) → **aporte disponível**
- **Slider de sensibilidade**: "e se você economizar X% a mais/menos?" → projeção atualiza em tempo real
- Slider opera sobre o **aporte** (quanto sobra para investir), não sobre grupos individuais
- Se a projeção ficar ruim: *"Reveja seu plano"* com navegação de volta às telas anteriores

---

## 4. Regras de Produto — Gastos Extraordinários

| Regra | Detalhe |
|-------|---------|
| Recorrência mínima | Bimestral — mensal pertence ao plano base (Tela 2) |
| Grupo obrigatório | Para conectar ao `budget_planning` e `expectativas_mes` |
| Subgrupo obrigatório | Granularidade dentro do grupo |
| Efeito no budget | Upsert automático no `budget_planning` ao salvar |
| Proteção do plano | UI bloqueia recorrência mensal e redireciona para Tela 2 |
| Isolamento | Extraordinários nunca escrevem em `budget_planning.valor_planejado` diretamente (ver seção 5) |

---

## 5. Arquitetura de Dados — Separação e Performance

### 5.1 Separação entre plano base e extraordinários

**Problema:** Se extraordinários escrevem em `budget_planning.valor_planejado`, ao deletar um extraordinário é impossível saber quanto subtrair sem rastrear o valor original — frágil e com risco de corrupção.

**Decisão:** `budget_planning` armazena **apenas o plano base recorrente** (Tela 2 do wizard). Extraordinários vivem exclusivamente em `base_expectativas` → `expectativas_mes`.

| Tabela | O que armazena |
|--------|---------------|
| `budget_planning` | Plano base por grupo/mês — só o que o usuário definiu na Tela 2 |
| `expectativas_mes` | Extraordinários expandidos por grupo/mês — criados/destruídos com segurança |

Queries que precisam do total planejado fazem a soma das duas:

```
total_planejado(grupo, mes) = budget_planning.valor_planejado
                            + SUM(expectativas_mes.valor WHERE grupo + mes)
```

**Benefício:** Deletar ou editar um extraordinário não toca em nada no `budget_planning`. Rollback é grátis.

A tela de budget consegue mostrar o breakdown:
> *"Transporte: R$ 800 base + R$ 2.000 IPVA em Março = R$ 2.800 esse mês"*

### 5.2 Solução do gargalo de performance

**Problema atual:** `get_cashflow` faz ~5 queries por mês × 12 meses = ~60 queries por request. Centralizar `get_planejado_por_grupo_mes` com JOIN em runtime tornaria isso ainda pior em escala.

**Solução: `expectativas_mes` como tabela materializada**

```
expectativas_mes
├── user_id
├── mes_referencia  (YYYY-MM, indexado)
├── grupo           (nullable — sazonais têm grupo)
├── subgrupo        (nullable)
├── tipo            (debito | credito)
├── valor
└── origem_expectativa_id  (FK para base_expectativas)
```

**Fluxo de escrita (acontece raramente — ao salvar o extraordinário):**
```
Usuário salva: "IPVA, R$ 2.000, Transporte, Março, anual, evoluir 5%"
    ↓
1. Salva em base_expectativas (com metadata_json de recorrência/evolução)
2. Expande e faz UPSERT em expectativas_mes (próximos 12 meses)
3. budget_planning não é alterado — total = budget + expectativas_mes (seção 5.1)
```

**Fluxo de leitura (hot path — acontece em todo request):**
```
get_cashflow / get_orcamento:
    → 1 query budget_planning (todos os grupos do ano, indexed)
    → 1 query expectativas_mes (todos os meses do ano, indexed)
    → merge em memória por grupo+mes
    → sem expansão em runtime, sem JOIN complexo
```

**Resultado:**
- Leitura = O(1) por mês — dados já materializados
- A query cara (expansão) acontece só no save — raramente
- Job diário/trigger garante rolagem dos 12 meses (quando Jan passa, Fev do próximo ano entra)
- Para projeção de longo prazo (30 anos): backend calcula on-demand com math puro, sem DB

### 5.3 Função centralizada no backend

Todos os serviços que precisam de "total planejado por grupo/mês" chamam uma única função:

```python
def get_planejado_por_grupo_mes(user_id, ano, mes):
    base = query budget_planning WHERE user_id + mes_referencia
    extras = query expectativas_mes WHERE user_id + mes_referencia
    return merge(base, extras)  # soma por grupo
```

Nenhum serviço sabe que existem duas tabelas por baixo.

---

## 6. Impacto nas Queries Existentes

Toda query que hoje lê só `budget_planning` para calcular "total planejado" precisará considerar `expectativas_mes`:

| Onde | O que muda |
|------|-----------|
| `get_resumo` (plano service) | `total_budget` = budget_planning + expectativas_mes |
| `get_cashflow` | `gastos_recorrentes` + `gastos_extras` via `expectativas_mes` materializada |
| `get_orcamento` | Meta por grupo = budget_planning + expectativas_mes do mês |
| `get_impacto_longo_prazo` | Usa `get_resumo` — herdado |
| Tela 4 wizard (resumo) | Breakdown: base + extraordinários → aporte disponível |
| Projeção longa (aposentadoria) | Backend, math puro, `user_financial_profile` — sem `budget_planning` |

---

## 7. Fluxo de Uso: Atualizar Plano com Gasto Extraordinário

### 7.1 Caso de uso
Usuário quer registrar IPVA de Março, que vai se repetir todo ano e crescer 5%.

### 7.2 Estrutura obrigatória

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| **nome** (descricao) | Sim | Ex: "IPVA" |
| **grupo** | Sim | Ex: "Transporte" — conecta ao orçamento |
| **subgrupo** | Sim | Ex: "IPVA" — granularidade |
| valor | Sim | |
| mes_inicio | Sim | Mês de início (1-12) |
| recorrencia | Sim | bimestral, trimestral, semestral, anual (**não mensal**) |
| evoluir, evolucaoValor, evolucaoTipo | Opcional | Para evolução anual |

### 7.3 Fluxo completo

```
Usuário adiciona: "IPVA, R$ 2.000, Transporte/IPVA, Março, anual, evoluir 5%"
    ↓
1. Salva em base_expectativas com metadata_json
2. Expande e upsert em expectativas_mes (Mar/26, Mar/27, Mar/28…, próximos 12 meses)
3. budget_planning não é alterado (seção 5.1)
4. Cashflow de Março: budget_planning base + expectativas_mes IPVA = total já correto
5. Projeção de aposentadoria: usa aporte recalculado — já reflete o IPVA anual
```

### 7.4 "Vale pra frente todos os meses" (recorrente)

Se o usuário adiciona algo recorrente (ex.: "a partir de Março, todo trimestre"):
- Atualiza `expectativas_mes` para próximos 12 meses (expandir e upsert)
- budget_planning não é alterado
- Projeção de aposentadoria reflete via aporte recalculado (total = budget + expectativas_mes)

---

## 8. Schema — Mudanças Necessárias

| Tabela | Mudança |
|--------|---------|
| `base_expectativas` | Adicionar `metadata_json` (nullable), `subgrupo` (nullable) |
| `budget_planning` | **Sem alteração** — total = budget + expectativas_mes (seção 5.1) |
| `expectativas_mes` | **Nova tabela** — materialização dos extraordinários expandidos |
| `user_financial_profile` | Absorver campos de `investimentos_cenarios` (taxa_retorno já existe) |
| `investimentos_cenarios` | Depreciada após migração |
| `investimentos_cenario_projecao` | Extinta — sem substituição (cálculo on-demand) |

---

## 9. Plano de Implementação

| Fase | Task | Prioridade |
|------|------|-----------|
| 1 | Migration: `metadata_json` + `subgrupo` em `base_expectativas` | Alta |
| 2 | Migration: criar `expectativas_mes` | Alta |
| 3 | Backend: `get_expectativas_por_mes` lê de `expectativas_mes` (não expande em runtime) | Alta |
| 4 | Backend: ao salvar expectativa, expande e materializa em `expectativas_mes` | Alta |
| 5 | Backend: `get_planejado_por_grupo_mes` centralizado | Alta |
| 6 | Backend: atualizar `get_resumo`, `get_cashflow`, `get_orcamento` para usar função central | Alta |
| 7 | Backend: projeção longa (30 anos) no plano service (math puro, sem `investimentos_cenarios`) | Média |
| 8 | Wizard: nova Tela 1 (renda + ganhos extras de renda) | Média |
| 9 | Wizard: nova Tela 2 (gastos por grupo + média 3 meses) | Média |
| 10 | Wizard: nova Tela 3 (gastos extraordinários — recorrência mínima bimestral) | Média |
| 11 | Wizard: nova Tela 4 (parâmetros aposentadoria + resumo + slider) | Média |
| 12 | Migrar `extras_json` de `investimentos_cenarios` → `base_expectativas` | Baixa |
| 13 | Depreciar `investimentos_cenarios` e `investimentos_cenario_projecao` | Baixa |
| 14 | Job diário: garantir rolagem dos próximos 12 meses em `expectativas_mes` | Baixa |

---

## 10. Decisões Finais

| Decisão | Escolha |
|---------|---------|
| Feature aposentadoria separada | **Extinta** — tudo migra para o Plano |
| Múltiplos cenários | **Não** — um único cenário por usuário |
| Fonte de verdade do plano real | **Construtor** (wizard 4 telas) |
| Extraordinários mensais | **Proibidos** — recorrência mínima bimestral |
| `budget_planning` para extraordinários | **Não** — tabela separada `expectativas_mes` |
| Projeção curta (12m) | Backend, usa `budget_planning` + `expectativas_mes` |
| Projeção longa (30 anos) | Backend, math puro com `user_financial_profile` |
| Performance hot path | `expectativas_mes` materializada — leitura O(1) |
| Grupo + subgrupo nos extraordinários | **Obrigatórios** |
| Slider de sensibilidade | Tela 4 do wizard, opera sobre aporte |
