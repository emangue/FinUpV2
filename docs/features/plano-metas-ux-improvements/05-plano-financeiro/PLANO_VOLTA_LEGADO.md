# Plano de Volta ao Legado — Compromissos e Expectativas

**Data:** 28/02/2026  
**Status:** ✅ Executado (sem migração de dados)  
**Objetivo:** Alinhar o sub-projeto 05-plano ao modelo de 3 camadas do legado, removendo `plano_compromissos` e adotando `budget_planning` + (futuro) `base_expectativas`.

---

## 1. Situação Atual vs Legado

### O que implementamos (Sprint 6)

| Item | Status | Problema |
|------|--------|----------|
| `user_financial_profile` | ✅ | OK — alinhado ao legado |
| `plano_metas_categoria` | ✅ | Redundante com `budget_planning` |
| `plano_compromissos` | ✅ | **Desvio** — não existe no legado; duplica budget |
| Renda (POST/GET) | ✅ | OK |
| Orçamento (GET) | ✅ | Usa `plano_metas` + fallback em `budget_planning` |
| CompromissosFixosList (frontend) | ✅ | UI que cadastra em `plano_compromissos` |

### O que o legado define

```
CAMADA 1 — REALIZADO
├── journal_entries
└── base_parcelas

CAMADA 2 — EXPECTATIVAS (base_expectativas)
   Sazonais, parcelas futuras, compromissos conhecidos
   → Soma ao plano base para projeção
   → Fase futura

CAMADA 3 — PLANO BASE
└── budget_planning  → meta mensal recorrente por grupo
   → Aluguel, financiamento, etc. ENTRAM AQUI
```

**Fórmula legado (Budget at risk):**
```
total_esperado = budget_planning.valor_planejado     ← plano base
              + SUM(base_expectativas do mês)        ← extras (sazonais, parcelas)
```

---

## 2. Decisão Arquitetural

**Remover** `plano_compromissos` e `plano_metas_categoria` como conceitos separados.

**Usar** apenas:
- `budget_planning` — metas recorrentes por grupo (inclui aluguel, financiamento etc.)
- `user_financial_profile` — renda
- (Futuro) `base_expectativas` — sazonais, parcelas futuras

**"Disponível"** = `Renda - SUM(budget_planning.valor_planejado)` do mês (ou subconjunto de grupos "fixos" se quisermos flag)

---

## 3. Plano de Execução

### Fase 1 — Migração de dados

**Pulada** — Nenhum dado de qualidade em `plano_compromissos`; migração não necessária.

### Fase 2 — Backend (remover plano_compromissos)

| Task | Descrição | Est. |
|------|-----------|------|
| B.1 | Remover endpoints `GET/POST/DELETE /plano/compromissos` do router | 0.5h |
| B.2 | Remover `PlanoCompromisso` do service, models, schemas | 0.5h |
| B.3 | Ajustar `disponivel_real` (A.07): usar `budget_planning` em vez de compromissos | 1h |
| B.4 | Migration: remover tabela `plano_compromissos` (ou deixar obsoleta, só dropar em fase posterior) | 0.5h |
| B.5 | Avaliar `plano_metas_categoria`: unificar com budget_planning ou manter só budget | 1h |

### Fase 3 — Frontend (remover CompromissosFixosList)

| Task | Descrição | Est. |
|------|-----------|------|
| F.1 | Remover `CompromissosFixosList` da tela Perfil Financeiro | 0.5h |
| F.2 | Remover API `getCompromissos`, `postCompromisso`, `deleteCompromisso` do frontend | 0.5h |
| F.3 | Ajustar `BudgetWidget`: disponível = renda - total budget (se aplicável) | 0.5h |
| F.4 | Adicionar link/CTA para `/mobile/budget` ou `/mobile/budget/manage` em Perfil Financeiro: "Gerenciar metas por grupo" | 0.5h |

### Fase 4 — Documentação e alinhamento

| Task | Descrição | Est. |
|------|-----------|------|
| D.1 | Atualizar `VISAO_FLUXO_DADOS.md`: remover "compromissos fixos" como item separado; reforçar budget_planning | 0.5h |
| D.2 | Atualizar `05-plano-financeiro/PLANO.md`: remover A.03, F.02; ajustar A.07 | 0.5h |
| D.3 | Atualizar PRD do 05-plano: S6 passa a ser "metas por grupo via budget" | 0.5h |

---

## 4. Ordem de Execução

```
1. M.1 (script migração) — se houver dados em plano_compromissos
2. B.1–B.4 (backend)
3. F.1–F.4 (frontend)
4. D.1–D.3 (docs)
```

---

## 5. O Que Fica na Tela Perfil Financeiro (após)

| Seção | Fonte |
|-------|-------|
| Renda mensal líquida | `user_financial_profile` |
| Metas por grupo | `budget_planning` — link para `/mobile/budget/manage` |
| Orçamento por categoria | `GET /plano/orcamento` (usa budget_planning) |

---

## 6. Próximos Passos (base_expectativas)

Quando implementarmos a Camada 2 — Expectativas:

- Criar `base_expectativas` (schema do legado)
- Tipos: `sazonal_plano`, `renda_plano`, `parcela_futura`
- `GET /budget/cashflow?ano=` — une realizado + expectativas + plano base
- Budget at risk — alertas antecipados por mês

Isso fica para **fase futura** (Construtor de Plano, wizard 4 etapas).

---

## 7. Checklist de Validação

- [ ] Nenhum endpoint `/plano/compromissos` ativo
- [ ] Perfil Financeiro mostra Renda + link para Metas (budget)
- [ ] Orçamento por categoria funciona com budget_planning
- [ ] BudgetWidget não quebra (sem compromissos)
- [ ] Dados migrados (se houver) de plano_compromissos → budget_planning
- [ ] Docs atualizados

---

## 8. Estimativa Total

| Fase | Estimativa |
|------|------------|
| Migração | 1.5h |
| Backend | 3.5h |
| Frontend | 2h |
| Docs | 1.5h |
| **Total** | **~8.5h** |
