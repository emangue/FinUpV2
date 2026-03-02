# Plano de Ajuste — Legado vs Atual

**Data:** 28/02/2026  
**Objetivo:** Trazer a implementação atual em linha com a visão do legado (`_legado/`).  
**Base:** `COMPARATIVO_LEGADO_VS_ATUAL.md`

---

## 1. Situação atual (resumo)

| O que temos | Status |
|-------------|--------|
| Renda declarada | ✅ |
| Metas por grupo (budget_planning) | ✅ |
| Conexão renda ↔ metas (disponivel_real) | ✅ |
| Orçamento por categoria (gasto vs meta) | ✅ |
| Card restrição orçamentária no Perfil | ✅ |
| BudgetWidget no dashboard | ✅ |

| O que falta | Prioridade |
|-------------|------------|
| Tela `/mobile/plano` como hub | Alta |
| Nudge "Anos perdidos" | Alta |
| Tabela de recibo anual (12 meses) | Média |
| Projeção 12 meses + slider | Média |
| Integração Plano ↔ Aposentadoria | Média |
| base_expectativas (sazonais, parcelas) | Baixa (fase 2) |
| Wizard 4 etapas (construtor unificado) | Baixa (fase 2) |
| Cashflow engine completo | Baixa (fase 2) |

---

## 2. Regra de edição (frame do wizard)

**Decisão:** Qualquer edição do plano (renda, metas, sazonais, aporte) deve usar o **mesmo frame** — o wizard em `/mobile/construir-plano`. Não criar fluxos paralelos (ex.: editar renda em tela separada).

**Preparação do solo:** Nas fases 1–3, já estabelecer:
- Rota `/mobile/construir-plano` (shell/placeholder)
- CTA "Editar plano" em `/mobile/plano` → vai para o wizard
- Contrato: as 4 etapas do wizard são o único ponto de edição

Enquanto o wizard não estiver completo, o "Editar plano" pode:
- **Opção A:** Abrir o wizard com as etapas já implementadas (renda, metas) e placeholder nas demais
- **Opção B:** Redirecionar temporariamente para os fluxos atuais (Perfil Financeiro, Gerenciar metas), com aviso de que em breve será unificado

**Objetivo:** Ao implementar o wizard (Fase 5), não precisar refatorar rotas nem CTAs — só preencher o frame.

---

## 3. Fases do plano de ajuste

### Fase 0 — Preparação do solo (≈ 2h)

**Objetivo:** Estabelecer o frame do wizard para que qualquer edição futura use esse fluxo.

| # | Task | Descrição | Est. | Dep. |
|---|------|-----------|------|------|
| 0.1 | Criar rota `/mobile/construir-plano` | Shell da página (layout, steps indicator vazio ou com placeholders) | 0.5h | — |
| 0.2 | Estrutura de etapas | Componente `PlanoWizard` com steps [1.Renda, 2.Gastos, 3.Sazonais, 4.Aporte] — navegação entre steps, conteúdo placeholder | 1h | 0.1 |
| 0.3 | Contrato de props/state | Definir `PlanoWizardState` (renda, gastosPorGrupo, sazonais, aporte) — estado compartilhado entre etapas | 0.5h | 0.2 |

**Entregável:** Rota existe, estrutura de steps pronta. Conteúdo real de cada etapa será preenchido nas fases seguintes (ou na Fase 5).

**Regra:** A partir daqui, qualquer nova tela de edição do plano é uma **etapa** do wizard, não uma rota separada.

---

### Fase 1 — Consolidação do hub (≈ 8h)

**Objetivo:** Ter uma tela central `/mobile/plano` que reúna o que já existe e adicione o nudge de anos perdidos.

| # | Task | Descrição | Est. | Dep. |
|---|------|-----------|------|------|
| 1.1 | Criar rota `/mobile/plano` | Página que agrega resumo + orçamento por grupo | 1h | — |
| 1.2 | Componente `PlanoResumoCard` | Reutiliza lógica de resumo: Renda \| Gastos \| Disponível \| Saldo | 1.5h | 1.1 |
| 1.3 | Integrar `OrcamentoCategorias` | Mesmo componente do Perfil Financeiro, com seletor de mês | 0.5h | 1.1 |
| 1.4 | Backend: `GET /plano/impacto-longo-prazo` | Cálculo: anos perdidos quando gasto > renda (juros compostos) | 2h | — |
| 1.5 | Componente `AnosPerdidasCard` | Exibe quando há déficit: "Com esse nível de gasto você está perdendo N anos de aposentadoria" | 1.5h | 1.4 |
| 1.6 | Link Plano na BottomNav | Garantir que tab "Plano" aponte para `/mobile/plano` | 0.5h | 1.1 |
| 1.7 | CTA "Editar plano" | Botão no hub que leva a `/mobile/construir-plano` (usa o frame da Fase 0) | 0.5h | 0.2, 1.1 |
| 1.8 | Redirecionar Perfil → Plano | Ou: Perfil Financeiro passa a ser subseção do Plano (decisão de UX) | 1h | 1.1 |

**Entregável:** Usuário acessa Plano e vê resumo + orçamento por grupo + alerta de anos perdidos + botão "Editar plano" que abre o wizard (frame).

---

### Fase 2 — Cashflow e recibo anual (≈ 10h)

**Objetivo:** Alinhado ao legado (TECH_SPEC, UX). Cashflow engine + tabela recibo. Projeção opcional.

**Referência:** `COMPARATIVO_FASE2_LEGADO.md`

| # | Task | Descrição | Est. | Dep. |
|---|------|-----------|------|------|
| 2.1 | Backend: `GET /plano/cashflow?ano=` | 12 meses: renda_esperada, gastos_recorrentes, gastos_realizados, aporte_planejado, saldo_projetado, status_mes (sem base_expectativas) | 2.5h | — |
| 2.2 | Componente `TabelaReciboAnual` | Mês \| Renda \| Gastos \| Aporte \| Saldo + status (✅⚠️❌) + resumo do ano | 2.5h | 2.1 |
| 2.3 | Integrar na tela `/mobile/plano` | CTA "Ver cashflow anual" → expande tabela | 0.5h | 2.2 |
| 2.4 | Backend: `PUT /plano/perfil` | Atualizar idade, aposentadoria, patrimônio, taxa retorno | 1h | — |
| 2.5 | Backend: `GET /plano/projecao?meses=12&reducao_pct=0` | Média histórica + projeção com slider (05-plano) | 2h | — |
| 2.6 | Componente `ProjecaoChart` | Gráfico + slider "Reduzir gastos em X%" (opcional) | 2.5h | 2.5 |

**Entregável:** Tabela recibo anual na tela Plano (core legado). ProjecaoChart como evolução.

---

### Fase 3 — Integração com aposentadoria (≈ 4h)

**Objetivo:** O aporte do plano alimenta a projeção de aposentadoria.

| # | Task | Descrição | Est. | Dep. |
|---|------|-----------|------|------|
| 3.1 | Endpoint ou campo de aporte planejado | Definir aporte mensal no plano (pode vir de disponivel_real ou campo dedicado) | 1h | — |
| 3.2 | PlanoAposentadoriaTab usa aporte do plano | Quando usuário tem plano, usar aporte planejado na projeção | 2h | 3.1 |
| 3.3 | Nudge bidirecional | "Se guardar R$ X a mais = aposentadoria N anos antes" | 1h | 3.2 |

**Entregável:** Projeção de aposentadoria considera o aporte definido no plano.

---

### Fase 4 — base_expectativas (fase futura, ≈ 16h)

**Objetivo:** Camada 2 do legado — sazonais, parcelas futuras, 13º.

| # | Task | Descrição | Est. | Dep. |
|---|------|-----------|------|------|
| 4.1 | Migration `base_expectativas` | Tabela conforme TECH_SPEC legado | 2h | — |
| 4.2 | CRUD base_expectativas | POST/GET/DELETE expectativas | 3h | 4.1 |
| 4.3 | Fase 6 no upload: parcelas futuras | Popular base_expectativas a partir de base_parcelas | 3h | 4.2 |
| 4.4 | Backend: cashflow com expectativas | Incluir base_expectativas no GET cashflow | 2h | 4.2 |
| 4.5 | UI: gastos sazonais | Form para IPVA, IPTU, 13º, etc. | 4h | 4.2 |
| 4.6 | Budget at risk | total_esperado = plano + expectativas; alertas antecipados | 2h | 4.4 |

**Entregável:** Sazonais e parcelas futuras integrados ao plano.

---

### Fase 5 — Wizard 4 etapas (fase futura, ≈ 10h)

**Objetivo:** Preencher o frame já preparado na Fase 0. O shell e a estrutura de steps existem; esta fase adiciona o conteúdo real de cada etapa.

| # | Task | Descrição | Est. | Dep. |
|---|------|-----------|------|------|
| 5.1 | Etapa 1: Renda + ganhos extraordinários | Form no step 1: campo renda + lista de ganhos extras (13º, bônus) | 3h | 4.1, 0.2 |
| 5.2 | Etapa 2: Gastos base | Proposta dos últimos 3 meses por grupo; usuário confirma/ajusta | 3h | 0.2 |
| 5.3 | Etapa 3: Gastos sazonais | Grid de meses com gastos extras (usa base_expectativas) | 2h | 4.2, 0.2 |
| 5.4 | Etapa 4: Aporte + recibo | Slider de aporte (teto = disponível) + tabela 12 meses | 2h | 2.3, 0.2 |
| 5.5 | Fluxo condicional | Sem plano → wizard; com plano → "Editar plano" abre wizard | — | 5.4 |

**Entregável:** Wizard completo. Qualquer edição (renda, metas, sazonais, aporte) passa por este frame.

---

## 4. Ordem de execução recomendada

```
FASE 0 (preparação do solo) → 2h   ← começar aqui: frame do wizard
    ↓
FASE 1 (consolidação)      → 8h   ← hub + CTA "Editar plano"
    ↓
FASE 2 (cashflow/recibo)    → 10h  ← cashflow primeiro, projeção opcional
    ↓
FASE 3 (aposentadoria)     → 4h
    ↓
FASE 4 (expectativas)      → 16h  ← fase futura
    ↓
FASE 5 (conteúdo do wizard)→ 10h  ← preenche o frame
```

**Total Fase 0–3:** ~24h (hub + frame pronto para evoluir)  
**Total Fase 4–5:** ~26h (legado completo)

---

## 5. Critérios de priorização

| Critério | Fase 0 | Fase 1 | Fase 2 | Fase 3 | Fase 4 | Fase 5 |
|----------|--------|--------|--------|--------|--------|
| Resolve "conta não fecha"? | — | ✅ (já temos) | ✅ | ✅ | ✅ | ✅ |
| Hub central do plano? | — | ✅ | ✅ | — | — | — |
| Prepara frame de edição? | ✅ | ✅ (CTA) | — | — | — | ✅ (conteúdo) |
| Impacto motivacional (nudge)? | — | ✅ | — | ✅ | — | — |
| Complexidade técnica | Baixa | Baixa | Média | Média | Alta | Alta |
| Depende de base_expectativas? | Não | Não | Não | Não | Sim | Parcial |

---

## 6. Checklist de validação

**Fase 0:**
- [ ] Rota `/mobile/construir-plano` existe e renderiza
- [ ] `PlanoWizard` com 4 steps (navegação entre eles)
- [ ] `PlanoWizardState` definido (tipagem/interface)

**Fase 1:**

- [ ] Tab "Plano" na BottomNav leva a `/mobile/plano`
- [ ] Tela Plano exibe: Renda | Gastos | Disponível | Saldo
- [ ] Orçamento por grupo com barras de progresso
- [ ] Seletor de mês funcional
- [ ] Quando gasto > renda: card "Anos perdidos" aparece
- [ ] Quando dentro do plano: card "Anos perdidos" não aparece
- [ ] Link "Gerenciar metas" leva a `/mobile/budget/manage`
- [ ] Perfil Financeiro continua acessível (via Plano ou menu)
- [ ] Botão "Editar plano" leva a `/mobile/construir-plano`

---

## 7. Referências

- **Legado:** `_legado/PRD.md`, `_legado/UX_PLANO_FINANCEIRO_INTEGRADO.md`, `_legado/02-TECH_SPEC/TECH_SPEC.md`
- **Comparativo geral:** `05-plano-financeiro/COMPARATIVO_LEGADO_VS_ATUAL.md`
- **Comparativo Fase 2:** `05-plano-financeiro/COMPARATIVO_FASE2_LEGADO.md`
- **Plano atual:** `05-plano-financeiro/PLANO.md`
- **Volta ao legado:** `05-plano-financeiro/PLANO_VOLTA_LEGADO.md`
