# 📋 PRD - Tela History (Mobile Wallet)

**Status:** 🟡 Em Desenvolvimento (MVP)  
**Versão:** 1.0  
**Data:** 02/02/2026  
**Autor:** Emanuel Mangue  
**Stakeholders:** Emanuel Mangue (PO + Dev)

---

## 📊 Sumário Executivo

**O que:** Interface mobile-first de visualização de carteira digital com gráfico donut e breakdown de categorias de gastos/poupanças.

**Por quê:** Iniciar desenvolvimento de interface mobile do sistema FinUp com dados mockados (sem backend) para validar UX e componentes reutilizáveis.

**Para quem:** Usuários mobile que precisam visualizar resumo financeiro mensal de forma visual e intuitiva (estilo iOS/Nubank).

**Quando:** MVP em 1 dia (02/02/2026)  
**ROI Estimado:** Base de componentes reutilizáveis para toda a aplicação mobile + validação de arquitetura frontend

---

## 🎯 1. Contexto e Problema

### 1.1 Situação Atual
- Sistema FinUp existe apenas em versão desktop/web
- Não há interface mobile otimizada
- Componentes frontend não seguem Atomic Design
- Não há biblioteca de componentes reutilizáveis

### 1.2 Problema a Resolver
Usuários não conseguem visualizar resumo financeiro de forma otimizada em dispositivos móveis. Além disso, o projeto precisa de uma base sólida de componentes UI para escalar.

**Impacto do Problema:**
- 🟡 **Médio:** UX mobile inexistente (mas é MVP, não afeta prod)
- 🟢 **Baixo:** Componentes não reutilizáveis (será resolvido agora)
- 🟢 **Baixo:** Falta de padrão visual (estabeleceremos um)

### 1.3 Justificativa
**Por que fazer agora?**
- Estabelecer fundação de componentes reutilizáveis
- Validar design system mobile antes de conectar backend
- Aprendizado: workflow-kit (Image-to-Code) + Atomic Design
- Desenvolvimento iterativo: UI → Lógica → Backend

---

## 🎯 2. Objetivos

### 2.1 Objetivo Principal
Criar interface mobile pixel-perfect da tela "History" com dados mockados, seguindo Atomic Design e usando Next.js + Tailwind.

### 2.2 Objetivos Secundários
1. Estabelecer biblioteca de componentes reutilizáveis (atoms → organisms)
2. Validar arquitetura frontend modular
3. Documentar processo de desenvolvimento (PRD → TECH SPEC → Code)

### 2.3 Objetivos SMART

| Critério | Descrição |
|----------|-----------|
| **S**pecific | Implementar tela History com: gráfico donut SVG, lista de categorias, progress bars, bottom navigation |
| **M**easurable | ✅ 100% dos componentes mapeados implementados<br>✅ Visual 90%+ similar ao design<br>✅ Lighthouse Performance ≥90 |
| **A**chievable | Sim - MVP simples, sem backend, dados mockados |
| **R**elevant | Estabelece base para todo frontend mobile |
| **T**ime-bound | MVP completo: 02/02/2026 (1 dia) |

---

## 👥 3. Personas e User Stories

### 3.1 Persona Principal

**Nome:** Maria, Usuária Mobile  
**Idade:** 32 anos  
**Ocupação:** Gerente de Projetos  
**Comportamento:** Usa smartphone 80% do tempo, prefere apps nativos/mobile-optimized  
**Dores:** Apps financeiros com UX desktop não funcionam bem no celular  
**Objetivos:** Ver resumo financeiro rápido, visual, intuitivo

### 3.2 User Stories

#### **US-01: Visualizar Resumo Mensal da Carteira**
**Como** Maria (usuária mobile)  
**Quero** ver quanto pousei este mês em formato visual (gráfico)  
**Para** entender rapidamente minha performance financeira

**Acceptance Criteria:**
- [ ] Gráfico donut mostra breakdown de gastos por categoria
- [ ] Valor total poupado ($327.50) está destacado no centro
- [ ] Meta mensal ($1000) está visível
- [ ] Mês atual (September 2026) está identificado

**Prioridade:** 🔴 Alta

---

#### **US-02: Ver Detalhamento de Categorias**
**Como** Maria  
**Quero** ver lista de categorias com percentuais exatos  
**Para** identificar onde estou gastando mais

**Acceptance Criteria:**
- [ ] Lista "Savings" mostra categorias com progress bars
- [ ] Lista "Expenses" mostra categorias com progress bars
- [ ] Cada categoria tem cor identificável (matching com gráfico)
- [ ] Percentuais são exibidos à direita de cada barra

**Prioridade:** 🔴 Alta

---

#### **US-03: Navegar Entre Seções do App**
**Como** Maria  
**Quero** acessar outras seções via bottom navigation  
**Para** explorar outras funcionalidades do app

**Acceptance Criteria:**
- [ ] Bottom nav tem 4 ícones: Home, Chart, User, Add
- [ ] Ícone ativo (Home) está highlighted com background azul
- [ ] Botão "Add" (FAB) está destacado
- [ ] Todos os botões são touch-friendly (≥44px)

**Prioridade:** 🟡 Média

---

#### **US-04: Mudar Período de Visualização**
**Como** Maria  
**Quero** trocar o mês visualizado  
**Para** comparar performance de meses anteriores

**Acceptance Criteria:**
- [ ] Selector de mês está visível no header
- [ ] Ao tocar, dropdown abre com opções (mockado)
- [ ] Mês selecionado é exibido claramente

**Prioridade:** 🟢 Baixa (V2 - implementar apenas UI mockado)

---

## 📋 4. Requisitos Funcionais

### 4.1 Requisitos de Interface

**RF-01: Gráfico Donut Interativo**
- **Descrição:** Gráfico circular (donut) mostra breakdown de gastos por categoria
- **Comportamento:** 
  - 5 segmentos coloridos com gaps de 1-2px
  - Pontas arredondadas (stroke-linecap: round)
  - Animação de entrada (grow)
  - Texto centralizado: mês, valor, meta
- **Validações:** 
  - Total dos percentuais = 100%
  - Cores distintas e acessíveis (contrast ≥4.5:1)
- **Prioridade:** Must Have

**RF-02: Lista de Categorias (Savings)**
- **Descrição:** Lista de 2 categorias (Home 43%, Shopping 25%) com progress bars
- **Comportamento:**
  - Cada linha: dot colorido + label + progress bar + percentage
  - Progress bar animada (transition 500ms)
  - Cores matching com gráfico donut
- **Validações:** N/A (dados mockados)
- **Prioridade:** Must Have

**RF-03: Lista de Categorias (Expenses)**
- **Descrição:** Lista de 3 categorias (Nutrition 20%, Health 8%, Home 4%)
- **Comportamento:** Mesma estrutura de RF-02
- **Prioridade:** Must Have

**RF-04: Bottom Navigation**
- **Descrição:** Barra fixa inferior com 4 ícones de navegação
- **Comportamento:**
  - Ícone "Home" ativo (background azul)
  - Outros ícones inativos (cinza)
  - Botão "Add" (FAB) destacado (azul, maior)
  - Touch targets ≥44px
- **Validações:** N/A (navegação mockada)
- **Prioridade:** Must Have

**RF-05: Header com Avatar e Selector**
- **Descrição:** Barra superior com título "History", avatar, selector de mês
- **Comportamento:**
  - Avatar circular 40x40px
  - Selector abre dropdown (mockado - não funcional no MVP)
- **Prioridade:** Should Have

### 4.2 Requisitos de Lógica de Negócio

**RF-10: Cálculo de Percentuais**
- **Descrição:** Percentuais das categorias são calculados baseados em valores mockados
- **Fórmula:** `percentage = (categoryValue / totalValue) * 100`
- **Exemplo:** Home $430 / Total $1000 = 43%
- **Prioridade:** Must Have (mas valores são mockados)

### 4.3 Requisitos de Integração

**RF-20: Dados Mockados (Sem Backend)**
- **Sistema:** Nenhum (dados hardcoded)
- **Endpoint:** N/A
- **Dados:** Objetos TypeScript em `/lib/constants.ts`
- **Prioridade:** Must Have (este é o objetivo do MVP)

---

## ⚙️ 5. Requisitos Não-Funcionais

### 5.1 Performance
- **RNF-01:** Tempo de carregamento inicial ≤1s (sem API calls)
- **RNF-02:** Lighthouse Performance ≥90
- **RNF-03:** First Contentful Paint ≤1.5s
- **RNF-04:** Gráfico SVG renderiza em <100ms

### 5.2 Acessibilidade
- **RNF-10:** Contraste de cores ≥4.5:1 (WCAG AA)
- **RNF-11:** Touch targets ≥44px (mobile-friendly)
- **RNF-12:** ARIA labels em gráfico SVG
- **RNF-13:** Keyboard navigation no bottom nav

### 5.3 Segurança
- **RNF-20:** N/A (sem autenticação/backend no MVP)

### 5.4 Compatibilidade
- **RNF-30:** iOS 14+ (Safari)
- **RNF-31:** Android 10+ (Chrome)
- **RNF-32:** Responsivo: 320px - 428px width

---

## 📐 6. Wireframes e Mockups

### 6.1 Fluxo Principal

```
┌─────────────────────────────┐
│   Tela History              │
│                             │
│   [Header]                  │
│   ┌─────────────────────┐   │
│   │   Donut Chart       │   │
│   │   $327.50           │   │
│   └─────────────────────┘   │
│                             │
│   Savings                   │
│   • Home        [===] 43%   │
│   • Shopping    [==]  25%   │
│                             │
│   Expenses                  │
│   • Nutrition   [==]  20%   │
│   • Health      [=]    8%   │
│   • Home        [-]    4%   │
│                             │
│   [Bottom Nav]              │
└─────────────────────────────┘
```

### 6.2 Layout Mobile (Detalhado)

```
┌───────────────────────────────┐ ← 100vw
│  ← History  👤  Month ▼       │ ← Header 64px
├───────────────────────────────┤
│                               │
│         ╭─────────╮           │ ← Padding 16px
│        ╱   Sept   ╲          │
│       │   $327.50  │          │ ← Donut 250x250
│        ╲ of $1000 ╱          │
│         ╰─────────╯           │
│                               │
│  Savings                      │ ← Section 24px gap
│  ● Home      [████] 43%       │ ← CategoryRow
│  ● Shopping  [██  ] 25%       │ ← 12px gap
│                               │
│  Expenses                     │
│  ● Nutrition [██  ] 20%       │
│  ● Health    [█   ]  8%       │
│  ● Home      [-   ]  4%       │
│                               │
├───────────────────────────────┤
│  🏠   📊   👤   ⊕            │ ← Bottom Nav 70px
└───────────────────────────────┘
```

### 6.3 Links Figma/Design
- Design original: Imagem anexada (Vadim Portnyagin - TikTok)
- Análise visual: [VISUAL_ANALYSIS_history_wallet.md](./VISUAL_ANALYSIS_history_wallet.md)

---

## 🎨 7. Design System

### 7.1 Cores
- **Primary:** `#3B82F6` (blue-500) - Botões, links, active states
- **Success:** `#10B981` (green-500) - Categoria Home (savings)
- **Purple:** `#8B5CF6` (violet-600) - Categoria Nutrition
- **Orange:** `#F97316` (orange-500) - Categoria (donut)
- **Pink:** `#EC4899` (pink-500) - Categoria Home (expenses)
- **Background:** `#F7F8FA` (gray-50 customizado)
- **Surface:** `#FFFFFF` (white)
- **Text Primary:** `#111827` (gray-900)
- **Text Secondary:** `#6B7280` (gray-500)
- **Text Disabled:** `#9CA3AF` (gray-400)
- **Border:** `#E5E7EB` (gray-200)

### 7.2 Tipografia
- **Font:** Inter / SF Pro Display (fallback: system-ui)
- **Heading Large:** `text-5xl font-bold` (48px) - Valor principal
- **Heading Medium:** `text-2xl font-semibold` (24px) - Não usado
- **Body Regular:** `text-base font-medium` (16px) - Section titles
- **Body Small:** `text-sm font-medium` (14px) - Category labels
- **Caption:** `text-xs font-normal` (12px) - Subtexts

### 7.3 Componentes
- **Cards:** rounded-3xl (24px), shadow-sm, p-6, bg-white
- **Buttons:** rounded-full, p-3, touch target 48x48px
- **Progress Bars:** h-3 (12px), rounded-full, transition-all duration-500
- **Gaps:** space-y-6 (24px) entre seções, gap-3 (12px) entre items

---

## 🔄 8. Fluxos de Usuário

### 8.1 Fluxo: Visualizar Resumo Mensal

```
1. Usuário abre app → Tela History carrega
2. Animação: Gráfico donut "cresce" (300ms)
3. Animação: Progress bars preenchem (500ms sequencial)
4. Usuário visualiza:
   - Valor poupado no centro
   - Breakdown visual no gráfico
   - Detalhes em listas abaixo
5. Usuário pode:
   - Rolar para ver mais categorias (se houver overflow)
   - Tocar em bottom nav para mudar seção
   - Tocar em month selector (não funcional no MVP)
```

### 8.2 Fluxo: Navegação (Mockado)

```
1. Usuário toca em ícone do bottom nav (Chart, User, Add)
2. (MVP) Nada acontece - navegação não implementada
3. (V2) Transição para tela correspondente
```

### 8.3 Fluxo: Mudança de Mês (Mockado)

```
1. Usuário toca em "Month ▼"
2. (MVP) Nada acontece - selector não funcional
3. (V2) Dropdown abre com lista de meses
4. (V2) Seleção atualiza dados
```

---

## 📏 9. Escopo

### 9.1 Incluído (In Scope)
✅ UI completa da tela History  
✅ Gráfico donut SVG artesanal com animações  
✅ Progress bars animadas para categorias  
✅ Bottom navigation estilizada  
✅ Componentes reutilizáveis (Atomic Design)  
✅ Dados mockados hardcoded  
✅ Responsivo mobile (320px - 428px)  

### 9.2 Excluído (Out of Scope)
❌ Integração com backend/API  
❌ Autenticação/login  
❌ Navegação funcional (bottom nav apenas visual)  
❌ Month selector funcional  
❌ Edição de categorias  
❌ Gráficos interativos (tooltips, hover)  
❌ Versão desktop/tablet  
❌ Testes E2E (apenas visual QA)  

### 9.3 Futuro (Nice to Have - V2)
🔮 Conexão com backend real  
🔮 Navegação entre telas  
🔮 Filtros por período  
🔮 Tooltips interativos no gráfico  
🔮 Animações avançadas (Framer Motion)  
🔮 Dark mode  

---

## 📊 10. Métricas de Sucesso

### 10.1 KPIs Primários

| Métrica | Baseline | Meta | Como Medir |
|---------|----------|------|------------|
| Similaridade Visual | N/A | ≥90% | Comparação visual lado a lado |
| Performance Lighthouse | N/A | ≥90 | Chrome DevTools |
| Componentes Reutilizáveis | 0 | 12+ | Contagem no Storybook |
| Cobertura Atomic Design | N/A | 100% | Todos atoms/molecules/organisms |

### 10.2 KPIs Secundários
- **Técnicos:** 
  - FCP ≤1.5s
  - Bundle size ≤150KB (gzipped)
  - Zero erros console
  - WCAG AA conformidade ≥95%
- **Desenvolvimento:**
  - Tempo implementação ≤1 dia
  - Código TypeScript 100% tipado
  - Zero any types

---

## ⏱️ 11. Cronograma

### 11.1 Milestones

| Fase | Entregável | Prazo | Status |
|------|------------|-------|--------|
| PRD | Aprovação | 02/02 14:00 | ✅ Completo |
| TECH SPEC | Código copy-paste | 02/02 16:00 | 🔄 Em Progresso |
| Implementação | Componentes Atoms | 02/02 18:00 | ⏳ Pendente |
| Implementação | Molecules/Organisms | 02/02 20:00 | ⏳ Pendente |
| QA Visual | Comparação pixel-perfect | 02/02 21:00 | ⏳ Pendente |
| Deploy | GitHub + Doc | 02/02 22:00 | ⏳ Pendente |

### 11.2 Estimativa de Esforço

| Atividade | Tempo Real | Observação |
|-----------|------------|------------|
| PRD | 1h | Completo |
| TECH SPEC | 2h | Em progresso |
| Atoms (5 componentes) | 1.5h | Avatar, Badge, Button, ProgressBar, Selector |
| Molecules (4 componentes) | 1.5h | CategoryRow, StatCard, HeaderBar, SectionHeader |
| Organisms (4 componentes) | 2.5h | DonutChart (complexo), CategoryList, BottomNav, WalletCard |
| Templates (1 layout) | 30min | MobileHistoryLayout |
| Página principal | 30min | app/history/page.tsx |
| Ajustes/QA | 1h | Comparação visual, fixes |
| **TOTAL** | **~10h** | **1 dia (com foco)** |

---

## 🚧 12. Riscos e Mitigações

### 12.1 Riscos Técnicos

**Risco 1: Cálculo de stroke-dasharray complexo para SVG**
- **Probabilidade:** Média
- **Impacto:** Médio (pode atrasar gráfico)
- **Mitigação:** Helper function testada isoladamente antes de integrar
- **Plano B:** Usar biblioteca Recharts (menos pixel-perfect mas funcional)

**Risco 2: Animações CSS não funcionam em Safari**
- **Probabilidade:** Baixa
- **Impacto:** Baixo (apenas estética)
- **Mitigação:** Testar em Safari desde o início
- **Plano B:** Remover animações complexas, manter fade simples

**Risco 3: Texto centralizado no SVG desalinhado**
- **Probabilidade:** Média
- **Impacto:** Baixo (visual apenas)
- **Mitigação:** Usar foreignObject com Tailwind (melhor controle)
- **Plano B:** Ajustar manualmente com coordenadas SVG

### 12.2 Riscos de Negócio

**Risco 4: Design muito específico dificulta reutilização**
- **Probabilidade:** Baixa
- **Impacto:** Médio
- **Mitigação:** Componentizar máximo possível (Atomic Design)
- **Plano B:** Aceitar componentes específicos, criar genéricos depois

**Risco 5: Tempo excede 1 dia**
- **Probabilidade:** Média
- **Impacto:** Baixo (é MVP pessoal)
- **Mitigação:** Cortar animações avançadas se necessário
- **Plano B:** Finalizar no dia seguinte

---

## 📚 13. Dependências

### 13.1 Dependências Técnicas
- [X] Next.js 14+ instalado
- [X] Tailwind CSS configurado
- [X] TypeScript configurado
- [ ] Lucide-react instalado (ícones)
- [ ] Estrutura de pastas criada

### 13.2 Dependências de Negócio
- [X] Aprovação do design (referência visual anexada)
- [X] Tempo disponível (1 dia)
- [X] Workflow-kit validado (fases 1 e 2 completas)

---

## ✅ 14. Aprovação

### 14.1 Stakeholders

| Nome | Papel | Status | Data |
|------|-------|--------|------|
| Emanuel Mangue | Product Owner | ✅ Aprovado | 02/02/2026 |
| Emanuel Mangue | Tech Lead | ✅ Aprovado | 02/02/2026 |
| Emanuel Mangue | Designer | ✅ Aprovado | 02/02/2026 |

### 14.2 Critérios de Aprovação
- [X] PRD completo e detalhado
- [X] User stories com acceptance criteria
- [X] Escopo claro (in/out)
- [X] Cronograma realista (1 dia)
- [X] Riscos identificados e mitigados

**Data de Aprovação:** 02/02/2026 14:00  
**Aprovado por:** Emanuel Mangue (PO)

---

## 📖 15. Anexos

### 15.1 Referências
- [Análise Visual Completa](./VISUAL_ANALYSIS_history_wallet.md)
- [Arquitetura Técnica](../02-TECH_SPEC/ARCHITECTURE_history_wallet.md)
- [Workflow-Kit](../../../../workflow-kit/README.md)
- Design original: Imagem anexada (Vadim Portnyagin)

### 15.2 Histórico de Versões

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | 02/02/2026 | Emanuel Mangue | Criação inicial baseada em workflow-kit + TEMPLATE_PRD.md |

---

**Próximo Passo:** Criar **TECH SPEC completo** com código copy-paste ready (`/docs/features/mobile-history/02-TECH_SPEC/TECH_SPEC.md`)
