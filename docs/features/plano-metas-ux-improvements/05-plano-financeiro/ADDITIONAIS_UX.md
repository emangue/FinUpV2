# Adicionais UX — Plano Financeiro

**Data:** 28/02/2026  
**Objetivo:** Documentar melhorias incrementais de UX solicitadas durante o uso do Plano.

---

## 1. Números compactos na tabela

**Problema:** Valores como "R$ 25.000" e "R$ 53.800" ocupam muito espaço; a tabela não cabe na tela.

**Solução:** Formato compacto `fmtCompact`:
- `>= 1M` → `R$ 1,2M`
- `>= 1k` → `R$ 25k`, `R$ 53,8k`
- `< 1k` → `R$ 500` (completo)

**Onde:** `TabelaReciboAnual.tsx` — colunas Renda, Gastos, Aporte, Saldo e rodapé Resumo.

**Status:** ✅ Implementado

---

## 2. Legenda no gráfico de projeção

**Problema:** Gráfico "Projeção de poupança" sem legenda clara (estilo Evolução Patrimonial).

**Solução:**
- Legenda textual acima do gráfico: "Patrimônio acumulado (R$ mil)"
- Valores sobre cada ponto do gráfico (ex: 640k, 760k) via `LabelList` do Recharts

**Onde:** `ProjecaoChart.tsx`

**Status:** ✅ Implementado

---

## 3. Adicionar gastos extraordinários no modal de detalhe

**Problema:** Usuário lembra de gastos no meio do caminho (IPVA, presente, conserto) e não tem onde registrar para aquele mês.

**Solução:** No modal "Cálculo exato — Mês/Ano":
- Botão "Adicionar gasto extraordinário"
- Form: descrição + valor
- Chama `POST /plano/expectativas` com `tipo_lancamento=debito`, `tipo_expectativa=sazonal_plano`
- Após salvar, refaz `GET /plano/cashflow` para atualizar a tabela

**Onde:** `TabelaReciboAnual.tsx` (modal de detalhe) + `api.ts` (`postExpectativa`)

**Status:** ✅ Implementado

---

## 4. Números sempre em milhares (k) + "ok" perto de zero

**Problema:** Eixo Y e rótulos dos pontos mostravam números longos (-27674, -21290) ou misturavam formato.

**Solução:** Função `fmtK`:
- `|valor| < 100` → exibe **"ok"** (próximo de zero)
- Demais → sempre em milhares: `27,7k`, `-21,3k`, `5k`

**Onde:** `ProjecaoChart.tsx` — YAxis `tickFormatter` e `LabelList` formatter.

**Status:** ✅ Implementado

---

## 5. Fonte menor na tabela Cashflow (igual tabela patrimônio)

**Problema:** Letra ainda muito grande na tabela Cashflow anual.

**Solução:** Usar `text-xs` e `py-1 px-2` (igual à tabela "Primeiros meses do plano" em plano-chart).

**Onde:** `TabelaReciboAnual.tsx`

**Status:** ✅ Implementado

---

## 6. Remover R$ da tabela Cashflow

**Problema:** Prefixo "R$" em cada célula ocupa espaço; o contexto já indica valores em reais.

**Solução:** `fmtCompact` sem "R$" — exibe "25,0k", "-1,3k", "0".

**Onde:** `TabelaReciboAnual.tsx`

**Status:** ✅ Implementado

---

## 7. Renda com realizado (>= 90% do esperado)

**Problema:** Renda só vinha do esperado (perfil). Precisamos considerar o realizado quando disponível.

**Regra:** Se `renda_realizada >= 0.9 * renda_esperada`, use renda_realizada; senão use renda_esperada.  
`renda_usada = max(0.9 * esperado, realizado)` quando há realizado; caso contrário, esperado.

**Fonte realizado:** `SUM(Valor)` WHERE `CategoriaGeral = 'Receita'` AND `MesFatura = YYYYMM` AND `IgnorarDashboard = 0`.

**Onde:** `plano/service.py` (get_cashflow, get_projecao), `api.ts`, `TabelaReciboAnual.tsx`.

**Status:** ✅ Implementado

---

## 8. Alinhamento ao plano principal (receita, despesas, aporte = investimentos)

**Regra:** Quando receita >= 90% do esperado, trocar TUDO para realizado:
- **Renda** = receita realizada (max 0.9×esperado)
- **Despesas** = despesas realizadas
- **Aporte** = investimentos realizados (CategoriaGeral = 'Investimentos')
- **Saldo** = renda - despesas - aporte

Quando não: usar plano (esperado, gastos_recorrentes, aporte_planejado).

**Onde:** `plano/service.py` (get_cashflow, get_projecao), frontend.

**Status:** ✅ Implementado

---

## 9. Scroll fixo no topo (igual ao dashboard)

**Problema:** Na tela Plano, o conteúdo inteiro rola junto. No dashboard, o seletor de mês/ano fica fixo no topo (`sticky top-0`).

**Solução:** Fixar header + seletor de mês no topo da tela Plano, como no dashboard. O conteúdo abaixo (Editar plano, Restrição orçamentária, Cashflow, Projeção, Orçamento por categoria) rola; o topo permanece visível.

**Onde:** `app/mobile/plano/page.tsx` — usar `sticky top-0` na área superior (header + MonthScrollPicker se aplicável).

**Status:** ✅ Implementado

---

## 10. Restrição orçamentária: valor real + comparação com plano (igual ao dash)

**Problema:** A caixa "Restrição orçamentária (metas)" mostra só Renda, Planejado e Disponível (valores planejados). O dashboard "Resumo do Mês" mostra valor real e comparação com o plano (ex.: "R$ 9.216 acima", "10,9x o plano").

**Solução:** Quando houver dados realizados no mês, exibir na Restrição orçamentária:
- Valor real (receitas, despesas, investidos realizados)
- Comparação com o plano (ex.: "X acima/abaixo", "% do plano")

**Onde:** `PlanoResumoCard.tsx` ou componente equivalente da Restrição orçamentária.

**Status:** ✅ Implementado

---

## 11. Perfil financeiro vs tela Plano

**Problema:** Existe tela "Perfil financeiro" (ou similar) e tela "Plano". O Plano já permite editar renda, metas, sazonais e aporte via "Editar plano" → construir-plano.

**Solução:** Avaliar se a tela Perfil financeiro é redundante. Se o Plano já resolve (editar plano, restrição, cashflow, projeção), considerar unificar ou remover a tela Perfil.

**Status:** ✅ Implementado (redireciona para /mobile/plano)

---

## 12. Resumo anual no gráfico de projeção (base vs economia)

**Problema:** O gráfico "Projeção de poupança" tem slider "Reduzir gastos em:" (0% a X%) e mostra uma linha de patrimônio acumulado. Não há resumo anual comparando visão base (0%) vs visão com economia (ex.: 10%).

**Solução:** Adicionar abaixo do gráfico um resumo anual:
- **Base (0%):** patrimônio final do ano, saldo acumulado
- **Com economia (X%):** patrimônio final se reduzir gastos em X%

Ex.: tabela ou texto: "Base: -17,4k | Com 10% economia: -8,2k"

**Onde:** `ProjecaoChart.tsx`

**Status:** ✅ Implementado

---

## 13. Três linhas no gráfico: Real | Plano | Plano com redução

**Problema:** O gráfico de projeção mostra só uma linha (plano com ou sem redução). Não preenche com o realizado ao longo do ano nem permite comparar "o que aconteceu" vs "o que foi planejado".

**Solução:** Três linhas no mesmo gráfico:
1. **Real** — Patrimônio acumulado realizado (meses passados com transações). Preenche com dados reais à medida que o ano avança.
2. **Plano** — Projeção planejada (0% redução). Linha de referência do que foi planejado.
3. **Plano com redução** — Projeção se reduzir gastos em X% (slider). Cenário de economia.

**Comportamento:**
- Meses passados: Real usa saldo acumulado do cashflow realizado; Plano e Plano com redução usam projeção até o mês atual e depois projetam.
- Meses futuros: Real não existe (ou linha tracejada "a preencher"); Plano e Plano com redução projetam.
- Legenda: "— Real" | "— Plano" | "— Plano com redução (X%)"

**Onde:** `ProjecaoChart.tsx` — combinar dados de `getCashflow` (realizado) com `getProjecao` (plano base e com redução).

**Status:** ✅ Implementado (legenda mínima — sem labels em todas as curvas)

---

## 14. Histórico de adicionais

| Data | Item | Status |
|------|------|--------|
| 28/02/2026 | Números compactos | ✅ |
| 28/02/2026 | Legenda gráfico projeção | ✅ |
| 28/02/2026 | Gastos extraordinários no detalhe | ✅ |
| 28/02/2026 | Números em k + "ok" perto de zero | ✅ |
| 28/02/2026 | Fonte menor tabela Cashflow (igual patrimônio) | ✅ |
| 28/02/2026 | Remover R$ da tabela Cashflow | ✅ |
| 28/02/2026 | Renda com realizado (>= 90% esperado) | ✅ |
| 28/02/2026 | Alinhamento: receita, despesas, aporte=investimentos | ✅ |
| 01/03/2026 | Scroll fixo no topo (igual dashboard) | ✅ |
| 01/03/2026 | Restrição orçamentária: valor real + comparação com plano | ✅ |
| 01/03/2026 | Perfil financeiro → Plano (redireciona) | ✅ |
| 01/03/2026 | Resumo anual no gráfico de projeção (base vs economia) | ✅ |
| 01/03/2026 | Três linhas no gráfico: Real \| Plano \| Plano com redução (legenda mínima) | ✅ |
