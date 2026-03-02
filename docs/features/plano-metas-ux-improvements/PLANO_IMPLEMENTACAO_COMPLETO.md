# Plano de Implementação Completo — Até 05 + Ajuste 06

**Data:** 28/02/2026  
**Objetivo:** Implementar tudo que não foi feito (01–05) e ajustar 06 para alinhar ao legado.

---

## Ordem de execução

```
BLOCO 1 — Ajustes rápidos (02, 03)
  ├── 2.1 EmptyStatePlano em /mobile/plano
  └── 3.2 Nudge "Crie seu Plano" em NudgeBanners

BLOCO 2 — 04 Upload pendente
  └── A.06 Migration: base_marcacoes.upload_history_id + base_parcelas.upload_history_id

BLOCO 3 — 05 Fase 2 (Cashflow + Recibo)
  ├── 2.1 GET /plano/cashflow?ano=
  ├── 2.2 TabelaReciboAnual
  ├── 2.3 Integrar na tela /mobile/plano
  ├── 2.4 PUT /plano/perfil
  ├── 2.5 GET /plano/projecao?meses=12&reducao_pct=0
  └── 2.6 ProjecaoChart

BLOCO 4 — 05 Fase 3 (Aposentadoria)
  ├── 3.1 Campo aporte_planejado no perfil
  ├── 3.2 PlanoAposentadoriaTab usa aporte do plano
  └── 3.3 Nudge bidirecional

BLOCO 5 — 05 Fase 4 (base_expectativas)
  ├── 4.1 Migration base_expectativas
  ├── 4.2 CRUD expectativas
  ├── 4.3 Fase 6 upload: parcelas futuras
  ├── 4.4 Cashflow com expectativas
  ├── 4.5 UI gastos sazonais
  └── 4.6 Budget at risk

BLOCO 6 — 05 Fase 5 (Wizard completo)
  ├── 5.1 Etapa 1: Renda + ganhos extras
  ├── 5.2 Etapa 2: Gastos base
  ├── 5.3 Etapa 3: Gastos sazonais
  ├── 5.4 Etapa 4: Aporte + recibo
  └── 5.5 Fluxo condicional

BLOCO 7 — 06 Ajuste ao legado
  └── Documentar PLANO.md com S11–S18; verificar badge Carteira
```

---

## Detalhamento por bloco

### BLOCO 1 — Ajustes rápidos

| Task | Arquivo | Ação |
|------|---------|------|
| EmptyStatePlano | plano/page.tsx | Quando !resumo && !orcamentoItems: EmptyState com CTA principal /mobile/construir-plano, secundário /mobile/upload |
| Nudge Crie Plano | NudgeBanners.tsx | Nova prioridade 2: primeiro_upload && !plano_criado → "Ótimo início! Crie seu Plano" + /mobile/plano |

### BLOCO 2 — 04 Migration

| Task | Descrição |
|------|-----------|
| A.06 | Migration: add upload_history_id (nullable FK) em base_marcacoes e base_parcelas |

### BLOCO 3 — 05 Fase 2

| Task | Descrição |
|------|-----------|
| 2.1 | Backend: GET /plano/cashflow?ano= — 12 meses com renda_esperada, gastos_recorrentes, gastos_realizados, aporte_planejado, saldo_projetado, status_mes |
| 2.2 | TabelaReciboAnual: Mês \| Renda \| Gastos \| Aporte \| Saldo + status + resumo ano |
| 2.3 | CTA "Ver cashflow anual" na tela plano → expande tabela |
| 2.4 | PUT /plano/perfil: idade, aposentadoria, patrimônio, taxa |
| 2.5 | GET /plano/projecao?meses=12&reducao_pct=0 |
| 2.6 | ProjecaoChart com slider |

### BLOCO 4 — 05 Fase 3

| Task | Descrição |
|------|-----------|
| 3.1 | user_financial_profile.aporte_planejado ou campo dedicado |
| 3.2 | PlanoAposentadoriaTab usa aporte do plano quando disponível |
| 3.3 | Nudge "Se guardar R$ X a mais = aposentadoria N anos antes" |

### BLOCO 5 — 05 Fase 4

| Task | Descrição |
|------|-----------|
| 4.1 | Migration base_expectativas |
| 4.2 | CRUD POST/GET/DELETE expectativas |
| 4.3 | Fase 6 upload: popular base_expectativas de base_parcelas |
| 4.4 | Cashflow inclui base_expectativas |
| 4.5 | UI gastos sazonais (form wizard etapa 3) |
| 4.6 | Budget at risk |

### BLOCO 6 — 05 Fase 5

| Task | Descrição |
|------|-----------|
| 5.1 | Wizard Etapa 1: Renda + ganhos extras (form real) |
| 5.2 | Wizard Etapa 2: Gastos base (proposta 3 meses) |
| 5.3 | Wizard Etapa 3: Gastos sazonais (grid) |
| 5.4 | Wizard Etapa 4: Aporte + recibo (slider + tabela) |
| 5.5 | Fluxo: sem plano → wizard; com plano → Editar abre wizard |

### BLOCO 7 — 06 Ajuste

| Task | Descrição |
|------|-----------|
| 6.1 | PLANO.md: "Atende S11–S18 do PRD legado" |
| 6.2 | Documentar integração com 05 (aporte) |
| 6.3 | Verificar badge dinâmico Carteira (S19.4) |
