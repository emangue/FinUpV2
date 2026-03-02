# Comparativo Geral — Pastas vs Legado

**Data:** 28/02/2026  
**Objetivo:** Garantir que cada sub-projeto (01–06) seja parte coerente do grande plano legado. Mapear gaps e alinhamentos.

---

## 1. Visão do Legado (fonte única)

O legado (`_legado/`) define:

| Documento | Conteúdo |
|-----------|----------|
| **PRD.md** | User stories S1–S30, features 2a–2o |
| **PLANO_IMPLEMENTACAO.md** | Sprints 0–9, tasks por sprint |
| **UX_PLANO_FINANCEIRO_INTEGRADO.md** | Fluxo do wizard, recibo, 3 camadas |
| **02-TECH_SPEC/TECH_SPEC.md** | Cashflow engine, base_expectativas, endpoints |

**Promessa central:** *"Ajudar a pessoa a construir um plano financeiro realista que conecta seus gastos reais ao seu futuro."*

---

## 2. Mapeamento: Legado → Pastas

| Legado (Sprint/PRD) | Pasta atual | Alinhado? | Observação |
|--------------------|-------------|-----------|------------|
| Sprint 0 — Admin gestão usuários | 01-admin-gestao-usuarios | ✅ | + grupos por usuário (evolução) |
| Sprint 1 — Bugs + Nav + Empty states | 02-ux-fundacao | ✅ | S19, S27, B1–B4 |
| Sprint 2 — Onboarding + Grupos padrão | 03-onboarding-grupos | ✅ | S24, S25, S26, S28, S29 |
| Sprint 3 — Upload inteligente | 04-upload-completo (Sprint 3) | ✅ | S20, S30 |
| Sprint 3.5 — Rollback | 04-upload-completo (Sprint 3.5) | ✅ | S31 |
| Sprint 4 — Multi-file + Classificação + Import | 04-upload-completo (Sprint 4) | ✅ | S21, S22, S23 |
| Sprint 5 — Modo exploração | 03-onboarding (demo) + 04 (planilha) | ⚠️ | Demo em 03; planilha em 04 |
| Sprint 6 — Backend Plano | 05-plano-financeiro | ⚠️ | Parcial: renda, resumo, orçamento; falta cashflow |
| Sprint 7 — Frontend Plano | 05-plano-financeiro | ⚠️ | Fase 0+1 feitas; falta cashflow, wizard completo |
| Sprint 8–9 — Patrimônio | 06-patrimonio-investimentos | ✅ | S11–S18 |

---

## 3. Análise por pasta

### 01-admin-gestao-usuarios

| Item legado | Status | Observação |
|-------------|--------|------------|
| Criar usuário + trigger grupos | ✅ | `_inicializar_grupos_usuario()` |
| Purge, reativar, stats | ✅ | Endpoints existem |
| Grupos por usuário (user_id) | ✅ | Evolução além do legado — correto |
| base_grupos_template | ✅ | Fonte para novos usuários |

**Conclusão:** Alinhado. Grupos por usuário é evolução necessária.

---

### 02-ux-fundacao

| Item legado | Status | Observação |
|-------------|--------|------------|
| B1–B4 (bugs) | ✅ | Replicar plano, loop nav, scroll, format |
| S19 (nav redesign) | ✅ | FAB Upload, Plano tab, Perfil no header |
| S27 (empty states) | ✅ | Início, Transações, Plano, Carteira |
| Tab Plano → /mobile/plano | ✅ | Atualizado na Fase 1 |

**Conclusão:** Alinhado.

---

### 03-onboarding-grupos

| Item legado | Status | Observação |
|-------------|--------|------------|
| S24 (welcome + choose path) | ✅ | welcome, choose-path |
| S25 (grupos padrão) | ✅ | Trigger no create_user |
| S26 (modo exploração) | ✅ | Demo mode |
| S28 (checklist) | ✅ | OnboardingChecklist |
| S29 (nudges contextuais) | ✅ | Banners |
| "Import planilha" na escolha | ⚠️ | Legado: 3ª opção; hoje pode ir para upload |

**Conclusão:** Alinhado. Import planilha pode ser via Upload (04).

---

### 04-upload-completo

| Item legado | Status | Observação |
|-------------|--------|------------|
| S20 (detecção automática) | ✅ | DetectionEngine, content_extractor |
| S30 (alerta duplicata) | ✅ | Integrado ao detect |
| S21 (multi-file) | ✅ | Batch upload |
| S22 (classificação em lote) | ✅ | BatchClassifyModal |
| S23 (import planilha) | ✅ | import-planilha |
| S31 (rollback) | ✅ | UploadHistory, rollback |
| Fase 6 upload → base_expectativas | ❌ | Legado: parcelas futuras; fora do escopo 04 |

**Conclusão:** Alinhado. Fase 6 (expectativas) é 05-plano Fase 4.

---

### 05-plano-financeiro

| Item legado | Status | Observação |
|-------------|--------|------------|
| Renda declarada | ✅ | user_financial_profile, /plano/renda |
| Metas por grupo | ✅ | budget_planning |
| Conexão renda ↔ metas | ✅ | disponivel_real |
| Hub /mobile/plano | ✅ | Fase 1 |
| Wizard frame /construir-plano | ✅ | Fase 0 |
| Nudge anos perdidos | ✅ | GET /impacto-longo-prazo |
| GET /plano/cashflow | ❌ | Fase 2 — ver COMPARATIVO_FASE2_LEGADO |
| Tabela recibo anual | ❌ | Fase 2 |
| base_expectativas | ❌ | Fase 4 (futura) |
| Wizard 4 etapas completo | ❌ | Fase 5 (conteúdo) |
| Integração aposentadoria | ❌ | Fase 3 |

**Conclusão:** Núcleo feito. Faltam Fases 2–5 conforme PLANO_DE_AJUSTE.

---

### 06-patrimonio-investimentos

| Item legado | Status | Observação |
|-------------|--------|------------|
| S11 (vínculo aporte) | 🔄 | Estrutura existe |
| S12 (match automático) | 🔄 | Sugestões |
| S13 (CDI renda fixa) | 🔄 | Job BACEN |
| S14 (posição ações) | 🔄 | brapi |
| S15 (IR estimado) | 🔄 | Regras por tipo |
| S16 (venda/resgate) | 🔄 | Vinculação |
| S17 (saldo corretora) | 🔄 | Produto saldo |
| S18 (indexadores) | 🔄 | CDI, IPCA, etc. |
| Badge Carteira (aportes pendentes) | ⚠️ | Legado: dinâmico; verificar se implementado |

**Conclusão:** Estrutura alinhada. Detalhes em PLANO 06.

---

## 4. Gaps transversais (afetam múltiplas pastas)

| Gap | Onde | Ação |
|-----|------|------|
| **Tab Plano** | 02, 05 | Já aponta para /mobile/plano ✅ |
| **Empty state Plano** | 02 | CTA deve ir para /mobile/plano ou /construir-plano |
| **Checklist "Crie seu Plano"** | 03 | Já vai para /mobile/plano ✅ |
| **Nudge "Crie seu Plano"** | 03 | Deve ir para /mobile/plano |
| **Fase 6 upload → expectativas** | 04, 05 | Pertence a 05 Fase 4 (base_expectativas) |
| **Aporte do plano → aposentadoria** | 05, 06 | 05 Fase 3 + integração em 06 |

---

## 5. Referências cruzadas (onde cada item do legado vive)

| Legado | Pasta | Arquivo |
|--------|-------|---------|
| S1–S4 (bugs) | 02 | PLANO.md |
| S5–S10 (plano) | 05 | PLANO_DE_AJUSTE.md, COMPARATIVO_LEGADO_VS_ATUAL.md |
| S11–S18 (patrimônio) | 06 | PLANO.md, PRD.md |
| S19 (nav) | 02 | PLANO.md |
| S20–S23 (upload) | 04 | PLANO.md |
| S24–S29 (onboarding) | 03 | PLANO.md |
| S30 (duplicata) | 04 | PLANO.md |
| S31 (rollback) | 04 | PLANO.md |
| 2n (admin) | 01 | PLANO.md |
| 2o (rollback rastreamento) | 04 | PLANO.md |
| Cashflow engine | 05 | COMPARATIVO_FASE2_LEGADO.md, PLANO_DE_AJUSTE Fase 2 |
| Wizard 4 etapas | 05 | PLANO_DE_AJUSTE Fase 0, 5 |
| base_expectativas | 05 | PLANO_DE_AJUSTE Fase 4 |

---

## 6. Resumo executivo

| Pasta | Alinhamento | Ação sugerida |
|-------|-------------|---------------|
| 01-admin | ✅ Completo | Manter |
| 02-ux-fundacao | ✅ Completo | Manter |
| 03-onboarding | ✅ Completo | Verificar CTAs apontam para /mobile/plano |
| 04-upload | ✅ Completo | Fase 6 (expectativas) documentar como dependência de 05 |
| 05-plano | ⚠️ Em progresso | Seguir PLANO_DE_AJUSTE; Fases 2–5 |
| 06-patrimonio | 🔄 Estrutura ok | Validar badge dinâmico Carteira |

**Princípio:** Cada pasta deve ter um trecho no PRD/PLANO que cite explicitamente o item do legado que atende. O AJUSTE_GERAL_LEGADO.md propõe as alterações concretas.
