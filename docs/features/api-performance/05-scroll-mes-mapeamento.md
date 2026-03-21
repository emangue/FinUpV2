# Mapeamento: Scroll do Mês — "Nasce no mês atual, pula para o mês com dados"

> Data: Março/2026

---

## Comportamento Atual (Bug)

O usuário abre o dashboard e percebe:

1. O `MonthScrollPicker` aparece centralizado no **mês atual** (março/2026)
2. Após alguns instantes, o scroll **se move suavemente** para o **último mês com dados** (ex: fevereiro/2026)
3. Só então os dados carregam no mês correto

Esse comportamento é visualmente confuso e desnecessário — o app "sabe" onde devia estar mas mostra outro lugar primeiro.

---

## Diagnóstico: Por Que Acontece

### Cause 1 — Fallback `?? new Date()` no render

**Arquivo:** `src/app/mobile/dashboard/page.tsx:150`

```tsx
<MonthScrollPicker
  selectedMonth={selectedMonth ?? new Date()}  // <-- problema
  onMonthChange={setSelectedMonth}
  ...
/>
```

`selectedMonth` começa como `null` (linha 37):
```typescript
const [selectedMonth, setSelectedMonth] = useState<Date | null>(null)
```

Enquanto o fetch de `last-month-with-data` não termina, o picker recebe `new Date()` (hoje) como selectedMonth. O componente renderiza, posiciona o scroll em março/2026, e quando o estado atualiza para o mês real, aciona o efeito de scroll suave.

---

### Cause 2 — Lista de meses centrada em `new Date()` (não no mês selecionado)

**Arquivo:** `src/components/mobile/month-scroll-picker.tsx:63-72`

```typescript
const months = React.useMemo(() => {
  const result: Date[] = []
  const start = subMonths(startOfMonth(new Date()), monthsRange)  // <-- sempre hoje

  for (let i = 0; i <= monthsRange * 2; i++) {
    result.push(addMonths(start, i))
  }

  return result
}, [monthsRange])
```

A lista de meses é gerada uma vez e nunca se atualiza porque `monthsRange` não muda. O ponto central é sempre **hoje**, não o mês selecionado. Isso causa dois problemas:

1. A lista pode não conter o mês com dados (ex: se o dado mais recente tem mais de 6 meses)
2. Mesmo que contenha, o scroll parte de "hoje" e navega até lá

---

### Cause 3 — Race condition entre auth e o pre-fetch

**Arquivo:** `src/app/mobile/dashboard/page.tsx:88-116`

```typescript
// N3: inicia o fetch antes do auth (elimina 1 RTT)
useEffect(() => {
  fetchLastMonthWithData('transactions')
    .then((last) => { _pendingLastMonth.current = last })
    .catch(() => {})
}, [])

// Default: usa resultado pré-buscado se disponível
useEffect(() => {
  if (!isAuth) return
  const pending = _pendingLastMonth.current
  if (pending) {           // <-- happy path: fetch terminou antes do auth
    ...setSelectedMonth(...)
  } else {                 // <-- race: auth resolveu antes do fetch
    fetchLastMonthWithData('transactions')
      .then((last) => { setSelectedMonth(...) })  // 1 RTT extra
  }
}, [isAuth])
```

Fluxo do bug (quando auth é mais rápido que o fetch):

```
t=0ms   mount
t=0ms   ├── fetch last-month-with-data (inicia)
t=0ms   └── fetch /auth/me (inicia)
t=50ms  auth/me resolve → isAuth = true
t=50ms  ├── _pendingLastMonth.current = null  (fetch ainda não voltou)
t=50ms  ├── MonthScrollPicker renderiza com new Date() → scroll em março
t=50ms  └── inicia fetchLastMonthWithData novamente
t=180ms ├── fetch resolve com { year: 2026, month: 2 }
t=180ms └── setSelectedMonth(fev/2026) → scroll suave de março → fev  ← usuário vê
```

---

## Fluxo Completo (Estado Atual)

```
mount
  ├── selectedMonth = null
  ├── prefetch last-month-with-data (background, sem esperar auth)
  └── prefetch /auth/me

auth resolve (isAuth = true)
  ├── check _pendingLastMonth.current
  │   ├── [happy path] pending != null → setSelectedMonth(lastMonth) → sem jump
  │   └── [race condition] pending = null → fetch again
  │       └── fetch resolve → setSelectedMonth → JUMP ← bug aqui

render com selectedMonth != null
  └── MonthScrollPicker recebe selectedMonth ?? new Date()
      └── [se null] picker mostra "hoje" → depois smooth scroll para o mês real
```

---

## Arquivos Envolvidos

| Arquivo | Linha | Problema |
|---------|-------|---------|
| `src/app/mobile/dashboard/page.tsx` | 37 | `useState<Date \| null>(null)` — sem valor inicial |
| `src/app/mobile/dashboard/page.tsx` | 150 | `selectedMonth ?? new Date()` — fallback para hoje |
| `src/components/mobile/month-scroll-picker.tsx` | 65 | `subMonths(startOfMonth(new Date()), monthsRange)` — lista sempre centrada em hoje |
| `src/components/mobile/month-scroll-picker.tsx` | 88 | `behavior: 'smooth'` — toda mudança de selectedMonth anima, inclusive a inicial |
| `src/app/mobile/dashboard/page.tsx` | 88-116 | Race condition entre auth e pre-fetch do último mês |

---

## Impacto

- **UX:** Usuário vê o scroll se mover a cada abertura do app (exceto quando o pre-fetch vence a corrida com auth)
- **Confiança:** App parece "hesitar" antes de mostrar os dados corretos
- **Performance:** Em alguns casos, 2 chamadas a `last-month-with-data` no cold start (race condition)
