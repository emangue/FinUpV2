# 📊 Feature: Sistema de Metas Financeiras (Wallet)

**Status:** 🟡 Fase 1 - PRD e TECH SPEC Completos  
**Versão:** 1.0  
**Última Atualização:** 02/02/2026

---

## 🎯 Quick Start - O que é esta Feature?

Sistema de **planejamento financeiro** que permite usuários:
- ✅ Definir **meta de economia mensal** (ex: R$ 1.000/mês)
- ✅ Atribuir **budgets a categorias** (ex: Alimentação R$ 600/mês)
- ✅ Visualizar **progresso em tempo real** (gráfico donut + barras)
- ✅ Receber **alertas ao atingir 80% do budget**

---

## 📂 Estrutura de Documentação

```
docs/features/metas-wallet/
├── README.md (você está aqui)
├── INDEX.md (índice navegável)
├── CHANGELOG.md (histórico de mudanças)
│
├── 01-PRD/
│   └── PRD.md (3.500 linhas - requisitos completos)
│
├── 02-TECH_SPEC/
│   └── TECH_SPEC.md (5.000 linhas - código copy-paste ready)
│
└── 03-DEPLOY/
    └── (será criado após implementação)
```

---

## 🚀 Status do Projeto

### ✅ Fase 1 - PRD (Completo)
- [x] Contexto e problema definido
- [x] Objetivos SMART
- [x] User stories (5 stories principais)
- [x] Wireframes e mockup
- [x] Requisitos funcionais (8 RFs)
- [ ] **Aprovação stakeholder** (BLOQUEANTE!)

### ✅ Fase 2 - TECH SPEC (Completo)
- [x] Database schema (3 tabelas novas)
- [x] Migrations Alembic
- [x] Backend models (SQLAlchemy)
- [x] Backend schemas (Pydantic)
- [x] Backend service (lógica de negócio)
- [x] Backend router (APIs)
- [x] Frontend componente (React/TypeScript)
- [x] DAG (ordem de implementação)
- [x] Testing strategy

### ⏳ Fase 3 - SPRINT (Aguardando)
- [ ] Sprint 1: Backend (2 semanas)
- [ ] Sprint 2: Frontend (2 semanas)
- [ ] Sprint 3: Testes + Bug fixes (2 semanas)

### ⏳ Fase 4 - DEPLOY (Aguardando)
- [ ] Deploy staging
- [ ] QA completo
- [ ] Deploy produção
- [ ] Monitoring

### ⏳ Fase 5 - POST-MORTEM (Aguardando)
- [ ] Retrospectiva (48h após deploy)
- [ ] Ações de melhoria

---

## 📖 Como Navegar Esta Documentação

### 1️⃣ **Para Stakeholders (Product Owners, Gerentes)**
- Leia: [PRD.md](./01-PRD/PRD.md)
- Seções importantes:
  - **Seção 2:** Objetivos SMART e KPIs
  - **Seção 3:** User Stories (o que usuário pode fazer)
  - **Seção 4:** Wireframes (como vai parecer)
  - **Seção 9:** Critérios de sucesso

### 2️⃣ **Para Desenvolvedores (Backend)**
- Leia: [TECH_SPEC.md](./02-TECH_SPEC/TECH_SPEC.md)
- Seções importantes:
  - **Seção 2:** Database Schema (copiar SQL)
  - **Seção 3:** Models SQLAlchemy (copiar Python)
  - **Seção 4:** Schemas Pydantic (copiar Python)
  - **Seção 5:** Router FastAPI (copiar Python)
  - **Seção 7:** DAG (ordem de implementação)

### 3️⃣ **Para Desenvolvedores (Frontend)**
- Leia: [TECH_SPEC.md](./02-TECH_SPEC/TECH_SPEC.md)
- Seções importantes:
  - **Seção 6:** Componente React (copiar TSX)
  - **Seção 7:** DAG (dependências)
  - **Seção 9:** Responsividade e Acessibilidade

### 4️⃣ **Para QA (Testers)**
- Leia: [TECH_SPEC.md](./02-TECH_SPEC/TECH_SPEC.md)
- Seções importantes:
  - **Seção 8:** Testing Strategy (Playwright tests)
  - **PRD Seção 3.2:** User Stories (casos de teste)
  - **PRD Seção 9:** Acceptance Criteria

---

## 🎨 Mockup Visual (Referência)

**Tela Principal:** Wallet (Mobile-first)

```
┌──────────────────────────────────┐
│   👤 Wallet         🔍 📅        │
├──────────────────────────────────┤
│                                  │
│   [Botão: Month ▼]               │
│                                  │
│      ╭─────────────╮             │
│     ╱   February   ╲            │
│    │   2026         │           │
│    │                 │           │
│    │   $ 327.50      │  ◀─ Economia
│    │   out of $1000  │           │
│    │                 │           │
│     ╲───────────────╱            │
│      ╰─────────────╯             │
│   [Gráfico Donut com cores]      │
│                                  │
│   ┌──────────┬──────────┐       │
│   │ Savings  │ Expenses │ ◀─ Tabs
│   └──────────┴──────────┘       │
│                                  │
│   🏠 Home            R$ 120/300  │
│   ▓▓▓▓▓▓▓░░░░ 43%               │
│                                  │
│   🍴 Alimentação     R$ 250/600 │
│   ▓▓▓▓░░░░░░ 42%                 │
│                                  │
│   🚗 Transporte      R$ 80/200  │
│   ▓▓▓░░░░░░░ 40%                 │
│                                  │
└──────────────────────────────────┘
```

**Paleta de Cores:**
- 🟢 Emerald-500 (#10B981) - Economia/sucesso
- 🔵 Blue-500 (#3B82F6) - Categoria Home
- 🟣 Purple-500 (#A855F7) - Categoria Saúde
- 🟠 Orange-500 (#F97316) - Categoria Compras
- 🔴 Red-500 (#EF4444) - Categoria Transporte / Alerta

---

## 📊 KPIs Esperados

| Métrica | Baseline | Meta (3 meses) |
|---------|----------|----------------|
| Usuários com meta ativa | 0% | 60% |
| Taxa cumprimento metas | N/A | 40% |
| Engajamento (aberturas/semana) | 3.2 | 5.5 |
| Retenção M1 | 72% | 85% |
| NPS | 48 | 65 |

---

## 🛠️ Stack Tecnológico

**Frontend:**
- Next.js 14 (App Router)
- React 18 + TypeScript 5
- Tailwind CSS 3
- Recharts 2.x (gráficos)
- Lucide Icons

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy (ORM)
- PostgreSQL 16 (produção)
- Alembic (migrations)

**Testes:**
- Pytest (backend)
- Playwright (E2E)

---

## 📅 Timeline Estimado

**Total:** 6 semanas (148h)

- **Semanas 1-2:** Backend (40h)
  - Database + Models + Service + Router

- **Semanas 3-4:** Frontend (60h)
  - Componente Wallet + Gráfico + Lista

- **Semanas 5-6:** Testes + Deploy (40h)
  - Testes E2E + Bug fixes + Deploy prod

---

## 🚨 Riscos Críticos

1. **Recharts lento em mobile** (Probabilidade: Média, Impacto: Alto)
   - Mitigação: Lazy load + memoização

2. **Cálculo incorreto de economia** (Probabilidade: Baixa, Impacto: Crítico)
   - Mitigação: Testes unitários extensivos

3. **Baixa adoção (<40%)** (Probabilidade: Média, Impacto: Alto)
   - Mitigação: Onboarding forçado + tutorial

---

## 📚 Referências Externas

**Benchmarks:**
- [Nubank Goals](https://nubank.com.br) - Gamificação
- [GuiaBolso Orçamento](https://guiabolso.com.br) - Budgets por categoria
- [Organizze](https://organizze.com.br) - Planejamento mensal

**Design:**
- [Mockup original](../../../app_dev/frontend/src/app/wallet/mockup-gemini.tsx)
- [Recharts Docs](https://recharts.org/en-US/examples/PieChartWithPaddingAngle)

---

## 👥 Time

- **Backend Developer:** 40h
- **Frontend Developer:** 60h
- **Designer:** 16h (mockups finais)
- **QA:** 24h (testes + validação)
- **Product Manager:** 8h (aprovações)

**Total:** 148h (~4 semanas-homem)

---

## 🔗 Links Rápidos

- 📋 [PRD Completo](./01-PRD/PRD.md) (requisitos de negócio)
- 🔧 [TECH SPEC Completo](./02-TECH_SPEC/TECH_SPEC.md) (código pronto)
- 📑 [INDEX Navegável](./INDEX.md) (busca por seção)
- 🎯 [WoW - Processo](../../WOW.md) (metodologia)

---

## ✅ Próximos Passos

### **Aguardando Aprovação do PRD:**

**Stakeholder deve:**
1. Ler [PRD.md](./01-PRD/PRD.md) completo
2. Validar objetivos de negócio (Seção 2)
3. Aprovar user stories (Seção 3)
4. Aprovar wireframes (Seção 4)
5. **Assinar aprovação** (PRD Seção 14)

**⚠️ Desenvolvimento só pode começar após aprovação!**

---

### **Após Aprovação:**

1. **Backend Team:**
   - Começar pelo DAG Item #1 (Database)
   - Seguir ordem do TECH_SPEC Seção 7

2. **Frontend Team:**
   - Aguardar APIs prontas (DAG Item #5)
   - Começar estrutura de página (DAG Item #6)

3. **QA Team:**
   - Preparar casos de teste (Playwright)
   - Validar acceptance criteria do PRD

---

## 📞 Contato

**Dúvidas sobre esta feature?**
- Product Owner: [Nome]
- Tech Lead: [Nome]
- Designer: [Nome]

---

**Criado com ❤️ usando WoW (Way of Working) v1.0**
