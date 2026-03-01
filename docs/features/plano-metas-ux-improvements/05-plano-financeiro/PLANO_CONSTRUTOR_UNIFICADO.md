# Plano de Alteração — Construtor de Plano Unificado

**Data:** 01/03/2026  
**Objetivo:** Unir o que tínhamos no plano de aposentadoria com o Construtor de Plano atual (4 etapas).  
**Status:** Planejamento — executar no final, após validação.

---

## Visão Geral

O Construtor de Plano (`/mobile/construir-plano`) hoje tem 4 etapas: Renda | Gastos | Sazonais | Aporte. Este plano define as alterações para:

1. **Etapa 1 (Renda):** Ganhos extraordinários + botões fixos + validação
2. **Etapa 2 (Gastos):** Ajuste por grupo com média dos últimos 3 meses
3. **Etapa 3 (Sazonais):** Cadastro de gastos sazonais com evolução anual
4. **Etapa 4:** Trocar "Aporte" por "Recibo do Ano" — projeção completa com evolução, inflação, taxa

---

## 1. Etapa 1 — Renda + Ganhos Extraordinários

### 1.1 Botões Voltar e Próximo

| Item | Descrição |
|------|-----------|
| **Posição** | Fixos na parte inferior da tela (sticky footer) |
| **Validação** | Só habilitar "Próximo" quando todos os campos obrigatórios estiverem preenchidos |
| **Implementação** | `position: sticky` ou `fixed` no footer; `disabled={!isStepValid}` |

### 1.2 Ganhos Extraordinários (da dinâmica do plano de aposentadoria)

**Origem:** `PersonalizarPlanoLayout.tsx` — seção "Aportes Extraordinários" (linhas ~716–934).

**Campos por item:**
- Descrição (texto)
- Valor (R$)
- Mês (1–12)
- Recorrência: único | trimestral | semestral | anual
- **Evoluir valor:** checkbox
- Se evoluir: valor de evolução + tipo (% ou R$)

**Persistência:** Integrar com `base_expectativas` (tipo `renda_plano`) ou criar modelo específico para ganhos extraordinários no plano financeiro.

**Backend:** Endpoints já existem em `/plano/expectativas` (POST, GET, DELETE). Tipo `renda_plano` para ganhos extras.

---

## 2. Etapa 2 — Gastos por Grupo (média 3 meses)

### 2.1 Objetivo

Permitir ajustar metas de gasto **nesta tela**, considerando a média dos últimos 3 meses por grupo.

### 2.2 Dados necessários

| Fonte | Descrição |
|-------|-----------|
| `GET /plano/orcamento?ano=&mes=` | Já retorna gasto vs meta por grupo |
| Média 3 meses | Novo endpoint ou campo: `GET /plano/grupos-media-3-meses?ano=&mes=` |
| `budget_planning` | Metas atuais por grupo |

### 2.3 UI

- Lista de grupos com:
  - Nome do grupo
  - Média últimos 3 meses (realizado)
  - Meta atual (editável)
  - Sugestão: pré-preencher com média 3 meses
- Botão "Usar média como meta" por grupo ou global

### 2.4 Backend

- Endpoint ou extensão para retornar média 3 meses por grupo (Despesa)
- `POST /plano/orcamento/bulk` ou uso de `budget_planning` bulk-upsert existente

---

## 3. Etapa 3 — Sazonais (IPVA, IPTU, 13º, etc.)

### 3.1 Objetivo

Cadastrar gastos sazonais **nesta tela**, com opção de evolução anual (como no plano legado).

### 3.2 Campos por item (espelho de Ganhos Extraordinários)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| Descrição | texto | Ex: "IPVA", "IPTU", "13º salário" |
| Valor (R$) | número | Valor base |
| Mês | 1–12 | Mês de ocorrência no ano |
| Recorrência | único \| trimestral \| semestral \| anual | Frequência |
| Evoluir anualmente | checkbox | Se o valor aumenta ano a ano |
| Evolução | % ou R$ | Valor/taxa de evolução |

### 3.3 Persistência

**Modelo:** `base_expectativas` — tipo `sazonal_plano`.

**Backend:** Endpoints existentes `POST/GET/DELETE /plano/expectativas`.

### 3.4 Integração com cashflow

O cashflow (`GET /plano/cashflow?ano=`) já usa `get_expectativas_por_mes` para meses não realizados. Sazonais entram em `gastos_extras_esperados`.

---

## 4. Etapa 4 — Recibo do Ano (substituir Aporte)

### 4.1 Objetivo

Não mais "Aporte" isolado. A Etapa 4 passa a ser o **Recibo do Ano** — visão consolidada considerando:

- Tudo que foi definido nas etapas 1–3
- Evolução até o final do plano
- Taxa de evolução ao longo dos anos
- Expectativa de inflação

### 4.2 Conteúdo da tela

| Bloco | Descrição |
|-------|-----------|
| **Resumo anual** | Tabela mês a mês: Renda | Gastos | Aporte | Saldo (reutilizar `TabelaReciboAnual` / `plano-chart`) |
| **Parâmetros** | Taxa de evolução (% a.a.), expectativa de inflação (% a.a.) |
| **Projeção** | Gráfico de evolução do patrimônio até o fim do plano |
| **Aporte** | Campo de aporte planejado (mantido, mas dentro do contexto do recibo) |

### 4.3 Integração com PersonalizarPlanoLayout

O `PersonalizarPlanoLayout` (plano de aposentadoria) já tem:
- Idade, aposentadoria, retorno, inflação
- Projeção com aportes extraordinários
- Tabela "Primeiros meses"

**Estratégia:** Reutilizar componentes e lógica. A Etapa 4 pode:
- Importar `TabelaReciboAnual` ou equivalente do plano-chart
- Usar `ProjecaoChart` do plano (já existe)
- Adicionar campos: taxa evolução, inflação esperada
- Persistir em `user_financial_profile`: `taxa_retorno_anual`, `aporte_planejado`; considerar `expectativa_inflacao` se não existir

---

## 5. Resumo de Tarefas (ordem sugerida)

### Fase A — UX base (botões, validação)

| # | Task | Descrição | Est. |
|---|------|-----------|------|
| A.1 | Botões fixos | Voltar/Próximo sticky no rodapé | 0.5h |
| A.2 | Validação por etapa | Desabilitar Próximo se campos vazios | 1h |

### Fase B — Etapa 1 (Renda + Ganhos Extraordinários)

| # | Task | Descrição | Est. |
|---|------|-----------|------|
| B.1 | Extrair componente | GanhosExtraordinariosEditor de PersonalizarPlanoLayout | 1h |
| B.2 | Integrar na Etapa 1 | Adicionar seção na PlanoWizard step 1 | 1h |
| B.3 | Persistência | Salvar em base_expectativas (renda_plano) | 1.5h |
| B.4 | Carregar ao abrir | Buscar expectativas tipo renda_plano | 0.5h |

### Fase C — Etapa 2 (Gastos com média 3 meses)

| # | Task | Descrição | Est. |
|---|------|-----------|------|
| C.1 | Backend média 3 meses | Endpoint ou campo em orcamento | 2h |
| C.2 | UI lista grupos | Exibir grupos com média e meta editável | 2h |
| C.3 | Salvar metas | Bulk upsert em budget_planning | 1h |

### Fase D — Etapa 3 (Sazonais)

| # | Task | Descrição | Est. |
|---|------|-----------|------|
| D.1 | Componente GastosSazonaisEditor | Espelho de GanhosExtraordinarios (débito) | 2h |
| D.2 | Integrar na Etapa 3 | Substituir texto "próxima versão" | 0.5h |
| D.3 | Persistência | base_expectativas tipo sazonal_plano | 1h |

### Fase E — Etapa 4 (Recibo do Ano)

| # | Task | Descrição | Est. |
|---|------|-----------|------|
| E.1 | Redefinir Etapa 4 | Trocar "Aporte" por "Recibo do Ano" | 1h |
| E.2 | Incluir TabelaReciboAnual | Resumo mês a mês | 0.5h |
| E.3 | Campos evolução/inflação | Taxa evolução, expectativa inflação | 1h |
| E.4 | Projeção até fim do plano | Gráfico + tabela (reutilizar ProjecaoChart) | 2h |
| E.5 | Aporte no contexto | Manter campo aporte dentro do recibo | 0.5h |

### Fase F — Integração e testes

| # | Task | Descrição | Est. |
|---|------|-----------|------|
| F.1 | Fluxo completo | Testar 1→2→3→4 com dados reais | 1h |
| F.2 | Documentação | Atualizar PRD e PLANO.md | 0.5h |

---

## 6. Estimativa Total

| Fase | Horas |
|------|-------|
| A (UX base) | 1.5h |
| B (Etapa 1) | 4h |
| C (Etapa 2) | 5h |
| D (Etapa 3) | 3.5h |
| E (Etapa 4) | 5h |
| F (Integração) | 1.5h |
| **Total** | **~20.5h** |

---

## 7. Referências

- `PLANO_VOLTA_LEGADO.md` — base_expectativas, budget_planning
- `UX_PLANO_FINANCEIRO_INTEGRADO.md` — GanhosExtraordinariosEditor, GastosSazonaisEditor
- `PersonalizarPlanoLayout.tsx` — dinâmica de extras (recorrência, evolução)
- `TabelaReciboAnual.tsx` — tabela mês a mês
- `ProjecaoChart.tsx` — gráfico de projeção

---

## 8. Checklist de Validação (após implementação)

- [ ] Voltar e Próximo fixos no rodapé
- [ ] Próximo desabilitado se etapa incompleta
- [ ] Etapa 1: Renda + Ganhos extraordinários (descrição, valor, mês, recorrência, evoluir)
- [ ] Etapa 2: Grupos com média 3 meses e meta editável
- [ ] Etapa 3: Sazonais com evolução anual
- [ ] Etapa 4: Recibo do ano com evolução, inflação, projeção
- [ ] Fluxo salva e carrega corretamente
