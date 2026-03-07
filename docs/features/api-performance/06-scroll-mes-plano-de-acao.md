# Plano de Ação: Scroll do Mês — Nasce no Mês Correto

> Objetivo: o `MonthScrollPicker` aparecer diretamente no último mês com dados, sem nenhum scroll visível.

---

## Solução Recomendada (A + B combinadas)

### Parte A — Tratar a race condition com `Promise.race` + `useState` com initializer

**Problema:** Auth pode resolver antes do pre-fetch, causando um segundo fetch e o jump.

**Solução:** Usar `Promise.race` entre auth e o fetch de `last-month-with-data` para garantir que o mês já está resolvido quando o picker for montado pela primeira vez.

**Arquivo:** `src/app/mobile/dashboard/page.tsx`

```typescript
// Antes
const [selectedMonth, setSelectedMonth] = useState<Date | null>(null)

const _pendingLastMonth = useRef<{ year: number; month: number } | null>(null)

useEffect(() => {
  fetchLastMonthWithData('transactions')
    .then((last) => { _pendingLastMonth.current = last })
    .catch(() => {})
}, [])

useEffect(() => {
  if (!isAuth) return
  const pending = _pendingLastMonth.current
  if (pending) {
    setSelectedMonth(new Date(pending.year, pending.month - 1, 1))
    ...
  } else {
    fetchLastMonthWithData('transactions').then(...)
  }
}, [isAuth])
```

```typescript
// Depois — inicia ambos em paralelo, espera os dois antes de renderizar
const [selectedMonth, setSelectedMonth] = useState<Date | null>(null)
const _lastMonthPromise = useRef<Promise<{ year: number; month: number }> | null>(null)

useEffect(() => {
  // Inicia o fetch imediatamente (sem esperar auth)
  _lastMonthPromise.current = fetchLastMonthWithData('transactions')
}, [])

useEffect(() => {
  if (!isAuth) return
  const promise = _lastMonthPromise.current ?? fetchLastMonthWithData('transactions')
  promise
    .then((last) => {
      setSelectedMonth(new Date(last.year, last.month - 1, 1))
      setSelectedYear(last.year)
      setLastMonthWithData(last)
    })
    .catch(() => {
      const now = new Date()
      setSelectedMonth(new Date(now.getFullYear(), now.getMonth(), 1))
    })
}, [isAuth])
```

**Diferença:** Em vez de guardar o *resultado* no ref (que pode estar null se o fetch não terminou), guarda a *Promise* — e quando auth resolve, aguarda a promise que já está em andamento. Elimina o segundo fetch e a race condition.

---

### Parte B — Não renderizar o picker até `selectedMonth` estar resolvido

**Problema:** `selectedMonth ?? new Date()` faz o picker aparecer no mês errado.

**Solução:** Renderizar um placeholder (skeleton) no lugar do picker enquanto `selectedMonth` for null.

**Arquivo:** `src/app/mobile/dashboard/page.tsx:148-155`

```tsx
// Antes
{period === 'month' ? (
  <MonthScrollPicker
    selectedMonth={selectedMonth ?? new Date()}
    onMonthChange={setSelectedMonth}
    ...
  />
) : (...)}
```

```tsx
// Depois
{period === 'month' ? (
  selectedMonth ? (
    <MonthScrollPicker
      selectedMonth={selectedMonth}
      onMonthChange={setSelectedMonth}
      ...
    />
  ) : (
    <MonthScrollPickerSkeleton />  // placeholder sem movimento
  )
) : (...)}
```

**Skeleton simples:**
```tsx
function MonthScrollPickerSkeleton() {
  return (
    <div className="flex gap-2 px-5 py-2 overflow-hidden">
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className="shrink-0 min-w-[60px] min-h-[44px] rounded-lg bg-gray-100 animate-pulse"
        />
      ))}
    </div>
  )
}
```

Com a Parte A, esse skeleton aparece por apenas ~0-50ms (tempo entre auth resolver e a promise de last-month terminar). Na maioria dos casos, nem pisca.

---

### Parte C — Centralizar a lista de meses no `selectedMonth` (não em `new Date()`)

**Problema:** `MonthScrollPicker` gera meses centrados em hoje. Se o mês com dados estiver fora do range, ele não aparece na lista.

**Arquivo:** `src/components/mobile/month-scroll-picker.tsx:63-72`

```typescript
// Antes — centrado em hoje, nunca se atualiza
const months = React.useMemo(() => {
  const result: Date[] = []
  const start = subMonths(startOfMonth(new Date()), monthsRange)
  for (let i = 0; i <= monthsRange * 2; i++) {
    result.push(addMonths(start, i))
  }
  return result
}, [monthsRange])
```

```typescript
// Depois — centrado no mês selecionado
const months = React.useMemo(() => {
  const result: Date[] = []
  const center = startOfMonth(selectedMonth)  // usa o mês passado como prop
  const start = subMonths(center, monthsRange)
  for (let i = 0; i <= monthsRange * 2; i++) {
    result.push(addMonths(start, i))
  }
  return result
}, [selectedMonth, monthsRange])
```

**Importante:** Isso faz a lista se recalcular quando o usuário navega para meses além do range. Isso é correto e necessário. O scroll para o mês selecionado sempre funcionará porque o mês sempre estará na lista.

---

### Parte D — Scroll inicial `instant`, mudanças do usuário `smooth`

**Problema:** O efeito de scroll sempre usa `behavior: 'smooth'`, incluindo o scroll inicial do componente ao montar. O usuário vê a animação mesmo quando não pediu.

**Arquivo:** `src/components/mobile/month-scroll-picker.tsx:74-93`

```typescript
// Antes — sempre smooth
React.useEffect(() => {
  if (selectedMonthRef.current && scrollContainerRef.current) {
    const container = scrollContainerRef.current
    const button = selectedMonthRef.current
    const scrollPosition = buttonLeft - (containerWidth / 2) + (buttonWidth / 2)
    container.scrollTo({ left: scrollPosition, behavior: 'smooth' })
  }
}, [selectedMonth])
```

```typescript
// Depois — instant no mount, smooth nas mudanças do usuário
const isMountedRef = React.useRef(false)

React.useEffect(() => {
  if (selectedMonthRef.current && scrollContainerRef.current) {
    const container = scrollContainerRef.current
    const button = selectedMonthRef.current
    const containerWidth = container.offsetWidth
    const buttonLeft = button.offsetLeft
    const buttonWidth = button.offsetWidth
    const scrollPosition = buttonLeft - (containerWidth / 2) + (buttonWidth / 2)

    container.scrollTo({
      left: scrollPosition,
      behavior: isMountedRef.current ? 'smooth' : 'instant',
    })
    isMountedRef.current = true
  }
}, [selectedMonth])
```

Com isso, o picker sempre abre exatamente no mês correto, sem animação de entrada. Cliques do usuário continuam com scroll suave.

---

## Resumo das Mudanças

| Parte | Arquivo | Mudança | Impacto |
|-------|---------|---------|---------|
| A | `dashboard/page.tsx` | Guardar Promise (não resultado) no ref | Elimina race condition e 2º fetch |
| B | `dashboard/page.tsx` | Skeleton em vez de `?? new Date()` | Picker nunca aparece no mês errado |
| C | `month-scroll-picker.tsx` | Lista centrada em `selectedMonth` | Mês com dados sempre visível no picker |
| D | `month-scroll-picker.tsx` | `instant` na montagem, `smooth` nas interações | Sem animação de "jump" visível |

---

## Arquivos a Modificar

| Arquivo | Linhas |
|---------|--------|
| `src/app/mobile/dashboard/page.tsx` | 37-42 (estado inicial), 62-63 (ref), 88-116 (efeitos de auth e fetch) |
| `src/app/mobile/dashboard/page.tsx` | 148-155 (render do picker — adicionar skeleton) |
| `src/components/mobile/month-scroll-picker.tsx` | 63-72 (months useMemo) |
| `src/components/mobile/month-scroll-picker.tsx` | 59-60 (novo ref para mount), 74-93 (efeito de scroll) |

---

## Resultado Esperado

```
mount
  ├── selectedMonth = null → picker mostra skeleton
  ├── promise de last-month-with-data iniciada
  └── fetch /auth/me iniciado

auth resolve (isAuth = true)
  └── await promise (já em andamento)
      └── resolve { year: 2026, month: 2 }
          ├── setSelectedMonth(fev/2026)
          └── picker monta com selectedMonth = fev/2026
              ├── lista de meses centrada em fev/2026 (Ago/25 → Ago/26)
              └── scroll instant para fev/2026  ← nenhum movimento visível

usuário navega para jan/2026
  └── smooth scroll para jan/2026  ← animação natural
```
