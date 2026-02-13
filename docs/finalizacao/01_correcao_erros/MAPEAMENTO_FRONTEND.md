# 🔍 MAPEAMENTO DE ERROS - FRONTEND

**Data:** 10/02/2026  
**Total de Erros:** 17 erros em 9 arquivos  
**Status:** ✅ Mapeamento Completo

---

## 📊 ESTATÍSTICAS GERAIS

| Categoria | Quantidade | % Total |
|-----------|------------|---------|
| **Type Mismatch** | 8 | 47% |
| **Property Does Not Exist** | 7 | 41% |
| **Wrong Comparison** | 2 | 12% |

### Por Prioridade:
- 🔴 **P0 (Bloqueante):** 9 erros (53%)
- 🟠 **P1 (Crítico):** 6 erros (35%)
- 🟡 **P2 (Médio):** 2 erros (12%)

### Por Arquivo:
- `EditGoalModal.tsx`: 5 erros
- `manage/page.tsx`: 5 erros
- `ManageGoalsListItem.tsx`: 3 erros
- `[goalId]/page.tsx`: 2 erros
- Outros: 1 erro cada

---

## 🔴 CATEGORIA 1: TYPE MISMATCH (8 erros)

### 1.1 - MobileHeader leftAction (2 ocorrências)
**Arquivos:**
- `/app/mobile/budget/[goalId]/page.tsx:75`
- `/app/mobile/budget/new/page.tsx:118`

**Erro:**
```typescript
Type '{ icon: JSX.Element; label: string; onClick: () => void; }' is not assignable 
to type '"back" | "logo" | null | undefined'.
```

**Prioridade:** 🔴 P0 (Bloqueante - funcionalidade não funciona)

**Causa Raiz:**
Componente `MobileHeader` espera `leftAction` como:
```typescript
leftAction?: 'back' | 'logo' | null;
```

Mas o código está passando um **objeto**:
```typescript
leftAction={{
  icon: <ArrowLeft className="w-5 h-5" />,
  label: 'Voltar',
  onClick: () => router.back()
}}
```

**Solução:**
- **Opção A (Recomendada):** Usar string simples `'back'` e deixar componente lidar com ação
- **Opção B:** Criar prop adicional `leftActionCustom` para objeto customizado
- **Opção C:** Mudar type de `leftAction` para aceitar objeto OU string

**Impacto:** Botão de voltar não funciona nas páginas de metas.

---

### 1.2 - Goal ID Type Mismatch (4 ocorrências)
**Arquivos:**
- `/features/goals/components/ManageGoalsListItem.tsx:141` (onToggle)
- `/features/goals/components/ManageGoalsListItem.tsx:149` (onEdit)
- `/app/mobile/budget/manage/page.tsx:37` (find)
- `/app/mobile/budget/manage/page.tsx:59` (find)

**Erro:**
```typescript
Argument of type 'number' is not assignable to parameter of type 'string'.
// OU
This comparison appears to be unintentional because the types 'number' and 'string' have no overlap.
```

**Prioridade:** 🔴 P0 (Bloqueante - funcionalidade não funciona)

**Causa Raiz:**
Interface `Goal` define `id` como **number**:
```typescript
export interface Goal {
  id: number  // ← Backend retorna number
  ...
}
```

Mas callbacks/buscas esperam **string**:
```typescript
onToggle: (goalId: string, isActive: boolean) => void
onEdit: (goalId: string) => void
const goal = goals.find((g) => g.id === goalId) // goalId é string
```

**Solução:**
- **Opção A (Recomendada):** Mudar callbacks para aceitar `number` (mais consistente com backend)
- **Opção B:** Converter `goal.id` para string ao chamar: `onToggle(String(goal.id), ...)`
- **Opção C:** Usar `.toString()` nos callbacks

**Impacto:** Toggle de meta ativa/inativa e edição não funcionam.

---

### 1.3 - Goal Status Property (1 ocorrência)
**Arquivo:** `/features/goals/hooks/use-goal-detail.ts:24`

**Erro:**
```typescript
Object literal may only specify known properties, and 'status' does not exist 
in type 'Goal | ((prevState: Goal | null) => Goal | null)'.
```

**Prioridade:** 🟠 P1 (Crítico - feature incompleta)

**Código:**
```typescript
setGoal({
  ...data,
  status: calculateGoalStatus(data)  // ← Erro aqui
})
```

**Causa Raiz:**
Interface `Goal` NÃO tem campo `status`, mas código tenta adicionar.

**Solução:**
- **Opção A (Recomendada):** Usar `GoalWithProgress` em vez de `Goal`
- **Opção B:** Adicionar `status` opcional em `Goal` interface
- **Opção C:** Criar nova interface local estendendo Goal

**Impacto:** Status calculado (ativo/atrasado/concluído) não aparece.

---

### 1.4 - Ativo Boolean vs Number (1 ocorrência)
**Arquivo:** `/app/mobile/budget/manage/page.tsx:26`

**Erro:**
```typescript
This comparison appears to be unintentional because the types 'boolean' and 'number' have no overlap.
```

**Código:**
```typescript
initialStates[goal.id] = goal.ativo === true || goal.ativo === 1
```

**Prioridade:** 🟡 P2 (Médio - workaround funciona mas incorreto)

**Causa Raiz:**
Backend pode retornar `ativo` como **boolean OU number** (SQLite inconsistência).
Interface TypeScript define como `boolean`:
```typescript
export interface Goal {
  ativo: boolean
}
```

**Solução:**
- **Opção A (Recomendada):** Backend normalizar para sempre boolean
- **Opção B:** Simplificar para `!!goal.ativo` (truthy check)
- **Opção C:** Mudar type para `ativo: boolean | number`

**Impacto:** Funciona mas TypeScript reclama (código defensivo).

---

## 🟠 CATEGORIA 2: PROPERTY DOES NOT EXIST (7 erros)

### 2.1 - Goal.orcamento (2 ocorrências)
**Arquivo:** `/features/goals/components/EditGoalModal.tsx:38,47`

**Erro:**
```typescript
Property 'orcamento' does not exist on type 'Goal'.
```

**Código:**
```typescript
const [orcamento, setOrcamento] = React.useState(goal.orcamento.toString())
...
setOrcamento(goal.orcamento.toString())
```

**Prioridade:** 🔴 P0 (Bloqueante - modal não abre)

**Causa Raiz:**
Interface `Goal` NÃO tem campo `orcamento`. Campo correto é **`valor_alvo`**.

**Solução:**
Substituir `goal.orcamento` por `goal.valor_alvo`:
```typescript
const [orcamento, setOrcamento] = React.useState(goal.valor_alvo.toString())
```

**Impacto:** Modal de edição quebra ao tentar abrir.

---

### 2.2 - Goal.categoria (3 ocorrências)
**Arquivos:**
- `/features/goals/components/ManageGoalsListItem.tsx:32`
- `/app/mobile/budget/manage/page.tsx:97`
- `/app/mobile/budget/manage/page.tsx:98`

**Erro:**
```typescript
Property 'categoria' does not exist on type 'Goal'.
```

**Código:**
```typescript
const icon = iconMap[goal.categoria?.toLowerCase() || 'investimento'] || '💼'
const gastosGoals = goals.filter((g) => g.categoria?.toLowerCase() !== 'investimento')
const investimentosGoals = goals.filter((g) => g.categoria?.toLowerCase() === 'investimento')
```

**Prioridade:** 🔴 P0 (Bloqueante - filtros não funcionam)

**Causa Raiz:**
Campo `categoria` não existe em `Goal`. Possível origem:
1. Backend não retorna esse campo
2. Deveria usar outro campo (ex: `nome`, `descricao`)
3. Campo foi removido mas código não atualizado

**Solução (REQUER INVESTIGAÇÃO):**
- **Análise necessária:** Verificar backend se retorna `categoria`
- **Se backend retorna:** Adicionar `categoria?: string` em interface
- **Se não retorna:** Implementar lógica alternativa (ex: baseado em vinculações)

**Impacto:** Ícones não aparecem, filtros gastos/investimentos quebram.

---

### 2.3 - Goal.mes_referencia (1 ocorrência)
**Arquivo:** `/features/goals/components/EditGoalModal.tsx:136`

**Erro:**
```typescript
Property 'mes_referencia' does not exist on type 'Goal'.
```

**Código:**
```typescript
<p className="text-xs text-gray-400 text-right">{goal.mes_referencia}</p>
```

**Prioridade:** 🟠 P1 (Crítico - informação faltando)

**Causa Raiz:**
Campo `mes_referencia` não existe em `Goal`. Campo correto é **`prazo`** (YYYY-MM).

**Solução:**
```typescript
<p className="text-xs text-gray-400 text-right">{goal.prazo}</p>
```

**Impacto:** Data de referência não aparece no modal.

---

### 2.4 - Goal.valor_atual (2 ocorrências)
**Arquivo:** `/features/goals/components/EditGoalModal.tsx:192,207`

**Erro:**
```typescript
Property 'valor_atual' does not exist on type 'Goal'.
```

**Código:**
```typescript
Valor atual: {formatCurrency(goal.valor_atual || 0)}
...
O valor atual (R$ {formatCurrency(goal.valor_atual || 0)}) é calculado automaticamente
```

**Prioridade:** 🔴 P0 (Bloqueante - valor incorreto)

**Causa Raiz:**
Campo `valor_atual` está **aninhado** em `progresso`:
```typescript
export interface Goal {
  progresso?: {
    valor_atual: number  // ← Aqui
    percentual: number
    falta: number
    categorias_vinculadas: number
  }
}
```

**Solução:**
```typescript
Valor atual: {formatCurrency(goal.progresso?.valor_atual || 0)}
```

**Impacto:** Valor atual aparece como 0 sempre.

---

### 2.5 - AuthContext.isLoading (1 ocorrência)
**Arquivo:** `/core/components/require-admin.tsx:41`

**Erro:**
```typescript
Property 'isLoading' does not exist on type 'AuthContextType'.
```

**Código:**
```typescript
const { user, isLoading } = useAuth()
```

**Prioridade:** 🟠 P1 (Crítico - loading state incorreto)

**Causa Raiz:**
Interface `AuthContextType` define campo como **`loading`** (não `isLoading`):
```typescript
interface AuthContextType {
  loading: boolean  // ← Nome correto
  ...
}
```

**Solução:**
```typescript
const { user, loading } = useAuth()  // ← Corrigir nome
```

**Impacto:** Loading state não funciona, tela pode aparecer vazia.

---

### 2.6 - Preview Transaction.occurrences (2 ocorrências)
**Arquivo:** `/app/mobile/preview/[sessionId]/page.tsx:131`

**Erro:**
```typescript
Property 'occurrences' does not exist on type '{ id: any; date: any; ... }'.
```

**Código:**
```typescript
.sort((a, b) => (b.occurrences || 0) - (a.occurrences || 0))
```

**Prioridade:** 🟡 P2 (Médio - sort não quebra mas não funciona)

**Causa Raiz:**
Interface local não define `occurrences`. Possível:
1. Backend não retorna esse campo
2. Campo foi removido
3. Deveria ser calculado no frontend

**Solução (REQUER INVESTIGAÇÃO):**
- **Análise necessária:** Verificar se backend retorna `occurrences`
- **Se retorna:** Adicionar `occurrences?: number` no type local
- **Se não retorna:** Remover sort ou implementar contagem frontend

**Impacto:** Ordenação por quantidade não funciona.

---

## 📋 CHECKLIST DE CORREÇÃO

### ✅ Fase 1 - Correções Simples (P0 - Bloqueantes)
- [ ] **1.1** - Corrigir `leftAction` em 2 páginas de budget (usar `'back'`)
- [ ] **2.1** - Substituir `goal.orcamento` por `goal.valor_alvo` (2 locais)
- [ ] **2.4** - Corrigir acesso a `goal.progresso?.valor_atual` (2 locais)
- [ ] **2.5** - Renomear `isLoading` para `loading` em require-admin
- [ ] **1.2** - Converter Goal IDs para number nos callbacks (4 locais)
- [ ] **2.2** - Investigar + corrigir campo `categoria` (3 locais)

### ✅ Fase 2 - Correções Médias (P1 - Críticas)
- [ ] **1.3** - Usar `GoalWithProgress` ou adicionar campo `status`
- [ ] **2.3** - Substituir `mes_referencia` por `prazo`

### ✅ Fase 3 - Correções Polimento (P2)
- [ ] **1.4** - Simplificar check de `ativo` para `!!goal.ativo`
- [ ] **2.6** - Investigar + corrigir sort por `occurrences`

---

## 🎯 RESUMO EXECUTIVO

### Problemas Principais:
1. **Inconsistência de Types**: Interfaces não refletem dados reais do backend
2. **Campos Renomeados**: `orcamento` → `valor_alvo`, `mes_referencia` → `prazo`
3. **Campos Aninhados**: `valor_atual` está em `progresso.valor_atual`
4. **IDs Misturados**: Goal IDs como number mas callbacks esperam string
5. **Campos Fantasma**: `categoria` e `occurrences` não existem ou não são retornados

### Tempo Estimado de Correção:
- **Fase 1 (P0):** 2-3 horas
- **Fase 2 (P1):** 1 hora
- **Fase 3 (P2):** 30 min
- **TOTAL:** ~4 horas

### Próximos Passos:
1. ✅ Revisar interface `Goal` com dados reais do backend
2. ✅ Corrigir P0 (bloqueantes) primeiro
3. ✅ Testar cada correção isoladamente
4. ✅ Verificar se backend retorna campos esperados
5. ✅ Atualizar types após confirmação

---

**📌 NOTA CRÍTICA:** Antes de corrigir, fazer **auditoria completa** do contrato backend-frontend:
- Chamar `/api/v1/goals/` e ver JSON exato retornado
- Comparar com interface `Goal` TypeScript
- Atualizar interface ANTES de corrigir código
