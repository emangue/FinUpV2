# Plano de Correção do Build Frontend

**Data:** 21/02/2026  
**Objetivo:** Resolver todos os erros que impedem `npm run build` de passar.

---

## Resumo dos Problemas

| Categoria | Arquivos | Erros | Causa |
|-----------|----------|-------|-------|
| **1. Testes Jest** | 6 arquivos em `features/investimentos/**/__tests__/*.test.tsx` | ~500 | TypeScript verifica arquivos de teste sem `@types/jest` |
| **2. plano-chart.tsx** | `features/plano-aposentadoria/components/plano-chart.tsx` | 2 | Tipo do callback `content` do LabelList (recharts) incompatível com Props da lib |

---

## Detalhamento

### 1. Arquivos de teste (Jest)

**Arquivos afetados:**
- `src/features/investimentos/__tests__/api-integration.test.tsx`
- `src/features/investimentos/__tests__/e2e-integration.test.tsx`
- `src/features/investimentos/__tests__/use-investimentos-integration.test.tsx`
- `src/features/investimentos/__tests__/utils.test.tsx`
- `src/features/investimentos/components/__tests__/export-investimentos.test.tsx`
- `src/features/investimentos/components/__tests__/portfolio-overview.test.tsx`
- `src/features/investimentos/hooks/__tests__/use-investimentos.test.tsx`

**Erro:** `Cannot find name 'describe'`, `'it'`, `'expect'`, `'jest'`, etc.  
**Causa:** O tsconfig inclui `**/*.tsx` e não há `@types/jest` instalado (ou os testes não estão excluídos do build de produção).

**Soluções possíveis (escolher uma):**

| Opção | Ação | Prós | Contras |
|-------|------|------|---------|
| **A** | Excluir `**/__tests__/**` e `**/*.test.tsx` do tsconfig | Rápido, testes não afetam build | Testes não são type-checked no build |
| **B** | Instalar `@types/jest` e `@types/node` | Testes type-checked | Pode exigir ajustes em jest.config |
| **C** | Mover testes para pasta fora de `src` (ex: `__tests__/` na raiz) | Separação clara | Reorganização maior |

**Recomendação:** Opção A – excluir testes do build. O Next.js não usa esses arquivos no bundle; o problema é só o `tsc` verificando tudo.

---

### 2. plano-chart.tsx (LabelList content)

**Arquivo:** `src/features/plano-aposentadoria/components/plano-chart.tsx`  
**Linhas:** 319 e 348

**Erro:** O tipo do callback `content` do `LabelList` (recharts) exige que `props` aceite `Props` da lib. A lib passa `value` como `string | number`, mas nosso tipo declara `value?: number`.

**Solução:** Remover a anotação de tipo explícita e deixar TypeScript inferir, OU usar tipo mais amplo:

```tsx
// Opção 1: Remover tipo (inferência)
content={(props) => { ... }}

// Opção 2: Usar tipo permissivo
content={(props: Record<string, unknown>) => { ... }}

// Opção 3: Aceitar value como string | number
content={(props: { x?: number | string; y?: number | string; value?: number | string; ... }) => { ... }}
```

**Recomendação:** Opção 3 – incluir `value?: number | string` no tipo.

---

## Plano de Execução (ordem sugerida)

1. **Excluir testes do tsconfig** (resolve ~500 erros)
   - Em `tsconfig.json`, adicionar em `exclude`:
     - `"**/__tests__/**"`
     - `"**/*.test.ts"`
     - `"**/*.test.tsx"`

2. **Corrigir plano-chart.tsx** (resolve 2 erros)
   - Nas linhas 319 e 348, alterar o tipo do parâmetro `props` para incluir `value?: number | string`

3. **Validar**
   - `npm run build` deve passar
   - `npx tsc --noEmit` deve passar (se ainda for usado)

---

### 3. useSearchParams sem Suspense (mobile/personalizar-plano)

**Arquivo:** `src/app/mobile/personalizar-plano/page.tsx`  
**Erro:** `useSearchParams() should be wrapped in a suspense boundary`  
**Solução:** Envolver o conteúdo que usa `useSearchParams` em `<Suspense fallback={...}>`. ✅

### 4. useSidebar sem SidebarProvider (transactions/mobile, dashboard/mobile)

**Arquivos:** `TransactionsMobileHeader`, `MobileHeader`  
**Erro:** `useSidebar must be used within a SidebarProvider`  
**Solução:** Remover `SidebarTrigger` dos headers mobile e substituir por `Link` para `/settings` (fluxo mobile não usa sidebar). ✅

### 5. Middleware → Proxy (Next.js 16)

**Arquivos:** `src/middleware.ts` → `src/proxy.ts`  
**Aviso:** `middleware` deprecado em favor de `proxy`  
**Solução:** Migrado para `proxy.ts` com função `proxy()`. Removido `middleware 2.ts` duplicado. ✅

---

## Checklist pós-correção

- [x] `npm run build` conclui sem erros
- [ ] Aplicação inicia com `npm run start`
- [ ] Dashboard mobile carrega em `/mobile/dashboard`
- [ ] Nenhum erro 404 nos endpoints de investimentos

---

## Arquivos já corrigidos nesta sessão

- `budget/page.tsx` – `categoria_geral` → `grupo` ✅
- `dashboard-layout.tsx` – criado (mínimo, sem sidebar) ✅
- `dashboard/mobile/layout.tsx` – usa BottomNavigation ✅
- `transactions/mobile/layout.tsx` – usa BottomNavigation ✅
- `api.config.ts` – `ADMIN_ALL` em SCREENS ✅
- `orcamento-tab.tsx` – tipagem do Promise.allSettled ✅
- `plano-chart.tsx` – dot retorna `<circle r={0}>` em vez de null ✅
- Arquivos duplicados (page 2, page 3, etc.) – removidos ✅
- `middleware.ts` → `proxy.ts` (Next.js 16) ✅
- `middleware 2.ts` – removido ✅
