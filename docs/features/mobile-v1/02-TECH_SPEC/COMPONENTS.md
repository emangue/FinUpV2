# Components Reference - Mobile Experience V1.0

**Data:** 31/01/2026  
**Versão:** 1.0

---

## 1. Índice de Componentes

### 1.1 Componentes Base (Core)
- [MobileHeader](#21-mobileheader) - Header unificado
- [BottomNavigation](#22-bottomnavigation) - Navegação inferior
- [IconButton](#23-iconbutton) - Botão de ícone genérico

### 1.2 Componentes de Filtros
- [MonthScrollPicker](#31-monthscrollpicker) - Scroll horizontal de meses
- [YTDToggle](#32-ytdtoggle) - Toggle Mês/YTD
- [SelectorBar](#33-selectorbar) - Tag + Dropdown (deprecated - usar MonthScrollPicker)

### 1.3 Componentes de Budget
- [TrackerCard](#41-trackercard) - Card de meta (design Trackers)
- [TrackerList](#42-trackerlist) - Lista de TrackerCards
- [CategoryRowInline](#43-categoryrowinline) - Progress inline
- [DonutChart](#44-donutchart) - Gráfico pizza
- [BudgetEditBottomSheet](#45-budgeteditbottomsheet) - Editar valor de meta
- [GrupoBreakdownBottomSheet](#46-grupobreakdownbottomsheet) - Drill-down subgrupos

### 1.4 Componentes de Dashboard
- [MetricCards](#51-metriccards) - Cards de métricas (existente)
- [CategoryExpensesMobile](#52-categoryexpensesmobile) - Top 5 + Demais
- [ChartAreaInteractive](#53-chartareainteractive) - Gráfico de área (existente)

### 1.5 Componentes de Transações
- [TransactionsList](#61-transactionslist) - Lista de transações (existente)
- [TransactionCard](#62-transactioncard) - Card individual de transação
- [TransactionFilterSheet](#63-transactionfiltersheet) - Filtros avançados

---

## 2. Componentes Base (Core)

### 2.1 MobileHeader

**Arquivo:** `src/components/mobile/mobile-header.tsx`

**Descrição:** Header unificado para todas as telas mobile.

**Props:**
```typescript
interface MobileHeaderProps {
  title: string;
  subtitle?: string;
  leftAction?: 'back' | 'logo' | null;
  rightActions?: Action[];
  onBack?: () => void;
  variant?: 'default' | 'centered';
}

interface Action {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}
```

**Uso:**
```tsx
// Dashboard
<MobileHeader 
  title="Dashboard"
  leftAction="logo"
  rightActions={[
    { icon: <Search />, label: 'Buscar', onClick: handleSearch },
    { icon: <Calendar />, label: 'Calendário', onClick: handleCalendar }
  ]}
/>

// Transações
<MobileHeader 
  title="Transações"
  leftAction="back"
  onBack={() => router.back()}
  rightActions={[
    { icon: <MoreHorizontal />, label: 'Filtros', onClick: openFilters }
  ]}
/>
```

**Código completo:** Ver TECH_SPEC.md (não duplicar aqui)

---

### 2.2 BottomNavigation

**Arquivo:** `src/components/mobile/bottom-navigation.tsx`

**Descrição:** Navegação inferior fixa com 5 tabs.

**Props:** Nenhuma (usa `usePathname()` internamente)

**Características:**
- 5 tabs: Dashboard, Transações, Metas, Upload, Profile
- FAB central opcional (Metas destacado)
- Posição fixa (`fixed bottom-0`)
- Altura: 80px (20rem)

**Uso:**
```tsx
// Layout Mobile (app/mobile/layout.tsx)
<div className="min-h-screen bg-white pb-20">
  {children}
  <BottomNavigation />
</div>
```

**Código completo:** Ver TECH_SPEC.md Seção 3.2

---

### 2.3 IconButton

**Arquivo:** `src/components/mobile/icon-button.tsx`

**Descrição:** Botão de ícone genérico reutilizável.

**Props:**
```typescript
interface IconButtonProps {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  variant?: 'default' | 'primary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}
```

**Uso:**
```tsx
<IconButton 
  icon={<Search className="w-5 h-5" />}
  label="Buscar"
  onClick={handleSearch}
  variant="default"
  size="md"
/>
```

**Variantes:**
- `default`: Cinza claro (bg-gray-100)
- `primary`: Preto (bg-black)
- `ghost`: Transparente

**Tamanhos:**
- `sm`: 40px (w-10 h-10)
- `md`: 44px (w-11 h-11) - WCAG mínimo
- `lg`: 56px (w-14 h-14) - FAB

---

## 3. Componentes de Filtros

### 3.1 MonthScrollPicker

**Arquivo:** `src/components/mobile/month-scroll-picker.tsx`

**Descrição:** Scroll horizontal para seleção de mês (substitui dropdown).

**Props:**
```typescript
interface MonthScrollPickerProps {
  selectedYear: number;
  selectedMonth: number;
  onMonthChange: (year: number, month: number) => void;
  disabled?: boolean; // Para desabilitar quando YTD ativo
}
```

**Características:**
- Scroll horizontal com snap to center
- Últimos 12 meses + próximos 3 meses
- Pill selecionada: preto com sombra
- Touch target 44px (WCAG)

**Uso:**
```tsx
<MonthScrollPicker
  selectedYear={2026}
  selectedMonth={2}
  onMonthChange={(year, month) => {
    setSelectedYear(year);
    setSelectedMonth(month);
    fetchMetrics(year, month);
  }}
  disabled={ytdMode === 'ytd'}
/>
```

**Código completo:** Ver PRD Seção 4.1.6

---

### 3.2 YTDToggle

**Arquivo:** `src/components/mobile/ytd-toggle.tsx`

**Descrição:** Toggle para alternar entre visão Mês/YTD.

**Props:**
```typescript
interface YTDToggleProps {
  mode: 'month' | 'ytd';
  onChange: (mode: 'month' | 'ytd') => void;
}
```

**Uso:**
```tsx
<YTDToggle
  mode={viewMode}
  onChange={(mode) => {
    setViewMode(mode);
    if (mode === 'ytd') {
      fetchMetrics(year, null); // YTD
    } else {
      fetchMetrics(year, month); // Mensal
    }
  }}
/>
```

**Visual:**
```
┌─────────────────────────┐
│ [  Mês  ] [  YTD  ]     │ ← Pills lado a lado
│    (ativo)   (inativo)  │
└─────────────────────────┘
```

**Código completo:** Ver PRD Seção 4.3.5

---

### 3.3 SelectorBar

**Arquivo:** `src/components/mobile/selector-bar.tsx`

**Descrição:** Barra com tag + dropdown (deprecated - usar MonthScrollPicker).

**Status:** ⚠️ **DEPRECATED** - Substituído por MonthScrollPicker

**Motivo:** MonthScrollPicker oferece melhor UX mobile (swipe vs 4 toques).

---

## 4. Componentes de Budget

### 4.1 TrackerCard

**Arquivo:** `src/components/mobile/tracker-card.tsx`

**Descrição:** Card de meta com ícone, nome, progress bar e valores.

**Props:**
```typescript
interface TrackerCardProps {
  category: string;
  frequency: string;
  currentAmount: number;
  totalAmount: number;
  icon: LucideIcon;
  colorScheme: CategoryColor;
  onClick?: () => void;
}

type CategoryColor = 'purple' | 'blue' | 'pink' | 'stone' | 'amber' | 'green';
```

**Uso:**
```tsx
<TrackerCard
  category="Moradia"
  frequency="Todo Mês"
  currentAmount={2100}
  totalAmount={2500}
  icon={Home}
  colorScheme="purple"
  onClick={() => openEditSheet('Moradia')}
/>
```

**Layout:**
```
┌────────────────────────────────────┐
│ [🏠]  Moradia           R$ 2.100   │
│       Todo Mês          de R$ 2.500│
│       ██████████░░░░ 84%           │
└────────────────────────────────────┘
```

**Características:**
- Ícone circular 48px
- Progress bar 6px com animação (300ms)
- Touch feedback: scale(0.95)
- Cores do Design System

**Código completo:** Ver MOBILE_STYLE_GUIDE.md

---

### 4.2 TrackerList

**Arquivo:** `src/components/mobile/tracker-list.tsx`

**Descrição:** Container scrollável de TrackerCards.

**Props:**
```typescript
interface TrackerListProps {
  items: TrackerItem[];
  onItemClick?: (item: TrackerItem) => void;
}

interface TrackerItem {
  id: string;
  category: string;
  frequency: string;
  currentAmount: number;
  totalAmount: number;
  icon: LucideIcon;
  colorScheme: CategoryColor;
}
```

**Uso:**
```tsx
<TrackerList
  items={budgets}
  onItemClick={(item) => openEditSheet(item.id)}
/>
```

**Características:**
- Gap de 16px entre cards
- Padding horizontal 20px
- Scroll vertical suave
- Loading skeleton

---

### 4.3 CategoryRowInline

**Arquivo:** `src/components/mobile/category-row-inline.tsx`

**Descrição:** Linha compacta com progress inline e badge de percentual.

**Props:**
```typescript
interface CategoryRowInlineProps {
  icon: React.ReactNode;
  name: string;
  value: number;
  total: number;
  color: string;
  onClick?: () => void;
}
```

**Uso:**
```tsx
<CategoryRowInline
  icon={<Home className="w-6 h-6 text-purple-800" />}
  name="Moradia"
  value={2100}
  total={2500}
  color="#9F7AEA"
  onClick={() => openBreakdown('Moradia')}
/>
```

**Layout:**
```
[🏠] Moradia  [84%] ██████████░░░░
     110px    48px   flex-1
```

**Diferença vs TrackerCard:**
| TrackerCard | CategoryRowInline |
|-------------|-------------------|
| 2 linhas (nome + progress abaixo) | 1 linha (tudo inline) |
| ~80px altura | 48px altura |
| Para edição | Para visualização |

**Código completo:** Ver PRD Seção 4.3.6

---

### 4.4 DonutChart

**Arquivo:** `src/components/mobile/donut-chart.tsx`

**Descrição:** Gráfico pizza (donut) com centro vazio para texto.

**Dependência:** `npm install recharts`

**Props:**
```typescript
interface DonutChartProps {
  data: {
    name: string;
    value: number;
    color: string;
  }[];
  total: number;
  centerLabel: string;       // "R$ 8.547,00"
  centerSubtitle: string;    // "realizado de R$ 10.000"
  periodLabel?: string;      // "Fevereiro 2026"
}
```

**Uso:**
```tsx
<DonutChart
  data={[
    { name: 'Moradia', value: 2100, color: '#DDD6FE' },
    { name: 'Alimentação', value: 1850, color: '#DBEAFE' },
    { name: 'Transporte', value: 950, color: '#E7E5E4' },
  ]}
  total={10000}
  centerLabel="R$ 8.547,00"
  centerSubtitle="realizado de R$ 10.000"
  periodLabel="Fevereiro 2026"
/>
```

**Características:**
- innerRadius: 80, outerRadius: 100
- Segmento cinza para parte não preenchida
- Texto centralizado (absolute positioning)
- Tamanho: 240px

**Código completo:** Ver PRD Seção 4.3.4

---

### 4.5 BudgetEditBottomSheet

**Arquivo:** `src/components/mobile/budget-edit-bottom-sheet.tsx`

**Descrição:** Bottom sheet para editar valor de uma meta.

**Props:**
```typescript
interface BudgetEditBottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  categoria: string;
  valorAtual: number;
  onSave: (novoValor: number) => void;
}
```

**Uso:**
```tsx
<BudgetEditBottomSheet
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  categoria="Alimentação"
  valorAtual={2000}
  onSave={(novoValor) => {
    updateBudget('Alimentação', novoValor);
    toast.success('Meta atualizada!');
  }}
/>
```

**Características:**
- Bottom sheet (posição inferior)
- Input numérico grande (h-14, text-2xl)
- Teclado numérico nativo (inputMode="decimal")
- Auto-focus no input
- Botões: [Cancelar] [Salvar] (h-12)

**Código completo:** Ver TECH_SPEC.md Seção 3.8

---

### 4.6 GrupoBreakdownBottomSheet

**Arquivo:** `src/components/mobile/grupo-breakdown-sheet.tsx`

**Descrição:** Bottom sheet com drill-down de subgrupos.

**Props:**
```typescript
interface GrupoBreakdownBottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  grupo: string;
  year: number;
  month: number;
}
```

**Uso:**
```tsx
<GrupoBreakdownBottomSheet
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  grupo="Cartão de Crédito"
  year={2026}
  month={2}
/>
```

**Comportamento:**
1. useEffect → fetch `/transactions/grupo-breakdown`
2. Loading skeleton (5 itens)
3. Renderiza lista de subgrupos
4. Toque em item → navega para `/transactions?grupo=X&subgrupo=Y`

**Layout:**
```
┌────────────────────────────────────┐
│ Cartão de Crédito                  │
│ Total: R$ 3.200,00                 │
├────────────────────────────────────┤
│ iFood        R$ 850,20  26.6%   → │
│ Uber         R$ 420,00  13.1%   → │
│ Netflix      R$ 55,90    1.7%   → │
│ Spotify      R$ 34,90    1.1%   → │
│ Outros       R$ 1.839   57.5%   → │
└────────────────────────────────────┘
```

**Código completo:** Ver TECH_SPEC.md Seção 3.9

---

## 5. Componentes de Dashboard

### 5.1 MetricCards

**Arquivo:** `src/features/dashboard/components/mobile/metric-cards.tsx`

**Descrição:** Cards de métricas principais (existente, reutilizar).

**Status:** ✅ **JÁ EXISTE** - Apenas validar e melhorar se necessário

**Características:**
- Card Principal: Saldo realizado + trend
- Card Unificado: Receitas e Despesas + Botão "Importar"
- Gráfico colapsável integrado

---

### 5.2 CategoryExpensesMobile

**Arquivo:** `src/components/mobile/category-expenses-mobile.tsx`

**Descrição:** Top 5 categorias + card "Demais" com drill-down.

**Props:**
```typescript
interface CategoryExpensesMobileProps {
  year: number;
  month: number;
  onCategoryClick?: (categoria: string) => void;
}
```

**Uso:**
```tsx
<CategoryExpensesMobile
  year={2026}
  month={2}
  onCategoryClick={(categoria) => {
    if (categoria === 'Demais') {
      openDemaisSheet();
    } else {
      router.push(`/transactions?grupo=${categoria}`);
    }
  }}
/>
```

**Layout:**
```
┌────────────────────────────────────┐
│ Gastos por Categoria (Top 5)      │
├────────────────────────────────────┤
│ 🏠 Moradia      R$ 2.100 (24.5%) → │
│ 🍔 Alimentação  R$ 1.850 (21.6%) → │
│ 🚗 Transporte   R$ 950  (11.1%)  → │
│ 💳 Cartão       R$ 3.200 (37.4%) → │
│ 💊 Saúde        R$ 450   (5.3%)  → │
│ + Demais (5)    R$ 987  (11.5%)  → │
└────────────────────────────────────┘
```

**Características:**
- Reutiliza lógica desktop (budget-vs-actual.tsx linhas 154-190)
- Toque em categoria → navega para /transactions
- Toque em "Demais" → bottom sheet com lista expandida

---

### 5.3 ChartAreaInteractive

**Arquivo:** `src/components/chart-area-interactive.tsx`

**Descrição:** Gráfico de área interativo (existente, reutilizar).

**Status:** ✅ **JÁ EXISTE** - Adaptar para mobile (scroll horizontal)

---

## 6. Componentes de Transações

### 6.1 TransactionsList

**Arquivo:** `src/features/transactions/components/transactions-list.tsx`

**Descrição:** Lista de transações (existente).

**Status:** ✅ **JÁ EXISTE** - Melhorar com bottom sheet de edição

---

### 6.2 TransactionCard

**Arquivo:** `src/components/mobile/transaction-card.tsx`

**Descrição:** Card individual de transação.

**Props:**
```typescript
interface TransactionCardProps {
  transaction: Transaction;
  onClick?: () => void;
}

interface Transaction {
  id: number;
  data: string;
  estabelecimento: string;
  grupo: string;
  subgrupo: string;
  valor: number;
  tipo: 'receita' | 'despesa';
  cartao: string;
}
```

**Layout:**
```
┌────────────────────────────────────┐
│ 15/12 - Mercado São José           │
│ Alimentação                        │
│              R$ 185,40          [⋮]│
└────────────────────────────────────┘
```

---

### 6.3 TransactionFilterSheet

**Arquivo:** `src/components/mobile/transaction-filter-sheet.tsx`

**Descrição:** Bottom sheet com filtros avançados (grupo, subgrupo, cartão).

**Props:**
```typescript
interface TransactionFilterSheetProps {
  isOpen: boolean;
  onClose: () => void;
  onApply: (filters: TransactionFilters) => void;
}

interface TransactionFilters {
  tipo?: 'receita' | 'despesa' | 'todas';
  grupo?: string;
  subgrupo?: string;
  cartao?: string;
  dataInicio?: string;
  dataFim?: string;
}
```

---

## 7. Guia de Estilos - Tailwind Classes

### 7.1 Touch Targets

```typescript
// Mínimo WCAG 2.5.5: 44x44px
'w-11 h-11'  // 44px

// Recomendado para botões primários: 48x48px
'w-12 h-12'  // 48px

// FAB (Floating Action Button): 56x56px
'w-14 h-14'  // 56px
```

---

### 7.2 Spacing

```typescript
// Padding horizontal de tela
'px-5'  // 20px

// Gap entre cards
'gap-4'  // 16px

// Padding de card
'p-4'   // 16px
```

---

### 7.3 Tipografia

```typescript
// Page Title
'text-[34px] font-bold leading-tight text-black'

// Section Title
'text-2xl font-bold leading-snug text-black'

// Category Name
'text-[17px] font-semibold leading-snug text-black'

// Frequency / Secondary
'text-[13px] font-normal leading-relaxed text-gray-400'
```

---

### 7.4 Cores

```typescript
// Backgrounds
'bg-purple-200'  // #DDD6FE
'bg-blue-200'    // #DBEAFE
'bg-pink-200'    // #FCE7F3
'bg-stone-200'   // #E7E5E4
'bg-amber-200'   // #FEF3C7
'bg-green-200'   // #D1FAE5

// Icons
'text-purple-800'  // #6B21A8
'text-blue-800'    // #1E40AF
'text-pink-800'    // #BE185D
'text-stone-600'   // #78716C
'text-amber-700'   // #D97706
'text-green-700'   // #047857

// Progress Bars
'bg-purple-500'  // #9F7AEA
'bg-blue-400'    // #60A5FA
'bg-pink-400'    // #F472B6
'bg-stone-400'   // #A8A29E
'bg-amber-400'   // #FCD34D
'bg-green-400'   // #6EE7B7
```

---

## 8. Checklist de Componente

Ao criar um novo componente mobile, validar:

### 8.1 Acessibilidade (WCAG 2.1 AA)

- [ ] Touch targets ≥ 44px
- [ ] Contraste de cores ≥ 4.5:1
- [ ] ARIA labels em botões de ícones
- [ ] `role` e `aria-*` apropriados
- [ ] Navegação por teclado (tab order)

### 8.2 Performance

- [ ] Lazy loading se possível
- [ ] Memoização (React.memo) se renderizações caras
- [ ] Evitar re-renders desnecessários
- [ ] Bundle size < 50KB

### 8.3 UX Mobile

- [ ] Touch feedback (active:scale-95)
- [ ] Transições suaves (150-300ms)
- [ ] Loading states (skeleton)
- [ ] Empty states
- [ ] Error states

### 8.4 TypeScript

- [ ] Props bem tipadas
- [ ] Sem `any` (usar `unknown` se necessário)
- [ ] Interfaces exportadas
- [ ] Documentação JSDoc

---

## 9. Storybook (Opcional - V2.0)

Para visualizar componentes isoladamente:

```bash
npm install --save-dev @storybook/react @storybook/addon-essentials
npx storybook init
```

**Exemplo:**

```typescript
// src/components/mobile/tracker-card.stories.tsx

import type { Meta, StoryObj } from '@storybook/react';
import { TrackerCard } from './tracker-card';
import { Home } from 'lucide-react';

const meta: Meta<typeof TrackerCard> = {
  title: 'Mobile/TrackerCard',
  component: TrackerCard,
  parameters: {
    layout: 'padded',
  },
};

export default meta;
type Story = StoryObj<typeof TrackerCard>;

export const Default: Story = {
  args: {
    category: 'Moradia',
    frequency: 'Todo Mês',
    currentAmount: 2100,
    totalAmount: 2500,
    icon: Home,
    colorScheme: 'purple',
  },
};

export const OverBudget: Story = {
  args: {
    category: 'Alimentação',
    frequency: 'Todo Mês',
    currentAmount: 2300,
    totalAmount: 2000,
    icon: Home,
    colorScheme: 'blue',
  },
};
```

---

**Fim da Components Reference**

**Data:** 31/01/2026  
**Versão:** 1.0
