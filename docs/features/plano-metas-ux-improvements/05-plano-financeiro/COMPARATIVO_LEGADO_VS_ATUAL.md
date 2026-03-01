# Comparativo: Legado vs Implementação Atual

**Data:** 28/02/2026  
**Objetivo:** Avaliar se o que construímos está alinhado ao que foi planejado no `_legado/`.

---

## 1. O que o legado queria (visão central)

### Problema que o legado identificou

> "Hoje o usuário tem dois mundos separados: Plano de Aposentadoria e Metas de Gastos. Metas de Gastos define quanto quer gastar por grupo — **mas sem âncora de renda**, sem evolução, sem conexão com o quanto sobra para investir. A pessoa pode criar um plano de gastos de R$ 20.000/mês ganhando R$ 15.000, e o app nunca avisa que a conta não fecha."  
> — UX_PLANO_FINANCEIRO_INTEGRADO.md

### Proposta do legado

> "Uma tela de construção de plano que **começa pela renda** e distribui o dinheiro de cima para baixo — gastos → sobra → aporte."

---

## 2. O que implementamos (Sprint 6 + ajustes)

| Item | Status | Observação |
|------|--------|------------|
| Renda declarada | ✅ | `user_financial_profile`, POST/GET `/plano/renda` |
| Metas por grupo | ✅ | Via `budget_planning` (link "Gerenciar metas por grupo") |
| **Conexão renda ↔ metas** | ✅ | `disponivel_real` = renda − total budget |
| Orçamento por categoria | ✅ | GET `/plano/orcamento` — gasto vs meta por grupo |
| Grupos com meta (sem gasto) | ✅ | Orçamento mostra metas mesmo sem transações |
| Card "Restrição orçamentária" | ✅ | Renda \| Planejado \| Disponível no Perfil Financeiro |
| BudgetWidget no dashboard | ✅ | Renda \| Gasto \| Disponível (ou Poupança %) |

**Conclusão:** A **âncora de renda** e a **conexão restrição orçamentária ↔ metas** estão implementadas. O usuário vê:
- Quanto ganha (renda)
- Quanto planejou gastar (total das metas)
- Quanto sobra (disponível = renda − planejado)

---

## 3. O que o legado planejou e ainda não existe

### 3.1 Tela principal do Plano (`/mobile/plano`)

O legado previa uma tela **Acompanhamento do Plano** como hub central:

```
Renda        R$ 15.000
Gastos     − R$ 12.800  (R$ 14.500 prev.) ⚠️
Aporte     − R$  1.800  (R$  2.500 prev.) ⚠️
Saldo          R$    400                    ✅

POR GRUPO
Alimentação  ██████████  R$2.700 / R$2.500  108% ⚠️
Casa         ████████░░  R$2.800 / R$3.000   93% ✅
...
```

**Hoje:** O conteúdo equivalente está em:
- Dashboard → BudgetWidget (resumo)
- Perfil Financeiro → OrcamentoCategorias (por grupo)
- Não existe uma tela dedicada `/mobile/plano` como hub.

### 3.2 Camada de expectativas (`base_expectativas`)

O legado definiu 3 camadas:

| Camada | Conteúdo | Status |
|--------|----------|--------|
| 1 — Realizado | journal_entries, base_parcelas | ✅ Existe |
| 2 — Expectativas | base_expectativas (sazonais, parcelas futuras, 13º) | ❌ Não existe |
| 3 — Plano base | budget_planning | ✅ Existe |

**Falta:** Tabela `base_expectativas` e toda a lógica de:
- Gastos sazonais (IPVA, IPTU, matrícula)
- Parcelas futuras (derivadas de base_parcelas)
- Rendas extraordinárias (13º, bônus)
- Budget at risk (total_esperado = plano + expectativas)

### 3.3 Construtor de Plano (wizard 4 etapas)

O legado previa um wizard completo em `/mobile/construir-plano`:

1. **Etapa 1:** Renda + ganhos extraordinários
2. **Etapa 2:** Gastos base (proposta dos últimos 3 meses)
3. **Etapa 3:** Gastos sazonais por mês
4. **Etapa 4:** Aporte + recibo anual (tabela mês a mês)

**Hoje:** Renda e metas são configuradas de forma fragmentada (Perfil Financeiro + Gerenciar metas). Não há wizard unificado.

### 3.4 Cashflow engine (`GET /budget/cashflow?ano=`)

O legado previa um endpoint que unifica:

- `realizado` (journal_entries)
- `expectativas` (base_expectativas)
- `plano` (budget_planning)
- `saldo` por mês
- `budget_at_risk` por grupo
- `nudge` (anos perdidos, custo em 30 anos)

**Hoje:** Não existe. Temos apenas GET `/plano/orcamento` (gasto vs meta por grupo) e GET `/plano/resumo` (renda, total_budget, disponivel_real).

### 3.5 Nudge "Anos perdidos"

> "Com esse nível de gasto você está perdendo N anos de aposentadoria"

**Hoje:** Não implementado. O PLANO.md do 05-plano prevê F.08 (AnosPerdidasCard) no Sprint 7.

### 3.6 Tabela de recibo anual

Mês \| Receita \| Despesa \| Aporte \| Saldo — com restrição ao salvar (bloquear aporte > saldo).

**Hoje:** Não existe.

### 3.7 Integração Plano ↔ Aposentadoria

O aporte definido no plano deveria alimentar a projeção de aposentadoria.

**Hoje:** Não integrado.

---

## 4. Resumo executivo

| Aspecto | Legado | Atual | Alinhado? |
|---------|--------|-------|-----------|
| **Âncora de renda** | Plano começa pela renda | Renda declarada em Perfil Financeiro | ✅ Sim |
| **Conexão restrição ↔ metas** | Saldo = Renda − Gastos planejados | disponivel_real = renda − total budget | ✅ Sim |
| **Metas por grupo** | budget_planning | budget_planning (via link Gerenciar metas) | ✅ Sim |
| **Orçamento por categoria** | Gastos vs plano por grupo | GET /plano/orcamento com barras | ✅ Sim |
| **Tela /mobile/plano** | Hub central de acompanhamento | Não existe como hub | ⚠️ Parcial |
| **base_expectativas** | Sazonais, parcelas, 13º | Não existe | ❌ Não |
| **Wizard 4 etapas** | Construtor unificado | Fragmentado (renda + metas separados) | ⚠️ Parcial |
| **Cashflow engine** | GET /budget/cashflow | Não existe | ❌ Não |
| **Nudge anos perdidos** | Alerta quando gasto > renda | Não existe | ❌ Não |
| **Tabela recibo anual** | 12 meses, restrição ao salvar | Não existe | ❌ Não |

---

## 5. Conclusão

**O que queríamos "lá atrás" (núcleo):**
- Plano com consciência de renda ✅
- Conexão entre restrição orçamentária e metas ✅
- Saldo disponível = renda − gastos planejados ✅

**O que construímos:** Uma versão **enxuta** que atende esse núcleo. Renda, metas e "disponível" estão conectados. O usuário vê a conta fechando (ou não) no Perfil Financeiro e no BudgetWidget.

**O que falta para o legado completo:**
- Tela `/mobile/plano` como hub
- `base_expectativas` (sazonais, parcelas)
- Cashflow engine
- Wizard 4 etapas
- Nudge anos perdidos
- Tabela de recibo anual
- Integração com aposentadoria

**Recomendação:** O que está feito está alinhado à intenção central do legado. Os itens faltantes são evoluções (Sprint 7 do 05-plano e além). Podemos priorizá-los conforme o roadmap.

---

## 6. Plano de ajuste

Para um plano de execução detalhado (tasks, estimativas, ordem), ver **`PLANO_DE_AJUSTE.md`**.
