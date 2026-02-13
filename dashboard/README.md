# 📊 Dashboard - Insights Financeiros

Dashboard de insights financeiros com gráficos de barras, donut charts e análise de receitas/despesas.

## 📁 Estrutura do Pacote

```
dashboard/
├── app/
│   ├── globals.css          # Estilos globais + Tailwind
│   ├── layout.tsx           # Layout principal
│   └── page.tsx             # Página do dashboard (278 linhas)
├── lib/
│   └── constants.ts         # Dados mockados (income + expenses)
├── types/
│   └── index.ts             # Interfaces TypeScript
├── package.json             # Dependências
├── tsconfig.json            # Configuração TypeScript
├── tailwind.config.ts       # Configuração Tailwind
├── postcss.config.js        # Configuração PostCSS
├── next.config.js           # Configuração Next.js
└── next-env.d.ts            # Types do Next.js
```

## 🚀 Como Usar no Projeto Principal

### Opção 1: Copiar para pasta específica (Recomendado)

```bash
# 1. Copiar arquivos para o projeto principal
cp -r dashboard/* /caminho/do/projeto/principal/

# 2. Instalar dependências
cd /caminho/do/projeto/principal
npm install

# 3. Rodar em desenvolvimento
npm run dev
```

### Opção 2: Adicionar como rota no Next.js existente

```bash
# 1. Copiar apenas a pasta app/insights
cp -r dashboard/app /caminho/projeto/app/insights

# 2. Copiar lib e types
cp -r dashboard/lib /caminho/projeto/src/
cp -r dashboard/types /caminho/projeto/src/

# 3. Acessar: http://localhost:3000/insights
```

## 📦 Dependências

```json
{
  "next": "14.2.35",
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "typescript": "^5.7.3",
  "tailwindcss": "^3.4.17"
}
```

## ✨ Funcionalidades

### 1️⃣ Gráfico de Barras (Income Trend)
- 7 meses de dados (Jan - Jul)
- Barras duplas: **Expenses (cinza) primeiro, Income (preto) depois**
- Tooltip interativo ao hover
- Alturas fixas em pixels (65px, 80px, 95px, etc.)

### 2️⃣ Tabs Interativas
- **Income**: Mostra fontes de receita
- **Expenses**: Mostra categorias de despesas
- **Budget**: (placeholder)

### 3️⃣ Donut Charts Dinâmicos
- **Tab Income**: 
  - Salary (₦20,000,000)
  - Wages (₦12,000,000)
  - Business (₦20,000,000)

- **Tab Expenses**:
  - Food (₦8,000,000)
  - Transport (₦5,000,000)
  - Shopping (₦7,000,000)
  - Bills (₦6,000,000)
  - Entertainment (₦4,000,000)
  - Healthcare (₦3,000,000)
  - Other (₦2,000,000)

### 4️⃣ Seletor de Mês
- Scroll horizontal com últimos 6 meses e próximos 6 meses
- Seleção visual (fundo preto quando ativo)

### 5️⃣ Navegação Inferior
- Home, Card, Insights
- Icons SVG nativos

## 🎨 Estilos Personalizados

### CSS Classes Customizadas

```css
/* globals.css */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
```

### Tailwind Classes Principais
- `bg-gray-50` - Fundo da página
- `bg-white` - Cards
- `rounded-3xl` - Bordas arredondadas
- `shadow-lg` - Sombras
- `text-gray-900` - Texto principal
- `text-gray-400` - Texto secundário

## 🔧 Customização

### Alterar Dados Mockados

Edite `lib/constants.ts`:

```typescript
export const monthlyData: MonthlyData[] = [
  { month: 'Jan', income: 5200000, expenses: 4100000 },
  // ... adicione mais meses
];

export const incomeSources: IncomeSource[] = [
  { name: 'Salary', amount: 20000000, color: '#1F2937' },
  // ... adicione mais fontes
];

export const expenseSources: IncomeSource[] = [
  { name: 'Food', amount: 8000000, color: '#1F2937' },
  // ... adicione mais categorias
];
```

### Integrar com API Real

Substitua os imports em `app/page.tsx`:

```typescript
// Antes (mock)
import { monthlyData } from '@/lib/constants';

// Depois (API)
const { data: monthlyData } = await fetch('/api/monthly-data').then(r => r.json());
```

## 📊 Estatísticas do Código

- **Total de linhas**: ~500 linhas
- **Componentes**: 1 página monolítica (pode ser componentizado)
- **TypeScript**: 100% tipado
- **CSS**: Apenas Tailwind + 7 linhas custom

## ⚠️ Importante

Este pacote contém **APENAS os arquivos fonte**:
- ❌ Não inclui `node_modules/`
- ❌ Não inclui `.next/` (build)
- ✅ Inclui apenas código-fonte e configurações

**Você precisará executar `npm install` no projeto de destino!**

---

**Última atualização**: 08/02/2026  
**Versão**: 1.0.0  
**Desenvolvido com**: Next.js 14 + TypeScript + Tailwind CSS
