# TECH SPEC — UX Fundação: Bugs + Navegação + Empty States

**Sub-projeto:** 02 | **Sprint:** 1 | Apenas frontend — sem migrations

---

## B1 — Corrigir navegação em loop

**Problema:** `router.back()` dentro de modais usa o histórico do browser, que pode estar vazio ou apontar para telas externas.

```tsx
// ❌ Antes (problemático)
<Button onClick={() => router.back()}>← Voltar</Button>

// ✅ Depois — destino explícito via prop
interface EditTransactionModalProps {
  onClose: () => void  // pai decide para onde voltar
  // ...
}

// Na página /mobile/transacoes:
<EditTransactionModal onClose={() => router.push('/mobile/transacoes')} />

// Na página /mobile/inicio:
<EditTransactionModal onClose={() => router.push('/mobile/inicio')} />
```

**Arquivos a verificar:**
- `src/features/transactions/components/edit-transaction-modal.tsx`
- Qualquer uso de `router.back()` em `src/app/mobile/`

```bash
# Encontrar todos os usos problemáticos:
grep -r "router\.back()" app_dev/frontend/src/app/mobile/ --include="*.tsx"
```

---

## B2 — Corrigir replicação de edição

**Causa provável:** estado de formulário compartilhado via Context ou store global, não isolado por instância de modal.

```tsx
// ❌ Antes — estado no store global (persiste entre modais)
const { editingTransaction, setEditing } = useTransactionStore()

// ✅ Depois — estado local por instância do modal
export function EditTransactionModal({ transaction, onClose, onSave }) {
  // Estado 100% local, zerado ao montar
  const [form, setForm] = useState({
    grupo: transaction.Grupo ?? "",
    valor: transaction.Valor ?? 0,
    // ...
  })
  // ...
}
```

**Diagnóstico primeiro:**
```bash
grep -r "useTransactionStore\|editingTransaction\|setEditing" \
  app_dev/frontend/src/ --include="*.tsx" | head -30
```

---

## B3 — Scroll em tabela mobile

```tsx
// src/features/transactions/components/transactions-table.tsx
<div
  className="overflow-y-auto"
  style={{
    WebkitOverflowScrolling: "touch",
    maxHeight: "calc(100dvh - 180px)",  // dvh = dynamic viewport height
  }}
>
  <table className="w-full">
    <thead className="sticky top-0 bg-background z-10 shadow-sm">
      {/* cabeçalho fixo */}
    </thead>
    <tbody>
      {/* linhas roláveis */}
    </tbody>
  </table>
</div>
```

---

## B4 — Centralizar formatação monetária

```ts
// src/lib/format.ts (criar se não existir)
export function formatBRL(value: number | null | undefined): string {
  if (value == null) return "R$ —"
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
  }).format(value)
}

// Uso nos componentes:
import { formatBRL } from "@/lib/format"
// Antes: {value.toFixed(2)}
// Depois: {formatBRL(value)}
```

**Encontrar usos diretos para substituir:**
```bash
grep -r "toFixed(2)\|\.toLocaleString" app_dev/frontend/src/ --include="*.tsx" | grep -v "node_modules"
```

---

## S19 — Redesign da navegação

### Bottom navigation (mobile)

```tsx
// src/components/bottom-nav.tsx
const NAV_ITEMS = [
  { href: "/mobile/inicio",       icon: Home,        label: "Início"     },
  { href: "/mobile/transacoes",   icon: List,        label: "Transações" },
  { href: "/mobile/upload",       icon: Upload,      label: "Upload", fab: true },
  { href: "/mobile/plano",        icon: Target,      label: "Plano"      },
  { href: "/mobile/carteira",     icon: TrendingUp,  label: "Carteira"   },
]

export function BottomNav() {
  const pathname = usePathname()
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-background border-t flex items-end justify-around px-2 pb-safe">
      {NAV_ITEMS.map(item => {
        const active = pathname.startsWith(item.href)
        if (item.fab) return (
          <Link key={item.href} href={item.href}
            className="flex flex-col items-center -mt-5 mb-1">
            <div className="w-14 h-14 rounded-full bg-primary flex items-center justify-center shadow-lg">
              <item.icon className="text-primary-foreground w-6 h-6" />
            </div>
            <span className="text-xs mt-1 text-primary font-medium">{item.label}</span>
          </Link>
        )
        return (
          <Link key={item.href} href={item.href}
            className={cn("flex flex-col items-center py-2 px-3 gap-1",
              active ? "text-primary" : "text-muted-foreground")}>
            <item.icon className={cn("w-5 h-5", active && "fill-primary")} />
            <span className="text-xs">{item.label}</span>
          </Link>
        )
      })}
    </nav>
  )
}
```

---

## S27 — Empty states

```tsx
// src/components/empty-state.tsx
interface EmptyStateProps {
  icon: string
  title: string
  description: string
  ctaLabel: string
  ctaHref: string
}

export function EmptyState({ icon, title, description, ctaLabel, ctaHref }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-6 text-center">
      <span className="text-5xl mb-4">{icon}</span>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground mb-6 max-w-xs">{description}</p>
      <Link href={ctaHref}>
        <Button>{ctaLabel} →</Button>
      </Link>
    </div>
  )
}

// Uso por tela:
// /mobile/inicio: <EmptyState icon="📊" title="Seus dados financeiros vão aparecer aqui"
//   description="Comece subindo seu extrato bancário" ctaLabel="Fazer upload" ctaHref="/mobile/upload" />
// /mobile/transacoes: icon="📋" title="Nenhuma transação ainda" ctaLabel="Fazer upload"
// /mobile/plano: icon="🎯" title="Crie seu Plano Financeiro" ctaLabel="Criar plano" ctaHref="/mobile/plano/novo"
// /mobile/carteira: icon="📈" title="Adicione seus investimentos" ctaLabel="Adicionar" ctaHref="/mobile/carteira/novo"
```

**Padrão de uso na tela:**
```tsx
if (isLoading) return <TableSkeleton />
if (!data || data.length === 0) return <EmptyState {...EMPTY_STATE_CONFIG[pathname]} />
return <NormalContent data={data} />
```

---

## Checklist

- [ ] `grep router.back()` → mapear todos os casos; substituir por `router.push(destino-explicito)`
- [ ] Diagnosticar origem do bug de replicação (store vs. context vs. ref compartilhada)
- [ ] Corrigir estado local em `EditTransactionModal`
- [ ] `formatBRL()` em `src/lib/format.ts` + substituir `toFixed(2)` nos componentes
- [ ] Scroll mobile: `overflow-y auto` + `dvh` + sticky header
- [ ] `BottomNav` com 5 itens + FAB de Upload
- [ ] Sidebar desktop atualizada com mesmos 5 destinos
- [ ] `EmptyState` component criado
- [ ] Empty state em `/mobile/inicio`, `/mobile/transacoes`, `/mobile/plano`, `/mobile/carteira`
- [ ] Empty state nunca aparece durante loading (guards de `isLoading`)
