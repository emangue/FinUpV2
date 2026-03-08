# Skill: Frontend — Guia de Desenvolvimento Next.js

Você é um assistente especialista no frontend do FinUpV2. Antes de sugerir qualquer mudança,
verifique se o padrão abaixo está sendo seguido. Esse guia é a fonte da verdade para
decisões de componentes, estado, API calls e styling no frontend.

---

## Estrutura do Projeto

```
app_dev/frontend/src/
├── app/                        # Next.js App Router (páginas e rotas)
│   ├── layout.tsx              # Root: AuthProvider + Toaster
│   ├── mobile/
│   │   └── layout.tsx          # Mobile: BottomNavigation + OnboardingGuard
│   └── api/[...proxy]/route.ts # Proxy reverso para o backend
├── components/
│   ├── ui/                     # shadcn/ui (Button, Dialog, Alert, etc.) — NÃO EDITE
│   ├── atoms/                  # Elementos básicos (Badge, ProgressBar, MonthSelector)
│   ├── molecules/              # Compostos (CategoryRow, StatCard, HeaderBar)
│   ├── organisms/              # Complexos (DonutChart, BottomNavigation)
│   └── mobile/                 # Específicos mobile (MobileHeader, TransactionCard)
├── contexts/
│   ├── AuthContext.tsx          # Estado de autenticação global
│   └── PendingUploadContext.tsx # Passagem de arquivo entre componentes
├── core/
│   ├── config/api.config.ts    # TODOS os endpoints do backend ficam aqui
│   ├── utils/api-client.ts     # fetchWithAuth, apiGet, apiPost, apiPatch, apiDelete
│   ├── hooks/use-require-auth.ts # Proteção de rotas
│   └── types/shared.types.ts   # Tipos compartilhados entre features
├── hooks/
│   ├── use-auth.ts             # Wrapper do AuthContext
│   └── use-mobile.ts           # Detecção de viewport mobile (< 768px)
├── lib/
│   ├── utils.ts                # cn() — merge de classes Tailwind
│   ├── format.ts               # formatBRL() e formatadores de data
│   └── logger.ts               # Console apenas em dev
├── features/                   # Features isoladas por domínio
│   └── {nome}/
│       ├── index.ts            # Barrel export
│       ├── types/index.ts
│       ├── services/{nome}-api.ts
│       ├── hooks/use-{nome}.ts
│       └── components/
│           ├── index.ts
│           └── {NomeComponent}.tsx
└── config/                     # Tokens de design mobile
    ├── mobile-animations.ts
    ├── mobile-colors.ts
    └── mobile-dimensions.ts
```

---

## Regras de API — SEMPRE USE ESTAS FUNÇÕES

### Funções disponíveis em `src/core/utils/api-client.ts`

```typescript
// Use estas — nunca raw fetch()
fetchWithAuth(url, options?)          // Fetch base com auth automático
fetchJsonWithAuth<T>(url, options?)   // Fetch + parse JSON + tratamento de erro

// Helpers preferidos (mais semânticos)
apiGet<T>(url)
apiPost<T>(url, data)
apiPatch<T>(url, data)
apiPut<T>(url, data)
apiDelete<T>(url)
```

### Endpoints em `src/core/config/api.config.ts`

```typescript
// ✅ CORRETO — URL vem da config centralizada
import { API_ENDPOINTS } from '@/core/config/api.config'
const data = await apiGet<MeuTipo>(API_ENDPOINTS.MEU_RECURSO)

// ❌ ERRADO — URL hardcoded no serviço ou componente
const data = await fetch('http://localhost:8000/api/v1/meu-recurso')
```

**Ao adicionar um novo endpoint, registre PRIMEIRO em `api.config.ts`.**

---

## Padrão de Feature Completa

### 1. types/index.ts
```typescript
export interface MeuItem {
  id: number
  nome: string
  valor: number
}

export interface MeuItemCreate {
  nome: string
  valor: number
}
```

### 2. services/meu-item-api.ts
```typescript
import { apiGet, apiPost, apiPatch, apiDelete } from '@/core/utils/api-client'
import { API_ENDPOINTS } from '@/core/config/api.config'
import type { MeuItem, MeuItemCreate } from '../types'

export async function fetchMeusItens(): Promise<MeuItem[]> {
  return apiGet<MeuItem[]>(API_ENDPOINTS.MEUS_ITENS)
}

export async function createMeuItem(data: MeuItemCreate): Promise<MeuItem> {
  return apiPost<MeuItem>(API_ENDPOINTS.MEUS_ITENS, data)
}

export async function updateMeuItem(id: number, data: Partial<MeuItemCreate>): Promise<MeuItem> {
  return apiPatch<MeuItem>(`${API_ENDPOINTS.MEUS_ITENS}/${id}`, data)
}

export async function deleteMeuItem(id: number): Promise<void> {
  return apiDelete(`${API_ENDPOINTS.MEUS_ITENS}/${id}`)
}
```

### 3. hooks/use-meu-item.ts
```typescript
'use client'
import { useState, useEffect, useCallback } from 'react'
import { fetchMeusItens, createMeuItem, deleteMeuItem } from '../services/meu-item-api'
import type { MeuItem, MeuItemCreate } from '../types'

export function useMeuItem() {
  const [items, setItems] = useState<MeuItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    let cancelled = false
    setLoading(true)
    try {
      const data = await fetchMeusItens()
      if (!cancelled) setItems(data)
    } catch (e) {
      if (!cancelled) setError('Erro ao carregar itens')
    } finally {
      if (!cancelled) setLoading(false)
    }
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    const cleanup = load()
    return () => { cleanup.then(fn => fn?.()) }
  }, [load])

  const create = useCallback(async (data: MeuItemCreate) => {
    const novo = await createMeuItem(data)
    setItems(prev => [...prev, novo])
    return novo
  }, [])

  const remove = useCallback(async (id: number) => {
    await deleteMeuItem(id)
    setItems(prev => prev.filter(i => i.id !== id))
  }, [])

  return { items, loading, error, refetch: load, create, remove }
}
```

### 4. components/MeuItemList.tsx
```typescript
'use client'
import { useMeuItem } from '../hooks/use-meu-item'
import { formatBRL } from '@/lib/format'
import { cn } from '@/lib/utils'

export function MeuItemList() {
  const { items, loading, error } = useMeuItem()

  if (loading) return <div>Carregando...</div>
  if (error) return <div className="text-red-500">{error}</div>

  return (
    <ul className="space-y-2">
      {items.map(item => (
        <li key={item.id} className={cn('p-3 rounded-lg bg-card')}>
          <span>{item.nome}</span>
          <span className="font-medium">{formatBRL(item.valor)}</span>
        </li>
      ))}
    </ul>
  )
}
```

### 5. index.ts (barrel export)
```typescript
export { MeuItemList } from './components/MeuItemList'
export { useMeuItem } from './hooks/use-meu-item'
export type * from './types'
```

---

## Routing e Páginas

### Desktop: `src/app/{rota}/page.tsx`
### Mobile: `src/app/mobile/{rota}/page.tsx`

```typescript
// Sempre proteja páginas autenticadas:
import { useRequireAuth } from '@/core/hooks/use-require-auth'

export default function MinhaPagina() {
  useRequireAuth()  // Redireciona para /auth/login se não autenticado
  // ...
}
```

### Quando criar rota mobile vs desktop
- Se a feature existe no desktop, criar a versão mobile em `/app/mobile/{rota}/`
- Mobile usa componentes de `/components/mobile/` (MobileHeader, BottomSheet)
- Desktop usa componentes de `/components/molecules/` e `/components/organisms/`
- Componentes de `/components/ui/` (shadcn) são usados em ambos

---

## Estado e Contexto

### Quando usar cada abordagem

| Situação | Solução |
|----------|---------|
| Estado local de UI (modal aberto, form field) | `useState` |
| Dados de uma feature (lista de itens, loading) | Hook customizado da feature |
| Estado compartilhado por toda a app (auth, usuário) | Context (`AuthContext`) |
| Passagem de dado entre páginas (ex: arquivo selecionado) | Context dedicado (`PendingUploadContext`) |
| Cache de servidor / sincronização | Não há React Query — use hook com `refetch` |

**Não existe Zustand, Redux ou React Query neste projeto.** Mantenha assim.

### Usando auth
```typescript
import { useAuth } from '@/hooks/use-auth'

const { user, isAuthenticated, logout } = useAuth()
```

---

## Styling com Tailwind

### Regras
- Use `cn()` de `@/lib/utils` para combinar classes condicionais
- Prefira classes Tailwind a inline styles
- Use CSS variables de `globals.css` para cores do tema (não hardcode hex)
- Dark mode: classe `.dark` no HTML — use variantes `dark:` do Tailwind

```typescript
import { cn } from '@/lib/utils'

// ✅ CORRETO
<div className={cn('p-4 rounded-lg', isActive && 'bg-primary text-primary-foreground')} />

// ❌ EVITE
<div style={{ backgroundColor: '#3b82f6', padding: 16 }} />
```

### Design tokens disponíveis
```css
/* Cores do tema (via CSS variables em globals.css) */
bg-background, bg-card, bg-primary, bg-secondary, bg-muted
text-foreground, text-muted-foreground, text-primary
border-border

/* Para mobile, use os tokens de src/config/ */
import { MOBILE_COLORS } from '@/config/mobile-colors'
import { MOBILE_DIMENSIONS } from '@/config/mobile-dimensions'
```

---

## TypeScript

- Use `interface` para shapes de objetos (entidades, props de componente)
- Use `type` para unions, aliases, tipos condicionais
- Tipos de API e domínio ficam em `features/{nome}/types/index.ts`
- Tipos compartilhados entre features ficam em `core/types/shared.types.ts`
- Sempre tipar o retorno das funções de serviço com generics: `apiGet<MeuTipo>(url)`

### Verificação SSR
```typescript
// Código que acessa window/document DEVE ter este guard:
if (typeof window !== 'undefined') {
  // código client-only
}
```

---

## Performance

### Memoize quando houver custo real
```typescript
// Computação cara sobre lista grande
const filtered = useMemo(() => items.filter(i => i.valor > 0), [items])

// Função passada como prop ou usada como dependência de useEffect
const handleSubmit = useCallback(async (data) => { ... }, [dep1, dep2])
```

### Parallel requests
```typescript
const [items, config] = await Promise.all([
  fetchMeusItens(),
  fetchConfig()
])
```

### Cancellation em useEffect (OBRIGATÓRIO para async)
```typescript
useEffect(() => {
  let cancelled = false
  fetchData().then(data => {
    if (!cancelled) setData(data)
  })
  return () => { cancelled = true }
}, [])
```

---

## Utilitários Disponíveis

```typescript
import { formatBRL } from '@/lib/format'           // "R$ 1.234,56"
import { cn } from '@/lib/utils'                    // merge de classes Tailwind
import { logger } from '@/lib/logger'               // console só em dev
import { useIsMobile } from '@/hooks/use-mobile'    // true se < 768px
import { useAuth } from '@/hooks/use-auth'          // usuário e auth state
import { useRequireAuth } from '@/core/hooks/use-require-auth'  // guard de rota
```

---

## O Que É OK Fazer

- ✅ Criar nova feature em `src/features/{nome}/` seguindo o padrão de 5 arquivos
- ✅ Adicionar endpoint em `api.config.ts` e implementar no serviço correspondente
- ✅ Criar componente em `atoms/`, `molecules/` ou `organisms/` conforme complexidade
- ✅ Usar shadcn/ui de `/components/ui/` para inputs, dialogs, buttons, cards
- ✅ Adicionar variante mobile em `/app/mobile/{rota}/` para features existentes
- ✅ Usar `useMemo`/`useCallback` quando a dependência exigir estabilidade
- ✅ Usar `Promise.all()` para requests paralelos independentes
- ✅ Criar Context dedicado para estado cross-feature quando necessário

## O Que NÃO Fazer

- ❌ Hardcodar URLs de API no componente ou hook — use `api.config.ts`
- ❌ Usar `fetch()` diretamente — use sempre `fetchWithAuth` ou os helpers `api*`
- ❌ Guardar token em localStorage — o backend usa httpOnly cookie (já configurado)
- ❌ Editar arquivos em `/components/ui/` — são gerenciados pelo shadcn
- ❌ Criar store global (Zustand, Redux) sem discussão — o projeto não usa
- ❌ Colocar lógica de negócio no componente — mova para o hook
- ❌ Colocar chamada de API no componente — mova para o serviço
- ❌ Esquecer `useRequireAuth()` em páginas autenticadas
- ❌ Esquecer cleanup/cancellation em useEffect com async
- ❌ Criar arquivo `page 2.tsx`, `page 3.tsx` — já há duplicatas históricas, não crie mais
- ❌ Usar magic numbers de cor inline — use CSS variables do tema
- ❌ Acessar `window` sem guard SSR (`typeof window !== 'undefined'`)

---

## Checklist Antes de Abrir PR

- [ ] Endpoint registrado em `api.config.ts`
- [ ] Serviço usa `apiGet/apiPost/apiPatch/apiDelete` (nunca raw fetch)
- [ ] Hook tem cancellation token no useEffect
- [ ] Componente não contém chamadas de API nem lógica de negócio
- [ ] Página protegida com `useRequireAuth()`
- [ ] Tipos definidos em `types/index.ts` da feature
- [ ] Barrel export atualizado em `index.ts` da feature
- [ ] Classes Tailwind usam `cn()` para condicionais
- [ ] Sem acesso a `window` sem guard SSR
- [ ] `useMemo`/`useCallback` usados onde há dependências instáveis
