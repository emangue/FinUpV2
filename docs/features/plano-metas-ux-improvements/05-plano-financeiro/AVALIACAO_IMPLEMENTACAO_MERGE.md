# Avaliação de Implementação — Merge Plano + Aposentadoria

**Data:** 01/03/2026  
**Objetivo:** Avaliar viabilidade, riscos e ordem de execução dos ajustes descritos em `AVALIACAO_MERGE_PLANO_APOSENTADORIA.md`.

---

## 1. Resumo Executivo

| Aspecto | Avaliação |
|---------|-----------|
| **Viabilidade técnica** | ✅ Alta — mudanças bem delimitadas |
| **Risco de regressão** | ⚠️ Médio — cashflow e orçamento são hot paths |
| **Esforço total estimado** | ~40–50h (backend + frontend + migração) |
| **Recomendação** | Implementar em fases; Fases 1–7 primeiro (backend + schema) |

---

## 2. Avaliação por Fase

### Fase 1–3: Migrations (Schema)

| Task | Viabilidade | Riscos | Observação |
|------|-------------|--------|------------|
| `metadata_json` + `subgrupo` em base_expectativas | ✅ Simples | Baixo | Colunas nullable; sem breaking change |
| Criar tabela `expectativas_mes` | ✅ Simples | Baixo | Nova tabela; não afeta código existente |

**Decisão confirmada:** Seguir seção 5.1 — **não** adicionar `valor_extraordinario` em budget_planning. Total = `budget_planning.valor_planejado + SUM(expectativas_mes)`.

---

### Fase 4–5: Backend — expectativas_mes

| Task | Viabilidade | Riscos | Observação |
|------|-------------|--------|------------|
| `get_expectativas_por_mes` ler de expectativas_mes | ✅ Médio | Médio | Hoje lê base_expectativas e agrega por mês. Trocar para expectativas_mes é direto, mas precisa garantir que a tabela está populada. |
| Ao salvar expectativa, expandir e materializar | ✅ Médio | Médio | Lógica de expansão existe em `PersonalizarPlanoLayout` (expandExtras). Portar para Python. Recorrência bimestral/trimestral/semestral/anual + evolução. |

**Dependência:** Fases 1–2 (migrations) devem estar aplicadas antes.

---

### Fase 6–7: Backend — Função central e impacto em queries

| Task | Viabilidade | Riscos | Observação |
|------|-------------|--------|------------|
| `get_planejado_por_grupo_mes` centralizado | ✅ Médio | Alto | **Hot path.** get_cashflow, get_orcamento, get_resumo usam budget. Qualquer bug afeta dashboard, plano, orçamento. |
| Atualizar get_resumo, get_cashflow, get_orcamento | ✅ Médio | Alto | get_cashflow hoje: gastos_recorrentes = SUM(budget_planning), gastos_extras = get_expectativas_por_mes. Novo: gastos = budget + expectativas_mes. Testes manuais obrigatórios. |

**Pontos de atenção:**
- `get_cashflow` linha 322–324: já usa `get_expectativas_por_mes`. Trocar para expectativas_mes deve manter o mesmo contrato de retorno.
- `get_orcamento` (plano service): retorna gasto vs meta por grupo. Meta hoje vem de `plano_metas_categoria` ou `budget_planning`. Com expectativas_mes, meta = budget + expectativas do mês.

---

### Fase 8: Projeção longa (30 anos) no backend

| Task | Viabilidade | Riscos | Observação |
|------|-------------|--------|------------|
| Projeção 30 anos no plano service | ✅ Médio | Baixo | Hoje roda no frontend (PersonalizarPlanoLayout). Portar para backend: loop de meses, juros compostos, aporte + extras expandidos. Sem DB pesado. |

**Reutilização:** A lógica de `expandExtras` do PersonalizarPlanoLayout pode ser portada. Entrada: user_financial_profile + base_expectativas (com metadata). Saída: série de patrimônio por mês.

---

### Fase 9–12: Wizard (4 telas)

| Task | Viabilidade | Riscos | Observação |
|------|-------------|--------|------------|
| Tela 1: Renda + ganhos extras de renda | ✅ Alto | Baixo | PlanoWizard já tem step 1 com renda. Adicionar seção "Ganhos extraordinários" (reutilizar UI de PersonalizarPlanoLayout). |
| Tela 2: Gastos por grupo + média 3 meses | ✅ Alto | Baixo | budget_planning já tem `valor_medio_3_meses`. Endpoint ou extensão para retornar por grupo. UI: lista editável. |
| Tela 3: Gastos extraordinários | ✅ Alto | Médio | Nova UI. Grupo + subgrupo obrigatórios. Recorrência mínima bimestral. Salvar → base_expectativas + materializar expectativas_mes. |
| Tela 4: Parâmetros aposentadoria + slider | ✅ Alto | Baixo | user_financial_profile já tem os campos. Slider de sensibilidade: variar aporte e recalcular projeção. |

**Dependência:** Backend (Fases 4–7) deve estar estável antes de conectar o wizard.

---

### Fase 13–15: Migração e depreciação

| Task | Viabilidade | Riscos | Observação |
|------|-------------|--------|------------|
| Migrar extras_json → base_expectativas | ⚠️ Médio | Médio | Script one-shot. Precisa mapear formato extras_json para base_expectativas + metadata_json. Validar com usuários que têm cenários. |
| Depreciar investimentos_cenarios | ⚠️ Baixo | Baixo | Não dropar tabela de imediato; marcar como deprecated. CTAs que levam a /personalizar-plano devem ir para /construir-plano. |
| Job rolagem 12 meses | ✅ Baixo | Baixo | Cron ou Celery: todo dia, garantir expectativas_mes tem próximos 12 meses. Se faltar, recalcular a partir de base_expectativas. |

---

## 3. Pontos de Atenção no Código Atual

### 3.1 Onde o plano de aposentadoria é referenciado

| Arquivo | Uso | Ação |
|---------|-----|------|
| `app/mobile/dashboard/page.tsx` | PlanoAposentadoriaTab | Trocar CTA para /construir-plano |
| `app/mobile/personalizar-plano/page.tsx` | Rota da tela | Redirecionar para /construir-plano ou remover |
| `features/plano-aposentadoria/*` | Componentes, API | Manter para migração gradual; depois remover ou absorver |
| `features/dashboard/orcamento-tab.tsx` | Link personalizar-plano | Trocar para construir-plano |
| `features/investimentos/*` | createCenario, getCenario, etc. | Manter até migração completa; plano não usará mais |

### 3.2 Inconsistência no documento

**Seção 5.1** diz: extraordinários vivem só em `expectativas_mes`; `budget_planning` não é alterado.

**Seção 7.3 e 8** mencionam `valor_extraordinario` em `budget_planning`.

**Recomendação:** Seguir 5.1. Não adicionar `valor_extraordinario` em budget_planning. Total planejado = `budget_planning.valor_planejado` + `SUM(expectativas_mes.valor)` por grupo/mês.

---

## 4. Ordem de Implementação Sugerida

```
1. Migrations (1–3) — schema pronto
2. Backend: expandir expectativa → expectativas_mes (5)
3. Backend: get_expectativas_por_mes ler expectativas_mes (4)
4. Backend: get_planejado_por_grupo_mes centralizado (6)
5. Backend: atualizar get_cashflow, get_resumo, get_orcamento (7)
6. Testes manuais: cashflow, orçamento, projeção 12m
7. Backend: projeção longa 30 anos (8)
8. Wizard: Telas 1–4 (9–12)
9. CTAs: personalizar-plano → construir-plano
10. Migração extras_json (13)
11. Job rolagem (15)
12. Depreciar investimentos_cenarios (14)
```

---

## 5. Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Regressão no cashflow | Testes manuais em cada mês; comparar antes/depois da mudança |
| expectativas_mes vazia no início | Ao criar expectativa, materializar imediatamente; job de rolagem como safety net |
| Usuários com cenários em investimentos_cenarios | Migração opcional; avisar que plano unificado é a nova experiência |
| Performance de get_cashflow | expectativas_mes é indexada por user_id + mes_referencia; 2 queries (budget + expectativas) em vez de N |

---

## 6. Conclusão

O plano é **viável e bem estruturado**. A separação entre `budget_planning` (base) e `expectativas_mes` (extraordinários) é sólida e evita corrupção ao deletar. A materialização dos próximos 12 meses resolve o gargalo de performance.

**Próximo passo:** Corrigir a inconsistência sobre `valor_extraordinario` no documento e iniciar Fase 1 (migrations).
