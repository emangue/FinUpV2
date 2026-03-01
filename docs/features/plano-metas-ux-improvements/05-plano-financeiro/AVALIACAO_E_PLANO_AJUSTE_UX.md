# Avaliação e Plano de Ajuste — UX Plano (itens 9–13)

**Data:** 01/03/2026  
**Base:** ADDITIONAIS_UX.md (itens 9, 10, 11, 12, 13)

---

## 1. Avaliação por item

### Item 9 — Scroll fixo no topo (igual ao dashboard)

| Critério | Avaliação |
|----------|-----------|
| **Impacto UX** | Alto. Usuário perde contexto ao rolar; no dashboard o seletor de mês fica visível. |
| **Esforço** | Baixo (1–2h). Replicar estrutura do dashboard: `flex flex-col h-screen` + `sticky top-0` na área superior. |
| **Risco** | Baixo. Padrão já usado no dashboard. |
| **Dependências** | Nenhuma. |
| **Recomendação** | ✅ Fazer. Prioridade alta. |

**Detalhe técnico:** O Plano hoje usa `min-h-screen` e `space-y-4`; o conteúdo rola junto. O dashboard usa `flex flex-col h-screen`, `sticky top-0` no header+seletor, e `flex-1 overflow-y-auto` no conteúdo. Aplicar o mesmo padrão no Plano.

**Complexidade:** O Plano tem MonthScrollPicker no meio da página ("Orçamento em:"), não no topo. Duas opções:
- **A:** Mover seletor de mês para o topo (igual dashboard) e fixar header + seletor.
- **B:** Fixar só o header; o seletor "Orçamento em:" continua no fluxo (menos consistente com o dashboard).

**Decisão:** Opção A — mover seletor para o topo e fixar, alinhando ao dashboard.

---

### Item 10 — Restrição orçamentária: valor real + comparação com plano

| Critério | Avaliação |
|----------|-----------|
| **Impacto UX** | Alto. Hoje só mostra planejado; o usuário quer ver realizado vs plano (como no Resumo do Mês). |
| **Esforço** | Médio (3–4h). Precisa buscar dados realizados (income-sources, budget/planning) e exibir comparação. |
| **Risco** | Baixo. APIs já existem. |
| **Dependências** | Nenhuma. |
| **Recomendação** | ✅ Fazer. Prioridade alta. |

**Detalhe técnico:** O `PlanoResumoCard` usa `getResumoPlano` (renda, total_budget, disponivel_real). O dashboard Resumo usa `fetchIncomeSources` + `fetchGoals` e exibe:
- Receitas: valor real + "sem plano" ou comparação
- Despesas: valor real + "X acima/abaixo"
- Investidos: valor real + "Xx o plano" ou "% do aporte"

**Implementação:** 
1. No PlanoResumoCard, quando `month` tiver transações, chamar também `fetchIncomeSources` e `fetchGoals` (ou criar endpoint `GET /plano/resumo-com-realizado?ano=&mes=` que retorne tudo).
2. Exibir grid 3 colunas: Receitas | Despesas | Investidos, com valor real e comparação (igual OrcamentoTab).
3. Manter fallback: quando sem realizado, exibir Renda | Planejado | Disponível (comportamento atual).

---

### Item 11 — Perfil financeiro vs tela Plano

| Critério | Avaliação |
|----------|-----------|
| **Impacto UX** | Médio. Reduz confusão e duplicação de telas. |
| **Esforço** | Baixo a médio (2–3h). Redirecionar ou unificar. |
| **Risco** | Baixo. Perfil Financeiro é subconjunto do Plano. |
| **Dependências** | Nenhuma. |
| **Recomendação** | ✅ Fazer. Prioridade média. |

**Análise de redundância:**

| Conteúdo | Perfil Financeiro | Plano |
|----------|-------------------|-------|
| Editar renda | RendaDeclaracaoForm (inline) | CTA "Editar plano" → construir-plano |
| Restrição orçamentária | ✅ | ✅ |
| Orçamento por categoria | ✅ | ✅ |
| Gerenciar metas | Link | Link |
| Cashflow anual | ❌ | ✅ |
| Projeção de poupança | ❌ | ✅ |
| Anos perdidos | ❌ | ✅ |

**Conclusão:** O Plano é superset. O Perfil Financeiro só acrescenta o formulário de renda inline. O Plano já permite editar renda via "Editar plano" → construir-plano.

**Opções:**
- **A:** Redirecionar "Perfil Financeiro" → `/mobile/plano`. Remover item do menu Profile.
- **B:** Manter link, mas abrir Plano (com scroll até Restrição). Mensagem: "Seu perfil financeiro está no Plano."
- **C:** Unificar: mover RendaDeclaracaoForm para dentro do Plano (acima da Restrição), como edição rápida. Depois remover tela Perfil Financeiro.

**Decisão:** Opção A — redirecionar para Plano. Mais simples; o usuário acessa tudo em um lugar.

---

### Item 12 — Resumo anual no gráfico de projeção (base vs economia)

| Critério | Avaliação |
|----------|-----------|
| **Impacto UX** | Médio. Torna explícita a diferença entre cenário base e com economia. |
| **Esforço** | Médio (2–3h). Calcular e exibir dois totais (base e com redução). |
| **Risco** | Baixo. ProjecaoChart já tem `reducaoPct` e `getProjecao`. |
| **Dependências** | Nenhuma. |
| **Recomendação** | ✅ Fazer. Prioridade média. |

**Detalhe técnico:** O `ProjecaoChart` chama `getProjecao(ano, 12, reducaoPct)`. Para o resumo:
1. Buscar projeção com `reducaoPct=0` (base) e com `reducaoPct` atual (economia).
2. Pegar o último mês de cada série → patrimônio final.
3. Exibir: "Base (0%): -17,4k | Com X% economia: -8,2k" (ou tabela compacta).

**Alternativa:** Manter uma única chamada e, a partir da série atual, calcular o acumulado final. O backend já retorna a série; o último valor é o patrimônio final do ano. Basta exibir esse valor + um segundo valor quando `reducaoPct > 0` (já temos a série com redução).

---

### Item 13 — Três linhas no gráfico: Real | Plano | Plano com redução

| Critério | Avaliação |
|----------|-----------|
| **Impacto UX** | Alto. Permite ver "o que aconteceu" vs "o que foi planejado" ao longo do ano. |
| **Esforço** | Médio-alto (4–6h). Combinar cashflow realizado + projeção; três séries no gráfico. |
| **Risco** | Baixo. Dados já existem (cashflow, projeção). |
| **Dependências** | Nenhuma. |
| **Recomendação** | ✅ Fazer. Prioridade alta. |

**Conceito:** O gráfico passa a ter três linhas:
1. **Real** — Patrimônio acumulado com dados realizados (meses passados). Preenche à medida que o ano avança.
2. **Plano** — Projeção planejada (0% redução). Linha de referência.
3. **Plano com redução** — Projeção com slider (ex.: 10%). Cenário "e se eu reduzir gastos?".

**Implementação:**
1. `getCashflow` já retorna saldo por mês. Acumular saldos até o mês atual → série "Real".
2. `getProjecao(ano, 12, 0)` → série "Plano".
3. `getProjecao(ano, 12, reducaoPct)` → série "Plano com redução".
4. Mesclar no chartData: para cada mês, `{ real, plano, planoReducao }`. Meses futuros: real = null (não desenhar ou tracejado).
5. Legenda mínima (evitar poluição): só quando fizer sentido; cores distintas bastam para distinguir as linhas.

**Detalhe:** O "Real" precisa de patrimônio inicial + saldos mensais. O cashflow tem `saldo_projetado` por mês; para realizado, usar `renda_usada - total_gastos` (ou equivalente) e acumular. Verificar se `getProjecao` ou `getCashflow` já expõe acumulado realizado.

---

## 2. Plano de ajuste (ordem de execução)

### Fase A — Quick wins (≈ 4h)

| # | Task | Item | Est. | Descrição |
|---|------|------|------|-----------|
| A.1 | Scroll fixo no topo | 9 | 1,5h | Reestruturar página Plano: header + seletor de mês fixos; conteúdo rolável. Mover MonthScrollPicker para o topo. |
| A.2 | Redirecionar Perfil Financeiro → Plano | 11 | 1h | No profile, botão "Perfil Financeiro" redireciona para `/mobile/plano`. Opcional: remover item ou renomear para "Plano". |
| A.3 | Resumo anual no ProjecaoChart | 12 | 2h | Abaixo do gráfico, exibir "Base: Xk | Com Y% economia: Zk" (patrimônio final do ano). |

### Fase B — Restrição com realizado (≈ 4h)

| # | Task | Item | Est. | Descrição |
|---|------|------|------|-----------|
| B.1 | API ou chamadas para realizado | 10 | 1,5h | Usar `fetchIncomeSources` + `fetchGoals` no PlanoResumoCard quando mês tiver dados; ou criar `GET /plano/resumo-mes?ano=&mes=` que retorne realizado + planejado. |
| B.2 | Layout Restrição com realizado | 10 | 2h | Quando houver realizado: exibir Receitas | Despesas | Investidos (valor real + comparação), estilo Resumo do Mês. |
| B.3 | Fallback sem realizado | 10 | 0,5h | Quando sem transações no mês: manter Renda | Planejado | Disponível. |

### Fase C — Três linhas no gráfico: Real | Plano | Plano com redução (≈ 5h)

| # | Task | Item | Est. | Descrição |
|---|------|------|------|-----------|
| C.1 | Série acumulado realizado | 13 | 2h | A partir do cashflow, calcular patrimônio acumulado mês a mês (patrimônio atual + saldos realizados). Backend ou frontend. |
| C.2 | Três linhas no ProjecaoChart | 13 | 2h | Adicionar séries Real, Plano (0%), Plano com redução (slider). Legenda e cores distintas. |
| C.3 | Meses futuros: Real = null | 13 | 0,5h | Para meses sem transações, Real não desenha ou usa tracejado "a preencher". |
| C.4 | Resumo anual (item 12) | 12 | 0,5h | Incluir no mesmo card: "Base: Xk \| Real: Yk \| Com Z% economia: Wk". |

---

## 3. Cronograma sugerido

```
Fase A (Quick wins)     → 4h   ← começar aqui
    ↓
Fase B (Restrição)      → 4h
    ↓
Fase C (3 linhas)       → 5h
```

**Total estimado:** 13h

---

## 4. Checklist de validação

**Item 9 — Scroll fixo:**
- [ ] Header "Plano" fixo ao rolar
- [ ] Seletor de mês fixo (ou integrado ao header)
- [ ] Conteúdo (Editar plano, Restrição, Cashflow, Projeção, Orçamento) rola normalmente

**Item 10 — Restrição com realizado:**
- [ ] Mês com transações: exibe Receitas, Despesas, Investidos com valor real e comparação
- [ ] Mês sem transações: exibe Renda, Planejado, Disponível (atual)
- [ ] Valores batem com o Resumo do Mês do dashboard

**Item 11 — Perfil Financeiro:**
- [ ] "Perfil Financeiro" no Profile leva a `/mobile/plano`
- [ ] Ou: item removido/renomeado; Plano é o único hub financeiro

**Item 12 — Resumo anual projeção:**
- [ ] Abaixo do gráfico: "Base (0%): Xk"
- [ ] Quando slider > 0: "Com Y% economia: Zk"
- [ ] Valores corretos (último mês da série)

**Item 13 — Três linhas no gráfico:**
- [ ] Linha "Real" visível (meses passados com dados)
- [ ] Linha "Plano" (0% redução)
- [ ] Linha "Plano com redução" (slider)
- [ ] Legenda clara e cores distintas
- [ ] Meses futuros: Real não desenha ou tracejado

---

## 5. Referências

| Arquivo | Uso |
|---------|-----|
| `app/mobile/plano/page.tsx` | Estrutura da página; scroll |
| `app/mobile/dashboard/page.tsx` | Modelo de layout fixo (sticky) |
| `features/plano/components/PlanoResumoCard.tsx` | Restrição orçamentária |
| `features/dashboard/components/orcamento-tab.tsx` | Resumo do Mês (valor real + comparação) |
| `features/plano/components/ProjecaoChart.tsx` | Gráfico + slider; resumo anual |
| `app/mobile/perfil/financeiro/page.tsx` | Tela a redirecionar |
| `app/mobile/profile/page.tsx` | Botão "Perfil Financeiro" |
