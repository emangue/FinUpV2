# 📊 Mapeamento do Estado Atual - Dashboard Mobile

**Data:** 13/02/2026  
**Objetivo:** Mapear estado atual do dashboard para identificar ajustes necessários

---

## 🎯 Visão Geral

Dashboard mobile está em **Sprint 3.2** - redesign completo baseado no protótipo "Insights".

**Arquivo principal:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx`

---

## 📱 1. ESTRUTURA ATUAL DO DASHBOARD

### Componentes Principais

```tsx
<DashboardMobilePage>
  ├── MobileHeader (título + botão download)
  ├── Date display (mês/ano selecionado)
  ├── MonthScrollPicker (scroll horizontal de meses)
  ├── YTDToggle (toggle mês/YTD)
  ├── WalletBalanceCard (saldo + change%)
  ├── Tabs (Receitas | Despesas | Orçamento)
  ├── BarChart (tendência de receitas)
  ├── DonutChart (fontes receita/despesas)
  └── Recent Transactions (botão "Ver Todas")
</DashboardMobilePage>
```

### Estados Atuais

```tsx
const [selectedMonth, setSelectedMonth] = useState<Date>(new Date())
const [period, setPeriod] = useState<YTDToggleValue>('month')
const [activeTab, setActiveTab] = useState<'income' | 'expenses' | 'budget'>('income')
```

---

## 🔍 2. COMPONENTES DETALHADOS

### 2.1. WalletBalanceCard

**Arquivo:** `features/dashboard/components/wallet-balance-card.tsx`

**Props atuais:**
```tsx
interface Props {
  balance: number          // Saldo do período
  changePercentage?: number // % de mudança (opcional)
}
```

**Estado atual:**
- ✅ Exibe saldo do período
- ✅ Exibe % de mudança (se disponível)
- ❓ **NÃO mostra despesas, receitas separadas**

**Fonte de dados:**
```tsx
const { metrics } = useDashboardMetrics(year, month)
// metrics.saldo_periodo
// metrics.change_percentage
```

### 2.2. YTDToggle

**Comportamento:**
- ✅ Toggle funcional: 'month' ↔ 'YTD'
- ✅ Afeta as queries (month = undefined quando YTD)

```tsx
const month = period === 'month' ? selectedMonth.getMonth() + 1 : undefined
```

### 2.3. DonutChart

**Arquivo:** `features/dashboard/components/donut-chart.tsx`

**Props:**
```tsx
interface Props {
  activeTab: 'income' | 'expenses' | 'budget'
  incomeSources: Array<{ grupo: string; total: number }>
  totalReceitas: number
  expenseSources: Array<{ grupo: string; total: number }>
  totalDespesas: number
}
```

**Comportamento:**
- ✅ Renderiza baseado em activeTab
- ✅ Mostra fontes de receita OU despesas
- ❓ **Clique no donut NÃO navega para metas**

---

## 🎯 3. IDENTIFICAÇÃO DE GAPS (Sub-frente 10a e 10b)

### 🔴 GAP 1: Quadro Principal Incompleto (Sub-frente 10a)

**Problema:** `WalletBalanceCard` só mostra **saldo total**.

**Esperado (segundo sub-frente):**
- Despesas do período
- Receitas do período
- Saldo (diferença)
- Toggle mês/YTD (✅ já existe)

**Solução proposta:**
1. Modificar `WalletBalanceCard` para aceitar 3 valores
2. OU criar novo componente `MainMetricsCard`

**Dados já disponíveis:**
```tsx
const { metrics } = useDashboardMetrics(year, month)
// metrics.total_receitas (disponível)
// metrics.total_despesas (disponível)
// metrics.saldo_periodo (disponível)
```

---

### 🔴 GAP 2: Clique no Donut NÃO Navega (Sub-frente 10b)

**Problema:** `DonutChart` não tem navegação para metas.

**Esperado:** Clique em fatia do donut → navega para `/mobile/goals` filtrado pelo grupo.

**Solução proposta:**
1. Adicionar `onClick` nas fatias do donut
2. Passar callback `onSegmentClick(grupo: string)`
3. No componente pai: `router.push('/mobile/goals?grupo=' + grupo)`

**Implementação necessária:**
```tsx
// donut-chart.tsx
interface Props {
  // ... props existentes
  onSegmentClick?: (grupo: string) => void  // NOVO
}

// page.tsx
<DonutChart
  // ... props existentes
  onSegmentClick={(grupo) => router.push(`/mobile/goals?grupo=${grupo}`)}
/>
```

---

## 📊 4. HOOKS E APIs UTILIZADOS

### Hooks Disponíveis

**Arquivo:** `features/dashboard/hooks/use-dashboard.ts`

```tsx
// 1. Métricas gerais (despesas, receitas, saldo, change%)
useDashboardMetrics(year: number, month?: number)

// 2. Fontes de receita
useIncomeSources(year: number, month?: number)
// Retorna: { sources, totalReceitas, loading }

// 3. Fontes de despesa
useExpenseSources(year: number, month?: number)
// Retorna: { sources, totalDespesas, loading }

// 4. Dados para BarChart (múltiplos meses)
useChartData(year: number, month?: number)
// Retorna: { chartData, loading }
```

### APIs Backend

**Endpoints usados:**

1. **GET `/api/v1/dashboard/metrics`**
   - Query: `year`, `month` (opcional)
   - Response: 
     ```json
     {
       "total_receitas": 5000,
       "total_despesas": 3000,
       "saldo_periodo": 2000,
       "change_percentage": 15.5
     }
     ```

2. **GET `/api/v1/dashboard/income-sources`**
   - Query: `year`, `month` (opcional)
   - Response: Lista de grupos com totais

3. **GET `/api/v1/dashboard/expense-sources`**
   - Query: `year`, `month` (opcional)
   - Response: Lista de grupos com totais

---

## ✅ 5. FUNCIONALIDADES JÁ IMPLEMENTADAS

### O que JÁ funciona:

- ✅ **MonthScrollPicker** - Scroll horizontal de meses funcional
- ✅ **YTDToggle** - Toggle mês/YTD muda queries
- ✅ **Autenticação** - Hook `useRequireAuth()` protege rota
- ✅ **Loading states** - Mostra "Carregando..." enquanto busca dados
- ✅ **Last month with data** - Busca último mês com transações automaticamente
- ✅ **Tabs** - Navegação entre Receitas/Despesas/Orçamento
- ✅ **BarChart** - Tendência de receitas ao longo dos meses
- ✅ **DonutChart** - Visualização de fontes de receita/despesas
- ✅ **Navigation** - Botão "Ver Todas" leva para `/mobile/transactions`

---

## 🔴 6. AJUSTES NECESSÁRIOS (RESUMO)

### Prioridade Alta (Sub-frente 10a)

**1. Quadro Principal de Métricas**
- [ ] Modificar `WalletBalanceCard` para mostrar 3 valores separados
- [ ] Layout: Despesas | Receitas | Saldo (em linha ou cards)
- [ ] Manter change percentage (✅ já implementado)
- [ ] Garantir toggle mês/YTD afeta todos os valores

### Prioridade Alta (Sub-frente 10b)

**2. Navegação do Donut para Metas**
- [ ] Adicionar `onSegmentClick` prop no `DonutChart`
- [ ] Implementar navegação para `/mobile/goals?grupo=X`
- [ ] Testar clique em cada fatia do donut
- [ ] Validar que página de metas recebe filtro corretamente

### Prioridade Média

**3. Melhorias de UX**
- [ ] Animações nas transições de mês
- [ ] Loading skeleton em vez de texto
- [ ] Error states (se API falhar)

---

## 📁 7. ARQUIVOS A MODIFICAR

### Sub-frente 10a (Quadro Principal)

**Opção 1 - Modificar existente:**
```
features/dashboard/components/wallet-balance-card.tsx
```

**Opção 2 - Criar novo (recomendado):**
```
features/dashboard/components/main-metrics-card.tsx (NOVO)
```

**Usar dados de:**
```
features/dashboard/hooks/use-dashboard.ts (useDashboardMetrics)
```

### Sub-frente 10b (Navegação Donut)

```
features/dashboard/components/donut-chart.tsx (modificar)
app/mobile/dashboard/page.tsx (adicionar callback)
```

---

## 🎯 8. PRÓXIMOS PASSOS

### Ordem Recomendada:

1. **Criar `MainMetricsCard`** (sub-frente 10a)
   - Substituir `WalletBalanceCard` por componente mais completo
   - Exibir despesas, receitas, saldo em cards separados
   - Manter change percentage

2. **Adicionar navegação no DonutChart** (sub-frente 10b)
   - Modificar `donut-chart.tsx` para aceitar `onSegmentClick`
   - Implementar navegação no `page.tsx`

3. **Testar toggle mês/YTD**
   - Validar que TODOS os componentes respondem corretamente
   - Verificar que APIs recebem `month` correto (ou undefined)

4. **Testar navegação para metas**
   - Clicar em cada fatia do donut
   - Verificar que filtro é aplicado na página de metas

---

## 📊 9. EXEMPLO DE LAYOUT ESPERADO

### Dashboard Atual (Visual):
```
┌──────────────────────────────────────────┐
│  Dashboard                  [Download]   │
├──────────────────────────────────────────┤
│  jan 2026                                │
├──────────────────────────────────────────┤
│  [Scroll de Meses: dez jan fev mar ...]  │
├──────────────────────────────────────────┤
│          [ Mês ]    [ YTD ]              │
├──────────────────────────────────────────┤
│  💳 Wallet Balance                       │
│  R$ 2.000,00                             │
│  +15.5% vs last period                   │  ⬅️ SÓ MOSTRA SALDO
├──────────────────────────────────────────┤
│  [Receitas] [Despesas] [Orçamento]      │
├──────────────────────────────────────────┤
│  📈 Tendência de Receitas                │
│  [BarChart]                              │
├──────────────────────────────────────────┤
│  🍩 Donut Chart                          │
│  [Fontes de Receita]                     │  ⬅️ NÃO TEM CLIQUE
└──────────────────────────────────────────┘
```

### Dashboard Esperado (Visual):
```
┌──────────────────────────────────────────┐
│  Dashboard                  [Download]   │
├──────────────────────────────────────────┤
│  jan 2026                                │
├──────────────────────────────────────────┤
│  [Scroll de Meses: dez jan fev mar ...]  │
├──────────────────────────────────────────┤
│          [ Mês ]    [ YTD ]              │
├──────────────────────────────────────────┤
│  ┌──────────┬──────────┬──────────┐     │
│  │ Despesas │ Receitas │  Saldo   │     │  ⬅️ 3 VALORES SEPARADOS
│  │ 3.000    │ 5.000    │ 2.000    │     │
│  │ -5%      │ +10%     │ +15.5%   │     │
│  └──────────┴──────────┴──────────┘     │
├──────────────────────────────────────────┤
│  [Receitas] [Despesas] [Orçamento]      │
├──────────────────────────────────────────┤
│  📈 Tendência de Receitas                │
│  [BarChart]                              │
├──────────────────────────────────────────┤
│  🍩 Donut Chart (clicável!)              │  ⬅️ CLIQUE → /mobile/goals?grupo=X
│  [Fontes de Receita]                     │
└──────────────────────────────────────────┘
```

---

## 🎯 RESUMO EXECUTIVO

### Estado Atual:
- ✅ Dashboard redesenhado (Sprint 3.2)
- ✅ YTD Toggle funcional
- ✅ DonutChart renderiza dados corretamente
- ⚠️ Quadro principal mostra APENAS saldo
- ⚠️ Donut NÃO navega para metas

### Ajustes Necessários:
1. **Sub-frente 10a:** Criar `MainMetricsCard` com despesas, receitas, saldo
2. **Sub-frente 10b:** Adicionar navegação do donut para metas

### Tempo Estimado:
- **10a:** 2-3 horas (criar componente + integração)
- **10b:** 1-2 horas (adicionar navegação + testes)
- **Total:** 3-5 horas (0.5-1 dia)

### Dependências:
- ✅ APIs já existem (`useDashboardMetrics`, `useIncomeSources`, `useExpenseSources`)
- ✅ Hooks prontos e funcionais
- ✅ Dados disponíveis (só precisa exibir diferente)

---

**Documentação criada para:** Frente 10 (Ajustes Dashboard)  
**Data:** 13/02/2026  
**Status:** 📝 Mapeamento completo - pronto para implementação
