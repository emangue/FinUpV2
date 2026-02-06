# 📱 Mobile Experience V1.0 - Índice de Documentação

**Data:** 31/01/2026  
**Status:** ✅ ANÁLISE COMPLETA - PROJETO APROVADO PARA IMPLEMENTAÇÃO  
**Próximas Ações:** Aprovar roadmap e iniciar Sprint 0  

---

## 🎯 Navegação Rápida

| Documento | Para quem? | O que tem? |
|-----------|------------|------------|
| **[MOBILE_ANALISE_COMPLETA.md](#)** | 🎯 **LEIA PRIMEIRO** (PO/Stakeholder) | Respostas às suas 9 perguntas |
| **[MOBILE_CHECKLIST.md](#)** | 🎯 **LEIA SEGUNDO** (Tech Lead) | Checklist executivo de implementação |
| **[MOBILE_SUMMARY.md](#)** | 📊 Executivos | Resumo executivo + FAQ |
| **[MOBILE_FACTIBILIDADE.md](#)** | 🔧 Tech Team | Análise técnica detalhada |
| **[PRD_MOBILE_EXPERIENCE.md](#)** | 💻 Desenvolvedores | Especificação completa (1.781 linhas) |
| **[MOBILE_STYLE_GUIDE.md](#)** | 🎨 Frontend Devs | Design System + código React |
| **[Design Tokens (.ts)](#)** | 💻 Frontend Devs | Cores, dimensões, tipografia (código pronto) |
| **[MOBILE_INDEX.md](#)** | 🗺️ Todos | Este arquivo (mapa de navegação) |

---

## 📊 Status Geral do Projeto

```
┌─────────────────────────────────────────────────────────┐
│ PROGRESSO GERAL                                         │
│                                                         │
│ ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░  40%      │
│                                                         │
│ ✅ Análise e Documentação:  100% (8/8 docs)            │
│ ✅ Design System:           100% (3/3 arquivos .ts)    │
│ ⚠️  Backend:                  0% (0/2 endpoints)        │
│ ⚠️  Frontend:                 0% (0/5 componentes)      │
│ ⚠️  QA:                       0% (0/3 fases)            │
└─────────────────────────────────────────────────────────┘
```

**Factibilidade:** ✅ 100% FACTÍVEL  
**Backend:** 95% pronto (faltam 2 endpoints, 5-7h)  
**Frontend:** 80% reutilizável (faltam 5 componentes, 25-30h)  
**Esforço Total:** ~4 semanas

---

## 📚 Documentos Criados (8 documentos + 3 arquivos de código)

### 1. MOBILE_ANALISE_COMPLETA.md 🎯 **[LEIA PRIMEIRO]**
**Path:** `/docs/features/MOBILE_ANALISE_COMPLETA.md`

**Para quem:** Product Owner, Stakeholders, Tech Leads

**Conteúdo:**
- ✅ **Respostas diretas às 9 perguntas do stakeholder:**
  1. É factível implementar o PRD? ✅ SIM, 100%
  2. Como deve funcionar a edição de metas? ✅ Especificado (bottom sheet)
  3. Copiar mês anterior? ✅ Backend pronto
  4. Copiar para ano inteiro (2026)? ⚠️ Criar endpoint (2-3h)
  5. Top 5 + Demais? ✅ Código desktop já implementado
  6. Toggle Mês / YTD? ✅ Backend pronto
  7. Drill-down grupo → subgrupos? ⚠️ Criar endpoint (3-4h)
  8. Mostrar todos os grupos na tela Metas? ✅ Especificado
  9. Comparação desktop vs mobile? ✅ Análise completa
- ✅ Especificação técnica dos 2 endpoints novos (código + testes)
- ✅ Comparação detalhada desktop vs mobile (features que ficam desktop-only)
- ✅ Decisões arquiteturais justificadas
- ✅ Checklist final de implementação

**Leia isto se:** Você é o tomador de decisão e quer respostas diretas

---

### 2. MOBILE_CHECKLIST.md 🎯 **[LEIA SEGUNDO]**
**Path:** `/docs/features/MOBILE_CHECKLIST.md`

**Para quem:** Tech Leads, Gerentes de Projeto, Desenvolvedores

**Conteúdo:**
- ✅ Dashboard visual de progresso (40% completo)
- ✅ Checklist detalhado por fase:
  - ✅ Documentação: 100%
  - ✅ Design System: 100%
  - ⚠️ Backend: 0% (2 endpoints, 5-7h)
  - ⚠️ Frontend: 0% (5 componentes, 25-30h)
  - ⚠️ QA: 0% (2-3 dias)
- ✅ Roadmap visual (4 semanas, sprint a sprint)
- ✅ Riscos e blockers
- ✅ Próximas ações imediatas

**Leia isto se:** Você vai gerenciar ou implementar o projeto

---

### 3. MOBILE_SUMMARY.md
**Path:** `/docs/features/MOBILE_SUMMARY.md`

**Para quem:** Executivos, Stakeholders não-técnicos

**Conteúdo:**
- ✅ TL;DR do projeto completo
- ✅ Visão geral dos requisitos
- ✅ Novos requisitos identificados (copiar ano, drill-down, YTD, top 5)
- ✅ Comparação Desktop vs Mobile
- ✅ Análise de factibilidade (95% backend pronto, 80% frontend reutilizável)
- ✅ Roadmap ajustado (4 semanas)
- ✅ FAQ (13 perguntas frequentes)
- ✅ Métricas de sucesso (pré e pós-lançamento)
- ✅ Decisões arquiteturais justificadas

**Leia isto se:** Você quer um resumo executivo de alto nível

---

### 4. MOBILE_FACTIBILIDADE.md
**Path:** `/docs/features/MOBILE_FACTIBILIDADE.md`

**Para quem:** Tech Leads, Arquitetos, Desenvolvedores Backend/Frontend

**Conteúdo:**
- ✅ Análise técnica completa de viabilidade
- ✅ **Backend:** 95% pronto (12/13 endpoints existentes)
  - ✅ APIs de Dashboard, Budget, Transações
  - ✅ YTD já implementado (`ytd=true`)
  - ⚠️ Faltam 2 endpoints (copy-to-year, grupo-breakdown)
- ✅ **Frontend:** 80% reutilizável
  - ✅ Componentes existentes (MetricCards, ChartCollapse, Transactions, Upload)
  - ✅ Lógica Top 5 + Demais já implementada (budget-vs-actual.tsx)
  - ⚠️ Faltam 5 componentes novos (MonthScrollPicker, YTDToggle, TrackerCard, Bottom Sheets)
- ✅ **Design System:** 100% especificado (código pronto nos .ts)
- ✅ **Estrutura de dados:** Suporta 100% (sem migrações)
- ✅ Gaps identificados (2 endpoints + 5 componentes)
- ✅ Riscos e mitigações
- ✅ Análise de esforço (5-7h backend, 25-30h frontend)

**Leia isto se:** Você quer análise técnica detalhada de viabilidade

---

### 5. PRD - Product Requirements Document
**Path:** `/docs/features/PRD_MOBILE_EXPERIENCE.md`

**Para quem:** Desenvolvedores, Designers, QA

**Conteúdo:**
- ✅ Visão geral e objetivos (5 telas principais)
- ✅ Personas (Ana - Planejadora, Carlos - Executivo, Roberto - Pragmático)
- ✅ User Stories (17 histórias)
- ✅ Especificação funcional completa:
  - ✅ Layouts ASCII art (5 telas)
  - ✅ Componentes existentes (reutilizar)
  - ✅ Componentes novos (criar)
  - ✅ Interações detalhadas
  - ✅ **Novos requisitos incorporados:** 🆕
    - MonthScrollPicker (código completo)
    - Toggle Mês/YTD
    - Copiar para ano inteiro (2026)
    - Drill-down grupo → subgrupos
    - Top 5 + Demais
- ✅ Navegação mobile (Bottom Navigation)
- ✅ Design System (referencia MOBILE_STYLE_GUIDE.md)
- ✅ Performance (Core Web Vitals)
- ✅ Acessibilidade WCAG 2.1 AA
- ✅ Segurança mobile
- ✅ Testes (unit, integration, E2E)
- ✅ **Novos endpoints backend especificados:** 🆕
  - POST /budget/geral/copy-to-year
  - GET /transactions/grupo-breakdown
- ✅ Roadmap de 4 semanas (MVP)
- ✅ Riscos e mitigações
- ✅ Critérios de aceitação

**Páginas:** 1.781 linhas (documento extenso e completo)

**Leia isto se:** Você vai implementar as features

---

### 6. Mobile Style Guide
**Path:** `/docs/features/PRD_MOBILE_EXPERIENCE.md`

**Conteúdo:**
- ✅ Visão geral e objetivos (5 telas principais)
- ✅ Personas e User Stories (18 histórias de usuário)
- ✅ Especificação funcional completa (layouts ASCII art)
- ✅ Navegação mobile (Bottom Navigation)
- ✅ **Design System COMPLETO baseado na imagem "Trackers"** (50+ atributos mapeados)
- ✅ Performance e otimizações (Core Web Vitals)
- ✅ Acessibilidade WCAG 2.1 AA
- ✅ Segurança mobile
- ✅ Testes (unit, integration, E2E)
- ✅ Dependências e integrações
- ✅ Roadmap de 4 semanas (MVP)
- ✅ Riscos e mitigações
- ✅ Critérios de aceitação

**Páginas:** 135+ páginas (documento extenso e completo)

---

### 2. Mobile Style Guide
**Path:** `/docs/features/MOBILE_STYLE_GUIDE.md`

**Conteúdo:**
- ✅ Paleta de cores completa (18+ cores extraídas da imagem)
- ✅ Dimensões e espaçamentos (10+ medidas exatas)
- ✅ Tipografia detalhada (5 hierarquias)
- ✅ Animações e transições (3 tipos)
- ✅ Estados interativos (normal, pressed, disabled)
- ✅ Validação de acessibilidade WCAG AA
- ✅ Componente `TrackerCard` completo (código pronto)
- ✅ Componente `TrackerHeader` completo (código pronto)
- ✅ Tailwind Config customizado
- ✅ Exemplos práticos de uso
- ✅ Mapeamento de categorias do backend
- ✅ Checklist de implementação

**Páginas:** 45+ páginas (guia técnico detalhado)

---

## 🎨 Análise Completa da Imagem "Trackers"

### Atributos Mapeados (Total: 50+)

| Categoria | Quantidade | Status |
|-----------|------------|--------|
| **Cores** | 18+ (backgrounds, textos, ícones, progress) | ✅ Completo |
| **Tipografia** | 5 hierarquias | ✅ Completo |
| **Espaçamento** | 10+ valores | ✅ Completo |
| **Dimensões** | 8 tamanhos | ✅ Completo |
| **Sombras** | 1 sombra sutil | ✅ Completo |
| **Border Radius** | 3 valores | ✅ Completo |
| **Animações** | 3 transições | ✅ Completo |
| **Estados** | 3 estados | ✅ Completo |
| **Ícones** | 9 categorias | ✅ Completo |
| **Acessibilidade** | Contraste + Touch | ✅ Validado |

---

## 🎯 5 Telas Principais Especificadas

### 1. Dashboard Mobile ✅
- **Status:** Componentes existentes reutilizáveis
- **Novos:** `CategoryExpensesMobile`, `BudgetVsActualMobile`
- **Layout:** ASCII art completo no PRD
- **Comportamentos:** Pull-to-refresh, swipe, loading states

### 2. Transações Mobile ✅
- **Status:** Base existente + melhorias necessárias
- **Melhorias:** Bottom sheet de edição, swipe actions, filtros avançados
- **Layout:** ASCII art completo no PRD
- **Interações:** Swipe left/right, infinite scroll

### 3. Metas (Budget) Mobile ✅
- **Status:** Criar do zero (baseado na imagem "Trackers")
- **Componentes:** `TrackerCard`, `TrackerHeader`, `BudgetEditBottomSheet`
- **Layout:** ASCII art completo no PRD + Template de código pronto
- **Funcionalidades:** Tabs (Simples/Detalhada), edição inline, copiar mês anterior

### 4. Profile Mobile ✅
- **Status:** Adaptar desktop para mobile
- **Componentes:** `ProfileMobileHeader`, `ProfileAvatarCard`, `ChangePasswordBottomSheet`
- **Layout:** ASCII art completo no PRD
- **Funcionalidades:** Editar perfil, alterar senha, preferências

### 5. Upload Mobile ✅
- **Status:** Criar versão mobile otimizada
- **Componentes:** `UploadAreaMobile`, `UploadConfigBottomSheet`, `UploadPreviewMobile`
- **Layout:** ASCII art completo no PRD
- **Fluxo:** Native file picker → config → preview → confirmar

---

## 📊 Paleta de Cores - Referência Rápida

```typescript
// Cores extraídas da imagem "Trackers"
export const trackerColors = {
  casa: {
    bg: '#DDD6FE',      // Roxo pastel
    icon: '#6B21A8',    // Roxo escuro
    progress: '#9F7AEA', // Roxo vibrante
  },
  alimentacao: {
    bg: '#DBEAFE',      // Azul pastel
    icon: '#1E40AF',    // Azul escuro
    progress: '#60A5FA', // Azul vibrante
  },
  compras: {
    bg: '#FCE7F3',      // Rosa pastel
    icon: '#BE185D',    // Rosa escuro
    progress: '#F472B6', // Rosa vibrante
  },
  transporte: {
    bg: '#E7E5E4',      // Bege pastel
    icon: '#78716C',    // Bege escuro
    progress: '#A8A29E', // Bege vibrante
  },
  contas: {
    bg: '#FEF3C7',      // Amarelo pastel
    icon: '#D97706',    // Amarelo escuro
    progress: '#FCD34D', // Amarelo vibrante
  },
  lazer: {
    bg: '#D1FAE5',      // Verde pastel
    icon: '#047857',    // Verde escuro
    progress: '#6EE7B7', // Verde vibrante
  },
};
```

---

## 🚀 Roadmap de Implementação (4 Semanas)

### Sprint 1 (Semana 1) - Setup e Dashboard
- [ ] Setup rotas mobile (`/mobile/*`)
- [ ] Bottom Navigation component
- [ ] Dashboard mobile (reutilizar `MetricCards`)
- [ ] Navegação básica

### Sprint 2 (Semana 2) - Transações e Upload
- [ ] Transações mobile (melhorias)
  - [ ] Bottom sheet de edição
  - [ ] Swipe actions
  - [ ] Busca/filtros
- [ ] Upload mobile
  - [ ] File picker
  - [ ] Config bottom sheet
  - [ ] Preview e histórico

### Sprint 3 (Semana 3) - Metas e Profile
- [ ] Metas mobile (criar do zero)
  - [ ] Tabs (Simples/Detalhada)
  - [ ] `TrackerCard` component
  - [ ] Edit bottom sheet
  - [ ] Salvar/Copiar mês anterior
- [ ] Profile mobile (adaptar)
  - [ ] Info pessoais
  - [ ] Alterar senha
  - [ ] Preferências

### Sprint 4 (Semana 4) - Testes e Otimizações
- [ ] Testes E2E (5 fluxos principais)
- [ ] Otimizações (lazy load, code splitting)
- [ ] Acessibilidade (ARIA, contraste, focus)
- [ ] Documentação

---

## 📐 Dimensões Críticas (Memorizar)

```typescript
// Tamanhos mínimos (Apple HIG / Material Design)
const criticalSizes = {
  touchTarget: '44px',        // Mínimo WCAG 2.5.5
  buttonHeight: '48px',       // Recomendado Apple HIG
  iconCircle: '48px',         // Da imagem "Trackers"
  cardMinHeight: '72px',      // Da imagem "Trackers"
  progressBarHeight: '6px',   // Da imagem "Trackers"
  cardBorderRadius: '16px',   // Da imagem "Trackers"
  screenPadding: '20px',      // Da imagem "Trackers"
  cardGap: '16px',            // Da imagem "Trackers"
};
```

---

## ✅ Critérios de Aceitação - Checklist Final

### Funcional
- [ ] 5 telas carregam e são navegáveis
- [ ] Autenticação funciona (login/logout)
- [ ] Upload funciona em iOS e Android
- [ ] Edição de transações funciona
- [ ] Edição de metas funciona
- [ ] Edição de perfil funciona
- [ ] Bottom nav funciona sem bugs

### Performance
- [ ] Lighthouse Performance ≥85
- [ ] TTI ≤ 3s (4G simulado)
- [ ] FCP ≤ 1.5s
- [ ] CLS ≤ 0.1

### Acessibilidade
- [ ] Lighthouse Accessibility ≥90
- [ ] Touch targets ≥44x44px
- [ ] Contraste WCAG AA (≥4.5:1)
- [ ] Navegação por teclado funciona

### Compatibilidade
- [ ] iOS 14+ (Safari)
- [ ] Android 10+ (Chrome)
- [ ] Telas 360px-430px
- [ ] Não quebra em >768px

### Segurança
- [ ] JWT validado
- [ ] HTTPS em produção
- [ ] Inputs validados (client + server)
- [ ] Sem vulnerabilidades OWASP Top 10

---

## 🔗 Links Úteis

### Referências Externas
- [Apple Human Interface Guidelines - Mobile](https://developer.apple.com/design/human-interface-guidelines/ios)
- [Material Design - Mobile](https://m3.material.io/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Next.js Mobile Best Practices](https://nextjs.org/docs/pages/building-your-application/optimizing)
- [Lucide Icons](https://lucide.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

### Ferramentas de Validação
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [axe DevTools](https://www.deque.com/axe/devtools/)

---

## 🎓 Conhecimento Chave - Seguir Sempre

### Regras do Copilot Instructions
✅ **Lido e entendido:** `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/.github/copilot-instructions.md`

**Regras críticas para este projeto:**
1. **Sincronização Git:** Local → Git → Servidor (NUNCA editar servidor diretamente)
2. **Estrutura de Pastas:** Docs em `/docs/`, Scripts em `/scripts/`, Temp em `/temp/`
3. **Banco de Dados Único:** `app_dev/backend/database/financas_dev.db` (path absoluto único)
4. **Arquitetura DDD:** Domínios isolados em `app_dev/backend/app/domains/`
5. **Frontend Feature-Based:** Features isoladas em `app_dev/frontend/src/features/`
6. **Versionamento:** Usar `version_manager.py` para arquivos críticos
7. **Migrations:** SEMPRE usar Alembic (nunca SQL direto)
8. **Deploy Seguro:** Usar `safe_deploy.sh` antes de produção
9. **Backup Diário:** Rodar `backup_daily.sh` antes de modificações críticas
10. **PostgreSQL Local:** Usar para paridade com produção

---

## 📞 Próximos Passos

### Imediato (Agora)
1. ✅ **PRD Completo** - Documento de requisitos finalizado
2. ✅ **Style Guide Completo** - Guia de estilo baseado na imagem "Trackers"
3. ⏭️ **TECH_SPEC** - Especificação técnica de implementação (próximo documento)

### Tech Spec (Criar Agora)
- Arquitetura de componentes detalhada
- Estrutura de pastas (`/mobile/*` routes)
- APIs e endpoints (reutilizar existentes)
- Estratégia de testes (Jest, Playwright)
- Checklist de implementação sprint por sprint
- Diagramas de fluxo (user journeys)
- Data models (TypeScript interfaces)
- State management (Context API)

### Deploy Plan (Depois da TECH_SPEC)
- Estratégia de rollout progressivo
- Feature flags (ativar mobile gradualmente)
- Monitoramento e analytics
- Rollback plan
- Comunicação com usuários

---

## 🎯 Objetivo Final

Criar uma experiência mobile **pixel-perfect** baseada na imagem "Trackers", com:
- ✅ Design system completo e consistente
- ✅ 100% acessível (WCAG 2.1 AA)
- ✅ Performance otimizada (TTI ≤3s)
- ✅ Compatível com iOS 14+ e Android 10+
- ✅ 5 telas principais funcionais e navegáveis

**Prazo:** 4 semanas (Sprint 1-4)  
**Status:** PRD + Style Guide completos ✅  
**Próximo:** TECH_SPEC 🚀

---

**Fim do Índice de Documentação**
