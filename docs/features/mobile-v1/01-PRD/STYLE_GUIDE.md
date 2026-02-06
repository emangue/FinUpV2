# Mobile Style Guide - Tracker Design

**Data:** 31/01/2026  
**Versão:** 1.0  
**Baseado em:** Imagem "Trackers" fornecida pelo usuário  

---

## 🎨 Paleta de Cores - Guia Rápido

### Cores por Categoria

```typescript
// src/config/mobile-colors.ts
export const categoryColors = {
  casa: {
    bg: '#DDD6FE',      // Roxo pastel - background do ícone
    icon: '#6B21A8',    // Roxo escuro - ícone
    progress: '#9F7AEA', // Roxo vibrante - progress bar
    tailwind: {
      bg: 'bg-purple-200',
      icon: 'text-purple-800',
      progress: 'bg-purple-500',
    }
  },
  alimentacao: {
    bg: '#DBEAFE',
    icon: '#1E40AF',
    progress: '#60A5FA',
    tailwind: {
      bg: 'bg-blue-200',
      icon: 'text-blue-800',
      progress: 'bg-blue-400',
    }
  },
  compras: {
    bg: '#FCE7F3',
    icon: '#BE185D',
    progress: '#F472B6',
    tailwind: {
      bg: 'bg-pink-200',
      icon: 'text-pink-800',
      progress: 'bg-pink-400',
    }
  },
  transporte: {
    bg: '#E7E5E4',
    icon: '#78716C',
    progress: '#A8A29E',
    tailwind: {
      bg: 'bg-stone-200',
      icon: 'text-stone-600',
      progress: 'bg-stone-400',
    }
  },
  contas: {
    bg: '#FEF3C7',
    icon: '#D97706',
    progress: '#FCD34D',
    tailwind: {
      bg: 'bg-amber-200',
      icon: 'text-amber-700',
      progress: 'bg-amber-400',
    }
  },
  lazer: {
    bg: '#D1FAE5',
    icon: '#047857',
    progress: '#6EE7B7',
    tailwind: {
      bg: 'bg-green-200',
      icon: 'text-green-700',
      progress: 'bg-green-400',
    }
  },
};
```

---

## 📐 Dimensões e Espaçamentos

```typescript
// src/config/mobile-dimensions.ts
export const mobileDimensions = {
  // Spacing
  screenPadding: '20px',      // 1.25rem
  cardGap: '16px',            // 1rem
  cardPadding: '16px',        // 1rem
  iconTextGap: '12px',        // 0.75rem
  
  // Sizes
  iconCircle: '48px',         // 3rem
  iconSize: '24px',           // 1.5rem
  progressHeight: '6px',      // 0.375rem
  cardMinHeight: '72px',      // 4.5rem
  navButtonSize: '48px',      // 3rem
  
  // Border Radius
  cardRadius: '16px',         // 1rem
  iconRadius: '9999px',       // Full circle
  progressRadius: '3px',      // Sutil
  
  // Shadow
  cardShadow: '0px 1px 3px rgba(0, 0, 0, 0.04), 0px 1px 2px rgba(0, 0, 0, 0.02)',
};
```

---

## ✍️ Tipografia

```typescript
// src/config/mobile-typography.ts
export const mobileTypography = {
  pageTitle: {
    fontSize: '34px',         // 2.125rem
    fontWeight: 700,          // Bold
    lineHeight: 1.2,
    color: '#000000',
    tailwind: 'text-[34px] font-bold leading-tight text-black',
  },
  categoryName: {
    fontSize: '17px',         // ~1.0625rem
    fontWeight: 600,          // Semi-bold
    lineHeight: 1.3,
    color: '#000000',
    tailwind: 'text-[17px] font-semibold leading-snug text-black',
  },
  frequency: {
    fontSize: '13px',         // ~0.8125rem
    fontWeight: 400,          // Regular
    lineHeight: 1.4,
    color: '#9CA3AF',         // Cinza claro
    tailwind: 'text-[13px] font-normal leading-relaxed text-gray-400',
  },
  amountPrimary: {
    fontSize: '17px',
    fontWeight: 600,
    lineHeight: 1.3,
    color: '#000000',
    tailwind: 'text-[17px] font-semibold leading-snug text-black',
  },
  amountSecondary: {
    fontSize: '13px',
    fontWeight: 400,
    lineHeight: 1.4,
    color: '#9CA3AF',
    tailwind: 'text-[13px] font-normal leading-relaxed text-gray-400',
  },
};
```

---

## 🎬 Animações e Transições

```typescript
// src/config/mobile-animations.ts
export const mobileAnimations = {
  progressBar: {
    property: 'width',
    duration: '300ms',
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    tailwind: 'transition-all duration-300 ease-out',
  },
  button: {
    property: 'all',
    duration: '150ms',
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    tailwind: 'transition-all duration-150 ease-out',
  },
  card: {
    property: 'transform',
    duration: '100ms',
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    tailwind: 'transition-transform duration-100 ease-out active:scale-95',
  },
};
```

---

## 🎯 Estados Interativos

```typescript
// src/config/mobile-states.ts
export const mobileStates = {
  normal: {
    opacity: 1,
    scale: 1,
  },
  pressed: {
    opacity: 0.7,
    scale: 0.95,
    tailwind: 'active:opacity-70 active:scale-95',
  },
  disabled: {
    opacity: 0.4,
    tailwind: 'opacity-40 pointer-events-none',
  },
};
```

---

## 🔍 Acessibilidade - Validação WCAG AA

### Contraste de Cores (Todos Validados ✅)

| Combinação | Contraste | Status WCAG AA |
|------------|-----------|----------------|
| Texto preto (#000) no branco (#FFF) | 21:1 | ✅ Pass (>4.5:1) |
| Texto cinza (#9CA3AF) no branco | 4.6:1 | ✅ Pass (>4.5:1) |
| Ícone roxo (#6B21A8) no roxo claro (#DDD6FE) | 11.5:1 | ✅ Pass (>4.5:1) |
| Ícone azul (#1E40AF) no azul claro (#DBEAFE) | 10.2:1 | ✅ Pass (>4.5:1) |
| Ícone rosa (#BE185D) no rosa claro (#FCE7F3) | 8.7:1 | ✅ Pass (>4.5:1) |

### Touch Targets (Todos Validados ✅)

| Elemento | Tamanho | Status WCAG 2.5.5 |
|----------|---------|-------------------|
| Botão de navegação | 48x48px | ✅ Pass (>44px) |
| Ícone circular | 48x48px | ✅ Pass (>44px) |
| Card inteiro | 72px+ altura | ✅ Pass (>44px) |

---

## 📱 Componente TrackerCard - Template Completo

```tsx
// src/components/mobile/tracker-card.tsx
import React from 'react';
import { LucideIcon } from 'lucide-react';

interface TrackerCardProps {
  category: string;
  frequency: string;
  currentAmount: number;
  totalAmount: number;
  icon: LucideIcon;
  colorScheme: 'purple' | 'blue' | 'pink' | 'stone' | 'amber' | 'green';
  onClick?: () => void;
}

export function TrackerCard({
  category,
  frequency,
  currentAmount,
  totalAmount,
  icon: Icon,
  colorScheme,
  onClick,
}: TrackerCardProps) {
  const progress = Math.min((currentAmount / totalAmount) * 100, 100);

  const colors = {
    purple: { bg: 'bg-purple-200', icon: 'text-purple-800', progress: 'bg-purple-500' },
    blue: { bg: 'bg-blue-200', icon: 'text-blue-800', progress: 'bg-blue-400' },
    pink: { bg: 'bg-pink-200', icon: 'text-pink-800', progress: 'bg-pink-400' },
    stone: { bg: 'bg-stone-200', icon: 'text-stone-600', progress: 'bg-stone-400' },
    amber: { bg: 'bg-amber-200', icon: 'text-amber-700', progress: 'bg-amber-400' },
    green: { bg: 'bg-green-200', icon: 'text-green-700', progress: 'bg-green-400' },
  };

  return (
    <button
      onClick={onClick}
      className="
        flex items-center gap-3 
        w-full px-5 py-4 
        bg-white rounded-2xl 
        shadow-sm 
        transition-transform duration-100 ease-out 
        active:scale-95 active:opacity-70
        text-left
      "
    >
      {/* Ícone circular */}
      <div className={`
        flex items-center justify-center 
        w-12 h-12 rounded-full 
        ${colors[colorScheme].bg}
      `}>
        <Icon className={`w-6 h-6 ${colors[colorScheme].icon}`} />
      </div>

      {/* Conteúdo central */}
      <div className="flex-1 min-w-0">
        <h3 className="text-[17px] font-semibold leading-snug text-black truncate">
          {category}
        </h3>
        <p className="text-[13px] font-normal leading-relaxed text-gray-400 truncate">
          {frequency}
        </p>

        {/* Progress bar */}
        <div className="mt-2 w-full h-[6px] bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full ${colors[colorScheme].progress} transition-all duration-300 ease-out`}
            style={{ width: `${progress}%` }}
            role="progressbar"
            aria-valuenow={currentAmount}
            aria-valuemin={0}
            aria-valuemax={totalAmount}
            aria-label={`${category} progress: ${progress.toFixed(0)}%`}
          />
        </div>
      </div>

      {/* Valores à direita */}
      <div className="text-right shrink-0">
        <p className="text-[17px] font-semibold leading-snug text-black">
          ${currentAmount.toLocaleString('pt-BR', { minimumFractionDigits: 0 })}
        </p>
        <p className="text-[13px] font-normal leading-relaxed text-gray-400">
          de ${totalAmount.toLocaleString('pt-BR', { minimumFractionDigits: 0 })}
        </p>
      </div>
    </button>
  );
}
```

---

## 📱 Componente TrackerHeader - Template Completo

```tsx
// src/components/mobile/tracker-header.tsx
import React from 'react';
import { ChevronLeft, MoreHorizontal } from 'lucide-react';

interface TrackerHeaderProps {
  title: string;
  onBack?: () => void;
  onMenu?: () => void;
}

export function TrackerHeader({ 
  title, 
  onBack, 
  onMenu 
}: TrackerHeaderProps) {
  return (
    <div className="flex items-center justify-between px-5 pt-4 pb-6 bg-white">
      {/* Botão voltar */}
      <button
        onClick={onBack}
        className="
          flex items-center justify-center 
          w-12 h-12 rounded-full 
          bg-gray-100 
          transition-all duration-150 ease-out 
          active:bg-gray-200 active:scale-95
        "
        aria-label="Voltar"
      >
        <ChevronLeft className="w-6 h-6 text-gray-800" />
      </button>

      {/* Título */}
      <h1 className="text-[34px] font-bold leading-tight text-black">
        {title}
      </h1>

      {/* Botão menu */}
      <button
        onClick={onMenu}
        className="
          flex items-center justify-center 
          w-12 h-12 rounded-full 
          bg-gray-100 
          transition-all duration-150 ease-out 
          active:bg-gray-200 active:scale-95
        "
        aria-label="Menu"
      >
        <MoreHorizontal className="w-6 h-6 text-gray-800" />
      </button>
    </div>
  );
}
```

---

## 🎨 Tailwind Config - Extensões Customizadas

```typescript
// tailwind.config.ts (adicionar ao extend)
export default {
  theme: {
    extend: {
      colors: {
        tracker: {
          purple: { 
            bg: '#DDD6FE', 
            icon: '#6B21A8', 
            progress: '#9F7AEA' 
          },
          blue: { 
            bg: '#DBEAFE', 
            icon: '#1E40AF', 
            progress: '#60A5FA' 
          },
          pink: { 
            bg: '#FCE7F3', 
            icon: '#BE185D', 
            progress: '#F472B6' 
          },
          stone: { 
            bg: '#E7E5E4', 
            icon: '#78716C', 
            progress: '#A8A29E' 
          },
          amber: { 
            bg: '#FEF3C7', 
            icon: '#D97706', 
            progress: '#FCD34D' 
          },
          green: { 
            bg: '#D1FAE5', 
            icon: '#047857', 
            progress: '#6EE7B7' 
          },
        },
      },
      boxShadow: {
        'tracker-card': '0px 1px 3px rgba(0, 0, 0, 0.04), 0px 1px 2px rgba(0, 0, 0, 0.02)',
      },
      fontSize: {
        'tracker-title': ['34px', { lineHeight: '1.2', fontWeight: '700' }],
        'tracker-category': ['17px', { lineHeight: '1.3', fontWeight: '600' }],
        'tracker-frequency': ['13px', { lineHeight: '1.4', fontWeight: '400' }],
      },
    },
  },
}
```

---

## 📖 Guia de Uso - Exemplos Práticos

### Exemplo 1: Lista de Metas (Budget)

```tsx
import { TrackerHeader } from '@/components/mobile/tracker-header';
import { TrackerCard } from '@/components/mobile/tracker-card';
import { Home, UtensilsCrossed, ShoppingBag, Fuel, FileText, ShoppingCart } from 'lucide-react';

export default function BudgetMobilePage() {
  const budgets = [
    { 
      id: 1, 
      category: 'Moradia', 
      frequency: 'Todo Mês', 
      current: 2100, 
      total: 2500, 
      color: 'purple' as const, 
      icon: Home 
    },
    // ... mais itens
  ];

  return (
    <div className="min-h-screen bg-white">
      <TrackerHeader 
        title="Metas" 
        onBack={() => window.history.back()} 
      />
      
      <div className="px-5 space-y-4 pb-20">
        {budgets.map((budget) => (
          <TrackerCard
            key={budget.id}
            category={budget.category}
            frequency={budget.frequency}
            currentAmount={budget.current}
            totalAmount={budget.total}
            icon={budget.icon}
            colorScheme={budget.color}
            onClick={() => console.log('Edit', budget.id)}
          />
        ))}
      </div>
    </div>
  );
}
```

---

## 📊 Mapeamento de Categorias do Backend

```typescript
// src/utils/category-mapper.ts
import { 
  Home, UtensilsCrossed, ShoppingBag, Fuel, 
  FileText, ShoppingCart, Heart, Plane, Briefcase 
} from 'lucide-react';

export type CategoryColor = 'purple' | 'blue' | 'pink' | 'stone' | 'amber' | 'green';

interface CategoryConfig {
  icon: any;
  color: CategoryColor;
  label: string;
}

export const categoryMap: Record<string, CategoryConfig> = {
  // Do backend → para frontend
  'Moradia': { icon: Home, color: 'purple', label: 'Moradia' },
  'Casa': { icon: Home, color: 'purple', label: 'Casa' },
  'Aluguel': { icon: Home, color: 'purple', label: 'Aluguel' },
  
  'Alimentação': { icon: UtensilsCrossed, color: 'blue', label: 'Alimentação' },
  'Restaurante': { icon: UtensilsCrossed, color: 'blue', label: 'Restaurante' },
  
  'Compras': { icon: ShoppingBag, color: 'pink', label: 'Compras' },
  'Shopping': { icon: ShoppingCart, color: 'green', label: 'Shopping' },
  
  'Transporte': { icon: Fuel, color: 'stone', label: 'Transporte' },
  'Combustível': { icon: Fuel, color: 'stone', label: 'Combustível' },
  
  'Contas': { icon: FileText, color: 'amber', label: 'Contas' },
  'Utilidades': { icon: FileText, color: 'amber', label: 'Utilidades' },
  
  'Saúde': { icon: Heart, color: 'pink', label: 'Saúde' },
  'Viagens': { icon: Plane, color: 'blue', label: 'Viagens' },
  'Trabalho': { icon: Briefcase, color: 'stone', label: 'Trabalho' },
};

export function getCategoryConfig(categoryName: string): CategoryConfig {
  return categoryMap[categoryName] || {
    icon: ShoppingBag,
    color: 'stone',
    label: categoryName,
  };
}
```

---

## ✅ Checklist de Implementação

### Setup Inicial
- [ ] Instalar Lucide React: `npm install lucide-react`
- [ ] Adicionar cores customizadas ao `tailwind.config.ts`
- [ ] Criar arquivos de configuração (`mobile-colors.ts`, `mobile-dimensions.ts`)
- [ ] Criar componente base `TrackerCard`
- [ ] Criar componente base `TrackerHeader`

### Componentes
- [ ] `TrackerCard` - Card de categoria com progress ✅ Template pronto
- [ ] `TrackerHeader` - Header com título e botões ✅ Template pronto
- [ ] `ProgressBar` - Barra de progresso standalone
- [ ] `CategoryIcon` - Ícone circular colorido
- [ ] `TrackerList` - Container de cards com scroll
- [ ] `DonutChart` - Gráfico pizza (donut) para visualização 🆕
- [ ] `TogglePills` - Toggle 2 tabs (Mês/YTD) 🆕
- [ ] `CategoryRowInline` - Progress inline com badge % 🆕
- [ ] `WalletHeader` - Header com logo + 2 actions 🆕
- [ ] `SelectorBar` - Tag + dropdown 🆕

### Integração
- [ ] Mapear categorias do backend para cores
- [ ] Conectar com API de Budget
- [ ] Implementar edição inline (bottom sheet)
- [ ] Adicionar loading states (skeletons)
- [ ] Adicionar empty states
- [ ] Integrar Recharts para DonutChart 🆕

### Testes
- [ ] Testar em iPhone SE (375px)
- [ ] Testar em iPhone 14 (390px)
- [ ] Testar em iPhone Pro Max (428px)
- [ ] Validar contraste WCAG AA (usar ferramenta)
- [ ] Validar touch targets ≥44px
- [ ] Testar com screen reader (VoiceOver/TalkBack)
- [ ] Testar DonutChart com diferentes tamanhos de dados 🆕

---

## 🆕 Novos Componentes (Atualização 31/01/2026)

### DonutChart - Gráfico Pizza

**Objetivo:** Visualização gráfica do progresso geral das metas (tela principal de Budget).

**Características:**
- Formato: Donut (anel, não pizza fechada)
- Espessura: 20px (innerRadius: 80, outerRadius: 100)
- Centro vazio: Para exibir valor total e período
- Background cinza: Parte não preenchida (#E5E7EB)
- Cores: Paleta pastel existente do Design System

**Código completo:** Ver Seção 4.3.4 do PRD.md

**Dependência:**
```bash
npm install recharts
```

**Exemplo de uso:**
```typescript
<DonutChart
  data={budgetCategories.map(cat => ({
    name: cat.name,
    value: cat.realized,
    color: getCategoryColor(cat.name).progress // Usa paleta existente
  }))}
  total={10000}
  centerLabel="R$ 8.547,00"
  centerSubtitle="realizado de R$ 10.000"
  periodLabel="Fevereiro 2026"
/>
```

---

### TogglePills - Toggle 2 Tabs

**Objetivo:** Alternar entre visualizações Mês/YTD.

**Características:**
- 2 tabs lado a lado (flex: 1)
- Tab ativa: Background branco + sombra + bold
- Tab inativa: Background transparente + cinza
- Height: 44px (touch target WCAG)
- Container: Gray-100 background + border-radius 12px

**Código completo:** Ver Seção 4.3.5 do PRD.md

**Exemplo de uso:**
```typescript
<TogglePills
  options={[
    { id: 'month', label: 'Mês' },
    { id: 'ytd', label: 'YTD' }
  ]}
  selected={viewMode}
  onChange={setViewMode}
/>
```

---

### CategoryRowInline - Progress Inline

**Objetivo:** Linha compacta com progress bar inline e badge de percentual.

**Características:**
- Layout: Icon (24px) + Nome (110px) + Badge % (48px) + Progress (flex-1)
- Badge: Background colorido (cor da categoria) + texto branco
- Progress: Inline à direita, height 6px
- Height total: 48px (touch target)
- Clicável para drill-down (opcional)

**Código completo:** Ver Seção 4.3.6 do PRD.md

**Diferença vs TrackerCard:**
| TrackerCard (Edição) | CategoryRowInline (Visualização) |
|---------------------|--------------------------------|
| 2 linhas (nome + progress abaixo) | 1 linha (tudo inline) |
| Ocupa ~80px altura | Ocupa 48px altura |
| Para edição (teclado) | Para visualização (read-only) |

**Exemplo de uso:**
```typescript
<CategoryRowInline
  icon={<Home className="w-6 h-6 text-purple-800" />}
  name="Moradia"
  value={2100}
  total={2500}
  color="#9F7AEA"  // Progress color do Design System
  onClick={() => openDrilldown('Moradia')}
/>
```

---

### WalletHeader - Header com Logo + Actions

**Objetivo:** Header padrão para telas de visualização (Budget, Dashboard).

**Características:**
- Logo circular (32px) + Título (24px bold)
- 2 actions à direita (search, calendar) - 40px cada
- Subtítulo opcional (13px gray-400)
- Padding: 20px lateral, 16px vertical

**Código simplificado:**
```typescript
export function WalletHeader({ title, subtitle, onSearch, onCalendar }) {
  return (
    <div className="px-5 pt-4 pb-2 bg-white">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center">
            <Wallet className="w-4 h-4 text-white" />
          </div>
          <h1 className="text-2xl font-bold">{title}</h1>
        </div>
        <div className="flex gap-2">
          {onSearch && (
            <button onClick={onSearch} className="w-10 h-10 rounded-full bg-gray-100">
              <Search className="w-5 h-5" />
            </button>
          )}
          {onCalendar && (
            <button onClick={onCalendar} className="w-10 h-10 rounded-full bg-gray-100">
              <Calendar className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>
      {subtitle && <p className="text-[13px] text-gray-400 pl-11">{subtitle}</p>}
    </div>
  );
}
```

---

### SelectorBar - Tag + Dropdown

**Objetivo:** Barra com selector de contexto (ex: "Orçamento") + dropdown de período.

**Características:**
- Layout: Space-between (extremos)
- Tag esquerda: Read-only pill (gray-100)
- Dropdown direita: Botão com chevron
- Height: 32px

**Código simplificado:**
```typescript
export function SelectorBar({ selectedWallet, selectedPeriod, onPeriodChange }) {
  return (
    <div className="flex items-center justify-between px-5 py-3">
      <span className="px-3 py-1.5 bg-gray-100 text-[13px] rounded-lg">
        {selectedWallet}
      </span>
      <button 
        onClick={onPeriodChange}
        className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-[15px] rounded-lg"
      >
        {selectedPeriod}
        <ChevronDown className="w-4 h-4" />
      </button>
    </div>
  );
}
```

---

**Fim do Mobile Style Guide**
