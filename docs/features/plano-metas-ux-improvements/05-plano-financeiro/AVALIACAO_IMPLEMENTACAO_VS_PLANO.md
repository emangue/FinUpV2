# Avaliação: Implementação vs Plano Construtor Unificado

**Data:** 01/03/2026  
**Referência:** `PLANO_CONSTRUTOR_UNIFICADO.md`  
**Branch:** `feature/merge-plano-aposentadoria`  
**Último commit:** `feat(plano): wizard UX - footer fixo, receitas extraordinárias, etapas 2-4`

---

## Resumo executivo

| Status | Itens |
|--------|-------|
| ✅ Implementado | 14 itens |
| ⚠️ Parcial | 3 itens |
| ❌ Pendente | 4 itens |

---

## Checklist detalhado

### Fase A — UX base (botões, validação)

| # | Task | Status | Observação |
|---|------|--------|------------|
| A.1 | Botões fixos no rodapé | ✅ | `fixed bottom-20` acima da bottom-nav |
| A.2 | Validação por etapa | ⚠️ | Só etapa 1 (renda > 0). Etapas 2–4 sem validação de campos obrigatórios |

### Fase B — Etapa 1 (Renda + Ganhos Extraordinários)

| # | Task | Status | Observação |
|---|------|--------|------------|
| B.1 | Extrair componente GanhosExtraordinariosEditor | ⚠️ | Não extraído; implementado inline na PlanoWizard |
| B.2 | Integrar na Etapa 1 | ✅ | Seção "Receitas extraordinárias" com lista + formulário |
| B.3 | Persistência base_expectativas (renda_plano) | ✅ | `postExpectativa` com `tipo_expectativa: 'renda_plano'` |
| B.4 | Carregar ao abrir | ✅ | `getExpectativas` filtrado por `renda_plano` |

**Campos por item (plano vs implementado):**

| Campo | Plano | Implementado |
|-------|-------|--------------|
| Descrição | ✅ | ✅ |
| Valor (R$) | ✅ | ✅ |
| Mês (1–12) | ✅ | ✅ |
| Recorrência | único \| trimestral \| semestral \| anual | ✅ + bimestral |
| Evoluir valor | checkbox | ❌ |
| Evolução (% ou R$) | se evoluir | ❌ |

### Fase C — Etapa 2 (Gastos com média 3 meses)

| # | Task | Status | Observação |
|---|------|--------|------------|
| C.1 | Backend média 3 meses | ✅ | `GET /plano/grupos-media-3-meses` |
| C.2 | UI lista grupos | ✅ | Nome, média 3 meses, meta editável |
| C.3 | Salvar metas | ✅ | `putOrcamentoBulk` (budget/planning bulk-upsert) |
| — | Botão "Usar média como meta" | ✅ | Global |

### Fase D — Etapa 3 (Sazonais)

| # | Task | Status | Observação |
|---|------|--------|------------|
| D.1 | Componente GastosSazonaisEditor | ⚠️ | Inline na PlanoWizard (não extraído) |
| D.2 | Integrar na Etapa 3 | ✅ | Lista + formulário add/remove |
| D.3 | Persistência sazonal_plano | ✅ | `postExpectativa` / `deleteExpectativa` |

**Campos por item (plano vs implementado):**

| Campo | Plano | Implementado |
|-------|-------|--------------|
| Descrição | ✅ | ✅ |
| Valor (R$) | ✅ | ✅ |
| Mês (1–12) | ✅ | ✅ |
| Recorrência | único \| trimestral \| semestral \| anual | ✅ + bimestral |
| Evoluir anualmente | checkbox | ❌ |
| Evolução (% ou R$) | se evoluir | ❌ |

### Fase E — Etapa 4 (Recibo do Ano)

| # | Task | Status | Observação |
|---|------|--------|------------|
| E.1 | Redefinir Etapa 4 | ✅ | "Recibo do Ano" com aporte no contexto |
| E.2 | TabelaReciboAnual | ✅ | Resumo mês a mês |
| E.3 | Campos evolução/inflação | ❌ | Taxa evolução e expectativa inflação não na Etapa 4 |
| E.4 | Projeção até fim do plano | ✅ | ProjecaoChart + projecaoLonga (30 anos) |
| E.5 | Aporte no contexto | ✅ | Campo aporte mantido |

### Fase F — Integração

| # | Task | Status | Observação |
|---|------|--------|------------|
| F.1 | Fluxo completo 1→2→3→4 | ✅ | Salva renda, metas, expectativas, aporte |
| F.2 | Documentação | 🔄 | Este documento |

---

## Itens pendentes (prioridade sugerida)

### 1. Evoluir valor (Etapas 1 e 3) — Média

- **O quê:** Checkbox "Evoluir valor" + campo evolução (% ou R$) para receitas extraordinárias e sazonais.
- **Onde:** PersonalizarPlanoLayout já tem; replicar na PlanoWizard.
- **Backend:** `metadata_json` em `base_expectativas` para armazenar `evoluir`, `evolucao_tipo`, `evolucao_valor`.

### 2. Campos evolução/inflação na Etapa 4 — Baixa

- **O quê:** Taxa de evolução (% a.a.) e expectativa de inflação (% a.a.) editáveis na Etapa 4.
- **Persistência:** `user_financial_profile` — `taxa_retorno_anual`, `expectativa_inflacao` (se existir).
- **Uso:** ProjecaoChart e projeção longa já usam parâmetros do perfil; falta UI para editar na Etapa 4.

### 3. Validação por etapa (2, 3, 4) — Baixa

- **O quê:** Desabilitar "Próximo" quando etapa incompleta (ex.: etapa 2 sem grupos, etapa 3 sem sazonais obrigatórios).
- **Nota:** Plano não exige sazonais obrigatórios; validação pode ser mínima.

### 4. Extrair componentes (opcional)

- **O quê:** `GanhosExtraordinariosEditor` e `GastosSazonaisEditor` como componentes reutilizáveis.
- **Benefício:** Reduz duplicação e facilita manutenção; não bloqueia uso atual.

---

## Backend e infraestrutura (já implementados)

| Item | Status |
|------|--------|
| `expectativas_mes` (materialização) | ✅ |
| `get_planejado_por_grupo_mes` | ✅ |
| `get_expectativas_por_mes` | ✅ |
| `get_projecao_longa` | ✅ |
| `get_grupos_media_3_meses` | ✅ |
| Recorrência em `ExpectativaCreate` | ✅ |
| Expansão 12 meses em `create_expectativa` | ✅ |
| Job `rolar_expectativas_mes.py` | ✅ |
| Backfill `backfill_expectativas_mes.py` | ✅ |
| CTAs `personalizar-plano` → `construir-plano` | ✅ |

---

## Conclusão

O Construtor de Plano está **funcional e alinhado ao plano** nas 4 etapas. Os itens pendentes são incrementais:

- **Evoluir valor** — melhoria de UX para cenários com inflação/crescimento.
- **Campos evolução/inflação na Etapa 4** — refinamento da projeção.
- **Validação** e **extração de componentes** — qualidade e manutenção.

O fluxo principal (renda → gastos → sazonais → recibo) está pronto para uso e testes.
