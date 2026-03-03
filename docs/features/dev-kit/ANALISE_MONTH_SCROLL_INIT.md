# Análise: Inicialização Ineficiente do Mês no Dashboard Mobile

**Data:** 2026-03-02
**Branch:** feature/merge-plano-aposentadoria
**Arquivos analisados:**
- `app_dev/frontend/src/app/mobile/dashboard/page.tsx`
- `app_dev/frontend/src/components/mobile/month-scroll-picker.tsx`
- `app_dev/frontend/src/features/dashboard/hooks/use-dashboard.ts`
- `app_dev/frontend/src/features/dashboard/services/dashboard-api.ts`
- `app_dev/backend/app/domains/dashboard/repository.py`

---

## 1. O que acontece hoje (mapeamento)

### Sequência de eventos ao abrir o Dashboard

```
Usuário abre /mobile/dashboard
        │
        ▼
[1] useState inicial: selectedMonth = new Date()  → mês ATUAL (ex: mar/2026)
        │
        ├─── [2a] 5 hooks disparam IMEDIATAMENTE com mês errado:
        │         GET /dashboard/metrics?year=2026&month=3
        │         GET /dashboard/income-sources?year=2026&month=3
        │         GET /dashboard/budget-vs-actual?year=2026&month=3
        │         GET /dashboard/chart-data?year=2026&month=3
        │         GET /dashboard/chart-data-yearly?...
        │
        └─── [2b] useEffect dispara fetchLastMonthWithData:
                  GET /dashboard/last-month-with-data?source=transactions
                  (consulta `journal_entries` no banco)
                        │
                        ▼
              [3] Resposta: { year: 2026, month: 1 }  ← mês real com dados
                        │
                        ▼
              [4] setSelectedMonth(new Date(2026, 0, 1))
                        │
                        ▼
              [5] React re-render → todos os 5 hooks cancelam
                  suas requisições em curso e REDISPARAM com:
                  GET /dashboard/metrics?year=2026&month=1
                  GET /dashboard/income-sources?year=2026&month=1
                  GET /dashboard/budget-vs-actual?year=2026&month=1
                  GET /dashboard/chart-data?year=2026&month=1
                  GET /dashboard/chart-data-yearly?...
                        │
                        ▼
              [6] MonthScrollPicker: useEffect com selectedMonth mudou
                  → scroll anima de mar/2026 para jan/2026
                        │
                        ▼
              [7] Dados finalmente chegam → tela renderiza
```

### Linha do tempo de requisições

```
t=0ms   ──── Auth check (useRequireAuth) ──────────────────────────────────
t=0ms   ──── fetchLastMonthWithData() disparado no useEffect ────────────── (bloqueante)
t=0ms   ──── 5 hooks disparam com mês ATUAL (dados vão ser descartados) ───
t=~80ms ──── last-month-with-data resolve → setSelectedMonth ──────────────
t=~80ms ──── 5 requisições em curso são CANCELADAS ────────────────────────
t=~80ms ──── 5 requisições NOVAS disparam com mês correto ─────────────────
t=~300ms─── dados chegam → tela renderiza ─────────────────────────────────
```

### Custo real

| Item | Quantidade | Observação |
|---|---|---|
| Requisições ao backend | 6 na inicialização | 5 com mês errado + 1 para descobrir o mês |
| Requisições desperdiçadas | 5 (ou 0 se mês atual = último mês) | Depende de quando o usuário acessa |
| Re-renders desnecessários | 2 | Um com mês atual, outro após correção |
| Animações de scroll extras | 1 | Scroll anima duas vezes |
| Bloqueio de UI | ~80ms (RTT do last-month-with-data) | Conteúdo não aparece até resolver |

### Pior caso: início de mês

Quando o usuário acessa em março e o último dado é de janeiro:
- 5 requisições de março são feitas e descartadas integralmente
- O usuário vê `Carregando...` por mais tempo
- O scroll pula de março → janeiro com animação visível

### No console (evidência do screenshot)

O console mostra `useExpenseSources – Buscando despesas` para `month: 3`, `month: 1` e outros meses repetidamente, confirmando os re-disparos.

---

## 2. Causa raiz

O problema está na inicialização em `dashboard/page.tsx`:

```typescript
// linha 37 — inicia com mês ATUAL, sem saber se há dados
const [selectedMonth, setSelectedMonth] = useState<Date>(new Date())

// linha 59-71 — hooks disparam IMEDIATAMENTE com mês atual
const { metrics } = useDashboardMetrics(year, month, ytdMonth)
const { } = useIncomeSources(year, month)
const { } = useExpenseSources(year, month)
const { } = useChartData(...)
const { } = useChartDataYearly(...)

// linha 79 — DEPOIS, busca qual mês usar de fato
useEffect(() => {
  fetchLastMonthWithData('transactions').then((last) => {
    setSelectedMonth(new Date(last.year, last.month - 1, 1))  // ← atualiza tarde demais
  })
}, [isAuth])
```

Os hooks de dados e o hook de descoberta do mês correto estão **desacoplados**: os dados são buscados antes de saber qual mês buscar.

---

## 3. Proposta de solução

### Abordagem: `null` como estado inicial + guard nas queries

A ideia central é: **não disparar nenhuma query de dados até saber qual mês mostrar.**

#### 3.1 Estado inicial `null`

```typescript
// Antes
const [selectedMonth, setSelectedMonth] = useState<Date>(new Date())

// Depois
const [selectedMonth, setSelectedMonth] = useState<Date | null>(null)
```

#### 3.2 Derivar year/month só quando o mês está resolvido

```typescript
const year  = selectedMonth ? selectedMonth.getFullYear() : null
const month = selectedMonth ? selectedMonth.getMonth() + 1 : null
```

#### 3.3 Guardar as queries até ter o mês

Cada hook recebe `enabled` (padrão React Query) ou equivalente com `skip`:

```typescript
// Opção A — com React Query (recomendado a longo prazo)
const { data: metrics } = useQuery({
  queryKey: ['metrics', year, month],
  queryFn: () => fetchDashboardMetrics(year!, month!),
  enabled: year !== null && month !== null,
})

// Opção B — sem React Query (solução mínima, sem mudar os hooks atuais)
// Basta não passar year/month enquanto são null:
const { metrics } = useDashboardMetrics(
  year ?? 0,
  month ?? undefined,
  ytdMonth
)
// E nos hooks: só executar o useEffect se year > 0
```

#### 3.4 Skeleton no MonthScrollPicker enquanto não há mês

```typescript
{selectedMonth === null ? (
  <div className="h-[60px] animate-pulse bg-gray-100 rounded" />
) : (
  <MonthScrollPicker
    selectedMonth={selectedMonth}
    onMonthChange={setSelectedMonth}
  />
)}
```

#### 3.5 Cache em localStorage (melhoria adicional)

Para eliminar o loading inicial na segunda visita:

```typescript
// Ao salvar
localStorage.setItem('lastSelectedMonth', selectedMonth.toISOString())

// Ao inicializar
const cached = localStorage.getItem('lastSelectedMonth')
const [selectedMonth, setSelectedMonth] = useState<Date | null>(
  cached ? new Date(cached) : null
)
```

- Na segunda visita, o mês cached é usado imediatamente
- As 5 queries disparam direto com o mês correto
- `fetchLastMonthWithData` corre em background e, se diferente, corrige

---

## 4. Sequência após a mudança

```
Usuário abre /mobile/dashboard
        │
        ▼
[1] selectedMonth = null  →  MonthScrollPicker: skeleton
    year/month = null     →  todos os 5 hooks: skip (não disparam)
        │
        ▼
[2] fetchLastMonthWithData() → GET /dashboard/last-month-with-data
        │
        ▼ (único round-trip)
[3] { year: 2026, month: 1 } → setSelectedMonth(jan/2026)
        │
        ▼
[4] year=2026, month=1 → 5 hooks disparam UMA VEZ com valores corretos
    MonthScrollPicker renderiza já no mês certo (sem animação dupla)
        │
        ▼
[5] Dados chegam → tela renderiza
```

### Comparativo

| Métrica | Hoje | Proposta |
|---|---|---|
| Requisições totais (pior caso) | 11 (6 init + 5 retry) | 6 (1 discovery + 5 data) |
| Requisições desperdiçadas | 5 | 0 |
| Re-renders desnecessários | 2 | 1 |
| Animações de scroll extras | 1 (dois saltos) | 0 (scroll direto) |
| Percepção de lentidão | Alta (conteúdo muda após render) | Baixa (conteúdo aparece correto) |

---

## 5. Arquivos a modificar

| Arquivo | Mudança |
|---|---|
| `app/mobile/dashboard/page.tsx` | `useState<Date \| null>(null)` + skip logic + skeleton no picker |
| `features/dashboard/hooks/use-dashboard.ts` | Guard `if (!year) return` nos `useEffect` de cada hook |
| `components/mobile/month-scroll-picker.tsx` | Sem mudança (já funciona com `selectedMonth: Date`) |

---

## 6. Variante com localStorage (two-pass otimista)

```
Visita 1:  null → discovery → queries (comportamento novo acima)
Visita 2+: cached → queries disparam → discovery em background → corrige se necessário
```

Benefício: elimina o skeleton na segunda visita. Custo: ~3 linhas de localStorage.

---

## 7. O que NÃO mudar

- A API `GET /dashboard/last-month-with-data` está correta e performática (query simples com `ORDER BY Ano DESC, Mes DESC LIMIT 1`).
- O `MonthScrollPicker` está correto; o problema não é nele, é em quando o mês é fornecido.
- Os hooks individuais estão corretos; o problema é que são chamados antes da hora.
