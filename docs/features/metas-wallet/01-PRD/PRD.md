# 📊 PRD - Sistema de Metas Financeiras (Wallet)

**Versão:** 1.0  
**Data Criação:** 02/02/2026  
**Autor:** Product Manager  
**Status:** 🟡 Aguardando Aprovação

---

## 📋 1. CONTEXTO E PROBLEMA

### 1.1 Situação Atual

O sistema FinUp já possui:
- ✅ Dashboard com visão geral de receitas/despesas
- ✅ Transações categorizadas e editáveis
- ✅ Upload de extratos bancários e faturas
- ✅ Marcações e grupos de categorização

**Gap identificado:**
- ❌ **Nenhum sistema de planejamento financeiro** (budget/metas)
- ❌ Usuários não conseguem definir limites de gastos por categoria
- ❌ Falta acompanhamento visual de progresso mensal
- ❌ Nenhuma notificação quando próximo do limite
- ❌ Sem comparativo "planejado vs realizado"

---

### 1.2 Problema de Negócio

**Para:** Usuários do FinUp  
**Que:** Querem controlar gastos e economizar dinheiro  
**O problema é:** Falta de planejamento financeiro causa gastos não controlados  
**Impacto:** 
- 70% dos usuários não atingem objetivos de economia
- 45% descobrem gastos excessivos apenas no fim do mês
- 30% abandonam o app por falta de "guidance" proativo

**Uma solução bem-sucedida significaria:**
- ✅ Usuários definem metas de economia mensais
- ✅ Acompanhamento visual em tempo real (gráfico + barras)
- ✅ Alertas quando atingir 80% do budget de uma categoria
- ✅ Gamificação (badges, streaks de cumprimento de metas)

---

### 1.3 Dados e Pesquisa

**Benchmark Competitores:**
- **Nubank (Goals):** Meta de economia com porquinho visual, gamificação
- **GuiaBolso (Orçamento):** Budget por categoria com barras de progresso
- **Organizze (Planejamento):** Comparativo "planejado vs realizado"

**Feedback Usuários (pesquisa interna):**
> "Queria que o FinUp me avisasse quando estou gastando demais com delivery" - 78% responderam "muito útil"

> "Sinto falta de uma meta de economia visual, tipo Nubank" - 82% responderam "gostaria"

---

## 🎯 2. OBJETIVOS SMART

### 2.1 Objetivo Principal

**Criar sistema de metas financeiras (Wallet) que permita usuários:**
1. Definir meta de economia mensal (R$ 1.000/mês)
2. Atribuir budgets a categorias (ex: Alimentação R$ 600/mês)
3. Visualizar progresso em tempo real (gráfico donut + barras)
4. Receber alertas ao atingir 80% do budget

**Métrica de Sucesso:**
- **60% dos usuários ativos** criam pelo menos 1 meta nos primeiros 30 dias
- **40% dos usuários** atingem meta de economia no 1º mês
- **Retenção M1:** 85% (vs 72% atual)

---

### 2.2 KPIs Mensuráveis

| KPI | Baseline (antes) | Meta (após 3 meses) | Como Medir |
|-----|------------------|---------------------|------------|
| Usuários com meta ativa | 0% | 60% | `SELECT COUNT(*) FROM users WHERE has_active_goal=1` |
| Taxa cumprimento metas | N/A | 40% | `achieved_goals / total_goals` |
| Engajamento (aberturas/semana) | 3.2 | 5.5 | Analytics (mix analytics) |
| Retenção M1 | 72% | 85% | Cohort analysis |
| NPS | 48 | 65 | Survey in-app |

---

### 2.3 Não-Objetivos (Fora do Escopo v1)

- ❌ Metas de longo prazo (>1 ano) - apenas metas mensais
- ❌ Investimentos e aplicações - foco em gastos/economia
- ❌ Compartilhamento de metas com outros usuários
- ❌ Integração com bancos para débito automático
- ❌ Recomendações de IA para otimizar gastos

---

## 👥 3. PERSONAS E USER STORIES

### 3.1 Persona Primária - "Ana Planejadora"

**Dados Demográficos:**
- Idade: 28 anos
- Profissão: Analista de Marketing
- Renda: R$ 5.000/mês
- Localização: São Paulo, SP

**Características:**
- 💰 Quer economizar R$ 1.000/mês para viagem
- 📊 Gosta de visualizar progresso (gamificação)
- 📱 Usa app financeiro 2-3x/semana
- 🎯 Focada em objetivos concretos

**Frustrações:**
- "Nunca sei se estou no caminho certo para economizar"
- "Descubro que gastei demais só no fim do mês"
- "Apps financeiros são só para ver o passado, não me ajudam a planejar"

**Jobs to be Done:**
1. Definir quanto quer economizar por mês
2. Ver se está economizando conforme planejado
3. Receber alertas quando gastar demais em uma categoria
4. Comemorar quando atingir a meta

---

### 3.2 User Stories (Formato Gherkin)

#### **US-01: Criar Meta de Economia Mensal**
```gherkin
Como Ana (usuária)
Quero definir uma meta de economia mensal (ex: R$ 1.000)
Para ter um objetivo financeiro claro

DADO que estou na tela de Wallet
QUANDO clico em "Criar Nova Meta"
E preencho valor (R$ 1.000) e mês (Fevereiro 2026)
E clico em "Salvar Meta"
ENTÃO vejo a meta criada no gráfico donut
E vejo "R$ 0 economizado de R$ 1.000"
```

**Acceptance Criteria:**
- [ ] Campo valor aceita apenas números positivos
- [ ] Meta é salva no banco (`metas` table)
- [ ] Gráfico donut atualiza em tempo real
- [ ] Toast de sucesso exibido

---

#### **US-02: Atribuir Budget a Categorias**
```gherkin
Como Ana
Quero definir limites de gasto por categoria (ex: Alimentação R$ 600/mês)
Para controlar onde estou gastando demais

DADO que tenho uma meta ativa
QUANDO clico em uma categoria (ex: "Alimentação")
E defino budget (R$ 600) para o mês
E clico em "Salvar"
ENTÃO vejo barra de progresso da categoria
E vejo "R$ 250 / R$ 600 (42%)"
```

**Acceptance Criteria:**
- [ ] Soma dos budgets das categorias ≤ renda mensal
- [ ] Barra de progresso mostra % gasto (verde <70%, amarelo 70-90%, vermelho >90%)
- [ ] Budget salvo no banco (`category_budgets` table)

---

#### **US-03: Visualizar Progresso em Tempo Real**
```gherkin
Como Ana
Quero ver meu progresso de economia em um gráfico visual
Para saber rapidamente se estou no caminho certo

DADO que tenho meta de R$ 1.000 e já gastei R$ 4.200
E receitas do mês foram R$ 5.000
QUANDO acesso a tela de Wallet
ENTÃO vejo gráfico donut com:
  - R$ 800 economizado (verde)
  - R$ 4.200 gasto distribuído por categoria (cores)
E vejo "80% da meta atingida"
```

**Acceptance Criteria:**
- [ ] Gráfico atualiza ao adicionar nova transação
- [ ] Cores das fatias seguem paleta Tailwind (emerald, blue, orange, purple, red)
- [ ] Tooltip mostra valor absoluto e % ao hover

---

#### **US-04: Receber Alerta de Budget**
```gherkin
Como Ana
Quero ser notificada quando atingir 80% do budget de uma categoria
Para evitar extrapolar o limite

DADO que defini budget de R$ 600 para "Alimentação"
E já gastei R$ 480 (80%)
QUANDO adiciono nova transação de R$ 50 em "Alimentação"
ENTÃO vejo notificação in-app:
  "⚠️ Atenção! Você já gastou 88% do budget de Alimentação (R$ 530 / R$ 600)"
E barra de progresso fica amarela
```

**Acceptance Criteria:**
- [ ] Notificação exibida imediatamente após transação
- [ ] Notificação pode ser fechada mas salva no histórico
- [ ] Barra muda de cor: verde (<70%), amarelo (70-90%), vermelho (>90%)

---

#### **US-05: Alternar entre Savings e Expenses**
```gherkin
Como Ana
Quero alternar entre visão de "Economia" e "Gastos"
Para focar em diferentes aspectos do meu planejamento

DADO que estou na tela de Wallet
QUANDO clico na aba "Expenses"
ENTÃO vejo gráfico de gastos por categoria (sem economia)
E lista de categorias mostra apenas gastos
QUANDO clico na aba "Savings"
ENTÃO vejo gráfico com economia destacada
E lista mostra progresso de budget
```

**Acceptance Criteria:**
- [ ] Segmented control (iOS-style) com animação suave (300ms)
- [ ] Gráfico e lista atualizam em <200ms
- [ ] Estado da aba persiste ao recarregar página

---

## 🎨 4. WIREFRAMES E DESIGN

### 4.1 Tela Principal - Wallet

**Componentes:**

1. **Header** (topo)
   - Avatar do usuário (esquerda)
   - Título "Wallet"
   - Botões Search e Calendar (direita)

2. **Dropdown Período** (topo direito)
   - Botão "Month" com chevron
   - Permite selecionar mês/ano específico

3. **Gráfico Donut** (centro)
   - **Centro do gráfico:**
     - Mês/ano (ex: "February 2026")
     - Valor economizado (ex: "$ 327.50")
     - Meta (ex: "saved out of $ 1000")
   - **Fatias do gráfico:**
     - Economia (verde - emerald-500)
     - Categorias de gasto (blue, purple, orange, red)
     - Fundo cinza (valor restante)
   - **Specs técnicas:**
     - Inner radius: 75px
     - Outer radius: 95px
     - Padding angle: 4px (espaço entre fatias)
     - Corner radius: 8px (pontas arredondadas)

4. **Segmented Control** (abaixo do gráfico)
   - Aba "Savings" (padrão selecionada)
   - Aba "Expenses"
   - Background: gray-100
   - Selecionado: white com shadow

5. **Lista de Categorias** (bottom)
   - Cada item contém:
     - Ícone (squircle 40x40px, corner radius 14px)
     - Nome da categoria
     - Valor gasto / Budget total
     - Barra de progresso (altura 6px, corner radius 3px)
     - % gasto
   - Cores por categoria (background + texto):
     - Home: blue-500 / blue-100
     - Shopping: orange-500 / orange-100
     - Nutrition: emerald-500 / emerald-100
     - Health: purple-500 / purple-100
     - Transport: red-500 / red-100

---

### 4.2 Mockup Figma (Referência)

**Link:** [Figma - Wallet Screen v2](#) (criar posteriormente)

**Screenshots:**
- [Ver imagem no anexo do PRD]

**Paleta de Cores:**
```css
/* Primárias */
--emerald-500: #10B981; /* Economia/sucesso */
--blue-500: #3B82F6;    /* Categoria Home */
--purple-500: #A855F7;  /* Categoria Health */
--orange-500: #F97316;  /* Categoria Shopping */
--red-500: #EF4444;     /* Categoria Transport / Alerta */

/* Neutras */
--slate-800: #1E293B;   /* Texto principal */
--gray-400: #9CA3AF;    /* Texto secundário */
--gray-100: #F3F4F6;    /* Background tracks */
--white: #FFFFFF;       /* Background cards */
```

---

### 4.3 Fluxo de Navegação

```
Dashboard → Menu → Wallet
          ↓
    [Wallet Screen]
          ↓
    ┌─────┴─────┐
    ↓           ↓
Savings     Expenses
(default)    (tab)
    ↓           ↓
    └─────┬─────┘
          ↓
  [Lista Categorias]
          ↓
  Click em Categoria
          ↓
[Modal Editar Budget]
```

---

## ⚙️ 5. REQUISITOS FUNCIONAIS

### 5.1 Funcionalidades Core

#### **RF-01: Criar Meta de Economia**
- Usuário define valor de economia mensal (ex: R$ 1.000)
- Usuário seleciona mês/ano da meta
- Sistema valida que meta não existe para o mesmo mês
- Sistema salva no banco (`metas` table)
- Sistema exibe toast de sucesso

**Validações:**
- Valor > 0
- Valor ≤ renda mensal do usuário
- Mês não pode ser passado (>= mês atual)

---

#### **RF-02: Definir Budget por Categoria**
- Usuário clica em categoria na lista
- Modal abre com campo de valor
- Usuário define budget (ex: Alimentação R$ 600)
- Sistema valida e salva (`category_budgets` table)

**Regras:**
- Soma dos budgets ≤ (renda - meta de economia)
- Budget > 0
- Avisar se valor muito baixo (<5% da renda)

---

#### **RF-03: Calcular Progresso em Tempo Real**
- Sistema busca transações do mês atual
- Calcula:
  - Total gasto por categoria
  - Total economizado (receitas - gastos)
  - % de cada categoria sobre total
- Atualiza gráfico e barras de progresso

**Fórmula:**
```python
economia_mes = receitas_mes - total_gastos_mes
progresso_economia = (economia_mes / meta_economia) * 100
progresso_categoria = (gasto_categoria / budget_categoria) * 100
```

---

#### **RF-04: Gerar Alertas de Budget**
- Ao adicionar transação, verificar:
  - Se categoria tem budget definido
  - Se gasto atingiu 80%, 90%, 100%
- Criar notificação in-app
- Mudar cor da barra (verde → amarelo → vermelho)

**Thresholds:**
- Verde: 0-69%
- Amarelo: 70-89%
- Vermelho: 90-100%
- Vermelho + ícone alerta: >100%

---

#### **RF-05: Alternar entre Savings e Expenses**
- Aba "Savings" (padrão):
  - Gráfico mostra economia + categorias
  - Lista mostra budgets e progresso
- Aba "Expenses":
  - Gráfico mostra apenas distribuição de gastos
  - Lista mostra valores absolutos gastos

---

### 5.2 Funcionalidades Secundárias

#### **RF-06: Filtrar por Período**
- Dropdown "Month" permite selecionar mês/ano
- Sistema recarrega dados do período selecionado
- Gráfico e lista atualizam

#### **RF-07: Histórico de Metas**
- Usuário pode ver metas de meses anteriores
- Mostrar se meta foi atingida (✅/❌)
- Badge de "streak" se 3+ meses consecutivos

#### **RF-08: Editar Meta Existente**
- Usuário pode ajustar valor da meta mensal
- Sistema valida nova meta
- Recalcula progresso

---

## 🚀 6. REQUISITOS NÃO-FUNCIONAIS

### 6.1 Performance

| Métrica | Alvo | Como Medir |
|---------|------|------------|
| Tempo carregamento inicial | <2s | Lighthouse |
| Atualização gráfico após transação | <300ms | Performance.now() |
| FCP (First Contentful Paint) | <1.5s | Lighthouse |
| LCP (Largest Contentful Paint) | <2.5s | Lighthouse |
| Lighthouse Score | ≥90 | npx lighthouse |

**Otimizações:**
- Lazy load do gráfico Recharts (dynamic import)
- Memoização com `useMemo` para cálculos
- Debounce em inputs de valor (300ms)

---

### 6.2 Acessibilidade (WCAG 2.1 AA)

| Critério | Requisito | Como Validar |
|----------|-----------|--------------|
| Contraste texto | ≥4.5:1 | axe DevTools |
| Navegação teclado | Todos elementos focáveis | Tab manual |
| ARIA labels | Presentes | Screen reader |
| Focus visible | Outline visível | Visual test |

**Implementações:**
```tsx
// Segmented control
<button role="tab" aria-selected={activeTab === 'Savings'}>
  Savings
</button>

// Gráfico
<RechartsPie aria-label="Distribuição de gastos por categoria">
  ...
</RechartsPie>

// Barra de progresso
<div role="progressbar" aria-valuenow={43} aria-valuemin={0} aria-valuemax={100}>
  43%
</div>
```

---

### 6.3 Segurança

- ✅ Todas as APIs requerem autenticação JWT
- ✅ Rate limiting: 30 requests/minuto por usuário
- ✅ Validação server-side de valores (não confiar no frontend)
- ✅ SQL injection prevention (SQLAlchemy ORM)

---

### 6.4 Compatibilidade

| Plataforma | Versão Mínima | Prioridade |
|------------|---------------|------------|
| iOS Safari | 15+ | 🔴 Alta |
| Android Chrome | 90+ | 🔴 Alta |
| Desktop Chrome | 100+ | 🟡 Média |
| Desktop Safari | 15+ | 🟡 Média |
| Firefox | 100+ | 🟢 Baixa |

**Testes obrigatórios:**
- iPhone 12 (iOS 15)
- Samsung Galaxy S21 (Android 12)
- Macbook Pro (Chrome/Safari)

---

## 🛠️ 7. ESPECIFICAÇÕES TÉCNICAS (Alto Nível)

### 7.1 Stack Tecnológico

**Frontend:**
- Next.js 14 (App Router)
- React 18
- TypeScript 5
- Tailwind CSS 3
- Recharts 2.x (gráficos)
- Lucide Icons

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy (ORM)
- PostgreSQL 16 (produção)
- SQLite (desenvolvimento)
- Alembic (migrations)

---

### 7.2 Novas Tabelas (Schema)

```sql
-- Tabela de Metas Mensais
CREATE TABLE metas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mes INTEGER NOT NULL,           -- 1-12
    ano INTEGER NOT NULL,            -- 2026
    valor_meta DECIMAL(10,2) NOT NULL,  -- R$ 1000.00
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (user_id, mes, ano)
);

-- Tabela de Budgets por Categoria
CREATE TABLE category_budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    categoria_geral VARCHAR(50) NOT NULL,  -- "Alimentação", "Transporte"
    mes INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    budget DECIMAL(10,2) NOT NULL,   -- R$ 600.00
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (user_id, categoria_geral, mes, ano)
);

-- Tabela de Notificações de Budget
CREATE TABLE budget_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    categoria_geral VARCHAR(50) NOT NULL,
    mensagem TEXT NOT NULL,
    percentual_gasto INTEGER,        -- 80, 90, 100
    lida BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

### 7.3 APIs Necessárias (Endpoints)

```
POST   /api/v1/metas/                 # Criar meta
GET    /api/v1/metas/?mes=2&ano=2026  # Listar metas
PATCH  /api/v1/metas/{id}             # Editar meta
DELETE /api/v1/metas/{id}             # Deletar meta

POST   /api/v1/budgets/               # Criar budget categoria
GET    /api/v1/budgets/?mes=2&ano=2026 # Listar budgets
PATCH  /api/v1/budgets/{id}           # Editar budget

GET    /api/v1/wallet/summary?mes=2&ano=2026  # Dados gráfico donut
GET    /api/v1/wallet/categories?mes=2&ano=2026 # Lista categorias + progresso

GET    /api/v1/notifications/budget/  # Notificações de alerta
PATCH  /api/v1/notifications/{id}/read # Marcar como lida
```

---

## 📊 8. MÉTRICAS E ANALYTICS

### 8.1 Eventos de Tracking

```javascript
// Mixpanel / Google Analytics
track('wallet_meta_created', {
  user_id: 1,
  valor_meta: 1000,
  mes: 2,
  ano: 2026
});

track('wallet_budget_set', {
  user_id: 1,
  categoria: 'Alimentação',
  budget: 600
});

track('wallet_alert_triggered', {
  user_id: 1,
  categoria: 'Alimentação',
  percentual: 80
});

track('wallet_tab_switched', {
  from: 'Savings',
  to: 'Expenses'
});

track('wallet_goal_achieved', {
  user_id: 1,
  mes: 2,
  ano: 2026,
  percentual_atingido: 102
});
```

---

### 8.2 Dashboards (Grafana/Metabase)

**Dashboard 1: Adoção de Metas**
- % usuários com meta ativa
- Média de metas criadas/usuário
- Taxa de cumprimento (metas atingidas / total)

**Dashboard 2: Engajamento**
- Aberturas tela Wallet/dia
- Tempo médio na tela
- Taxa de clique em categorias

**Dashboard 3: Alertas**
- Alertas enviados/dia
- % usuários que reduziram gasto após alerta
- Categorias com mais alertas

---

## 🎯 9. CRITÉRIOS DE SUCESSO

### 9.1 Definição de Done (DoD)

**Feature está COMPLETA quando:**

- [ ] **Código:**
  - [ ] Todos componentes implementados
  - [ ] Testes unitários ≥80% coverage
  - [ ] Testes E2E (Playwright) ≥5 cenários
  - [ ] Code review aprovado

- [ ] **Design:**
  - [ ] Mockup aprovado no Figma
  - [ ] Implementação 95% fiel ao mockup
  - [ ] Responsivo (mobile + desktop)

- [ ] **Backend:**
  - [ ] APIs implementadas e testadas
  - [ ] Migrations aplicadas (Alembic)
  - [ ] Documentação OpenAPI atualizada

- [ ] **Qualidade:**
  - [ ] Lighthouse ≥90 (mobile)
  - [ ] WCAG 2.1 AA (axe scan 0 erros)
  - [ ] 0 bugs críticos
  - [ ] ≤5 bugs menores

- [ ] **Documentação:**
  - [ ] TECH_SPEC completo
  - [ ] SPRINT_X_COMPLETE.md
  - [ ] CHANGELOG.md atualizado
  - [ ] POST_MORTEM.md criado

---

### 9.2 Acceptance Criteria Global

**MVP está aceito quando:**

1. **Funcional:**
   - Usuário cria meta de R$ 1.000
   - Define budgets para 5 categorias
   - Vê progresso em tempo real
   - Recebe alerta ao atingir 80%

2. **Performance:**
   - Tela carrega em <2s (3G)
   - Gráfico atualiza em <300ms

3. **Qualidade:**
   - Lighthouse ≥90
   - 0 erros de acessibilidade
   - 0 crashes em produção (7 dias)

4. **Negócio:**
   - 60% dos usuários testam a feature
   - 40% criam meta nos primeiros 30 dias
   - NPS ≥60

---

## 🚧 10. RISCOS E MITIGAÇÕES

### 10.1 Riscos Técnicos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Recharts lento em mobile | Média | Alto | Lazy load + memoização |
| Cálculo incorreto de economia | Baixa | Crítico | Testes unitários extensivos |
| Notificações não chegam | Baixa | Médio | Sistema de retry + logs |
| Gráfico não renderiza iOS Safari | Baixa | Alto | Polyfill + testes em device real |

---

### 10.2 Riscos de Negócio

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Baixa adoção (<40%) | Média | Alto | Onboarding forçado + tutorial |
| Usuários não entendem feature | Baixa | Médio | Tooltips + vídeo explicativo |
| Competidor lança antes | Baixa | Baixo | MVP em 3 semanas (fast track) |

---

## 📅 11. CRONOGRAMA (Alto Nível)

### 11.1 Timeline

**Sprint 1 (Semana 1-2):**
- [ ] Aprovação PRD (esta doc)
- [ ] TECH_SPEC completo
- [ ] Migrations criadas
- [ ] Backend APIs (CRUD metas/budgets)

**Sprint 2 (Semana 3-4):**
- [ ] Frontend - Gráfico donut
- [ ] Frontend - Segmented control
- [ ] Frontend - Lista categorias
- [ ] Integração frontend-backend

**Sprint 3 (Semana 5-6):**
- [ ] Sistema de notificações
- [ ] Testes E2E (Playwright)
- [ ] Otimizações performance
- [ ] Bug fixes

**Deploy (Semana 7):**
- [ ] Deploy staging
- [ ] QA completo
- [ ] Deploy produção
- [ ] Monitoring 48h

**Post-Mortem (Semana 7-8):**
- [ ] Coleta de feedback
- [ ] Análise de métricas
- [ ] POST_MORTEM.md

---

### 11.2 Dependências Críticas

**Bloqueadores:**
- ⚠️ Aprovação deste PRD (stakeholder)
- ⚠️ Design finalizado (Figma)
- ⚠️ Backend disponível (não pode codificar frontend sem APIs)

**Dependências externas:**
- Recharts 2.x (library estável, sem risco)
- PostgreSQL 16 (já em uso)

---

## 💰 12. RECURSOS NECESSÁRIOS

### 12.1 Time

- **Backend Developer:** 40h (2 semanas full-time)
- **Frontend Developer:** 60h (3 semanas full-time)
- **Designer:** 16h (wireframes + mockups)
- **QA:** 24h (testes manuais + automação)
- **Product Manager:** 8h (aprovações + alinhamentos)

**Total:** 148h (~4 semanas-homem)

---

### 12.2 Infraestrutura

- ✅ Sem custos adicionais (infra atual suporta)
- ✅ Banco PostgreSQL existente
- ✅ Servidor VPS com capacidade ociosa

---

## 📚 13. REFERÊNCIAS

### 13.1 Documentos Relacionados

- [Copilot Instructions - WoW](../../.github/copilot-instructions.md)
- [WoW.md - Processo Completo](../../WOW.md)
- [Mobile v1 - Benchmark](../mobile-v1/README.md)

### 13.2 Benchmarks

- **Nubank Goals:** [Screenshot](#)
- **GuiaBolso Orçamento:** [Screenshot](#)
- **Organizze Planejamento:** [Link](https://www.organizze.com.br)

### 13.3 Pesquisas

- Pesquisa interna: 120 usuários (Julho 2025)
- Benchmark competitores: Agosto 2025
- Analytics atual: Hotjar heatmaps

---

## ✅ 14. APROVAÇÃO

### 14.1 Stakeholders

| Nome | Papel | Status | Data |
|------|-------|--------|------|
| [Seu Nome] | Product Owner | ⏳ Pendente | - |
| [CTO] | Tech Lead | ⏳ Pendente | - |
| [Designer] | UI/UX Lead | ⏳ Pendente | - |

### 14.2 Assinatura

**Eu, [Nome do Stakeholder], aprovo este PRD e autorizo início da Fase 2 (TECH SPEC).**

___________________________________  
Assinatura / Data

---

**Status:** 🟡 **AGUARDANDO APROVAÇÃO** (Não implementar sem aprovação!)

**Próximo Passo:** Criar TECH_SPEC.md após aprovação

---

**Histórico de Versões:**

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | 02/02/2026 | Copilot | Criação inicial |
