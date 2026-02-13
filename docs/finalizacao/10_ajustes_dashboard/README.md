# 🔟 Ajustes Dashboard

**Frente:** Ajustes Dashboard  
**Status:** 🔴 Não Iniciado  
**Prioridade:** 🔴 CRÍTICA  
**Responsável:** A definir  
**Data Início:** A definir  
**Deadline:** A definir

---

## 🎯 Objetivo

Realizar ajustes finais no dashboard principal para exibir corretamente despesas, receitas e saldo, além de garantir que o clique no donut navegue para metas.

---

## 📋 Escopo

### Incluído
- ✅ Ajuste do quadro principal com despesas/receitas/saldo
- ✅ Toggle mês atual vs YTD (Year-to-Date)
- ✅ Clique no donut levando para metas
- ✅ Validação de dados exibidos
- ✅ Responsividade mobile

### Excluído
- ❌ Novos gráficos/visualizações
- ❌ Mudanças em outros componentes do dashboard
- ❌ Refatoração completa do dashboard

---

## 📊 Sub-frente 10a: Quadro Principal

### Objetivo
Ajustar o quadro principal do dashboard para exibir despesas, receitas e saldo do mês atual ou YTD.

### 10a.1 Layout Desejado

```
┌─────────────────────────────────────┐
│ Dashboard - [Mês ▼] [YTD]          │
├─────────────────────────────────────┤
│                                     │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│ │Despesas │ │Receitas │ │ Saldo   ││
│ │ 🔴      │ │ 🟢      │ │ 📊      ││
│ │R$ 8.500 │ │R$ 12.000│ │R$ 3.500 ││
│ │         │ │         │ │ (+41%)  ││
│ └─────────┘ └─────────┘ └─────────┘│
│                                     │
│ Toggle: [ Mês Atual ] [ YTD ]      │
│                                     │
└─────────────────────────────────────┘
```

### 10a.2 Estrutura de Dados

**Backend - API Endpoint:**
```python
# app/domains/dashboard/router.py
@router.get("/summary")
def get_dashboard_summary(
    period: str = Query('month', regex='^(month|ytd)$'),
    year: int = Query(...),
    month: int = Query(None, ge=1, le=12),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna resumo financeiro para dashboard
    
    Args:
        period: 'month' para mês específico, 'ytd' para ano até hoje
        year: Ano de referência
        month: Mês (obrigatório se period='month')
    """
    if period == 'month':
        if not month:
            raise HTTPException(400, "Mês é obrigatório para period='month'")
        
        filters = [
            JournalEntry.user_id == user_id,
            JournalEntry.Ano == year,
            JournalEntry.Mes == month,
            JournalEntry.IgnorarDashboard == 0
        ]
    else:  # YTD
        current_month = datetime.now().month
        filters = [
            JournalEntry.user_id == user_id,
            JournalEntry.Ano == year,
            JournalEntry.Mes <= current_month,  # Até mês atual
            JournalEntry.IgnorarDashboard == 0
        ]
    
    # Despesas
    despesas = db.query(func.sum(JournalEntry.Valor)).filter(
        *filters,
        JournalEntry.CategoriaGeral == 'Despesa'
    ).scalar() or 0
    
    # Receitas
    receitas = db.query(func.sum(JournalEntry.Valor)).filter(
        *filters,
        JournalEntry.CategoriaGeral == 'Receita'
    ).scalar() or 0
    
    # Saldo
    saldo = receitas - abs(despesas)
    saldo_percentual = (saldo / receitas * 100) if receitas > 0 else 0
    
    return {
        "period": period,
        "year": year,
        "month": month if period == 'month' else None,
        "despesas": abs(despesas),
        "receitas": receitas,
        "saldo": saldo,
        "saldo_percentual": round(saldo_percentual, 2)
    }
```

### 10a.3 Frontend - Componente

```typescript
// src/features/dashboard/components/summary-cards.tsx
export function SummaryCards() {
  const [period, setPeriod] = useState<'month' | 'ytd'>('month')
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1)
  const currentYear = new Date().getFullYear()
  
  const { data, isLoading } = useDashboardSummary({
    period,
    year: currentYear,
    month: period === 'month' ? selectedMonth : undefined
  })
  
  if (isLoading) return <LoadingSkeleton />
  
  return (
    <div className="space-y-4">
      {/* Header com seletor */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {period === 'month' && (
            <Select 
              value={selectedMonth.toString()} 
              onValueChange={(v) => setSelectedMonth(parseInt(v))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {MONTHS.map((month, idx) => (
                  <SelectItem key={idx} value={(idx + 1).toString()}>
                    {month}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>
        
        <ToggleGroup 
          type="single" 
          value={period} 
          onValueChange={(v) => v && setPeriod(v as 'month' | 'ytd')}
        >
          <ToggleGroupItem value="month">Mês Atual</ToggleGroupItem>
          <ToggleGroupItem value="ytd">YTD</ToggleGroupItem>
        </ToggleGroup>
      </div>
      
      {/* Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Despesas</CardTitle>
            <span className="text-2xl">🔴</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(data.despesas)}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Receitas</CardTitle>
            <span className="text-2xl">🟢</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(data.receitas)}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Saldo</CardTitle>
            <span className="text-2xl">📊</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(data.saldo)}
            </div>
            <p className={`text-sm ${data.saldo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {data.saldo >= 0 ? '+' : ''}{data.saldo_percentual.toFixed(2)}%
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
```

### Checklist 10a
- [ ] API `/dashboard/summary` implementada
- [ ] Endpoint retorna dados corretos para mês
- [ ] Endpoint retorna dados corretos para YTD
- [ ] Componente `SummaryCards` criado
- [ ] Toggle mês/YTD funciona
- [ ] Seletor de mês funciona (quando period='month')
- [ ] Cards exibem valores corretos
- [ ] Saldo percentual calculado corretamente
- [ ] Responsivo para mobile
- [ ] Testado com dados reais

---

## 🎯 Sub-frente 10b: Clique no Donut → Metas

### Objetivo
Garantir que ao clicar em uma fatia do gráfico donut de despesas, o usuário seja levado para a tela de metas com o grupo correspondente selecionado.

### 10b.1 Identificar Gráfico Donut Atual

**Localizar componente:**
```bash
# Buscar componente de donut
grep -r "Donut\|DonutChart\|PieChart" app_dev/frontend/src/features/dashboard --include="*.tsx"

# Ou buscar por biblioteca de gráficos
grep -r "recharts\|chart.js\|nivo" app_dev/frontend/src/features/dashboard
```

### 10b.2 Adicionar Navegação ao Clique

**Exemplo com Recharts:**
```typescript
// src/features/dashboard/components/expenses-donut.tsx
import { useRouter } from 'next/navigation'
import { PieChart, Pie, Cell } from 'recharts'

export function ExpensesDonut() {
  const router = useRouter()
  const { data: expenses } = useExpensesByGroup()
  
  const handleClick = (entry: any) => {
    const grupo = entry.name
    // Navegar para metas com grupo pré-selecionado
    router.push(`/budget?grupo=${encodeURIComponent(grupo)}`)
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Despesas por Grupo</CardTitle>
      </CardHeader>
      <CardContent>
        <PieChart width={300} height={300}>
          <Pie
            data={expenses}
            dataKey="valor"
            nameKey="grupo"
            cx="50%"
            cy="50%"
            onClick={handleClick}  // ← Adicionar onClick
            style={{ cursor: 'pointer' }}  // ← Mostrar que é clicável
          >
            {expenses.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={COLORS[index % COLORS.length]} 
              />
            ))}
          </Pie>
        </PieChart>
      </CardContent>
    </Card>
  )
}
```

### 10b.3 Receber Parâmetro na Tela de Metas

```typescript
// src/app/budget/page.tsx
export default function BudgetPage() {
  const searchParams = useSearchParams()
  const grupoPreSelecionado = searchParams.get('grupo')
  
  const [selectedGroup, setSelectedGroup] = useState(
    grupoPreSelecionado || ''
  )
  
  useEffect(() => {
    if (grupoPreSelecionado) {
      // Scroll ou highlight do grupo
      setSelectedGroup(grupoPreSelecionado)
    }
  }, [grupoPreSelecionado])
  
  return (
    <div>
      <h1>Metas</h1>
      
      <Select value={selectedGroup} onValueChange={setSelectedGroup}>
        <SelectTrigger>
          <SelectValue placeholder="Selecione um grupo" />
        </SelectTrigger>
        <SelectContent>
          {grupos.map(g => (
            <SelectItem 
              key={g.id} 
              value={g.nome}
              className={g.nome === grupoPreSelecionado ? 'bg-blue-100' : ''}
            >
              {g.nome}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      
      {/* Resto da tela */}
    </div>
  )
}
```

### 10b.4 Adicionar Feedback Visual

```typescript
// Tooltip no hover
<Pie
  data={expenses}
  onClick={handleClick}
  onMouseEnter={(_, index) => setHoveredIndex(index)}
  onMouseLeave={() => setHoveredIndex(null)}
>
  {expenses.map((entry, index) => (
    <Cell 
      key={`cell-${index}`}
      fill={COLORS[index % COLORS.length]}
      fillOpacity={hoveredIndex === index ? 0.8 : 1}
    />
  ))}
</Pie>

// Adicionar cursor pointer
<style jsx>{`
  .recharts-pie {
    cursor: pointer;
  }
`}</style>
```

### Checklist 10b
- [ ] Identificado componente de donut
- [ ] onClick adicionado ao donut
- [ ] Navegação para /budget funciona
- [ ] Parâmetro ?grupo= é enviado
- [ ] Tela de metas recebe parâmetro
- [ ] Grupo é pré-selecionado ao chegar em metas
- [ ] Cursor pointer mostra que é clicável
- [ ] Hover mostra feedback visual
- [ ] Testado com múltiplos grupos
- [ ] Funciona em mobile

---

## 🧪 Validação Geral

### Fluxo Completo de Teste

```markdown
1. [ ] Acessar dashboard
2. [ ] Verificar que cards exibem valores corretos
3. [ ] Toggle para YTD
4. [ ] Verificar que valores mudaram (YTD vs mês)
5. [ ] Toggle para Mês Atual
6. [ ] Selecionar mês diferente
7. [ ] Verificar que valores mudaram
8. [ ] Clicar em fatia do donut (ex: Alimentação)
9. [ ] Verificar que navegou para /budget?grupo=Alimentação
10. [ ] Verificar que grupo Alimentação está selecionado
11. [ ] Voltar para dashboard
12. [ ] Testar fluxo em mobile
```

### Validações de Dados

```python
# Script de validação
# scripts/testing/validate_dashboard_data.py
def validate_dashboard_data(user_id: int, year: int, month: int):
    """
    Valida que dados do dashboard estão corretos
    """
    # Calcular manualmente
    despesas_esperadas = db.query(func.sum(JournalEntry.Valor)).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.Ano == year,
        JournalEntry.Mes == month,
        JournalEntry.CategoriaGeral == 'Despesa',
        JournalEntry.IgnorarDashboard == 0
    ).scalar() or 0
    
    # Buscar da API
    response = requests.get(f'/api/v1/dashboard/summary?period=month&year={year}&month={month}')
    data = response.json()
    
    # Comparar
    assert abs(data['despesas'] - abs(despesas_esperadas)) < 0.01, "Despesas incorretas"
    
    print("✓ Dados do dashboard validados!")
```

---

## 📊 Métricas

### Progresso
```
10a - Quadro Principal:   ░░░░░░░░░░ 0%
10b - Clique no Donut:    ░░░░░░░░░░ 0%
Validação:                ░░░░░░░░░░ 0%
TOTAL:                    ░░░░░░░░░░ 0%
```

---

## 🚧 Riscos

1. **Médio:** Cálculos de despesas/receitas incorretos
2. **Médio:** Toggle YTD mostra dados errados
3. **Baixo:** Clique no donut não navega

### Mitigações
1. Script de validação de dados
2. Testar YTD com dados reais do ano
3. Adicionar tratamento de erro na navegação

---

## 📝 Próximos Passos

1. [ ] Implementar API `/dashboard/summary`
2. [ ] Criar componente `SummaryCards`
3. [ ] Testar toggle mês/YTD
4. [ ] Identificar componente donut
5. [ ] Adicionar onClick ao donut
6. [ ] Implementar recebimento de parâmetro em metas
7. [ ] Testar fluxo completo
8. [ ] Validar dados com script

---

## 🔗 Referências

- [PLANO_FINALIZACAO.md](./PLANO_FINALIZACAO.md)
- Dashboard atual: `app_dev/frontend/src/features/dashboard/`
- APIs: `app_dev/backend/app/domains/dashboard/`

---

**Última Atualização:** 10/02/2026
