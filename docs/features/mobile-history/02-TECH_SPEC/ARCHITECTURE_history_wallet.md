# 02_ARCHITECTURE - History Wallet Screen

**Data:** 02/02/2026  
**Fase:** 2 - Arquitetura Técnica (Workflow-Kit)  
**Feature:** Tela History - Visualização de Carteira e Gastos

---

## 🏗️ TEMPLATE DE ARQUITETURA

### 1. MAPA DE COMPONENTES (ATOMIC DESIGN)

#### 1.1 Atoms (Componentes Indivisíveis)

- [X] **Avatar**: Imagem circular 40x40px com border opcional
- [X] **Badge**: Dot colorido circular (8x8px) para indicar categorias
- [X] **IconButton**: Botão circular com ícone (Home, Chart, User, Search)
- [X] **ProgressBar**: Barra de progresso horizontal com track e fill
- [X] **Text**: Componentes de texto (Heading, Body, Caption) com variantes
- [X] **MonthSelector**: Dropdown/selector de mês estilizado

#### 1.2 Molecules (Combinações Simples)

- [X] **CategoryRow**: Badge + Label + ProgressBar + Percentage
  - Composição: Badge (Atom) + Text (Atom) + ProgressBar (Atom)
  - Props: `label`, `color`, `percentage`, `icon`
  
- [X] **StatCard**: Container branco com sombra para estatísticas
  - Composição: Card container + Children
  - Props: `children`, `padding`, `shadow`
  
- [X] **HeaderBar**: Barra superior com título e controles
  - Composição: Text (title) + Avatar + MonthSelector
  - Props: `title`, `avatarSrc`, `selectedMonth`, `onMonthChange`
  
- [X] **SectionHeader**: Título de seção com ícone opcional
  - Composição: Icon (opcional) + Text
  - Props: `title`, `icon`, `variant`

#### 1.3 Organisms (Seções Complexas)

- [X] **DonutChart**: Gráfico circular com texto central e legendas
  - Composição: SVG customizado + CenterText + Optional Legend
  - Props: `data[]`, `total`, `subtitle`, `size`
  - Dados: `{ label, value, color }`
  
- [X] **CategoryList**: Lista de categorias com progress bars
  - Composição: Múltiplos CategoryRow
  - Props: `categories[]`, `title`, `type` (savings/expenses)
  
- [X] **BottomNavigation**: Barra de navegação inferior com 4 ícones
  - Composição: 4x IconButton + 1 FAB (Add button)
  - Props: `activeTab`, `onTabChange`

- [X] **WalletSummaryCard**: Card principal com gráfico + categorias
  - Composição: HeaderBar + DonutChart + CategoryList (Savings) + CategoryList (Expenses)
  - Props: `user`, `month`, `data`, `categories[]`

#### 1.4 Templates

- [X] **MobileHistoryLayout**: Layout completo da tela History
  - Composição: WalletSummaryCard + BottomNavigation
  - Background: `#F7F8FA`

---

### 2. DECISÕES CRÍTICAS: VISUALIZAÇÕES DE DADOS

#### GRÁFICO 1: Donut Chart (Anel Circular)

**[X] ESTRATÉGIA A: SVG Artesanal + CSS**

**Quando escolher**:
- ✅ Design altamente customizado (pontas arredondadas, gaps específicos)
- ✅ Pontas arredondadas em todos os segmentos (`stroke-linecap: round`)
- ✅ Poucos dados (5 categorias apenas)
- ✅ Gaps de 1-2px entre segmentos (branco)
- ✅ Controle pixel-perfect do stroke (16px)

**Vantagens**: 
- Controle total sobre gaps e pontas arredondadas
- Bundle menor (sem biblioteca pesada)
- Animações CSS customizadas simples

**Desvantagens**: 
- Matemática manual (cálculo de `stroke-dasharray` e `stroke-dashoffset`)
- Sem escalas automáticas (mas não precisamos)

**[ ] ESTRATÉGIA B: Biblioteca (Recharts/VisX/Chart.js)**
- ❌ Recharts não suporta gaps precisos e stroke-linecap customizado
- ❌ Maior bundle size
- ❌ Menos controle sobre estética fina

---

**✅ DECISÃO FINAL**: **ESTRATÉGIA A - SVG Artesanal**

**JUSTIFICATIVA**:
O design exige características específicas que bibliotecas não suportam bem:
1. Gaps de 1-2px entre segmentos (difícil em Recharts)
2. Pontas arredondadas em TODOS os segmentos (`stroke-linecap: round`)
3. Stroke fixo de 16px
4. Apenas 5 segmentos (dados simples)
5. Controle pixel-perfect é prioridade

**IMPLEMENTAÇÃO PLANEJADA**:

```typescript
// Abordagem: SVG <circle> com stroke-dasharray
// Cada segmento = <circle> separado com:
// - cx, cy: centro (125, 125)
// - r: raio (100px para stroke 16px = diâmetro 232px)
// - stroke-width: 16
// - stroke-linecap: round
// - stroke-dasharray: [segmentLength, gapLength, restOfCircle]
// - stroke-dashoffset: rotação para posição correta

// Cálculo matemático:
// Circunferência: 2 * PI * r = 2 * 3.14159 * 100 = 628.32
// Percentual 43% = 628.32 * 0.43 = 270.18
// Gap de 2px entre segmentos

// Animação: CSS @keyframes para crescer de 0 to 100%
```

#### Outros Elementos de Dados: Progress Bars

**DECISÃO**: **CSS Puro (não precisa de biblioteca)**

**Implementação**:
- Container: `<div>` com background `#E5E7EB`, height 12px, rounded-full
- Fill: `<div>` interno com width = percentage, background colorido, rounded-full
- Transição CSS para animar mudanças de valor

---

### 3. MODELAGEM DE DADOS (TYPESCRIPT)

#### 3.1 Interfaces Principais

```typescript
// Interface para usuário
interface User {
  id: string;
  name: string;
  avatar: string; // URL
}

// Interface para categoria
interface Category {
  id: string;
  label: string;
  color: string; // HEX color
  percentage: number; // 0-100
  type: 'savings' | 'expenses';
}

// Interface para dados do gráfico donut
interface DonutChartData {
  label: string;
  value: number; // valor monetário
  color: string; // HEX
  percentage: number; // calculado
}

// Interface para dados da carteira
interface WalletData {
  month: string; // "September 2026"
  saved: number; // 327.50
  total: number; // 1000
  categories: Category[];
}

// Interface para navegação
interface NavTab {
  id: string;
  icon: React.ElementType; // Lucide icon
  label: string;
  active: boolean;
}
```

#### 3.2 Constantes & Mocks

```typescript
// Dados mockados para desenvolvimento

export const MOCK_USER: User = {
  id: '1',
  name: 'Vadim Portnyagin',
  avatar: 'https://i.pravatar.cc/150?u=vadim'
};

export const MOCK_WALLET_DATA: WalletData = {
  month: 'September 2026',
  saved: 327.50,
  total: 1000,
  categories: [
    {
      id: '1',
      label: 'Home',
      color: '#3B82F6', // blue
      percentage: 43,
      type: 'savings'
    },
    {
      id: '2',
      label: 'Shopping',
      color: '#10B981', // green
      percentage: 25,
      type: 'savings'
    },
    {
      id: '3',
      label: 'Nutrition',
      color: '#10B981', // green
      percentage: 20,
      type: 'expenses'
    },
    {
      id: '4',
      label: 'Health',
      color: '#8B5CF6', // purple
      percentage: 8,
      type: 'expenses'
    },
    {
      id: '5',
      label: 'Home',
      color: '#EC4899', // pink
      percentage: 4,
      type: 'expenses'
    }
  ]
};

export const MOCK_DONUT_DATA: DonutChartData[] = [
  { label: 'Home', value: 430, color: '#10B981', percentage: 43 },
  { label: 'Shopping', value: 250, color: '#3B82F6', percentage: 25 },
  { label: 'Nutrition', value: 200, color: '#8B5CF6', percentage: 20 },
  { label: 'Health', value: 80, color: '#F97316', percentage: 8 },
  { label: 'Home', value: 40, color: '#EC4899', percentage: 4 }
];

export const NAV_TABS: NavTab[] = [
  { id: 'home', icon: 'Home', label: 'Home', active: true },
  { id: 'chart', icon: 'BarChart3', label: 'Chart', active: false },
  { id: 'user', icon: 'User', label: 'Profile', active: false },
  { id: 'add', icon: 'Plus', label: 'Add', active: false }
];

// Cores da paleta (para fácil referência)
export const COLORS = {
  background: '#F7F8FA',
  surface: '#FFFFFF',
  primary: '#3B82F6',
  success: '#10B981',
  purple: '#8B5CF6',
  orange: '#F97316',
  pink: '#EC4899',
  textPrimary: '#111827',
  textSecondary: '#6B7280',
  textDisabled: '#9CA3AF',
  border: '#E5E7EB'
} as const;
```

---

### 4. STACK TÉCNICA DEFINIDA

#### 4.1 Core
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: useState local (sem necessidade de Zustand para MVP)

#### 4.2 Bibliotecas Específicas
- **Ícones**: `lucide-react` (Home, BarChart3, User, Plus, ChevronDown)
- **Gráficos**: SVG puro (sem biblioteca)
- **Animações**: CSS puro + Tailwind transitions
- **Formulários**: N/A (não tem forms nesta tela)
- **Datas**: Não necessário (apenas display)

#### 4.3 Estrutura de Pastas Proposta

```
/app
  /history
    /page.tsx                      # Página principal History
/components
  /atoms
    /Avatar.tsx                    # Avatar circular
    /Badge.tsx                     # Dot colorido
    /IconButton.tsx                # Botão com ícone
    /ProgressBar.tsx               # Barra de progresso
    /MonthSelector.tsx             # Dropdown de mês
  /molecules
    /CategoryRow.tsx               # Badge + Label + ProgressBar + %
    /StatCard.tsx                  # Card branco
    /HeaderBar.tsx                 # Header com avatar
    /SectionHeader.tsx             # Título de seção
  /organisms
    /DonutChart.tsx                # Gráfico SVG artesanal
    /CategoryList.tsx              # Lista de CategoryRow
    /BottomNavigation.tsx          # Tab bar inferior
    /WalletSummaryCard.tsx         # Card principal completo
  /templates
    /MobileHistoryLayout.tsx       # Layout da página
/lib
  /utils.ts                        # Funções helper (ex: calcular stroke-dasharray)
  /constants.ts                    # Cores, mocks, configs
/types
  /index.ts                        # Interfaces TypeScript (User, WalletData, etc)
```

---

### 5. CONSIDERAÇÕES TÉCNICAS ESPECIAIS

#### 5.1 Performance
- [X] Lazy loading: Não necessário (tela pequena)
- [X] Memoização: React.memo para DonutChart (cálculos SVG)
- [ ] Virtualization: N/A (5 categorias apenas)

#### 5.2 Acessibilidade
- [X] ARIA labels para gráfico SVG (`role="img"`, `aria-label="Wallet breakdown"`)
- [X] Keyboard navigation no bottom nav (tab + enter)
- [X] Focus states visíveis (ring-2 ring-blue-500)
- [X] Contraste de cores adequado:
  - Background #F7F8FA vs Text #111827: ✅ 11.4:1 (AAA)
  - Blue #3B82F6 vs White: ✅ 4.5:1 (AA)

#### 5.3 Responsividade
- [X] Mobile-first (320px - 428px width)
- [ ] Breakpoints customizados: Não necessário para MVP
- [X] Gráfico responsivo: viewBox preserva aspect ratio
- [X] Touch-friendly: Botões > 44px (tab bar icons 48x48px)

#### 5.4 Animações
- [X] Animação de entrada do gráfico: `@keyframes grow` (stroke-dashoffset 0 to 100%)
- [X] Transições de estado: `transition-all duration-300 ease-out`
- [X] Progress bars: `transition-width duration-500`
- [X] Loading states: Skeleton opcional (não no MVP)

---

### 6. RISCOS E DESAFIOS TÉCNICOS

#### Desafio 1: Cálculo preciso do stroke-dasharray para gaps
- **Problema**: Gaps de 1-2px entre segmentos requer matemática exata
- **Solução**: Helper function `calculateDonutSegments(data, gapSize)`
  ```typescript
  // Pseudo-código
  const circumference = 2 * Math.PI * radius;
  const gapInPercent = (gapSize / circumference) * 100;
  for each segment:
    segmentLength = (percentage - gapInPercent) * circumference / 100;
    dashArray = [segmentLength, gapLength, restOfCircle];
  ```
- **Esforço Estimado**: 2 horas

#### Desafio 2: Pontas arredondadas em segmentos pequenos (<5%)
- **Problema**: Segmento de 4% com pontas arredondadas pode parecer "bolinha"
- **Solução**: Condicional - se percentage < 5%, usar `stroke-linecap: butt`
- **Esforço Estimado**: 30 minutos

#### Desafio 3: Texto centralizado preciso no donut
- **Problema**: SVG text alignment pode variar entre browsers
- **Solução**: Usar `<foreignObject>` com div Tailwind (melhor controle)
  ```html
  <foreignObject x="50" y="100" width="150" height="100">
    <div className="text-center">
      <p className="text-xs text-gray-400">September 2026</p>
      <p className="text-4xl font-bold">$327.50</p>
    </div>
  </foreignObject>
  ```
- **Esforço Estimado**: 1 hora

#### Desafio 4: Bottom navigation fixa sem scroll
- **Problema**: Garantir que bottom nav fique fixo mesmo com overflow de conteúdo
- **Solução**: Layout com `flex flex-col min-h-screen` + `flex-1` no content
- **Esforço Estimado**: 15 minutos

---

### 7. DETALHAMENTO DE COMPONENTES CRÍTICOS

#### 7.1 DonutChart Component

**Props:**
```typescript
interface DonutChartProps {
  data: DonutChartData[];
  centerText: {
    title: string;      // "$327.50"
    subtitle: string;   // "September 2026"
    caption: string;    // "saved out of $1000"
  };
  size?: number;        // Default: 250px
  strokeWidth?: number; // Default: 16px
  gapSize?: number;     // Default: 2px
}
```

**Lógica Interna:**
1. Calcular circunferência: `2 * PI * (size/2 - strokeWidth/2)`
2. Para cada segmento, calcular `stroke-dasharray`:
   - Comprimento do segmento: `circumference * (percentage/100) - gapSize`
   - Gap: `gapSize`
   - Resto: `circumference - (segmentLength + gapSize)`
3. Calcular `stroke-dashoffset` para rotacionar segmento corretamente
4. Renderizar `<circle>` para cada segmento com animação CSS

**SVG Structure:**
```html
<svg viewBox="0 0 250 250">
  <!-- Segmento 1 -->
  <circle
    cx="125" cy="125" r="109"
    stroke="#10B981"
    strokeWidth="16"
    strokeLinecap="round"
    strokeDasharray="270 2 356.32"
    strokeDashoffset="0"
    transform="rotate(-90 125 125)"
    className="animate-grow"
  />
  <!-- Repetir para cada segmento -->
  
  <!-- Texto central -->
  <foreignObject x="50" y="90" width="150" height="80">
    <div className="flex flex-col items-center justify-center">
      <p className="text-xs text-gray-400">September 2026</p>
      <p className="text-4xl font-bold text-gray-900">$327.50</p>
      <p className="text-xs text-gray-400">saved out of $1000</p>
    </div>
  </foreignObject>
</svg>
```

#### 7.2 CategoryRow Component

**Props:**
```typescript
interface CategoryRowProps {
  label: string;
  color: string;
  percentage: number;
  icon?: 'dot' | 'icon'; // Default: 'dot'
}
```

**Structure:**
```html
<div className="flex items-center gap-3">
  <!-- Badge (dot colorido) -->
  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
  
  <!-- Label -->
  <span className="text-sm font-medium text-gray-900">{label}</span>
  
  <!-- Spacer -->
  <div className="flex-1" />
  
  <!-- Progress Bar -->
  <div className="w-32 h-3 bg-gray-200 rounded-full overflow-hidden">
    <div 
      className="h-full rounded-full transition-all duration-500"
      style={{ 
        width: `${percentage}%`, 
        backgroundColor: color 
      }}
    />
  </div>
  
  <!-- Percentage -->
  <span className="text-xs font-medium w-10 text-right" style={{ color }}>
    {percentage}%
  </span>
</div>
```

---

## ✅ CHECKLIST DE QUALIDADE

- [X] Todos os componentes foram mapeados (Atomic Design)
- [X] Estratégia de gráficos foi decidida (SVG Artesanal) e justificada
- [X] Interfaces TypeScript foram definidas completamente
- [X] Stack técnica está completa (Next.js + Tailwind + Lucide)
- [X] Riscos técnicos foram identificados e mitigados
- [X] Componentes críticos (DonutChart, CategoryRow) foram detalhados

---

## 🚀 PRÓXIMO PASSO

Após validar esta arquitetura, avançar para:
1. **PRD Completo** (documentar requisitos funcionais)
2. **TECH SPEC Completo** (código copy-paste ready)
3. **03_CONSTRUCTION_GUIDE.md** (implementação passo a passo)
