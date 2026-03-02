# PRD — Plano Financeiro
> Sub-projeto 05 | Sprints 6, 7 | ~28h  
> Dependência: Sub-projeto 03 (perfil financeiro do usuário criado no onboarding)

---

## 1. Problema

O usuário sabe quanto gastou, mas não sabe quanto **deveria gastar**. Sem orçamento, sem meta de poupança e sem projeção, o app é apenas um histórico — não uma ferramenta de mudança de comportamento. Além disso, não há qualquer conexão entre o padrão de gastos atual e o impacto no longo prazo (aposentadoria, liberdade financeira).

---

## 2. Objetivo

Transformar o app em uma ferramenta de planejamento financeiro real: o usuário declara sua renda, define metas por categoria, acompanha o desvio em tempo real, e vê o impacto direto de seus gastos nos anos de trabalho necessários até a independência financeira.

---

## 3. Escopo (IN)

| ID | Feature | Sprint |
|----|---------|--------|
| S5 | Declaração de renda mensal líquida | 6 |
| S6 | Metas por grupo (via budget_planning — volta ao legado) | 6 |
| S7 | Nudge de desvio por categoria (real vs. planejado) | 6 |
| S8 | Seletor de mês de referência + preview de projeção 12 meses | 7 |
| S9 | Tabela detalhada por categoria com % do orçamento | 7 |
| S10 | Cálculo "anos perdidos" — impacto dos gastos na aposentadoria | 7 |

---

## 4. Escopo (OUT)

- Planejamento por objetivos específicos (viagem, casa, carro) — future
- Integração Open Banking para detectar renda automaticamente
- Conta conjunta / planejamento familiar
- Importação de investimentos externos (não vinculados ao extrato)

---

## 5. Dependências de Outros Sub-projetos

| Dep | Motivo |
|-----|--------|
| **03-onboarding-grupos** (HARD) | `user_financial_profile` é criado durante onboarding; renda é salva neste modelo |
| **04-upload-completo** (soft) | Quanto mais dados de transações, mais precisa é a projeção |

---

## 6. User Stories

### S5 — Declaração de renda mensal líquida

**Como** usuário,  
**Quero** declarar minha renda mensal líquida,  
**Para que** o app possa calcular minha taxa de poupança real e orçamento por categoria.

**Acceptance Criteria:**
- [ ] Campo de renda acessível em "Perfil" e no wizard de onboarding (S24)
- [ ] Renda salva em `user_financial_profile.renda_mensal_liquida`
- [ ] Dashboard exibe: Renda declarada | Gasto total | Poupado este mês (R$ e %)
- [ ] Se renda não declarada: nudge "Declare sua renda para ver sua taxa de poupança"
- [ ] Renda pode ser atualizada a qualquer momento

### S6 — Metas por grupo (budget_planning)

**Como** usuário,  
**Quero** definir metas de gasto por grupo (Casa, Alimentação, etc.),  
**Para que** o app compare gasto real vs. planejado e mostre desvios.

**Acceptance Criteria:**
- [ ] Perfil > Financeiro → link "Gerenciar metas por grupo" → `/mobile/budget/manage`
- [ ] Metas salvas em `budget_planning` (modelo legado)
- [ ] Dashboard mostra: Renda | Gasto | Poupança %
- [ ] Orçamento por categoria com barras de progresso (gasto vs. meta)

### S7 — Nudge de desvio por categoria

**Como** usuário,  
**Quero** ver em tempo real quando estou gastando mais que o planejado em uma categoria,  
**Para que** eu possa ajustar o comportamento antes do fechamento do mês.

**Acceptance Criteria:**
- [ ] Na tela de categorias: barra de progresso por grupo (gasto atual / meta)
- [ ] Cores: verde (< 80%), amarelo (80-100%), vermelho (> 100%)
- [ ] Banner no topo do dashboard se qualquer grupo > 100%: "⚠️ Alimentação: R$ 450 de R$ 400 (112%)"
- [ ] Meta por grupo definida em "Plano" (interface de orçamento)
- [ ] Se meta não definida: mostrar apenas gasto absoluto (sem barra)

### S8 — Seletor de mês de referência + projeção 12 meses

**Como** usuário,  
**Quero** escolher um mês de referência para meu orçamento e ver a projeção dos próximos 12 meses,  
**Para que** eu possa planejar com antecedência e ver o impacto das mudanças de comportamento.

**Acceptance Criteria:**
- [ ] Seletor de mês de início do plano (padrão: mês atual)
- [ ] Gráfico de barras ou linha: 12 meses à frente, projetando renda e gastos com base na média histórica
- [ ] Projeção ajustável: slider "Se eu reduzir gastos em X%" → nova linha no gráfico
- [ ] Acumulado projetado de poupança ao final de 12 meses

### S9 — Tabela detalhada por categoria

**Como** usuário,  
**Quero** ver um breakdown detalhado dos meus gastos por categoria com percentual do orçamento,  
**Para que** eu identifique quais categorias estão pesando mais no meu orçamento.

**Acceptance Criteria:**
- [ ] Tabela: Categoria | Gasto do mês | Meta | % utilizado | Tendência (↑↓→)
- [ ] Ordenável por gasto absoluto, % utilizado, categoria
- [ ] Drill-down por categoria: lista das transações individuais daquele mês
- [ ] Exportável como CSV (nice-to-have)
- [ ] Comparativo mês a mês: "este mês vs. mês anterior" por categoria

### S10 — "Anos perdidos" — impacto na aposentadoria

**Como** usuário consciente de longo prazo,  
**Quero** ver quantos anos de trabalho os meus gastos acima do planejado representam,  
**Para que** o impacto do comportamento atual seja tangível e motivador.

**Acceptance Criteria:**
- [ ] Card "Impacto no longo prazo" na tela de Plano
- [ ] Input: idade atual, idade alvo para aposentadoria, patrimônio atual, taxa de retorno esperada (padrão: 8% a.a.)
- [ ] Cálculo: déficit mensal (gasto - planejado) × 12 × fator de juros compostos = custo de oportunidade
- [ ] Exibir: "Seus gastos acima do planejado este mês representam X dias/meses/anos de trabalho a mais"
- [ ] Linguagem motivacional, não punitiva: "Cada R$ 100 economizados hoje = 3 dias a menos de trabalho"

---

## 7. UX / Wireframes

### Dashboard com Plano

```
┌─────────────────────────────────────────────────────┐
│ 📊 Dezembro 2025                             [Plano] │
├─────────────────────────────────────────────────────┤
│  Renda: R$ 8.000    Gasto: R$ 5.200   💚 Poupando 35% │
│  Comprometido: R$ 1.200   Disponível: R$ 6.800       │
├─────────────────────────────────────────────────────┤
│ ⚠️ Alimentação ultrapassou a meta (R$450 / R$400)    │
└─────────────────────────────────────────────────────┘
```

### Tela de Plano — Orçamento por categoria

```
┌────────────────────────────────────────────────┐
│ Categoria      Gasto    Meta    Uso             │
├────────────────────────────────────────────────┤
│ 🍔 Alimentação  R$450   R$400   ████████░░ 112% 🔴 │
│ 🚗 Transporte   R$280   R$350   ████████░░  80% 🟡 │
│ 🏠 Moradia      R$1200  R$1200  ██████████ 100% 🟡 │
│ 🎭 Lazer        R$180   R$300   ██████░░░░  60% 🟢 │
└────────────────────────────────────────────────┘
```

### Card "Anos Perdidos"

```
┌─────────────────────────────────────────────┐
│ ⏳ Impacto no longo prazo                    │
│                                             │
│  Gasto além do plano: R$ 230/mês            │
│                                             │
│  Isso equivale a:                           │
│  📅 28 dias a mais de trabalho por ano      │
│  🏦 R$ 38.400 a menos em 10 anos*           │
│                                             │
│  * Considerando 8% a.a. de retorno          │
│  [Ajustar parâmetros ▼]                     │
└─────────────────────────────────────────────┘
```

---

## 8. Riscos

| Risco | Probabilidade | Mitigação |
|-------|--------------|-----------|
| Usuário não declarar renda → cálculos sem sentido | Alto | Nudge proeminente + fallback "Por enquanto, mostrando apenas gastos" |
| Projeção de 12 meses com poucos dados históricos | Médio | Aviso "Baseado em X meses de dados — mais dados = projeção mais precisa" |
| Fórmula de "anos perdidos" parecer punitiva | Médio | UX com linguagem motivacional; parâmetros de aposentadoria configuráveis |
| Meta por categoria muito trabalhosa de definir | Alto | Default: 30% renda para alimentação, 20% moradia, etc. (ajustável) |

---

## 9. Métricas de Sucesso

| Métrica | Meta |
|---------|------|
| % de usuários que declaram renda | > 60% em 30 dias |
| % de usuários que definem metas em ≥ 3 categorias | > 40% |
| Engajamento com card "Anos perdidos" (cliques em "Ajustar") | > 25% dos usuários |
| NPS após 60 dias de uso do Plano | > 40 |
