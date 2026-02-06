# 02_ARCHITECT_PLAN.md (Fase de Arquitetura Técnica)

## 🎯 OBJETIVO DESTA FASE
Definir a estratégia técnica, escolher bibliotecas, estruturar componentes e modelar dados. **AINDA NÃO GERAR CÓDIGO DE UI.**

---

## 📋 PROMPT DE ATIVAÇÃO
**Copie e cole no chat do Copilot/IA:**

```
Atue como Tech Lead e Arquiteto de Software especialista em React/Next.js.

CONTEXTO: Você acabou de receber a análise visual completa no arquivo "VISUAL_ANALYSIS_[nome].md".

TAREFA: Com base naquela análise, preencha o template abaixo (02_ARCHITECT_PLAN.md) definindo:
1. A estrutura de componentes (Atomic Design)
2. A estratégia para implementar gráficos/visualizações
3. As interfaces TypeScript dos dados
4. As decisões técnicas críticas

REGRAS:
- Priorize reutilização e manutenibilidade
- Para gráficos, escolha entre SVG Puro vs Bibliotecas e JUSTIFIQUE
- Defina tipos TypeScript completos
- Considere performance e acessibilidade

FORMATO DE SAÍDA: Crie um novo arquivo chamado "ARCHITECTURE_[nome-da-tela].md" com o conteúdo preenchido.
```

---

## 🏗️ TEMPLATE DE ARQUITETURA

### 1. MAPA DE COMPONENTES (ATOMIC DESIGN)

#### 1.1 Atoms (Componentes Indivisíveis)
Liste os menores blocos de UI:
- [ ] **[NomeDoAtomo]**: [Breve descrição - Ex: Avatar circular 40x40]
- [ ] **[NomeDoAtomo]**: [Descrição]
- [ ] **[NomeDoAtomo]**: [Descrição]

*Props comuns de Átomos: size, color, variant, disabled*

#### 1.2 Molecules (Combinações Simples)
Liste componentes que agrupam átomos:
- [ ] **[NomeDaMolecula]**: [Descrição e composição - Ex: SearchBar (Icon + Input)]
- [ ] **[NomeDaMolecula]**: [Descrição]
- [ ] **[NomeDaMolecula]**: [Descrição]

*Props comuns: label, value, onChange, placeholder*

#### 1.3 Organisms (Seções Complexas)
Liste blocos grandes e autônomos:
- [ ] **[NomeDoOrganismo]**: [Descrição - Ex: Header completo com nav e profile]
- [ ] **[NomeDoOrganismo]**: [Descrição]
- [ ] **[NomeDoOrganismo]**: [Descrição]

*Props comuns: data, isLoading, onAction*

#### 1.4 Templates
- [ ] **[NomeDoTemplate]**: [Layout da página - Ex: DashboardLayout com sidebar]

---

### 2. DECISÕES CRÍTICAS: VISUALIZAÇÕES DE DADOS

Para cada gráfico identificado na Fase 1, aplique a **DECISION MATRIX**:

#### GRÁFICO 1: [Nome do Gráfico]

**[ ] ESTRATÉGIA A: SVG Artesanal + CSS**
- **Quando escolher**:
  - Design altamente customizado (glow, gradients não-lineares)
  - Pontas arredondadas específicas (`stroke-linecap: round`)
  - Poucos dados (< 20 pontos)
  - Animações customizadas com Framer Motion
  
- **Vantagens**: Controle pixel-perfect, bundle menor
- **Desvantagens**: Matemática manual, sem escalas automáticas

**[ ] ESTRATÉGIA B: Biblioteca (Recharts/VisX/Chart.js)**
- **Quando escolher**:
  - Eixos X/Y complexos com labels automáticas
  - Tooltips interativos sofisticados
  - Muitos dados (> 30 pontos)
  - Zoom, pan, ou outras interações avançadas
  
- **Vantagens**: Responsividade automática, tooltips prontos
- **Desvantagens**: Customização limitada, bundle maior

**✅ DECISÃO FINAL**: [A ou B]

**JUSTIFICATIVA**:
[Explique sua escolha baseada nas características do design]

**IMPLEMENTAÇÃO PLANEJADA**:
- **Se SVG**: [Descreva abordagem - Ex: Usar `<circle>` com `stroke-dasharray`]
- **Se Biblioteca**: [Descreva customizações - Ex: Remover grid, customizar cores]

---

#### GRÁFICO 2: [Nome do Gráfico]
[Repetir estrutura acima para cada gráfico]

---

### 3. MODELAGEM DE DADOS (TYPESCRIPT)

#### 3.1 Interfaces Principais
```typescript
// EXEMPLO - Ajuste conforme necessário

// Interface para dados de usuário
interface User {
  id: string;
  name: string;
  avatar?: string;
}

// Interface para transações/dados financeiros
interface Transaction {
  id: string;
  date: string; // ISO format
  amount: number;
  category: string;
  type: 'income' | 'expense';
}

// Interface para categorias
interface Category {
  id: string;
  label: string;
  icon: React.ElementType; // Lucide icon
  color: string; // Tailwind class ou HEX
  percent: number;
}

// Interface para dados de gráficos
interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

// Adicione mais conforme necessário...
```

#### 3.2 Constantes & Mocks
```typescript
// EXEMPLO - Dados mockados para desenvolvimento

export const MOCK_USER: User = {
  id: '1',
  name: 'Vadim Portnyagin',
  avatar: 'https://i.pravatar.cc/150?u=vadim'
};

export const MOCK_CATEGORIES: Category[] = [
  {
    id: '1',
    label: 'Home',
    icon: Home, // lucide-react
    color: 'bg-blue-500',
    percent: 43
  },
  // ... mais categorias
];

// Adicione mais mocks...
```

---

### 4. STACK TÉCNICA DEFINIDA

#### 4.1 Core
- **Framework**: [Ex: Next.js 14+ (App Router)]
- **Language**: [TypeScript]
- **Styling**: [Tailwind CSS]
- **State Management**: [useState local, Zustand, Context API, etc]

#### 4.2 Bibliotecas Específicas
- **Ícones**: [lucide-react, react-icons, heroicons]
- **Gráficos** (se Estratégia B): [recharts, visx, chart.js]
- **Animações**: [framer-motion, react-spring, ou CSS puro]
- **Formulários** (se houver): [react-hook-form, formik]
- **Datas** (se houver): [date-fns, dayjs]

#### 4.3 Estrutura de Pastas Proposta
```
/app
  /page.tsx                    # Página principal
/components
  /atoms
    /Avatar.tsx
    /Button.tsx
    /Badge.tsx
  /molecules
    /StatCard.tsx
    /CategoryRow.tsx
  /organisms
    /WalletCard.tsx
    /ChartSection.tsx
  /layout
    /Header.tsx
    /BottomNav.tsx
/lib
  /utils.ts                    # Funções helper
  /constants.ts                # Cores, configs
/types
  /index.ts                    # Interfaces TypeScript
```

---

### 5. CONSIDERAÇÕES TÉCNICAS ESPECIAIS

#### 5.1 Performance
- [ ] Lazy loading para gráficos pesados?
- [ ] Memoização de componentes caros?
- [ ] Virtualization para listas longas?

#### 5.2 Acessibilidade
- [ ] ARIA labels para gráficos
- [ ] Keyboard navigation
- [ ] Focus states visíveis
- [ ] Contraste de cores adequado (WCAG AA)

#### 5.3 Responsividade
- [ ] Breakpoints customizados necessários?
- [ ] Gráficos responsivos (viewBox, aspect-ratio)
- [ ] Touch-friendly (botões > 44px)

#### 5.4 Animações
- [ ] Animação de entrada dos gráficos
- [ ] Transições de estado (hover, active)
- [ ] Loading states

---

### 6. RISCOS E DESAFIOS TÉCNICOS

#### Desafio 1: [Ex: Gráfico de Donut com pontas arredondadas]
- **Problema**: Recharts não suporta `stroke-linecap` customizado
- **Solução**: Migrar para SVG puro com cálculo de `stroke-dasharray`
- **Esforço Estimado**: 2-3 horas

#### Desafio 2: [Outro desafio identificado]
- **Problema**: [Descrição]
- **Solução**: [Abordagem]
- **Esforço Estimado**: [Tempo]

---

## ✅ CHECKLIST DE QUALIDADE

Antes de avançar para a Fase 3, confirme:
- [ ] Todos os componentes foram mapeados (Atomic Design)
- [ ] Estratégia de gráficos foi decidida e justificada
- [ ] Interfaces TypeScript foram definidas
- [ ] Stack técnica está completa
- [ ] Riscos técnicos foram identificados

---

## 🚀 PRÓXIMO PASSO
Após preencher este documento, avance para **03_CONSTRUCTION_GUIDE.md**
