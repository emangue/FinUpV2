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

## 9. Histórico de adicionais

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
