# Sprint 6 — Full-stack: Goals, Budget, Dev Skills e Cursor Pagination

> **Escopo:** Backend + Frontend + arquivos de skill.
> **Itens:** B1 · B3 · D · C1
> **Pré-requisito:** Sprint 5 (A1 — `invalidate_cashflow_cache` usado em B3)
> **Nota:** D (dev skills) é completamente independente — pode ser feito a qualquer momento.

---

## Índice

- [B1 — Optimistic updates em Goals](#b1--optimistic-updates-em-goals)
- [B3 — Batch range update goals](#b3--batch-range-update-goals)
- [D — Skills de desenvolvimento](#d--skills-de-desenvolvimento)
- [C1 — Cursor pagination em transações](#c1--cursor-pagination-em-transações)

---

## B1 — Optimistic updates em Goals

**Problema:** Toda mutação (criar, editar, excluir) dispara um full refetch. O usuário espera 300–500ms por ação.
**Impacto:** Ações de CRUD em goals se tornam instantâneas (UI atualiza antes da resposta do servidor).
**Escopo:** Frontend only — `src/features/goals/hooks/use-goals.ts`.

---

### Microação 1 — Criar helper de goal optimista

**Arquivo:** `app_dev/frontend/src/features/goals/hooks/use-goals.ts`

```typescript
function makeOptimisticGoal(data: CreateGoalInput): Goal {
  return {
    id: `temp-${Date.now()}`,    // id temporário, substituído após resposta do servidor
    ...data,
    ativo: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    _optimistic: true,           // flag para UI mostrar estado pendente se necessário
  }
}
```

---

### Microação 2 — Implementar `createGoal` com optimistic update

```typescript
// Antes
async function createGoal(data: CreateGoalInput) {
  await api.post('/budget/planning/bulk-upsert', [data])
  await loadGoals()  // full refetch
}

// Depois
async function createGoal(data: CreateGoalInput) {
  const optimistic = makeOptimisticGoal(data)
  setGoals(prev => [...prev, optimistic])   // UI atualiza imediatamente

  try {
    const [saved] = await api.post<Goal[]>('/budget/planning/bulk-upsert', [data])
    // Substitui o item optimista pelo item real do servidor
    setGoals(prev => prev.map(g => g.id === optimistic.id ? saved : g))
  } catch (err) {
    // Rollback: remove o item optimista
    setGoals(prev => prev.filter(g => g.id !== optimistic.id))
    throw err
  }
}
```

---

### Microação 3 — Implementar `updateGoal` com optimistic update

```typescript
// Antes
async function updateGoal(id: string, data: Partial<Goal>) {
  await api.patch(`/budget/planning/toggle/${id}`, data)
  await loadGoals()
}

// Depois
async function updateGoal(id: string, data: Partial<Goal>) {
  const previousGoals = goals   // snapshot para rollback

  setGoals(prev => prev.map(g => g.id === id ? { ...g, ...data } : g))

  try {
    const updated = await api.patch<Goal>(`/budget/planning/toggle/${id}`, data)
    setGoals(prev => prev.map(g => g.id === id ? updated : g))
  } catch (err) {
    setGoals(previousGoals)
    throw err
  }
}
```

---

### Microação 4 — Implementar `deleteGoal` com optimistic update

```typescript
// Antes
async function deleteGoal(id: string) {
  await api.delete(`/budget/${id}`)
  await loadGoals()
}

// Depois
async function deleteGoal(id: string) {
  const previousGoals = goals

  setGoals(prev => prev.filter(g => g.id !== id))

  try {
    await api.delete(`/budget/${id}`)
    // Sucesso — UI já está correta
  } catch (err) {
    setGoals(previousGoals)
    throw err
  }
}
```

---

### Checklist B1

- [ ] Criar meta: aparece na lista imediatamente, sem loading
- [ ] Editar meta: valor atualiza na UI antes da resposta do servidor
- [ ] Excluir meta: some da lista imediatamente
- [ ] Em caso de erro do servidor: UI volta ao estado anterior (rollback)
- [ ] Nenhum `loadGoals()` (full refetch) chamado em fluxos normais de CRUD

---

## B3 — Batch range update goals

**Problema:** `aplicarAteFinAno=true` faz 1 chamada por mês restante (até 12 chamadas em paralelo).
**Impacto:** 12 requests → 1 request, executado em 1 transação no banco.
**Escopo:** Backend (novo endpoint) + Frontend (`goals-api.ts`).
**Pré-requisito:** Sprint 5 (A1 — `invalidate_cashflow_cache` para invalidar os meses afetados).

---

### Microação 1 — Criar endpoint `PUT /budget/planning/bulk-range`

**Arquivo:** `app_dev/backend/app/domains/budget/router.py`

```python
from pydantic import BaseModel

class BulkRangeInput(BaseModel):
    goal_categoria: str
    goal_grupo: str
    valor: float
    mes_inicio: str    # 'YYYY-MM'
    mes_fim: str       # 'YYYY-MM'

@router.put("/planning/bulk-range")
def bulk_range_update(
    data: BulkRangeInput,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Aplica o mesmo valor para todos os meses entre mes_inicio e mes_fim.
    Executa em 1 transação no backend.
    """
    from dateutil.relativedelta import relativedelta
    from datetime import datetime

    inicio = datetime.strptime(data.mes_inicio, "%Y-%m")
    fim = datetime.strptime(data.mes_fim, "%Y-%m")

    meses = []
    current = inicio
    while current <= fim:
        meses.append(current.strftime("%Y-%m"))
        current += relativedelta(months=1)

    # Upsert em batch dentro de 1 transação
    service.bulk_upsert_goals(
        db, user_id,
        categoria=data.goal_categoria,
        grupo=data.goal_grupo,
        valor=data.valor,
        meses=meses,
    )

    # Invalida cache de cashflow para os meses afetados
    from app.domains.plano.service import invalidate_cashflow_cache
    invalidate_cashflow_cache(db, user_id, mes_referencia=meses)

    return {"updated": len(meses), "meses": meses}
```

---

### Microação 2 — Criar `bulk_upsert_goals` no service de budget

**Arquivo:** `app_dev/backend/app/domains/budget/service.py`

```python
def bulk_upsert_goals(
    db: Session,
    user_id: int,
    categoria: str,
    grupo: str,
    valor: float,
    meses: list[str],
):
    """Upsert de budget_planning para múltiplos meses em 1 transação."""
    for mes_ref in meses:
        existing = db.query(BudgetPlanning).filter_by(
            user_id=user_id,
            categoria=categoria,
            grupo=grupo,
            mes_referencia=mes_ref,
        ).first()

        if existing:
            existing.valor = valor
        else:
            db.add(BudgetPlanning(
                user_id=user_id,
                categoria=categoria,
                grupo=grupo,
                valor=valor,
                mes_referencia=mes_ref,
            ))
    db.commit()
```

---

### Microação 3 — Substituir loop de chamadas no frontend

**Arquivo:** `app_dev/frontend/src/features/goals/services/goals-api.ts`

```typescript
// Antes — 1 chamada por mês
async function updateGoalValor(goalId: string, valor: number, aplicarAteFinAno: boolean) {
  if (aplicarAteFinAno) {
    const mesesRestantes = getMesesRestantesDoAno()
    await Promise.all(
      mesesRestantes.map(mes => api.patch(`/budget/planning/${goalId}`, { valor, mes }))
    )
  } else {
    await api.patch(`/budget/planning/${goalId}`, { valor })
  }
}

// Depois — 1 chamada para o range inteiro
async function updateGoalValor(
  goalCategoria: string,
  goalGrupo: string,
  valor: number,
  mesInicio: string,
  aplicarAteFinAno: boolean,
) {
  if (aplicarAteFinAno) {
    const anoAtual = new Date().getFullYear()
    await api.put('/budget/planning/bulk-range', {
      goal_categoria: goalCategoria,
      goal_grupo: goalGrupo,
      valor,
      mes_inicio: mesInicio,
      mes_fim: `${anoAtual}-12`,
    })
  } else {
    await api.patch('/budget/planning/bulk-upsert', [{
      categoria: goalCategoria,
      grupo: goalGrupo,
      valor,
      mes_referencia: mesInicio,
    }])
  }
}
```

---

### Checklist B3

- [ ] `PUT /budget/planning/bulk-range` executa em 1 transação no banco
- [ ] Frontend faz 1 request (era até 12)
- [ ] Cache de cashflow invalidado para os meses afetados
- [ ] Resposta inclui `{ updated: N, meses: [...] }` para debug

---

## D — Skills de desenvolvimento

**Problema:** Processos recorrentes (deploy, migration, nova feature) são realizados manualmente sem guia padronizado.
**Escopo:** Criar arquivos em `.claude/commands/`.
**Pré-requisito:** Nenhum.

---

### Microação 1 — Criar `/deploy`

**Arquivo:** `.claude/commands/deploy.md`

```markdown
# Skill: Deploy

## Contexto do projeto
- Host SSH: `minha-vps-hostinger`
- Path na VM: `/var/www/finup`
- Compose prod: `docker-compose.prod.yml`
- Containers: `finup_backend_prod` (:8000), `finup_frontend_app_prod` (:3003), `finup_frontend_admin_prod` (:3001)
- Scripts: `scripts/deploy/deploy_docker_build_local.sh` e `scripts/deploy/deploy_docker_vm.sh`

## Antes de executar, verifique
1. `git status -uno` → sem mudanças não commitadas
2. Branch atual está correta para o deploy
3. `ssh minha-vps-hostinger echo ok` → SSH acessível

## Passos

### 1. Push
```bash
git push origin $(git branch --show-current)
```

### 2. Escolha o script
- VM com memória suficiente (> 1GB livre): usar `deploy_docker_vm.sh` (build na VM)
- VM com risco de OOM: usar `deploy_docker_build_local.sh` (build local + SCP)

### 3. Execute
```bash
# Opção A — build na VM
bash scripts/deploy/deploy_docker_vm.sh

# Opção B — build local
bash scripts/deploy/deploy_docker_build_local.sh
```

### 4. Migrations (se houver)
```bash
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic upgrade head"
```

### 5. Validar
```bash
ssh minha-vps-hostinger "curl -s http://localhost:8000/health"
```

## Regras
- NUNCA editar arquivos diretamente na VM
- Em caso de falha: `ssh minha-vps-hostinger "cd /var/www/finup && docker compose -f docker-compose.prod.yml rollback"`
```

---

### Microação 2 — Criar `/migration`

**Arquivo:** `.claude/commands/migration.md`

```markdown
# Skill: Migration Alembic

## Contexto
- Container dev: `finup_backend_dev`
- Migrations: `app_dev/backend/migrations/versions/`
- Guard: `migrations/env.py` bloqueia SQLite (PostgreSQL only)

## Antes de executar, confirme
1. Descrição da mudança (ex: "Add plano_cashflow_mes table")
2. `models.py` do domínio já foi atualizado?

## Passos

### 1. Gerar migration
```bash
docker exec finup_backend_dev alembic revision --autogenerate -m "Descrição da mudança"
```

### 2. Revisar o arquivo gerado
- `upgrade()` contém a mudança esperada
- `downgrade()` reverte corretamente
- Campos NOT NULL sem default em tabelas com dados existentes têm `server_default`

### 3. Testar em dev
```bash
docker exec finup_backend_dev alembic upgrade head
docker exec finup_backend_dev alembic downgrade -1
docker exec finup_backend_dev alembic upgrade head
```

## Armadilhas
- Campo NOT NULL sem server_default em tabela com dados = falha em prod
- Nunca commitar migrations sem testar upgrade + downgrade
```

---

### Microação 3 — Criar `/new-api-domain`

**Arquivo:** `.claude/commands/new-api-domain.md`

```markdown
# Skill: Novo Domínio FastAPI

## Estrutura a criar
```
app/domains/{nome}/
├── __init__.py
├── models.py
├── schemas.py
├── repository.py
├── service.py
└── router.py
```

## Regras obrigatórias
- `user_id = Column(Integer, ForeignKey("users.id"), nullable=False)` em todo model
- Todo repository filtra por `user_id` em todo WHERE
- Todo endpoint usa `Depends(get_current_user_id)`
- Registrar em `app/main.py`: `app.include_router({nome}_router, prefix="/api/v1")`

## Após criar
```bash
docker exec finup_backend_dev alembic revision --autogenerate -m "Add {nome} table"
docker exec finup_backend_dev alembic upgrade head
```
```

---

### Microação 4 — Criar `/new-feature`

**Arquivo:** `.claude/commands/new-feature.md`

```markdown
# Skill: Nova Feature Frontend

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
- URLs nunca hardcoded: sempre via `ENDPOINTS` de `src/config/api.config.ts`
- Sempre `fetchWithAuth` (nunca `fetch()` direto)
- Cache in-memory com TTL se dados são lidos com frequência (usar `in-memory-cache.ts`)
- Mobile: `src/app/mobile/{nome}/page.tsx` | Desktop: `src/app/{nome}/page.tsx`
```

---

### Microação 5 — Criar `/new-processor`

**Arquivo:** `.claude/commands/new-processor.md`

```markdown
# Skill: Novo Processador Raw

## Contexto
Processadores em `app_dev/backend/app/domains/upload/processors/raw/{formato}/`

## Assinatura obrigatória
```python
def process_{banco}_{tipo}(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str = None,
    final_cartao: str = None,
) -> Tuple[List[RawTransaction], BalanceValidation]:
```

## Campos obrigatórios do RawTransaction
`banco`, `tipo_documento`, `nome_arquivo`, `data_criacao`, `data` (DD/MM/YYYY),
`lancamento`, `valor` (float, negativo=débito), `nome_cartao`, `final_cartao`, `mes_fatura` (AAAAMM)

## Após criar
1. Registrar em `registry.py`
2. Testar: `balance_validation.is_valid == True`
```

---

### Microação 6 — Criar `/branch`

**Arquivo:** `.claude/commands/branch.md`

```markdown
# Skill: Criação de Branch

## Workflow de fases
```
Phase 1: PRD     → docs/features/{nome}/01-PRD/PRD.md
Phase 2: TECH    → docs/features/{nome}/02-TECH_SPEC/TECH_SPEC.md
Phase 3: SPRINT  → docs/features/{nome}/03-SPRINT/SPRINTX_COMPLETE.md
Phase 4: DEPLOY  → docs/features/{nome}/04-DEPLOY/DEPLOY_CHECKLIST.md
Phase 5: POST    → docs/features/{nome}/05-POST/POST_MORTEM.md
```

## Passos
```bash
git checkout -b {tipo}/{nome}
mkdir -p docs/features/{nome}
```

## Regra crítica
NUNCA editar arquivos diretamente na VM. Todo código vai via git push + deploy.
```

---

### Checklist D

- [ ] `.claude/commands/deploy.md` criado
- [ ] `.claude/commands/migration.md` criado
- [ ] `.claude/commands/new-api-domain.md` criado
- [ ] `.claude/commands/new-feature.md` criado
- [ ] `.claude/commands/new-processor.md` criado
- [ ] `.claude/commands/branch.md` criado
- [ ] Testar: `/deploy` abre o arquivo de skill

---

## C1 — Cursor pagination em transações

**Problema:** Paginação offset degrada linearmente com o volume de dados (OFFSET 1000 = lê 1000 + retorna 10).
**Impacto:** Usuários com muitas transações terão paginação mais rápida.
**Escopo:** Backend (novo parâmetro `cursor`) + Frontend (atualizar lógica de paginação).
**Nota:** Mantém backward-compat com a paginação offset existente.

---

### Microação 1 — Adicionar suporte a cursor no router

**Arquivo:** `app_dev/backend/app/domains/transactions/router.py`

```python
@router.get("/list")
def list_transactions(
    # Paginação atual (manter para compatibilidade)
    page: int = 1,
    limit: int = 10,
    # Cursor-based (novo — se informado, tem prioridade)
    cursor: Optional[str] = None,   # id da última transação vista
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    # ... filtros existentes permanecem inalterados
):
    if cursor:
        items = service.get_transactions_after_cursor(db, user_id, cursor, limit)
    else:
        items = service.get_transactions_paged(db, user_id, page, limit)

    next_cursor = str(items[-1].id) if len(items) == limit else None

    return {
        "items": items,
        "next_cursor": next_cursor,
        "has_more": next_cursor is not None,
    }
```

---

### Microação 2 — Criar `get_transactions_after_cursor` no service

**Arquivo:** `app_dev/backend/app/domains/transactions/service.py`

```python
def get_transactions_after_cursor(
    db: Session,
    user_id: int,
    cursor: str,    # id da última transação vista
    limit: int,
) -> list[Transaction]:
    return (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.id < int(cursor),   # id decrescente = mais recente primeiro
        )
        .order_by(Transaction.id.desc())
        .limit(limit)
        .all()
    )
```

---

### Microação 3 — Atualizar o frontend para usar cursor

**Arquivo:** `app_dev/frontend/src/features/transactions/hooks/use-transactions.ts` (ou equivalente)

```typescript
// Estado de paginação
const [cursor, setCursor] = useState<string | null>(null)
const [hasMore, setHasMore] = useState(true)
const [items, setItems] = useState<Transaction[]>([])

async function loadMore() {
  const params = new URLSearchParams({ limit: '20' })
  if (cursor) params.set('cursor', cursor)

  const response = await fetchWithAuth(`${ENDPOINTS.TRANSACTIONS_LIST}?${params}`)
  const { items: newItems, next_cursor, has_more } = await response.json()

  setItems(prev => cursor ? [...prev, ...newItems] : newItems)
  setCursor(next_cursor)
  setHasMore(has_more)
}

// Ao mudar filtros: resetar cursor
useEffect(() => {
  setCursor(null)
  setItems([])
  loadMore()
}, [filtros])
```

---

### Checklist C1

- [ ] `GET /transactions/list?cursor=123` retorna transações com `id < 123`
- [ ] `GET /transactions/list?page=1` continua funcionando (backward-compat)
- [ ] `next_cursor` é null quando não há mais páginas
- [ ] Frontend reseta cursor ao mudar filtros (não concatena dados de filtros diferentes)
- [ ] Índice em `Transaction.id` existe no banco (verificar)

---

## Resumo do Sprint 6

| Item | Scope | Dep. | Risco |
|------|-------|------|-------|
| B1 — Optimistic updates | Frontend | — | Médio (rollback em caso de erro) |
| B3 — Batch range goals | Backend + Frontend | Sprint 5 (A1) | Médio (nova transação no banco) |
| D — Dev skills | `.claude/commands/` | — | Nenhum |
| C1 — Cursor pagination | Backend + Frontend | — | Baixo (backward-compat) |

**Ordem sugerida:** D (qualquer momento) → B1 → C1 → B3 (após Sprint 5)
