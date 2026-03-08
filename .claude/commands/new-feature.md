# Skill: Nova Feature Frontend

## Contexto
Next.js 14 App Router. Features em `src/features/{nome}/`.

## Antes de criar, pergunte
1. Nome da feature (kebab-case)
2. Endpoints de backend que ela consome
3. Componentes necessários (listagem, formulário, modal?)
4. Precisa de página? (mobile / desktop / ambas / nenhuma)

## Estrutura a criar
```
src/features/{nome}/
├── index.ts
├── types/index.ts
├── services/{nome}-api.ts
├── hooks/use-{nome}.ts
└── components/
    ├── index.ts
    └── {NomeComponent}.tsx
```

## Regras
- URLs nunca hardcoded: sempre via `ENDPOINTS` de `src/core/config/api.config.ts`
- Sempre `fetchWithAuth` (nunca `fetch()` direto)
- Hooks com cancellation token via `AbortController` + cleanup no useEffect
- Cache in-memory com TTL se dados são lidos com frequência (usar `in-memory-cache.ts`)
- Não editar `/components/ui/` (gerenciado pelo shadcn)
- Mobile: `src/app/mobile/{nome}/page.tsx` | Desktop: `src/app/{nome}/page.tsx`

## Padrão de hook
```typescript
export function use{Nome}() {
  const [data, setData] = useState<Tipo[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    fetch{Nome}()
      .then((result) => { if (!cancelled) setData(result) })
      .catch((err) => { if (!cancelled) setError(err.message) })
      .finally(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [])

  return { data, loading, error }
}
```
