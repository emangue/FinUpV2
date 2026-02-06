# Mobile Experience V1.0 - Complete Documentation Index

**Data:** 31/01/2026 (Criação) | 01/02/2026 (Atualização V1.1)  
**Status:** ✅ Documentação Completa + Auditoria  
**Versão:** 1.1

**📝 CHANGELOG V1.1 (01/02/2026):**
- ✅ PRD atualizado (V1.0 → V1.1) com findings de auditoria
- ✅ TECH_SPEC atualizado (V1.0 → V1.1) com componentes ausentes + User Stories
- ✅ Cronograma atualizado: Sprint 0 de 12-15h → 29-35h (crítico)
- ✅ Adicionados 3 componentes: TrackerList, CategoryExpensesMobile, IconButton
- ✅ Adicionada Seção 5.4 (User Stories) e 9.5 (Estados de UI)
- ✅ AUDITORIA_QUALIDADE.md criado (80% modularidade, 75% cobertura)

---

## 🎯 Quick Start - Por Onde Começar?

### Para Product Managers / Stakeholders
👉 Comece por: [01-PRD/SUMMARY.md](./01-PRD/SUMMARY.md) (15 min de leitura)

### Para Developers
👉 Comece por: [02-TECH_SPEC/README.md](./02-TECH_SPEC/README.md) (10 min de leitura)

### Para Designers
👉 Comece por: [01-PRD/STYLE_GUIDE.md](./01-PRD/STYLE_GUIDE.md) (20 min de leitura)

### Para QA / Testers
👉 Comece por: [02-TECH_SPEC/TECH_SPEC.md](./02-TECH_SPEC/TECH_SPEC.md) Seção 6 (Testes)

---

## 📚 Estrutura de Documentação

```
mobile-v1/
├── README.md                      # Este arquivo (navegação)
├── CHANGELOG.md                   # Histórico de mudanças
│
├── 01-PRD/                        # Product Requirements
│   ├── README.md                  # Navegação da pasta PRD
│   ├── PRD.md                     # ⭐ Documento principal (4900+ linhas) V1.1
│   ├── STYLE_GUIDE.md             # Design System completo
│   ├── SUMMARY.md                 # Resumo executivo
│   ├── INDEX.md                   # Quick reference
│   ├── CHECKLIST.md               # Checklist de implementação
│   ├── FACTIBILIDADE.md           # Análise de viabilidade
│   ├── ANALISE_STAKEHOLDER.md     # Respostas a perguntas
│   ├── ANALISE_NOVA_TELA_METAS.md # Análise da tela de Metas
│   ├── AUDITORIA_UX.md            # Auditoria de UX
│   └── PRD_REVIEW.md              # Revisão técnica do PRD
│
└── 02-TECH_SPEC/                  # Technical Specification
    ├── README.md                  # Navegação da pasta Tech Spec
    ├── TECH_SPEC.md               # ⭐ Especificação técnica completa V1.1
    ├── API_SPEC.md                # Especificação de APIs (V1.2)
    ├── COMPONENTS.md              # Referência de componentes
    ├── TESTING_STRATEGY.md        # Estratégia de testes incremental
    ├── IMPLEMENTATION_GUIDE.md    # Ordem de implementação (DAG)
    ├── BACKEND_VALIDATION.md      # Validação do backend existente
    ├── DEPLOY_MAP.md              # Paths absolutos e deploy
    ├── BUDGET_STRUCTURE_ANALYSIS.md # Análise estrutura de metas
    ├── INFRASTRUCTURE.md          # Infraestrutura (dev + prod)
    ├── EXECUTIVE_SUMMARY.md       # Resumo executivo correções
    └── AUDITORIA_QUALIDADE.md     # 🆕 Auditoria modularidade + cobertura
```

---

## 📖 Documentos por Categoria

### 1. Visão Geral e Planejamento

| Documento | Linhas | Tempo de Leitura | Descrição |
|-----------|--------|------------------|-----------|
| [README.md](./README.md) | ~300 | 10 min | Navegação geral do projeto |
| [SUMMARY.md](./01-PRD/SUMMARY.md) | ~550 | 15 min | Resumo executivo com métricas |
| [INDEX.md](./01-PRD/INDEX.md) | ~320 | 8 min | Quick reference e navegação |
| [CHECKLIST.md](./01-PRD/CHECKLIST.md) | ~200 | 5 min | Checklist de implementação |

---

### 2. Product Requirements

| Documento | Linhas | Tempo de Leitura | Descrição |
|-----------|--------|------------------|-----------|
| [PRD.md](./01-PRD/PRD.md) | 4900+ | 2-3 horas | ⭐ Especificação completa de requisitos **V1.1** |
| [FACTIBILIDADE.md](./01-PRD/FACTIBILIDADE.md) | ~800 | 30 min | Análise técnica de viabilidade |
| [ANALISE_STAKEHOLDER.md](./01-PRD/ANALISE_STAKEHOLDER.md) | ~700 | 25 min | Respostas a perguntas específicas |
| [ANALISE_NOVA_TELA_METAS.md](./01-PRD/ANALISE_NOVA_TELA_METAS.md) | ~710 | 25 min | Deep dive na tela de Metas |
| [AUDITORIA_UX.md](./01-PRD/AUDITORIA_UX.md) | ~400 | 15 min | Auditoria de UX e acessibilidade |
| [PRD_REVIEW.md](./01-PRD/PRD_REVIEW.md) | ~300 | 10 min | Revisão técnica do PRD |

---

### 3. Design System

| Documento | Linhas | Tempo de Leitura | Descrição |
|-----------|--------|------------------|-----------|
| [STYLE_GUIDE.md](./01-PRD/STYLE_GUIDE.md) | ~760 | 30 min | ⭐ Design System completo (cores, dimensões, componentes) |

**Conteúdo do Style Guide:**
- Paleta de cores (6 categorias)
- Dimensões e espaçamentos
- Tipografia (7 estilos)
- Animações e transições
- Estados interativos
- Validação WCAG AA
- Componentes prontos:
  - TrackerCard
  - TrackerHeader
  - DonutChart
  - TogglePills
  - CategoryRowInline
  - WalletHeader
  - SelectorBar

---

### 4. Technical Specification

| Documento | Linhas | Tempo de Leitura | Descrição |
|-----------|--------|------------------|-----------|
| [TECH_SPEC.md](./02-TECH_SPEC/TECH_SPEC.md) | ~2800 | 1.5-2 horas | ⭐ Especificação técnica completa **V1.1** |
| [API_SPEC.md](./02-TECH_SPEC/API_SPEC.md) | ~950 | 45 min | Especificação de APIs (V1.2 atualizada) |
| [COMPONENTS.md](./02-TECH_SPEC/COMPONENTS.md) | ~750 | 45 min | Referência de componentes (20+) |
| [TESTING_STRATEGY.md](./02-TECH_SPEC/TESTING_STRATEGY.md) | ~450 | 20 min | Estratégia incremental de testes |
| [IMPLEMENTATION_GUIDE.md](./02-TECH_SPEC/IMPLEMENTATION_GUIDE.md) | ~800 | 35 min | Ordem de implementação (DAG) |
| [BACKEND_VALIDATION.md](./02-TECH_SPEC/BACKEND_VALIDATION.md) | ~650 | 25 min | Validação do backend existente |
| [DEPLOY_MAP.md](./02-TECH_SPEC/DEPLOY_MAP.md) | ~350 | 15 min | Paths absolutos e workflow deploy |
| [BUDGET_STRUCTURE_ANALYSIS.md](./02-TECH_SPEC/BUDGET_STRUCTURE_ANALYSIS.md) | ~600 | 25 min | Estrutura de metas (budget_planning) |
| [INFRASTRUCTURE.md](./02-TECH_SPEC/INFRASTRUCTURE.md) | ~850 | 35 min | Infraestrutura dev + prod (SQLite/PostgreSQL) |
| [EXECUTIVE_SUMMARY.md](./02-TECH_SPEC/EXECUTIVE_SUMMARY.md) | ~250 | 10 min | Resumo executivo - Correções críticas |
| [AUDITORIA_QUALIDADE.md](./02-TECH_SPEC/AUDITORIA_QUALIDADE.md) | ~450 | 20 min | 🆕 Auditoria modularidade + cobertura PRD |

**Conteúdo da Tech Spec (V1.1):**
- Stack tecnológico
- Arquitetura frontend (rotas, estrutura, middleware)
- Design System (mobile-colors, dimensions, typography, **animations**)
- Componentes mobile (**12 especificações completas** - 3 novos)
- Endpoints backend (15 existentes + **4 novos**)
- Fluxos de dados (3 diagramas)
- **User Stories detalhadas** (6 USs completas - **novo**)
- **Estados de UI** (loading, empty, error - **novo**)
- Testes (unitários, E2E, a11y)
- Deploy e infraestrutura
- Cronograma (4 sprints, **92-124 horas** - atualizado)
- Checklist de qualidade
- Riscos e mitigações

---

### 5. APIs e Integrações

| Documento | Seção | Descrição |
|-----------|-------|-----------|
| [API_SPEC.md](./02-TECH_SPEC/API_SPEC.md) | Seção 1 | Autenticação |
| [API_SPEC.md](./02-TECH_SPEC/API_SPEC.md) | Seção 2 | Dashboard (3 endpoints) |
| [API_SPEC.md](./02-TECH_SPEC/API_SPEC.md) | Seção 3 | Budget (5 endpoints, 2 novos) |
| [API_SPEC.md](./02-TECH_SPEC/API_SPEC.md) | Seção 4 | Transactions (4 endpoints, 1 novo) |
| [API_SPEC.md](./02-TECH_SPEC/API_SPEC.md) | Seção 5 | Upload (1 endpoint) |
| [API_SPEC.md](./02-TECH_SPEC/API_SPEC.md) | Seção 6 | Profile (3 endpoints) |
| [API_SPEC.md](./02-TECH_SPEC/API_SPEC.md) | Seção 10 | Exemplos de integração |

**Novos Endpoints Necessários (Sprint 0):**
1. `POST /api/v1/budget/planning/copy-to-year` - Copiar meta para ano inteiro
2. `GET /api/v1/transactions/grupo-breakdown` - Drill-down subgrupos
3. `GET /api/v1/budget/planning` - Buscar metas por grupo (**corrigido:** era `/budget/geral`)
4. `POST /api/v1/budget/planning/bulk-upsert` - Salvar metas (**corrigido:** era `/budget/geral/bulk-upsert`)

**Nota:** Endpoints 3 e 4 substituem endpoints incorretos no PRD original (descoberto na auditoria).

---

## 🎨 Design Assets

### Imagem de Referência: "Trackers"
**Localização:** Fornecida pelo usuário (não versionada)

**Componentes extraídos:**
- Paleta de cores (6 categorias)
- Layout de cards
- Progress bars
- Tipografia
- Espaçamentos

**Status:** ✅ Completamente mapeado no STYLE_GUIDE.md

---

## 📊 Métricas de Documentação (V1.1)

| Métrica | V1.0 | V1.1 | Δ |
|---------|------|------|---|
| **Total de documentos** | 20 | **22** | +2 |
| **Total de linhas** | ~16.000 | **~19.000** | +3.000 |
| **Componentes especificados** | 9 | **12** | +3 |
| **Endpoints documentados** | 17 | **19** | +2 |
| **Telas mobile** | 5 | **5** | = |
| **Código TypeScript/React pronto** | 30+ | **45+** | +15 |
| **Diagramas de fluxo** | 3 | **3** | = |
| **User stories detalhadas** | 0 | **6** | +6 |
| **Personas** | 3 | **3** | = |
| **Ambientes documentados** | 2 | **2** | = |
| **Sprint 0 (horas)** | 12-15h | **29-35h** | +17-20h |
| **Total (horas)** | 88-114h | **92-124h** | +4-10h |

**Novos Documentos V1.1:**
- `AUDITORIA_QUALIDADE.md` (+450 linhas)
- PRD Seção 16.6 (+850 linhas)
- TECH_SPEC Seções 2.3.4, 3.10-3.12, 5.4, 9.5 (+1.800 linhas)
- Cronograma atualizado com dependências

---

## ✅ Status de Implementação

### Backend

| Endpoint | Status | Esforço | Sprint |
|----------|--------|---------|--------|
| Dashboard APIs (3) | ✅ Pronto | 0h | - |
| Budget APIs (existentes) | ✅ Pronto | 0h | - |
| Transactions APIs (existentes) | ✅ Pronto | 0h | - |
| Upload API | ✅ Pronto | 0h | - |
| Profile APIs | ✅ Pronto | 0h | - |
| **GET /api/v1/budget/planning** | ❌ Criar | 2-3h | Sprint 0 |
| **POST /api/v1/budget/planning/bulk-upsert** | ❌ Criar | 3-4h | Sprint 0 |
| **POST /api/v1/budget/planning/copy-to-year** | ❌ Criar | 3-4h | Sprint 0 |
| **GET /api/v1/transactions/grupo-breakdown** | ❌ Criar | 3-4h | Sprint 0 |
| **Backend Modularidade (3 fixes)** | ❌ Corrigir | 9h | Sprint 0 🔴 |

**Total Backend:** 80% pronto | **20-24 horas faltando (Sprint 0 crítico)**

---

### Frontend

| Componente | Status | Esforço |
|------------|--------|---------|
| MetricCards | ✅ Existe | 0h (validar) |
| TransactionsList | ✅ Existe | 0h (melhorar) |
| Upload mobile | ✅ Existe | 0h (validar) |
| **BottomNavigation** | ❌ Criar | 2-3h |
| **MobileHeader** | ❌ Criar | 2h |
| **MonthScrollPicker** | ❌ Criar | 4-6h |
| **YTDToggle** | ❌ Criar | 2-3h |
| **TrackerCard** | ❌ Criar | 4-6h |
| **DonutChart** | ❌ Criar | 3-4h |
| **CategoryRowInline** | ❌ Criar | 2-3h |
| **BudgetEditBottomSheet** | ❌ Criar | 3-4h |
| **GrupoBreakdownBottomSheet** | ❌ Criar | 4-6h |
| **CategoryExpensesMobile** | ❌ Criar | 3-4h |
| Tela Dashboard mobile | ❌ Integrar | 4-6h |
| Tela Budget mobile | ❌ Criar | 8-12h |
| Tela Profile mobile | ❌ Adaptar | 4-6h |

**Total Frontend:** 80% reutilizável | 80-100 horas de dev

---

### Design System

| Arquivo | Status |
|---------|--------|
| mobile-colors.ts | ✅ Código pronto |
| mobile-dimensions.ts | ✅ Código pronto |
| mobile-typography.ts | ✅ Código pronto |
| TrackerCard | ✅ Código pronto |
| TrackerHeader | ✅ Código pronto |
| DonutChart | ✅ Código pronto |
| TogglePills | ✅ Código pronto |
| CategoryRowInline | ✅ Código pronto |

**Total Design System:** 100% especificado

---

## 🚀 Roadmap de Implementação

### Sprint 0: Preparação (2 dias)
**Esforço:** 12-15 horas
- [ ] Backend: Criar 2 endpoints novos
- [ ] Frontend: Setup estrutura de pastas
- [ ] Frontend: Criar design tokens

---

### Sprint 1: Dashboard + Componentes Base (Semana 1)
**Esforço:** 19-26 horas
- [ ] BottomNavigation
- [ ] MobileHeader
- [ ] MonthScrollPicker
- [ ] YTDToggle
- [ ] Dashboard mobile
- [ ] CategoryExpensesMobile

---

### Sprint 2: Transações + Upload (Semana 2)
**Esforço:** 8-11 horas
- [ ] Melhorias Transações mobile
- [ ] Upload mobile (validação)
- [ ] Testes E2E

---

### Sprint 3: Metas (Semana 3)
**Esforço:** 25-34 horas
- [ ] TrackerCard
- [ ] DonutChart
- [ ] CategoryRowInline
- [ ] BudgetEditBottomSheet
- [ ] Tela Budget mobile (visualização + edição)
- [ ] Integração copy-to-year

---

### Sprint 4: Profile + Polish (Semana 4)
**Esforço:** 24-28 horas
- [ ] Profile mobile
- [ ] GrupoBreakdownBottomSheet
- [ ] Integração grupo-breakdown
- [ ] Otimizações de performance
- [ ] Testes de acessibilidade

---

**Total Geral:** 88-114 horas (11-14 dias úteis)

---

## 🎯 Decisões Arquiteturais Chave

### 1. Por que MonthScrollPicker em vez de Dropdown?
**Decisão:** ✅ Scroll horizontal

**Motivo:**
- Dropdown: 4 ações (tocar, abrir, scrollar, selecionar)
- Scroll: 1 ação (swipe)
- **Economia: 75% menos interações**

**Persona Carlos:** "Acesso rápido no Uber, sem abrir menus"

---

### 2. Por que YTD Toggle em vez de Sempre Mostrar Ambos?
**Decisão:** ✅ Toggle [Mês] / [YTD]

**Motivo:**
- Tela mobile pequena (360-430px)
- Toggle: usuário escolhe contexto (mês ou ano)
- Backend já suporta (`ytd=true`)

**Persona Ana:** "Quero saber se estou no caminho no ano todo"

---

### 3. Por que Bottom Sheet em vez de Modal?
**Decisão:** ✅ Bottom Sheet

**Motivo:**
- Bottom Sheet: Alcance natural do polegar
- Modal: Centro da tela (dificulta alcance)
- Padrão mobile (Material Design, iOS HIG)

---

### 4. Por que Top 5 + Demais?
**Decisão:** ✅ Top 5 + Demais (Dashboard)

**Motivo:**
- Lógica já implementada no desktop
- Top 5 representa ~80% dos gastos (Pareto)
- Evita scroll infinito em tela pequena

**Requisito Solicitado:** "Não precisamos mostrar todos os grupos"

---

## 📞 Contatos e Responsabilidades

| Área | Responsável | Ações | Documentos |
|------|-------------|-------|------------|
| **Product** | Stakeholder | Aprovar PRD, validar UX | SUMMARY.md, PRD.md |
| **Backend** | Dev Backend | Criar 2 endpoints (5-7h) | API_SPEC.md |
| **Frontend** | Dev Frontend | Implementar componentes (80-100h) | TECH_SPEC.md, COMPONENTS.md |
| **Design** | Designer | Validar Design System | STYLE_GUIDE.md |
| **QA** | Tester | Testes E2E, a11y, cross-browser | TECH_SPEC.md Seção 6 |

---

## 🔗 Links Externos

### Referências de Design
- [WCAG 2.1 AA Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design - Mobile](https://m3.material.io/)
- [iOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

### Stack Técnico
- [Next.js 14 Docs](https://nextjs.org/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Shadcn/ui](https://ui.shadcn.com/)
- [Recharts](https://recharts.org/)

---

## 🚨 Gaps Críticos

| Gap | Impacto | Prioridade | Sprint | Status |
|-----|---------|------------|--------|--------|
| **Estrutura de Metas (budget_planning)** | 🔴 CRÍTICO | 🔴 Alta | Sprint 0 | ⚠️ Identificado |
| **Paths de Deploy (DEPLOY_MAP)** | 🔴 CRÍTICO | 🔴 Alta | Sprint 0 | ✅ Documentado |
| POST /budget/planning (GET) | 🔴 Alto | 🔴 Alta | Sprint 0 | ❌ Criar |
| POST /budget/planning/bulk-upsert | 🔴 Alto | 🔴 Alta | Sprint 0 | ❌ Criar |
| POST /budget/geral/copy-to-year | 🔴 Alto (Persona Ana precisa) | 🔴 Alta | Sprint 0 | ❌ Criar |
| GET /transactions/grupo-breakdown | 🟡 Médio (drill-down nice-to-have) | 🟡 Média | Sprint 0 | ❌ Criar |
| MonthScrollPicker | 🔴 Alto (UX melhor que dropdown) | 🔴 Alta | Sprint 1 | - |
| YTDToggle | 🟡 Médio (visão anual) | 🟡 Média | Sprint 1 | - |
| TrackerCard | 🔴 Alto (Design System) | 🔴 Alta | Sprint 3 | - |

**Conclusão:** 2 problemas críticos identificados e documentados:
1. ⚠️ **Estrutura de metas** - PRD assumiu `budget_geral`, mas deve usar `budget_planning`
2. ✅ **Deploy** - DEPLOY_MAP.md criado com todos os paths absolutos

**Ação imediata:** Ler EXECUTIVE_SUMMARY.md e BUDGET_STRUCTURE_ANALYSIS.md

---

## 📝 Histórico de Alterações

| Data | Versão | Mudanças | Autor |
|------|--------|----------|-------|
| 31/01/2026 | 1.0 | Criação da documentação completa | Product Team |
| 31/01/2026 | 1.1 | ⚠️ Identificação de 2 problemas críticos + 3 docs novos | Tech Team |

**Documentos criados (V1.0):**
- ✅ PRD.md (4500+ linhas)
- ✅ STYLE_GUIDE.md (760 linhas)
- ✅ SUMMARY.md (550 linhas)
- ✅ FACTIBILIDADE.md (800 linhas)
- ✅ ANALISE_STAKEHOLDER.md (700 linhas)
- ✅ ANALISE_NOVA_TELA_METAS.md (710 linhas)
- ✅ TECH_SPEC.md (1000 linhas)
- ✅ API_SPEC.md (700 linhas)
- ✅ COMPONENTS.md (750 linhas)
- ✅ TESTING_STRATEGY.md (450 linhas)
- ✅ IMPLEMENTATION_GUIDE.md (800 linhas)
- ✅ BACKEND_VALIDATION.md (650 linhas)
- ✅ Design tokens (3 arquivos TypeScript)
- ✅ Código completo de 9 componentes

**Documentos críticos adicionados (V1.1):**
- 🆕 DEPLOY_MAP.md (350 linhas) - Paths absolutos e workflow deploy
- 🆕 BUDGET_STRUCTURE_ANALYSIS.md (600 linhas) - Análise estrutura de metas
- 🆕 INFRASTRUCTURE.md (850 linhas) - Infraestrutura (dev SQLite + prod PostgreSQL)
- 🆕 EXECUTIVE_SUMMARY.md (250 linhas) - Resumo executivo correções

**Problemas identificados e corrigidos (V1.1):**
1. ⚠️ PRD/API_SPEC assumiu `budget_geral`, corrected to `budget_planning` ✅
2. ⚠️ Tech spec não tinha paths absolutos de deploy → DEPLOY_MAP.md criado ✅
3. ⚠️ Faltava documentação de infraestrutura → INFRASTRUCTURE.md criado ✅

---

## 🔄 Próximos Passos

### Imediato (HOJE - CRÍTICO)

1. ✅ Revisar documentação com time
2. ⚠️ **LER EXECUTIVE_SUMMARY.md** - 2 problemas críticos identificados
3. ⚠️ **LER BUDGET_STRUCTURE_ANALYSIS.md** - Estrutura de metas incorreta
4. ⚠️ **LER DEPLOY_MAP.md** - Paths absolutos para deploy
5. ⏳ Atualizar API_SPEC.md (substituir `/budget/geral` por `/budget/planning`)
6. ⏳ Aprovar roadmap corrigido (4 semanas)

### Sprint 0 (Preparação - URGENTE)

1. [ ] Criar branch `feature/mobile-v1`
2. [ ] **Criar endpoints `/budget/planning` (GET + POST bulk-upsert)** - 5-7h
3. [ ] Implementar `/budget/geral/copy-to-year` - 3-4h
4. [ ] Implementar `/transactions/grupo-breakdown` - 3-4h
5. [ ] Setup estrutura frontend (ver DEPLOY_MAP.md)
6. [ ] Configurar design tokens

**Total Sprint 0:** ~15-20 horas (2-3 dias)

### Sprint 1 (Semana 1)

Ver Roadmap acima

---

**Fim do INDEX - Mobile Experience V1.0**

**Data:** 31/01/2026  
**Versão:** 1.1  
**Status:** ⚠️ 2 Problemas Críticos Identificados + Soluções Documentadas  
**Próxima revisão:** Após correção de API_SPEC.md

---

**🚨 AÇÃO IMEDIATA:**
1. Ler [EXECUTIVE_SUMMARY.md](./02-TECH_SPEC/EXECUTIVE_SUMMARY.md) (10 min)
2. Ler [BUDGET_STRUCTURE_ANALYSIS.md](./02-TECH_SPEC/BUDGET_STRUCTURE_ANALYSIS.md) (25 min)
3. Ler [INFRASTRUCTURE.md](./02-TECH_SPEC/INFRASTRUCTURE.md) (35 min)
4. Ler [DEPLOY_MAP.md](./02-TECH_SPEC/DEPLOY_MAP.md) (15 min)

**Total:** ~85 min para entender infraestrutura, problemas e soluções

**IMPORTANTE:** Esta documentação garante que todas as informações críticas estão consolidadas e acessíveis. SEMPRE consulte antes de implementar!
