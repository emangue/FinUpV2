# ✅ CHECKLIST DE CORREÇÃO - ERROS APP_DEV

**Data Início:** 10/02/2026  
**Total de Erros:** 17 (frontend) + 0 (backend sintaxe) = **17 erros**  
**Escopo:** ✅ 100% dos erros serão corrigidos  
**Tempo Estimado Total:** **6.5 - 8.5 horas** (inclui investigações + testes gerais)

---

## 📊 RESUMO EXECUTIVO

### Distribuição por Prioridade:
| Prioridade | Quantidade | % Total | Tempo Est. |
|------------|------------|---------|------------|
| 🔴 P0 (Bloqueante) | 9 | 53% | 3-4h |
| 🟠 P1 (Crítico) | 6 | 35% | 1-2h |
| 🟡 P2 (Médio) | 2 | 12% | 30min |

### Status:
- ⏳ **Mapeamento:** ✅ Completo
- ⏳ **Análise de Causa:** ✅ Completo
- ⏳ **Priorização:** ✅ Completo
- 🔴 **Correções:** ❌ Não iniciado
- 🔴 **Testes:** ❌ Não iniciado

---

## 🔴 FASE 1 - CORREÇÕES P0 (BLOQUEANTES)

### 1.1 ✅ MobileHeader leftAction (2 arquivos)

**Arquivos:**
- [ ] `/app/mobile/budget/[goalId]/page.tsx:75`
- [ ] `/app/mobile/budget/new/page.tsx:118`

**Erro:** Type object não aceito em leftAction (espera string)

**Solução (Opção A - Recomendada):**
```typescript
// ANTES (quebrado):
leftAction={{
  icon: <ArrowLeft className="w-5 h-5" />,
  label: 'Voltar',
  onClick: () => router.back()
}}

// DEPOIS (correto):
leftAction="back"  // ← Componente MobileHeader já lida com isso
```

**Teste:**
1. Abrir `/mobile/budget/[goalId]`
2. Verificar que botão "Voltar" aparece
3. Clicar e verificar que volta para página anterior

**Tempo Estimado:** 10 minutos

---

### 1.2 ✅ Goal.orcamento → Goal.valor_alvo (2 linhas)

**Arquivo:**
- [ ] `/features/goals/components/EditGoalModal.tsx:38`
- [ ] `/features/goals/components/EditGoalModal.tsx:47`

**Erro:** Property 'orcamento' não existe

**Solução:**
```typescript
// ANTES (quebrado):
const [orcamento, setOrcamento] = React.useState(goal.orcamento.toString())
setOrcamento(goal.orcamento.toString())

// DEPOIS (correto):
const [orcamento, setOrcamento] = React.useState(goal.valor_alvo.toString())
setOrcamento(goal.valor_alvo.toString())
```

**Teste:**
1. Abrir modal de edição de meta
2. Verificar que campo "Orçamento" carrega valor correto
3. Editar e salvar
4. Verificar que valor persiste

**Tempo Estimado:** 5 minutos

---

### 1.3 ✅ Goal.valor_atual aninhado (2 linhas)

**Arquivo:**
- [ ] `/features/goals/components/EditGoalModal.tsx:192`
- [ ] `/features/goals/components/EditGoalModal.tsx:207`

**Erro:** Property 'valor_atual' não existe no root

**Solução:**
```typescript
// ANTES (quebrado):
{formatCurrency(goal.valor_atual || 0)}

// DEPOIS (correto):
{formatCurrency(goal.progresso?.valor_atual || 0)}
```

**Teste:**
1. Abrir modal de edição de meta com gastos existentes
2. Verificar que "Valor Atual" mostra número > 0
3. Verificar cálculo de percentual está correto

**Tempo Estimado:** 5 minutos

---

### 1.4 ✅ AuthContext isLoading → loading (1 linha)

**Arquivo:**
- [ ] `/core/components/require-admin.tsx:41`

**Erro:** Property 'isLoading' não existe (correto é 'loading')

**Solução:**
```typescript
// ANTES (quebrado):
const { user, isLoading } = useAuth()

// DEPOIS (correto):
const { user, loading } = useAuth()

// E ajustar uso:
if (loading) return <LoadingSpinner />
```

**Teste:**
1. Fazer logout
2. Tentar acessar rota admin (`/admin`)
3. Verificar que mostra loading → redirect para login
4. Fazer login como admin
5. Verificar acesso permitido

**Tempo Estimado:** 10 minutos

---

### 1.5 ✅ Goal ID Type Mismatch (4 linhas)

**Arquivos:**
- [ ] `/features/goals/components/ManageGoalsListItem.tsx:141`
- [ ] `/features/goals/components/ManageGoalsListItem.tsx:149`
- [ ] `/app/mobile/budget/manage/page.tsx:37`
- [ ] `/app/mobile/budget/manage/page.tsx:59`

**Erro:** number vs string incompatibility

**Solução (Opção A - Mudar callbacks):**

**1. Atualizar props de ManageGoalsListItem:**
```typescript
// ANTES:
interface ManageGoalsListItemProps {
  onToggle: (goalId: string, isActive: boolean) => void
  onEdit: (goalId: string) => void
}

// DEPOIS:
interface ManageGoalsListItemProps {
  onToggle: (goalId: number, isActive: boolean) => void
  onEdit: (goalId: number) => void
}
```

**2. Atualizar chamadas em manage/page.tsx:**
```typescript
// ANTES:
const handleToggle = (goalId: string, isActive: boolean) => {
  const goal = goals.find((g) => g.id === goalId)  // ← Erro aqui
}

// DEPOIS:
const handleToggle = (goalId: number, isActive: boolean) => {
  const goal = goals.find((g) => g.id === goalId)  // ← OK agora
}
```

**Teste:**
1. Ir para `/mobile/budget/manage`
2. Toggle ativo/inativo de uma meta
3. Verificar que estado persiste
4. Clicar em "Editar" meta
5. Verificar que abre modal correto

**Tempo Estimado:** 20 minutos

---

### 1.6 ⚠️ Goal.categoria (3 linhas) - REQUER INVESTIGAÇÃO

**Arquivos:**
- [ ] `/features/goals/components/ManageGoalsListItem.tsx:32`
- [ ] `/app/mobile/budget/manage/page.tsx:97`
- [ ] `/app/mobile/budget/manage/page.tsx:98`

**Erro:** Property 'categoria' não existe

**ANTES DE CORRIGIR:**
1. [ ] Verificar backend `/api/v1/goals/` retorna campo `categoria`
2. [ ] Se SIM: Adicionar em interface Goal
3. [ ] Se NÃO: Implementar lógica alternativa

**Opções de Solução:**

**A) Backend retorna `categoria`:**
```typescript
// Adicionar em /features/goals/types/index.ts
export interface Goal {
  ...
  categoria?: string  // ← Adicionar
}
```

**B) Backend NÃO retorna (calcular no frontend):**
```typescript
// Criar helper function
function getGoalCategoria(goal: Goal): string {
  // Lógica: baseado em vinculações ou nome
  // Ex: se goal.nome.includes('investimento') → 'investimento'
  return 'investimento'  // ou 'gasto'
}

// Usar:
const icon = iconMap[getGoalCategoria(goal)]
const gastosGoals = goals.filter((g) => getGoalCategoria(g) !== 'investimento')
```

**Teste (após decisão):**
1. Listar metas em `/mobile/budget/manage`
2. Verificar que ícones aparecem corretamente
3. Verificar que filtros Gastos/Investimentos funcionam
4. Verificar que metas aparecem na seção correta

**Tempo Estimado:** 1-2 horas (inclui investigação)

---

## 🟠 FASE 2 - CORREÇÕES P1 (CRÍTICAS)

### 2.1 ✅ Goal status não definido

**Arquivo:**
- [ ] `/features/goals/hooks/use-goal-detail.ts:24`

**Erro:** Tentando adicionar `status` em objeto Goal

**Solução (Opção A):**
```typescript
// ANTES:
const [goal, setGoal] = useState<Goal | null>(null)

setGoal({
  ...data,
  status: calculateGoalStatus(data)  // ← Erro
})

// DEPOIS:
const [goal, setGoal] = useState<GoalWithProgress | null>(null)

setGoal({
  ...data,
  status: calculateGoalStatus(data)  // ← OK agora
})
```

**Teste:**
1. Abrir detalhes de uma meta
2. Verificar que badge de status aparece (Ativo/Atrasado/Concluído)
3. Verificar cor do badge está correta

**Tempo Estimado:** 15 minutos

---

### 2.2 ✅ Goal.mes_referencia → prazo

**Arquivo:**
- [ ] `/features/goals/components/EditGoalModal.tsx:136`

**Erro:** Campo não existe (correto é `prazo`)

**Solução:**
```typescript
// ANTES:
<p className="text-xs text-gray-400 text-right">{goal.mes_referencia}</p>

// DEPOIS:
<p className="text-xs text-gray-400 text-right">{goal.prazo}</p>
```

**Teste:**
1. Abrir modal de edição de meta
2. Verificar que data de prazo aparece (formato YYYY-MM)
3. Verificar que está no local correto

**Tempo Estimado:** 5 minutos

---

## 🟡 FASE 3 - CORREÇÕES P2 (MÉDIO)

### 3.1 ✅ Ativo boolean vs number

**Arquivo:**
- [ ] `/app/mobile/budget/manage/page.tsx:26`

**Erro:** Comparação desnecessária (boolean || number)

**Solução:**
```typescript
// ANTES (defensivo mas verboso):
initialStates[goal.id] = goal.ativo === true || goal.ativo === 1

// DEPOIS (simplificado):
initialStates[goal.id] = !!goal.ativo
```

**Teste:**
1. Criar meta ativa
2. Criar meta inativa
3. Ir para `/mobile/budget/manage`
4. Verificar que toggles inicializam corretamente

**Tempo Estimado:** 5 minutos

---

### 3.2 ⚠️ Preview occurrences (2 linhas) - REQUER INVESTIGAÇÃO

**Arquivo:**
- [ ] `/app/mobile/preview/[sessionId]/page.tsx:131`

**Erro:** Property 'occurrences' não existe

**ANTES DE CORRIGIR:**
1. [ ] Verificar backend retorna `occurrences` no preview
2. [ ] Se SIM: Adicionar no type local
3. [ ] Se NÃO: Remover sort ou calcular frontend

**Opções de Solução:**

**A) Backend retorna (adicionar type):**
```typescript
interface PreviewItem {
  ...
  occurrences?: number
}
```

**B) Backend não retorna (remover sort):**
```typescript
// Remover completamente:
.sort((a, b) => (b.occurrences || 0) - (a.occurrences || 0))

// Ou usar outro critério:
.sort((a, b) => a.description.localeCompare(b.description))
```

**Teste:**
1. Fazer upload de arquivo
2. Ir para preview
3. Verificar que grupos aparecem (ordenados ou não)
4. Verificar sem erro de console

**Tempo Estimado:** 30 minutos

---

## 🔍 FASE 4 - VALIDAÇÃO BACKEND

### 4.1 ✅ Auditoria de Schema Goal

**Tarefa:**
- [ ] Chamar `/api/v1/goals/` com autenticação
- [ ] Salvar JSON completo retornado
- [ ] Comparar campo por campo com interface TypeScript
- [ ] Documentar divergências

**Comandos:**
```bash
# 1. Obter token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@financas.com","password":"[SUA_SENHA]"}' \
  | jq '.access_token'

# 2. Chamar goals
curl http://localhost:8000/api/v1/goals/ \
  -H "Authorization: Bearer [TOKEN]" \
  | jq '.' > /tmp/goals_response.json

# 3. Analisar campos
cat /tmp/goals_response.json | jq '.[0] | keys'
```

**Verificar:**
- [ ] Campo `categoria` existe?
- [ ] Campo `ativo` é boolean ou 0/1?
- [ ] Campo `progresso` está aninhado?
- [ ] Todos os campos do Goal interface existem?

**Tempo Estimado:** 30 minutos

---

### 4.2 ✅ Normalização de Boolean no Backend

**Se `ativo` retorna 0/1 em vez de boolean:**

**Arquivo:** `/app/domains/goals/schemas.py`

```python
from pydantic import BaseModel, validator

class GoalResponse(BaseModel):
    ativo: bool
    
    @validator('ativo', pre=True)
    def normalize_bool(cls, v):
        """Garante que SQLite 0/1 vira bool"""
        return bool(v)
```

**Teste:**
```bash
# Após mudança:
curl http://localhost:8000/api/v1/goals/ \
  -H "Authorization: Bearer [TOKEN]" \
  | jq '.[0].ativo'

# Deve retornar: true ou false (não 0 ou 1)
```

**Tempo Estimado:** 15 minutos

---

## 📋 ORDEM DE EXECUÇÃO ATUALIZADA (100% DOS ERROS)

### 🔍 FASE 0 - INVESTIGAÇÃO OBRIGATÓRIA (1-2h)
**⚠️ EXECUTAR ANTES DE QUALQUER CORREÇÃO**

#### 0.1 - Auditoria Backend Goal Schema
- [ ] Iniciar backend: `./scripts/deploy/quick_start.sh`
- [ ] Obter token JWT:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@financas.com","password":"[SENHA]"}' \
  | jq -r '.access_token' > /tmp/token.txt
```
- [ ] Buscar goals reais:
```bash
TOKEN=$(cat /tmp/token.txt)
curl http://localhost:8000/api/v1/goals/ \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.' > /tmp/goals_response.json
```
- [ ] Analisar campos retornados:
```bash
cat /tmp/goals_response.json | jq '.[0] | keys'
```
- [ ] **DECISÃO 1:** Campo `categoria` existe?
  - ✅ SIM → Adicionar em `Goal` interface TypeScript
  - ❌ NÃO → Criar função `getGoalCategoria()` frontend
- [ ] **DECISÃO 2:** Campo `ativo` é boolean ou 0/1?
  - Se 0/1 → Adicionar validator no backend
- [ ] Documentar decisões em `/tmp/investigacao_goals.md`

**Tempo:** 30-45 min

---

#### 0.2 - Investigar Preview Occurrences
- [ ] Verificar response de `/api/v1/upload/preview/{sessionId}`:
```bash
TOKEN=$(cat /tmp/token.txt)
# Fazer upload de arquivo primeiro para obter sessionId
curl http://localhost:8000/api/v1/upload/preview/[SESSION_ID] \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.[0] | keys' | grep occurrences
```
- [ ] **DECISÃO:** Campo `occurrences` existe?
  - ✅ SIM → Adicionar no type local PreviewItem
  - ❌ NÃO → Remover sort ou usar outro campo
- [ ] Documentar decisão

**Tempo:** 15-30 min

**✅ Checkpoint:** Após esta fase, você saberá EXATAMENTE o que corrigir.

---

### 🚀 FASE 1 - Quick Wins (1h)
**Correções simples sem investigação**

- [ ] **1.1** - MobileHeader leftAction (10min) - 2 arquivos
- [ ] **1.2** - Goal.orcamento → valor_alvo (5min) - 2 linhas
- [ ] **1.3** - Goal.valor_atual aninhado (5min) - 2 linhas
- [ ] **1.4** - AuthContext loading (10min) - 1 linha
- [ ] **2.2** - Goal.mes_referencia → prazo (5min) - 1 linha
- [ ] **3.1** - Simplificar check ativo (5min) - 1 linha

**Subtotal:** ~40 min de correção + 20 min testes = **1h**

---

### ⚙️ FASE 2 - Correções Médias (1h)
**Correções que requerem mudanças de interface**

- [ ] **1.5** - Goal ID type mismatch (30min)
  - Mudar interfaces + callbacks em 4 locais
  - Testar toggle e edição
- [ ] **2.1** - Goal status (15min)
  - Usar `GoalWithProgress` type
  - Testar badge de status

**Subtotal:** ~45 min de correção + 15 min testes = **1h**

---

### 🔬 FASE 3 - Correções Baseadas em Investigação (1-2h)
**Aplicar decisões da Fase 0**

- [ ] **1.6** - Goal.categoria (30min-1h)
  - Aplicar solução decidida na Fase 0
  - Testar ícones e filtros
- [ ] **3.2** - Preview occurrences (15-30min)
  - Aplicar solução decidida na Fase 0
  - Testar preview upload
- [ ] **4.2** - Backend normalization (se necessário) (15min)
  - Adicionar validator para `ativo` boolean
  - Testar que retorna true/false

**Subtotal:** ~1-2h

---

### ✅ FASE 4 - TESTES GERAIS DO APP (2-3h)
**⚠️ OBRIGATÓRIO: Testar TODAS as telas e funcionalidades**

#### 4.1 - Testes de Autenticação (15min)
- [ ] Login com admin@financas.com
- [ ] Login com teste@email.com
- [ ] Logout
- [ ] Refresh da página (token persiste?)
- [ ] Acesso a rota protegida sem login (redirect?)
- [ ] Acesso admin sem ser admin (bloqueado?)

#### 4.2 - Testes de Dashboard (20min)
- [ ] Dashboard carrega sem erros
- [ ] Métricas aparecem (receitas, despesas, saldo)
- [ ] Gráficos renderizam
- [ ] Filtros de mês/ano funcionam
- [ ] Toggle Mês/YTD funciona
- [ ] Donut charts aparecem

#### 4.3 - Testes de Metas (Budget) (45min)
- [ ] **Listar Metas** (`/mobile/budget`)
  - [ ] Metas aparecem
  - [ ] Ícones corretos (após fix categoria)
  - [ ] Valores corretos
  - [ ] Progresso visível
- [ ] **Criar Meta** (`/mobile/budget/new`)
  - [ ] Formulário abre
  - [ ] Botão voltar funciona (após fix leftAction)
  - [ ] Campos validam
  - [ ] Salvar persiste
- [ ] **Editar Meta** (`/mobile/budget/[goalId]`)
  - [ ] Modal abre (após fix orcamento)
  - [ ] Valores carregam corretos
  - [ ] Valor atual aparece (após fix aninhado)
  - [ ] Prazo aparece (após fix mes_referencia)
  - [ ] Salvar atualiza
- [ ] **Gerenciar Metas** (`/mobile/budget/manage`)
  - [ ] Lista carrega
  - [ ] Filtros Gastos/Investimentos funcionam (após fix categoria)
  - [ ] Toggle ativo/inativo funciona (após fix ID mismatch)
  - [ ] Botão editar abre meta correta (após fix ID)
- [ ] **Vincular Orçamentos**
  - [ ] Lista de vinculações aparece
  - [ ] Toggle vinculação funciona
  - [ ] Progresso recalcula

#### 4.4 - Testes de Upload (30min)
- [ ] **Upload** (`/mobile/upload`)
  - [ ] Dialog abre
  - [ ] Selecionar arquivo funciona
  - [ ] Upload processa
  - [ ] Redirect para preview
- [ ] **Preview** (`/mobile/preview/[sessionId]`)
  - [ ] Transações aparecem (após fix occurrences)
  - [ ] Grupos/subgrupos carregam
  - [ ] Botão adicionar grupo funciona
  - [ ] Marcar transação funciona
  - [ ] Confirmar funciona
- [ ] **Histórico**
  - [ ] Lista de uploads aparece
  - [ ] Status corretos

#### 4.5 - Testes de Transações (20min)
- [ ] **Lista** (`/mobile/transactions`)
  - [ ] Transações carregam
  - [ ] Filtros funcionam
  - [ ] Paginação funciona
- [ ] **Editar Transação**
  - [ ] Modal abre
  - [ ] Campos carregam
  - [ ] Salvar atualiza
- [ ] **Excluir Transação**
  - [ ] Confirmação aparece
  - [ ] Exclusão funciona

#### 4.6 - Testes de Navegação (15min)
- [ ] Todos os botões "Voltar" funcionam (após fix leftAction)
- [ ] Menu lateral abre/fecha
- [ ] Links do menu funcionam
- [ ] Navegação entre telas fluida
- [ ] Nenhum erro 404

#### 4.7 - Testes de Perfil/Settings (10min)
- [ ] Perfil carrega (`/mobile/profile`)
  - [ ] Dados do usuário aparecem
  - [ ] Loading state funciona (após fix isLoading)
- [ ] Configurações funcionam

#### 4.8 - Testes de Console/Logs (15min)
- [ ] Abrir DevTools Console
- [ ] Navegar por todas as telas principais
- [ ] **Verificar:**
  - [ ] ❌ ZERO erros vermelhos
  - [ ] ⚠️ Warnings aceitáveis apenas
  - [ ] ✅ Logs de debug ok (serão limpos na Frente 2)

#### 4.9 - Testes de Build (10min)
- [ ] Frontend build sem erros:
```bash
cd app_dev/frontend
npm run build
```
- [ ] Backend inicia sem erros:
```bash
./scripts/deploy/quick_start.sh
tail -30 temp/logs/backend.log
```

**Subtotal Testes:** ~2h 30min

---

### 📊 TEMPO TOTAL ATUALIZADO

- **Fase 0 (Investigação):** 1-2h
- **Fase 1 (Quick Wins):** 1h
- **Fase 2 (Médias):** 1h  
- **Fase 3 (Com Investigação):** 1-2h
- **Fase 4 (Testes Gerais):** 2.5h
- **TOTAL:** **6.5 - 8.5 horas**

---

## ✅ CHECKLIST FINAL DE ACEITAÇÃO

### ✅ Critérios Obrigatórios para Marcar Frente 1 como Completa:

#### Erros Corrigidos:
- [ ] ✅ 17/17 erros TypeScript resolvidos (100%)
- [ ] ✅ 0 erros de build
- [ ] ✅ 0 warnings críticos

#### Testes de Build:
- [ ] ✅ Frontend: `npm run build` sem erros
- [ ] ✅ Backend: inicia sem erros
- [ ] ✅ Nenhum erro de importação

#### Testes Funcionais (Fase 4 completa):
- [ ] ✅ Autenticação funcionando (login/logout/refresh)
- [ ] ✅ Dashboard carrega e exibe dados
- [ ] ✅ Metas: criar/editar/listar/gerenciar/vincular
- [ ] ✅ Upload: upload/preview/confirmar
- [ ] ✅ Transações: listar/editar/excluir
- [ ] ✅ Navegação: todos os botões "Voltar" funcionam
- [ ] ✅ Perfil e Settings acessíveis

#### Testes de Console:
- [ ] ✅ ZERO erros vermelhos no console
- [ ] ✅ Warnings aceitáveis apenas (logs a limpar na Frente 2)
- [ ] ✅ Backend logs sem errors críticos

#### Documentação:
- [ ] ✅ RELATORIO_FINAL.md criado
- [ ] ✅ Lições aprendidas documentadas
- [ ] ✅ README.md atualizado com status ✅ Completo

---

## 🎯 MÉTRICAS DE SUCESSO

| Métrica | Antes | Depois (Meta) |
|---------|-------|---------------|
| Erros TypeScript | 17 | 0 |
| Build Warnings | ? | 0 |
| Console Errors (runtime) | ? | 0 |
| Features Quebradas | 6+ | 0 |
| Tempo Total Gasto | 0h | 7h |

---

## 📝 NOTAS FINAIS

### Riscos Identificados:
1. ⚠️ Campo `categoria` pode requerer mudança backend (maior impacto)
2. ⚠️ Campo `occurrences` pode não existir (decisão: remover sort?)
3. ⚠️ Outros erros podem surgir após correções (efeito cascata)

### Dependências Externas:
- ✅ Backend rodando em localhost:8000
- ✅ Banco de dados com metas de teste
- ✅ Usuário admin@financas.com ativo

### Próximos Passos Após Correções:
1. ✅ Documentar mudanças em CHANGELOG
2. ✅ Atualizar tipos TypeScript em repo
3. ✅ Commitar com mensagem detalhada
4. ✅ Criar PR para review
5. ✅ Testar em ambiente de staging
6. ✅ Marcar Frente 1 como ✅ Completa
7. ✅ Avançar para Frente 6 (Segurança)

---

**Status Final:** 📋 Checklist pronto para execução
