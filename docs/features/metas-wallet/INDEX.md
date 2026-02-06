# 📑 INDEX - Sistema de Metas Financeiras (Wallet)

**Navegação rápida por seção** - Use Ctrl+F para buscar

---

## 🎯 RESUMO EXECUTIVO (1 minuto)

**O que é:** Sistema de planejamento financeiro com metas e budgets  
**Para quem:** Usuários que querem economizar dinheiro mensalmente  
**Problema:** 70% não atingem objetivos de economia (sem planejamento)  
**Solução:** Meta visual + budgets por categoria + alertas em tempo real  
**Esforço:** 6 semanas (148h)  
**Status:** 🟡 Aguardando aprovação do PRD

---

## 📋 PRD (Product Requirements Document)

### Contexto e Problema
- [Situação Atual](./01-PRD/PRD.md#11-situação-atual)
- [Problema de Negócio](./01-PRD/PRD.md#12-problema-de-negócio)
- [Dados e Pesquisa](./01-PRD/PRD.md#13-dados-e-pesquisa)

### Objetivos
- [Objetivos SMART](./01-PRD/PRD.md#21-objetivo-principal)
- [KPIs Mensuráveis](./01-PRD/PRD.md#22-kpis-mensuráveis)
- [Não-Objetivos (Fora do Escopo)](./01-PRD/PRD.md#23-não-objetivos-fora-do-escopo-v1)

### Personas e User Stories
- [Persona: Ana Planejadora](./01-PRD/PRD.md#31-persona-primária---ana-planejadora)
- [US-01: Criar Meta de Economia](./01-PRD/PRD.md#us-01-criar-meta-de-economia-mensal)
- [US-02: Atribuir Budget a Categorias](./01-PRD/PRD.md#us-02-atribuir-budget-a-categorias)
- [US-03: Visualizar Progresso em Tempo Real](./01-PRD/PRD.md#us-03-visualizar-progresso-em-tempo-real)
- [US-04: Receber Alerta de Budget](./01-PRD/PRD.md#us-04-receber-alerta-de-budget)
- [US-05: Alternar entre Savings e Expenses](./01-PRD/PRD.md#us-05-alternar-entre-savings-e-expenses)

### Design
- [Wireframes e Mockups](./01-PRD/PRD.md#41-tela-principal---wallet)
- [Paleta de Cores](./01-PRD/PRD.md#42-mockup-figma-referência)
- [Fluxo de Navegação](./01-PRD/PRD.md#43-fluxo-de-navegação)

### Requisitos
- [Requisitos Funcionais (RF-01 a RF-08)](./01-PRD/PRD.md#51-funcionalidades-core)
- [Requisitos Não-Funcionais](./01-PRD/PRD.md#6-requisitos-não-funcionais)
  - [Performance](./01-PRD/PRD.md#61-performance)
  - [Acessibilidade (WCAG 2.1 AA)](./01-PRD/PRD.md#62-acessibilidade-wcag-21-aa)
  - [Segurança](./01-PRD/PRD.md#63-segurança)

### Especificações Técnicas (Alto Nível)
- [Stack Tecnológico](./01-PRD/PRD.md#71-stack-tecnológico)
- [Novas Tabelas (Schema)](./01-PRD/PRD.md#72-novas-tabelas-schema)
- [APIs Necessárias](./01-PRD/PRD.md#73-apis-necessárias-endpoints)

### Métricas e Analytics
- [Eventos de Tracking](./01-PRD/PRD.md#81-eventos-de-tracking)
- [Dashboards](./01-PRD/PRD.md#82-dashboards-grafanametabase)

### Critérios de Sucesso
- [Definição de Done (DoD)](./01-PRD/PRD.md#91-definição-de-done-dod)
- [Acceptance Criteria Global](./01-PRD/PRD.md#92-acceptance-criteria-global)

### Riscos e Cronograma
- [Riscos Técnicos e de Negócio](./01-PRD/PRD.md#10-riscos-e-mitigações)
- [Timeline (7 semanas)](./01-PRD/PRD.md#111-timeline)
- [Dependências Críticas](./01-PRD/PRD.md#112-dependências-críticas)

### Aprovação
- [Stakeholders e Assinatura](./01-PRD/PRD.md#14-aprovação)

---

## 🔧 TECH SPEC (Technical Specification)

### Arquitetura
- [Diagrama Geral](./02-TECH_SPEC/TECH_SPEC.md#11-diagrama-geral)
- [Decisões Arquiteturais (DA-01 a DA-03)](./02-TECH_SPEC/TECH_SPEC.md#12-decisões-arquiteturais)

### Database
- [Schema SQL Completo](./02-TECH_SPEC/TECH_SPEC.md#21-tabelas-novas)
  - [Tabela: metas](./02-TECH_SPEC/TECH_SPEC.md#tabela-metas)
  - [Tabela: category_budgets](./02-TECH_SPEC/TECH_SPEC.md#tabela-category_budgets)
  - [Tabela: budget_notifications](./02-TECH_SPEC/TECH_SPEC.md#tabela-budget_notifications)
- [Migrations Alembic (código completo)](./02-TECH_SPEC/TECH_SPEC.md#22-migrations-alembic)

### Backend - Models
- [Meta (SQLAlchemy)](./02-TECH_SPEC/TECH_SPEC.md#31-models)
- [CategoryBudget (SQLAlchemy)](./02-TECH_SPEC/TECH_SPEC.md#31-models)
- [BudgetNotification (SQLAlchemy)](./02-TECH_SPEC/TECH_SPEC.md#31-models)

### Backend - Schemas
- [MetaCreate, MetaUpdate, MetaResponse (Pydantic)](./02-TECH_SPEC/TECH_SPEC.md#4-backend---schemas-pydantic)
- [CategoryBudgetCreate, Update, Response](./02-TECH_SPEC/TECH_SPEC.md#4-backend---schemas-pydantic)
- [WalletSummaryResponse, WalletCategoriesResponse](./02-TECH_SPEC/TECH_SPEC.md#4-backend---schemas-pydantic)

### Backend - API Endpoints
- [Router Completo (FastAPI)](./02-TECH_SPEC/TECH_SPEC.md#51-router-principal)
  - POST /api/v1/wallet/metas
  - GET /api/v1/wallet/metas
  - PATCH /api/v1/wallet/metas/{id}
  - POST /api/v1/wallet/budgets
  - GET /api/v1/wallet/summary
  - GET /api/v1/wallet/categories
  - GET /api/v1/wallet/notifications

### Backend - Service Layer
- [WalletService (código completo)](./02-TECH_SPEC/TECH_SPEC.md#52-service-layer-lógica-de-negócio)
  - create_meta()
  - list_metas()
  - update_meta()
  - create_budget()
  - get_wallet_summary()
  - get_wallet_categories()
  - _calcular_economia_mes()
  - _calcular_gastos_por_categoria()

### Frontend
- [WalletPage Component (React/TypeScript)](./02-TECH_SPEC/TECH_SPEC.md#6-frontend---componente-principal)
  - Gráfico Donut (Recharts)
  - Segmented Control (iOS-style)
  - Lista de Categorias com Barras
  - API Integration

### Ordem de Implementação
- [DAG (Dependency Graph)](./02-TECH_SPEC/TECH_SPEC.md#7-dependency-graph-dag)
  - Item #1: Database
  - Item #2: Backend Models
  - Item #3: Backend Schemas
  - Item #4: Backend Service
  - Item #5: Backend Router
  - Item #6: Frontend API Client
  - Item #7: Frontend Componentes
  - Item #8: Testes
  - Item #9: Deploy

### Testes
- [Testing Strategy](./02-TECH_SPEC/TECH_SPEC.md#8-testing-strategy)
  - [Testes Unitários (Pytest)](./02-TECH_SPEC/TECH_SPEC.md#81-testes-unitários-backend)
  - [Testes E2E (Playwright)](./02-TECH_SPEC/TECH_SPEC.md#82-testes-e2e-playwright)

### Performance e Acessibilidade
- [Responsividade (Breakpoints)](./02-TECH_SPEC/TECH_SPEC.md#91-breakpoints)
- [ARIA Labels](./02-TECH_SPEC/TECH_SPEC.md#92-aria-labels)

### Deploy
- [Deploy Checklist (Resumo)](./02-TECH_SPEC/TECH_SPEC.md#10-deploy-checklist-resumo)

---

## 📊 VISUALIZAÇÕES E EXEMPLOS

### Mockup Visual
```
┌──────────────────────────────────┐
│   👤 Wallet         🔍 📅        │ ← Header
├──────────────────────────────────┤
│                                  │
│   [Botão: Month ▼]               │ ← Dropdown período
│                                  │
│      ╭─────────────╮             │
│     ╱   February   ╲            │
│    │   2026         │           │
│    │                 │           │ ← Gráfico Donut
│    │   $ 327.50      │           │   (Recharts)
│    │   out of $1000  │           │
│    │                 │           │
│     ╲───────────────╱            │
│      ╰─────────────╯             │
│                                  │
│   ┌──────────┬──────────┐       │ ← Segmented Control
│   │ Savings  │ Expenses │       │   (iOS-style)
│   └──────────┴──────────┘       │
│                                  │
│   🏠 Home            R$ 120/300  │ ← Lista de Categorias
│   ▓▓▓▓▓▓▓░░░░ 43%               │   com barras progresso
│                                  │
│   🍴 Alimentação     R$ 250/600 │
│   ▓▓▓▓░░░░░░ 42%                 │
│                                  │
│   🚗 Transporte      R$ 80/200  │
│   ▓▓▓░░░░░░░ 40%                 │
│                                  │
└──────────────────────────────────┘
```

### Exemplo de API Request/Response

**POST /api/v1/wallet/metas**
```bash
curl -X POST http://localhost:8000/api/v1/wallet/metas \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "mes": 2,
    "ano": 2026,
    "valor_meta": 1000.00
  }'
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "mes": 2,
  "ano": 2026,
  "valor_meta": 1000.00,
  "valor_economizado": 327.50,
  "progresso_percentual": 32.8,
  "created_at": "2026-02-02T10:30:00",
  "updated_at": null
}
```

---

**GET /api/v1/wallet/summary?mes=2&ano=2026**
```json
{
  "mes": 2,
  "ano": 2026,
  "meta_valor": 1000.00,
  "economia_atual": 327.50,
  "progresso_percentual": 32.8,
  "receitas_mes": 5000.00,
  "gastos_mes": 4672.50,
  "chart_data": [
    { "name": "Economia", "value": 327.50, "color": "#10B981" },
    { "name": "Alimentação", "value": 600.00, "color": "#3B82F6" },
    { "name": "Transporte", "value": 300.00, "color": "#F97316" },
    { "name": "Saúde", "value": 200.00, "color": "#A855F7" }
  ]
}
```

---

## 🔍 BUSCA POR TERMO

### Buscar por Funcionalidade
- **Criar meta:** [PRD US-01](./01-PRD/PRD.md#us-01) | [Backend Service](./02-TECH_SPEC/TECH_SPEC.md#52-service-layer)
- **Definir budget:** [PRD US-02](./01-PRD/PRD.md#us-02) | [Backend Router](./02-TECH_SPEC/TECH_SPEC.md#51-router-principal)
- **Visualizar progresso:** [PRD US-03](./01-PRD/PRD.md#us-03) | [Frontend Component](./02-TECH_SPEC/TECH_SPEC.md#6-frontend)
- **Alertas:** [PRD US-04](./01-PRD/PRD.md#us-04) | [Backend Notifications](./02-TECH_SPEC/TECH_SPEC.md#52-service-layer)
- **Gráfico donut:** [PRD Wireframe](./01-PRD/PRD.md#41-tela-principal) | [Frontend Recharts](./02-TECH_SPEC/TECH_SPEC.md#6-frontend)

### Buscar por Tecnologia
- **PostgreSQL:** [PRD Schema](./01-PRD/PRD.md#72-novas-tabelas) | [Tech SQL](./02-TECH_SPEC/TECH_SPEC.md#21-tabelas-novas)
- **Alembic:** [Tech Migrations](./02-TECH_SPEC/TECH_SPEC.md#22-migrations-alembic)
- **FastAPI:** [Tech Router](./02-TECH_SPEC/TECH_SPEC.md#51-router-principal)
- **Recharts:** [Tech Frontend](./02-TECH_SPEC/TECH_SPEC.md#6-frontend)
- **Playwright:** [Tech Tests](./02-TECH_SPEC/TECH_SPEC.md#82-testes-e2e)

### Buscar por Seção
- **Objetivos de negócio:** [PRD Seção 2](./01-PRD/PRD.md#2-objetivos-smart)
- **User stories:** [PRD Seção 3.2](./01-PRD/PRD.md#32-user-stories-formato-gherkin)
- **Database schema:** [Tech Seção 2](./02-TECH_SPEC/TECH_SPEC.md#2-database-schema)
- **APIs:** [Tech Seção 5](./02-TECH_SPEC/TECH_SPEC.md#5-backend---api-endpoints)
- **Testes:** [Tech Seção 8](./02-TECH_SPEC/TECH_SPEC.md#8-testing-strategy)
- **Deploy:** [Tech Seção 10](./02-TECH_SPEC/TECH_SPEC.md#10-deploy-checklist)

---

## 📊 TABELAS E CHECKLISTS

### KPIs Principais
| Métrica | Baseline | Meta (3 meses) | Como Medir |
|---------|----------|----------------|------------|
| Usuários com meta | 0% | 60% | SQL COUNT |
| Taxa cumprimento | N/A | 40% | achieved/total |
| Engajamento | 3.2/semana | 5.5/semana | Analytics |
| Retenção M1 | 72% | 85% | Cohort |
| NPS | 48 | 65 | Survey |

### Checklist de Aprovação (Stakeholder)
- [ ] Leu PRD completo
- [ ] Objetivos SMART validados
- [ ] User stories aprovadas
- [ ] Wireframes aprovados
- [ ] Escopo definido (incluído/excluído)
- [ ] Timeline aceito (6 semanas)
- [ ] Recursos aprovados (148h)
- [ ] **Assinou aprovação final** (BLOQUEANTE!)

### Checklist de Implementação (Dev Team)
- [ ] Migrations criadas e aplicadas
- [ ] Models SQLAlchemy testados
- [ ] Schemas Pydantic validados
- [ ] Service layer com lógica de negócio
- [ ] Router com todos endpoints
- [ ] Frontend componente funcional
- [ ] Gráfico donut renderizando
- [ ] Testes unitários ≥80% coverage
- [ ] Testes E2E ≥5 cenários
- [ ] Lighthouse ≥90
- [ ] WCAG ≥90% (axe scan)

### Checklist de Deploy
- [ ] Backup banco criado
- [ ] Migrations aplicadas produção
- [ ] Build frontend sem erros
- [ ] APIs testadas (curl/Postman)
- [ ] Smoke tests passando
- [ ] Health checks OK
- [ ] Monitoring ativo (logs)
- [ ] Stakeholders notificados
- [ ] POST_MORTEM agendado (48h)

---

## 🔗 LINKS EXTERNOS

### Benchmarks
- [Nubank Goals](https://nubank.com.br) - Gamificação e porquinho
- [GuiaBolso](https://guiabolso.com.br) - Orçamento por categoria
- [Organizze](https://organizze.com.br) - Planejamento mensal

### Documentação Técnica
- [Recharts Docs](https://recharts.org/en-US/examples/PieChartWithPaddingAngle)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Alembic Docs](https://alembic.sqlalchemy.org)
- [Playwright Docs](https://playwright.dev)

### Interno (FinUp)
- [WoW - Processo](../../WOW.md)
- [Copilot Instructions](../../../.github/copilot-instructions.md)
- [Mobile v1 - Benchmark](../mobile-v1/README.md)

---

## 📞 CONTATOS

**Dúvidas sobre esta feature?**
- **Product Owner:** [Nome] - [email]
- **Tech Lead:** [Nome] - [email]
- **Designer:** [Nome] - [email]
- **QA Lead:** [Nome] - [email]

**Para sugestões/melhorias:**
- Criar issue no GitHub com label `wallet`
- Mencionar no canal #finup-wallet (Slack)

---

## 🔄 HISTÓRICO DE VERSÕES

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | 02/02/2026 | Copilot | Criação inicial (PRD + TECH SPEC) |

---

**Última atualização:** 02/02/2026  
**Próxima revisão:** Após aprovação do PRD
