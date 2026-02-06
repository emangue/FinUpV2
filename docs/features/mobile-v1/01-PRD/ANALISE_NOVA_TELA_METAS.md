# Análise - Nova Tela de Metas (Wallet History)

**Data:** 31/01/2026 23:30  
**Stakeholder:** Emangue  
**Referência:** Imagem "Wallet History" (#217)

---

## 🎯 Solicitações do Stakeholder

### 1. Copiar layout completo da tela "Wallet History"
> "Gostei e gostaria de copiar o layout completo. Ele está em linha com o que temos hoje de design system ou precisamos de ajustes?"

### 2. Tela de ajuste de metas igual à primeira imagem (Trackers)
> "Para a tela de ajuste das metas, aí acho que faz total sentido usar um layout muito parecido com o da primeira imagem enviada"

---

## 📊 Análise Visual Completa - "Wallet History"

### Mapeamento de Elementos (Top → Bottom)

```
┌─────────────────────────────────────────┐
│ [Header: History] [🔍] [📅]             │ ← Header com título + 2 actions
│ Vadim Portnyagin                        │ ← Subtítulo (username)
├─────────────────────────────────────────┤
│ [Wallet]                  [Month ▼]     │ ← Selector + Dropdown
├─────────────────────────────────────────┤
│                                         │
│        [Gráfico Pizza com Gradiente]    │ ← Donut Chart (80% preenchido)
│             September 2026              │ ← Data centralizada
│            $ 327.50                     │ ← Valor principal (34px bold)
│       saved out of $ 1 000              │ ← Valor meta (13px gray)
│                                         │
├─────────────────────────────────────────┤
│    [Savings]       [Expenses]           │ ← Toggle Tabs (Pills)
├─────────────────────────────────────────┤
│ 🏠 Home          [43%] ████████         │ ← Lista de categorias
│ 🛒 Shopping      [43%] ████████         │   com progress bars inline
│ 🥗 Nutrition     [43%] ████████         │
│ 💊 Health        [43%] ████████         │
│ 🏠 Home          [43%] ████████         │
└─────────────────────────────────────────┘
│ [🏠] [🍕] [👤] [➕ Add]                  │ ← Bottom Nav (FAB azul)
└─────────────────────────────────────────┘
```

---

## 🎨 Análise de Design System - Comparação

### ✅ **COMPATÍVEL** com Design System Atual

| Elemento | Nova Tela (Wallet) | Design System Atual (Trackers) | Status |
|----------|-------------------|-------------------------------|--------|
| **Background** | #FFFFFF (branco) | #FFFFFF | ✅ Igual |
| **Card Radius** | 16px | 16px | ✅ Igual |
| **Screen Padding** | 20px lateral | 20px | ✅ Igual |
| **Icon Circle** | ~48px | 48px | ✅ Igual |
| **Progress Height** | ~6px | 6px | ✅ Igual |
| **Font Title** | 34px bold | 34px bold | ✅ Igual |
| **Font Category** | 17px semibold | 17px semibold | ✅ Igual |
| **Font Subtitle** | 13px gray | 13px gray-400 | ✅ Igual |

### ⚠️ **NOVOS ELEMENTOS** (não estavam no Trackers)

| Elemento | Especificação | Compatível? | Ação |
|----------|--------------|-------------|------|
| **Donut Chart (Pizza)** | Gradiente 5 cores + base cinza | ⚠️ **NOVO** | ✅ Adicionar ao DS |
| **Valor Central Grande** | $327.50 (34px bold preto) | ⚠️ **NOVO** | ✅ Adicionar ao DS |
| **Toggle Pills (Savings/Expenses)** | 2 tabs pill-style | ⚠️ **NOVO** | ✅ Adicionar ao DS |
| **Progress Inline (badge %)** | Badge colorido com % | ⚠️ **PARCIAL** | ⚠️ Ajustar formato |
| **Dropdown "Month"** | Cinza com chevron | ⚠️ **NOVO** | ✅ Adicionar ao DS |
| **Header 3 elementos** | Título + 2 icons (search/calendar) | ⚠️ **NOVO** | ✅ Adicionar ao DS |

---

## 🔍 Detalhamento Técnico - Novos Componentes

### 1. **Donut Chart (Gráfico Pizza)**

**Características visuais:**
- Formato: Donut (anel, não pizza fechada)
- Espessura: ~20px
- Progresso: ~80% preenchido
- Background: Cinza claro (#E5E7EB)
- Cores: 5 segmentos (verde, azul, roxo, laranja, vermelho)
- Centro: Vazio (para texto)

**Cores dos segmentos (extraídas da imagem):**
```typescript
const donutColors = {
  segment1: '#10B981',  // Verde (Home 1)
  segment2: '#3B82F6',  // Azul (Shopping)
  segment3: '#A855F7',  // Roxo (Nutrition)
  segment4: '#F59E0B',  // Laranja (Health)
  segment5: '#EF4444',  // Vermelho (Home 2)
  background: '#E5E7EB' // Cinza base (não preenchido)
};
```

**Specs técnicas:**
```typescript
interface DonutChartProps {
  data: {
    label: string;
    value: number;
    color: string;
  }[];
  total: number;
  centerLabel: string;       // "$ 327.50"
  centerSubtitle: string;    // "saved out of $ 1 000"
  size?: number;             // Default: 200px
  strokeWidth?: number;      // Default: 20px
}
```

**Implementação recomendada:**
- Biblioteca: **Recharts** (já usamos no projeto)
- Componente: `<PieChart>` com `<Pie>` tipo "donut"
- SVG otimizado (melhor que Canvas para mobile)

**Código base (TypeScript/React):**
```typescript
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

export function DonutChart({ data, total, centerLabel, centerSubtitle }: DonutChartProps) {
  const totalValue = data.reduce((sum, item) => sum + item.value, 0);
  const progressPercent = (totalValue / total) * 100;

  return (
    <div className="relative w-full max-w-[200px] mx-auto">
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={70}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
            startAngle={90}
            endAngle={-270}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      
      {/* Centro: Texto sobreposto */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <p className="text-xs text-gray-500 mb-1">{centerSubtitle}</p>
        <p className="text-[34px] font-bold text-black leading-none">{centerLabel}</p>
        <p className="text-sm text-gray-400 mt-1">
          {progressPercent.toFixed(0)}%
        </p>
      </div>
    </div>
  );
}
```

---

### 2. **Toggle Pills (Savings/Expenses)**

**Características visuais:**
- 2 tabs lado a lado
- Tab ativa: Background branco + texto preto + bold
- Tab inativa: Background transparente + texto cinza
- Border radius: 12px
- Height: 44px (touch target)
- Padding: 16px horizontal

**CSS:**
```css
.toggle-pills {
  display: flex;
  gap: 8px;
  padding: 4px;
  background: #F3F4F6;  /* Gray-100 */
  border-radius: 12px;
}

.toggle-pill {
  flex: 1;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 400;
  color: #9CA3AF;  /* Gray-400 */
  background: transparent;
  transition: all 150ms;
  cursor: pointer;
}

.toggle-pill.active {
  background: #FFFFFF;
  color: #000000;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

**TypeScript:**
```typescript
interface TogglePillsProps {
  options: { id: string; label: string }[];
  selected: string;
  onChange: (id: string) => void;
}

export function TogglePills({ options, selected, onChange }: TogglePillsProps) {
  return (
    <div className="flex gap-2 p-1 bg-gray-100 rounded-xl">
      {options.map((option) => (
        <button
          key={option.id}
          onClick={() => onChange(option.id)}
          className={cn(
            'flex-1 h-11 rounded-lg text-[15px] transition-all duration-150',
            selected === option.id
              ? 'bg-white text-black font-semibold shadow-sm'
              : 'bg-transparent text-gray-400 font-normal active:bg-gray-200'
          )}
          role="tab"
          aria-selected={selected === option.id}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
```

---

### 3. **Progress Inline com Badge (%)**

**Diferença vs Trackers:**

| Trackers (Anterior) | Wallet (Nova Tela) |
|---------------------|-------------------|
| Progress bar abaixo do nome | Progress inline à direita |
| % não mostrado | Badge colorido com % |
| Ocupa 2 linhas | Ocupa 1 linha |

**Nova estrutura:**
```
┌─────────────────────────────────────────┐
│ [🏠] Home        [43%] ████████░░░░░░   │
│  ↑    ↑           ↑        ↑             │
│ Icon Nome       Badge  Progress bar     │
└─────────────────────────────────────────┘
```

**Specs:**
- Badge: 40px width × 24px height
- Border radius: 6px
- Background: Cor da categoria (ex: azul #3B82F6)
- Text: Branco, 13px semibold
- Progress bar: Inline à direita, height 6px

**CSS:**
```css
.category-row {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 48px;
  padding: 0 20px;
}

.category-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.category-name {
  flex: 0 0 100px;
  font-size: 17px;
  font-weight: 600;
  color: #000;
}

.category-badge {
  width: 48px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #FFF;
  flex-shrink: 0;
}

.category-progress-wrapper {
  flex: 1;
  height: 6px;
  background: #E5E7EB;
  border-radius: 3px;
  overflow: hidden;
}

.category-progress-bar {
  height: 100%;
  transition: width 300ms;
}
```

**TypeScript:**
```typescript
interface CategoryRowProps {
  icon: React.ReactNode;
  name: string;
  percent: number;
  color: string;
}

export function CategoryRow({ icon, name, percent, color }: CategoryRowProps) {
  return (
    <div className="flex items-center gap-3 h-12 px-5">
      {/* Icon */}
      <div className="w-6 h-6 flex-shrink-0">
        {icon}
      </div>
      
      {/* Name */}
      <span className="flex-[0_0_100px] text-[17px] font-semibold text-black truncate">
        {name}
      </span>
      
      {/* Badge % */}
      <div
        className="w-12 h-6 flex items-center justify-center rounded-md text-[13px] font-semibold text-white flex-shrink-0"
        style={{ backgroundColor: color }}
      >
        {percent}%
      </div>
      
      {/* Progress bar inline */}
      <div className="flex-1 h-[6px] bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full transition-all duration-300"
          style={{ width: `${percent}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
```

---

### 4. **Header com 3 Elementos**

**Layout:**
```
┌─────────────────────────────────────────┐
│ [Logo] History          [🔍]  [📅]      │
│        Vadim Portnyagin                 │
└─────────────────────────────────────────┘
```

**Specs:**
- Logo: 32px círculo (preto com ícone branco)
- Título: 24px bold preto
- Subtítulo: 13px gray-400
- Actions: 2 ícones (search, calendar) 24px cada
- Padding: 20px lateral, 16px vertical

**TypeScript:**
```typescript
interface WalletHeaderProps {
  title: string;
  subtitle?: string;
  onSearch?: () => void;
  onCalendar?: () => void;
}

export function WalletHeader({ title, subtitle, onSearch, onCalendar }: WalletHeaderProps) {
  return (
    <div className="px-5 pt-4 pb-2 bg-white">
      <div className="flex items-center justify-between mb-1">
        {/* Logo + Title */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center">
            <Wallet className="w-4 h-4 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-black">{title}</h1>
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-2">
          {onSearch && (
            <button
              onClick={onSearch}
              className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center active:bg-gray-200"
              aria-label="Buscar"
            >
              <Search className="w-5 h-5 text-gray-600" />
            </button>
          )}
          {onCalendar && (
            <button
              onClick={onCalendar}
              className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center active:bg-gray-200"
              aria-label="Calendário"
            >
              <Calendar className="w-5 h-5 text-gray-600" />
            </button>
          )}
        </div>
      </div>
      
      {/* Subtitle */}
      {subtitle && (
        <p className="text-[13px] text-gray-400 pl-11">{subtitle}</p>
      )}
    </div>
  );
}
```

---

### 5. **Selector + Dropdown Inline**

**Layout:**
```
┌─────────────────────────────────────────┐
│ [Wallet]                    [Month ▼]   │
└─────────────────────────────────────────┘
```

**Specs:**
- Selector (Wallet): Tag pill cinza, 13px
- Dropdown (Month): Botão cinza, 15px, chevron down
- Gap: Space-between (ocupam extremos)
- Height: 32px

**TypeScript:**
```typescript
interface SelectorBarProps {
  selectedWallet: string;
  selectedPeriod: string;
  onPeriodChange: (period: string) => void;
}

export function SelectorBar({ selectedWallet, selectedPeriod, onPeriodChange }: SelectorBarProps) {
  return (
    <div className="flex items-center justify-between px-5 py-3">
      {/* Wallet Tag (read-only) */}
      <span className="px-3 py-1.5 bg-gray-100 text-gray-700 text-[13px] font-medium rounded-lg">
        {selectedWallet}
      </span>
      
      {/* Period Dropdown */}
      <button
        onClick={() => onPeriodChange(selectedPeriod)}
        className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 text-[15px] font-medium rounded-lg active:bg-gray-200"
      >
        {selectedPeriod}
        <ChevronDown className="w-4 h-4" />
      </button>
    </div>
  );
}
```

---

## ✅ Compatibilidade com Design System Atual

### Cores

| Categoria | Wallet (Nova) | Trackers (Atual) | Compatível? |
|-----------|--------------|------------------|-------------|
| Home 1 | #3B82F6 (azul) | #DDD6FE (roxo bg) | ⚠️ **Ajustar** |
| Shopping | #F59E0B (laranja) | #FCE7F3 (rosa bg) | ⚠️ **Ajustar** |
| Nutrition | #10B981 (verde) | #D1FAE5 (verde bg) | ✅ **Compatível** |
| Health | #A855F7 (roxo) | N/A | ✅ **Adicionar** |
| Home 2 | #EF4444 (vermelho) | N/A | ✅ **Adicionar** |

**Ação necessária:** Expandir paleta do Design System para incluir cores sólidas (não só pastéis).

---

### Tipografia

| Elemento | Wallet (Nova) | Trackers (Atual) | Compatível? |
|----------|--------------|------------------|-------------|
| Valor principal | 34px bold | 34px bold | ✅ **Igual** |
| Categoria | 17px semibold | 17px semibold | ✅ **Igual** |
| Subtítulo | 13px gray | 13px gray-400 | ✅ **Igual** |
| Badge % | 13px semibold branco | N/A | ✅ **Adicionar** |

**Ação:** Nenhuma. Tipografia 100% compatível.

---

### Dimensões

| Elemento | Wallet (Nova) | Trackers (Atual) | Compatível? |
|----------|--------------|------------------|-------------|
| Icon size | 24px | 24px | ✅ **Igual** |
| Icon circle | N/A (só ícone) | 48px | ⚠️ **Adaptar** |
| Progress height | 6px | 6px | ✅ **Igual** |
| Card padding | 20px | 20px | ✅ **Igual** |
| Touch target | 44px (pills) | 44px | ✅ **Igual** |

**Ação:** Considerar remover background circular dos ícones (usar só ícone colorido).

---

## 🎨 Atualização do Design System Necessária

### 1. **Adicionar ao STYLE_GUIDE.md**

#### Novos Componentes:
- `DonutChart` (Gráfico Pizza)
- `TogglePills` (2 tabs)
- `CategoryRowInline` (progress inline com badge)
- `WalletHeader` (header com 3 elementos)
- `SelectorBar` (wallet + dropdown)

#### Novas Cores:
```typescript
// Adicionar ao mobile-colors.ts
export const solidColors = {
  blue: '#3B82F6',
  green: '#10B981',
  purple: '#A855F7',
  orange: '#F59E0B',
  red: '#EF4444',
  gray: '#9CA3AF',
};
```

#### Novos Tokens de Tipografia:
```typescript
// Adicionar ao mobile-typography.ts
export const typography = {
  // ... existentes ...
  valueHuge: {
    fontSize: '34px',
    fontWeight: 700,
    lineHeight: 1.0,
    color: '#000000',
    tailwind: 'text-[34px] font-bold leading-none text-black'
  },
  badgePercent: {
    fontSize: '13px',
    fontWeight: 600,
    lineHeight: 1.0,
    color: '#FFFFFF',
    tailwind: 'text-[13px] font-semibold leading-none text-white'
  },
};
```

---

### 2. **Criar Arquivos Novos**

```
app_dev/frontend/src/
├── components/mobile/
│   ├── donut-chart.tsx              # NOVO - Gráfico pizza
│   ├── toggle-pills.tsx             # NOVO - Toggle 2 tabs
│   ├── category-row-inline.tsx      # NOVO - Progress inline
│   ├── wallet-header.tsx            # NOVO - Header 3 elementos
│   └── selector-bar.tsx             # NOVO - Wallet + dropdown
└── config/
    ├── mobile-colors.ts             # Atualizar: adicionar solidColors
    └── mobile-typography.ts         # Atualizar: adicionar valueHuge, badgePercent
```

---

## 📝 Comparação: Tela de Visualização vs Tela de Edição

### Tela de Visualização (Wallet - Nova)
**Objetivo:** Mostrar progresso geral do mês

**Componentes:**
- ✅ Donut Chart (visual)
- ✅ Toggle Pills (Savings/Expenses)
- ✅ Progress Inline com Badge %
- ✅ Read-only (sem edição)

**Interações:**
- Tocar em categoria → Drill-down (bottom sheet com subgrupos)
- Toggle Savings/Expenses → Troca de view
- Dropdown Month → Seletor de mês

---

### Tela de Edição (Trackers - Primeira imagem)
**Objetivo:** Editar valores de metas por categoria

**Componentes:**
- ✅ TrackerCard (com progress bar abaixo)
- ✅ Campos editáveis (input numérico)
- ✅ Botão "Copiar mês anterior"
- ✅ Botão "Colar para o ano"

**Interações:**
- Tocar em card → Bottom sheet com teclado numérico
- Editar valor → Atualiza backend
- Copiar/Colar → Ações rápidas

---

## ✅ Recomendação Final

### Para a Tela de Visualização (Budget/Metas)
**Usar layout "Wallet History" (nova imagem):**
- ✅ Donut Chart no topo (progresso geral)
- ✅ Toggle Pills (Mês / YTD)
- ✅ Progress Inline com Badge %
- ✅ Lista de categorias read-only

**Arquivos a criar:**
- `/mobile/budget/page.tsx` (tela principal)
- `DonutChart` component
- `TogglePills` component
- `CategoryRowInline` component

**Esforço:** 8-10 horas

---

### Para a Tela de Edição (Budget Edit)
**Usar layout "Trackers" (primeira imagem):**
- ✅ TrackerCard para cada categoria
- ✅ Progress bar abaixo (não inline)
- ✅ Bottom sheet para editar
- ✅ Botões de ação (copiar/colar)

**Arquivos a criar:**
- `BudgetEditBottomSheet` component
- `BudgetCopyActions` component (copiar mês, colar ano)

**Esforço:** 4-6 horas

---

## 🚀 Próximos Passos

### 1. Aprovar Design (Hoje)
- [ ] Confirmar uso do layout "Wallet History" para visualização
- [ ] Confirmar uso do layout "Trackers" para edição
- [ ] Decidir se mantém icon circle ou usa só ícone (recomendação: manter circle)

### 2. Atualizar Design System (1-2h)
- [ ] Adicionar `solidColors` ao `mobile-colors.ts`
- [ ] Adicionar `valueHuge` e `badgePercent` ao `mobile-typography.ts`
- [ ] Atualizar STYLE_GUIDE.md com novos componentes

### 3. Implementar Componentes (8-10h)
- [ ] DonutChart (2-3h)
- [ ] TogglePills (1-2h)
- [ ] CategoryRowInline (1-2h)
- [ ] WalletHeader (1h)
- [ ] SelectorBar (1h)
- [ ] Budget page integration (2-3h)

### 4. Integração com Backend (2h)
- [ ] Conectar DonutChart com API `/dashboard/budget-vs-actual`
- [ ] Conectar CategoryRowInline com dados de categorias
- [ ] Toggle Mês/YTD

---

## 📊 Resumo Executivo

**Compatibilidade com Design System:**
- ✅ **85% compatível** (cores, tipografia, dimensões)
- ⚠️ **15% novos elementos** (donut chart, toggle pills, progress inline)

**Ação necessária:**
- ✅ Expandir Design System com 5 novos componentes
- ✅ Adicionar cores sólidas (não só pastéis)
- ✅ Criar 2 telas: visualização (Wallet) + edição (Trackers)

**Esforço total:**
- Design System: 1-2h
- Componentes novos: 8-10h
- Integração: 2h
- **Total: 11-14 horas**

**Recomendação:** ✅ **APROVAR** - Layout moderno, UX superior, compatível com DS atual

---

**Próxima ação:** Aguardar aprovação do stakeholder para atualizar PRD e STYLE_GUIDE com novos componentes.
