# Cursor Rules — Conteúdo Completo

Cada seção abaixo é o conteúdo exato de um arquivo `.mdc` a criar em `.cursor/rules/`.
Formato: frontmatter com `globs` de escopo + regras concisas com exemplos DO/DON'T.

---

## `security-backend.mdc`

```
---
description: Padrões de segurança obrigatórios para código Python/FastAPI do FinUp
globs: app_dev/backend/**/*.py
alwaysApply: false
---

# Segurança Backend — FinUp

## Autenticação e autorização

SEMPRE usar `Depends(get_current_user_id)` em endpoints protegidos:
```python
# ✅
@router.get("/items")
def list_items(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):

# ❌
@router.get("/items")
def list_items(db: Session = Depends(get_db)):
```

## Isolamento de dados por usuário

SEMPRE filtrar por `user_id` no banco. NUNCA filtrar em Python depois do `.all()`:
```python
# ✅
db.query(Model).filter(Model.user_id == user_id, Model.ativo == True).all()

# ❌ — carrega dados de todos os usuários
all_items = db.query(Model).all()
return [i for i in all_items if i.user_id == user_id]
```

## Queries SQL

NUNCA concatenar strings em `text()`:
```python
# ✅
db.execute(text("SELECT * FROM t WHERE user_id = :uid"), {"uid": user_id})

# ❌ — SQL injection
db.execute(text(f"SELECT * FROM t WHERE user_id = {user_id}"))
```

Preferir ORM sempre que possível. Usar `text()` só para window functions ou CTEs complexas.

## Upload de arquivos

SEMPRE validar extensão, MIME type e tamanho ANTES de ler o conteúdo:
```python
# ✅
_validar_arquivo(file)
file_bytes = await file.read()
if len(file_bytes) > MAX_UPLOAD_BYTES:
    raise HTTPException(413, "Arquivo muito grande")

# ❌
file_bytes = await file.read()  # DoS: aceita qualquer tamanho
```

Extensões permitidas: csv, xls, xlsx, pdf, ofx, txt
Tamanho máximo: 50MB

## Respostas de erro

NUNCA expor stack traces ou detalhes de infraestrutura em respostas HTTP:
```python
# ✅
raise HTTPException(500, "Erro interno")

# ❌
raise HTTPException(500, str(e))  # expõe path, query, etc.
```

## Logs

NUNCA logar senhas, tokens ou valores financeiros:
```python
# ✅
logger.info("login_ok user_id=%s", user_id)

# ❌
logger.info("login user=%s senha=%s", email, senha)
```

## Rate limiting

Endpoints de auth DEVEM ter `@limiter.limit("3/minute")` ou mais restritivo.
```

---

## `security-frontend.mdc`

```
---
description: Padrões de segurança obrigatórios para código TypeScript/React do FinUp
globs: app_dev/frontend/**/*.{ts,tsx}
alwaysApply: false
---

# Segurança Frontend — FinUp

## Autenticação

NUNCA armazenar token JWT em localStorage. O backend seta cookie httpOnly automaticamente:
```typescript
// ✅ — cookie httpOnly enviado automaticamente pelo browser
const response = await fetch('/api/v1/auth/me', { credentials: 'include' })

// ❌ — roubável por qualquer XSS
localStorage.setItem('authToken', token)
const token = localStorage.getItem('authToken')
```

## dangerouslySetInnerHTML

SEMPRE validar valores antes de usar em style tags ou innerHTML:
```typescript
// ✅
const isValidColor = (c: string) =>
  /^#[0-9A-Fa-f]{3,8}$/.test(c) ||
  /^(rgb|hsl)a?\([\d\s,%.]+\)$/.test(c) ||
  /^var\(--[\w-]+\)$/.test(c)
const safeColor = isValidColor(color) ? color : 'transparent'

// ❌
<style dangerouslySetInnerHTML={{ __html: `--color: ${color}` }} />
```

## Console e dados financeiros

NUNCA logar valores financeiros no console (visível para qualquer pessoa com DevTools):
```typescript
// ✅ — apenas metadata, nunca valores
console.log('useExpenseSources: ok', { count: sources.length })

// ❌ — expõe dados do usuário
console.log('total:', total_despesas)
console.log('response:', apiData)
```

Em produção, `removeConsole` no `next.config.ts` elimina todos os `console.log`.
Mas a regra de ouro é: nunca logar o valor, só a contagem ou o status.

## Variáveis de ambiente

NUNCA expor secrets em `NEXT_PUBLIC_*`. Essas variáveis ficam no bundle do browser:
```typescript
// ✅ — ok, é uma URL pública
NEXT_PUBLIC_API_URL=http://api.meufinup.com.br

// ❌ — qualquer pessoa vê no bundle
NEXT_PUBLIC_JWT_SECRET=...
NEXT_PUBLIC_DB_PASSWORD=...
```
```

---

## `perf-backend.mdc`

```
---
description: Padrões de performance para queries e serviços Python/FastAPI do FinUp
globs: app_dev/backend/**/*.py
alwaysApply: false
---

# Performance Backend — FinUp

## N+1: nunca fazer query dentro de loop

```python
# ✅ — 1 query, O(1) lookup no dict
items = db.query(Item).filter(Item.user_id == user_id, Item.ano == ano).all()
items_por_mes = {i.mes: i for i in items}
for mes in meses:
    item = items_por_mes.get(mes)

# ❌ — N queries para N meses
for mes in meses:
    item = db.query(Item).filter(Item.mes == mes).first()
```

## Filtros no banco, não em Python

```python
# ✅
db.query(JournalEntry).filter(
    JournalEntry.user_id == user_id,
    JournalEntry.GRUPO == grupo,
    JournalEntry.DATA >= data_inicio
).all()

# ❌ — carrega tudo e filtra em memória
entries = db.query(JournalEntry).all()
return [e for e in entries if e.user_id == user_id and e.GRUPO == grupo]
```

## Paginação obrigatória em listagens

```python
# ✅
db.query(Model).filter(...).limit(limit).offset(offset).all()

# ❌ — sem limite, pode retornar milhares de registros
db.query(Model).filter(...).all()
```

## SELECT específico em vez de SELECT *

```python
# ✅ — só os campos necessários
db.query(JournalEntry.id, JournalEntry.VALOR, JournalEntry.DATA).filter(...).all()

# ❌ — carrega todos os campos incluindo blobs e campos não usados
db.query(JournalEntry).filter(...).all()
```

## Dados de múltiplos meses

Pré-buscar tudo em 1-2 queries, nunca uma query por mês:
```python
# ✅
rows = db.query(Model).filter(
    Model.user_id == user_id,
    Model.ano == ano
).all()
por_mes = defaultdict(list)
for r in rows:
    por_mes[r.mes].append(r)

# ❌ — 12 queries para um ano
for mes in range(1, 13):
    rows = db.query(Model).filter(Model.mes == mes).all()
```

## Índices

Colunas filtradas frequentemente DEVEM ter índice:
- Sempre: `user_id` em todas as tabelas
- Sempre: `(user_id, ano)`, `(user_id, mes)` em tabelas temporais
- Foreign keys sem índice são lentidão garantida
```

---

## `perf-frontend.mdc`

```
---
description: Padrões de performance para React/Next.js no FinUp
globs: app_dev/frontend/**/*.{ts,tsx}
alwaysApply: false
---

# Performance Frontend — FinUp

## useEffect: primitivos como dependência, nunca objetos

```typescript
// ✅ — só re-executa quando year ou month mudam
useEffect(() => { fetchData(year, month) }, [year, month])

// ❌ — params é um objeto novo a cada render → loop infinito ou re-fetch desnecessário
const params = { year, month }
useEffect(() => { fetchData(params) }, [params])
```

## Requests paralelos com Promise.all

```typescript
// ✅ — executa em paralelo, total = max(t1, t2)
const [dashboard, budget] = await Promise.all([
  fetchDashboard(year, month),
  fetchBudget(year, month)
])

// ❌ — executa em série, total = t1 + t2
const dashboard = await fetchDashboard(year, month)
const budget = await fetchBudget(year, month)
```

## staleTime em React Query / SWR

```typescript
// ✅ — dados financeiros mudam pouco, cache por 5 minutos
useQuery({
  queryKey: ['dashboard', year, month],
  queryFn: () => fetchDashboard(year, month),
  staleTime: 5 * 60 * 1000
})

// ❌ — re-fetch a cada foco de janela (padrão)
useQuery({ queryKey: [...], queryFn: ... })
```

## useMemo para cálculos caros

```typescript
// ✅
const totaisPorGrupo = useMemo(() =>
  transactions.reduce((acc, t) => {
    acc[t.grupo] = (acc[t.grupo] || 0) + t.valor
    return acc
  }, {} as Record<string, number>),
  [transactions]
)

// ❌ — recalcula a cada render
const totaisPorGrupo = transactions.reduce(...)
```

## Componentes Server vs Client (Next.js App Router)

Padrão do projeto: componentes de dados são Server Components, interatividade é Client:
```typescript
// ✅ — busca dados no servidor, sem JS no cliente
// app/dashboard/page.tsx (sem 'use client')
const data = await fetchDashboard(year, month)

// ✅ — só marca como client se precisar de estado/evento
'use client'
export function DashboardChart({ data }: Props) { ... }
```
```

---

## `new-domain.mdc`

```
---
description: Convenções obrigatórias ao criar ou editar um domínio backend no FinUp
globs: app_dev/backend/app/domains/**/*.py
alwaysApply: false
---

# Novo Domínio Backend — FinUp

## Estrutura obrigatória

Todo domínio DEVE ter exatamente estes arquivos:
```
domains/<nome>/
├── __init__.py
├── models.py       # SQLAlchemy ORM
├── schemas.py      # Pydantic request/response
├── repository.py   # Acesso ao banco (apenas queries)
├── service.py      # Regras de negócio (chama repository)
└── router.py       # Endpoints FastAPI (chama service)
```

## models.py

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class MinhaModel(Base):
    __tablename__ = "minha_tabela"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    # user_id é OBRIGATÓRIO em toda tabela de dados do usuário
```

## repository.py

```python
class MinhaRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, user_id: int) -> list[MinhaModel]:
        return self.db.query(MinhaModel).filter(
            MinhaModel.user_id == user_id  # user_id SEMPRE presente
        ).all()
```

## router.py

```python
from app.shared.dependencies import get_current_user_id

router = APIRouter(prefix="/meu-dominio", tags=["MeuDominio"])

@router.get("/")
def list_items(
    user_id: int = Depends(get_current_user_id),  # auth SEMPRE
    db: Session = Depends(get_db)
):
    service = MinhaService(db)
    return service.list_items(user_id)
```

## Registrar em main.py

Após criar o domínio, adicionar em `app/main.py`:
```python
from .domains.meu_dominio.router import router as meu_dominio_router
app.include_router(meu_dominio_router, prefix="/api/v1", tags=["MeuDominio"])
```
```

---

## `new-feature.mdc`

```
---
description: Convenções obrigatórias ao criar ou editar uma feature frontend no FinUp
globs: app_dev/frontend/src/features/**/*.{ts,tsx}
alwaysApply: false
---

# Nova Feature Frontend — FinUp

## Estrutura obrigatória

```
src/features/<nome>/
├── components/     # Componentes React específicos desta feature
├── hooks/          # Custom hooks (use-<nome>.ts)
├── services/       # Chamadas à API (fetch functions)
├── types/          # TypeScript types/interfaces
└── index.ts        # Re-exports públicos da feature
```

## services/ — cliente de API

```typescript
// features/<nome>/services/<nome>-service.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL

export async function fetchItems(year: number, month: number) {
  const res = await fetch(`${API_BASE}/api/v1/<nome>?year=${year}&month=${month}`, {
    credentials: 'include'  // sempre: envia cookie httpOnly
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
```

## hooks/ — estado e dados

```typescript
// features/<nome>/hooks/use-<nome>.ts
export function useItems(year: number, month: number) {
  // primitivos como dependência, nunca objeto
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    fetchItems(year, month)
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [year, month])  // primitivos

  return { data, loading, error }
}
```

## Tratamento de erro

Sempre expor `error` e `loading` junto com `data`. Nunca silenciar erros:
```typescript
// ✅
const { data, loading, error } = useItems(year, month)
if (error) return <ErrorState message={error} />
if (loading) return <LoadingState />

// ❌
const { data } = useItems(year, month)
// sem feedback de erro ou loading
```
```

---

## `migration.mdc`

```
---
description: Boas práticas obrigatórias ao escrever migrations Alembic para PostgreSQL
globs: app_dev/backend/alembic/versions/**/*.py
alwaysApply: false
---

# Migrations Alembic — FinUp

## Sempre escrever downgrade()

```python
# ✅
def upgrade():
    op.add_column('tabela', sa.Column('novo_campo', sa.String))

def downgrade():
    op.drop_column('tabela', 'novo_campo')  # OBRIGATÓRIO

# ❌ — sem downgrade, rollback impossível
def downgrade():
    pass
```

## Índices em PostgreSQL: CONCURRENTLY

```python
# ✅ — não bloqueia a tabela em produção
op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_id ON tabela (user_id)")

# ❌ — bloqueia a tabela, downtime em produção
op.create_index('idx_user_id', 'tabela', ['user_id'])
```

Nota: `CREATE INDEX CONCURRENTLY` não pode rodar dentro de uma transação.
Adicionar `connection.execute(text("COMMIT"))` antes se necessário.

## Adicionar coluna NOT NULL em tabela existente: 3 passos

```python
# Passo 1: adicionar nullable (sem quebrar)
op.add_column('tabela', sa.Column('novo', sa.String, nullable=True))

# Passo 2: popular com valor padrão (migration separada ou mesmo upgrade)
op.execute("UPDATE tabela SET novo = 'default' WHERE novo IS NULL")

# Passo 3: adicionar constraint NOT NULL (migration separada)
op.alter_column('tabela', 'novo', nullable=False)

# ❌ — quebra tabelas com dados existentes
op.add_column('tabela', sa.Column('novo', sa.String, nullable=False))
```

## Migrations destrutivas: aviso explícito

```python
def upgrade():
    # ⚠️ DESTRUTIVO: dados da coluna 'campo_antigo' serão perdidos
    # Backup foi feito em: scripts/deploy/backup_daily.sh
    op.drop_column('tabela', 'campo_antigo')
```

## Nomenclatura

Formato: `YYYY_descricao_clara.py`
```
2026_01_add_expectativas_mes.py       ✅
2026_02_remove_cenario_projecao.py    ✅
abc123_migration.py                    ❌
```

## Migrations de dados vs schema

Separar sempre em migrations diferentes:
1. Migration de schema (ADD/DROP/ALTER coluna)
2. Migration de dados (UPDATE/INSERT baseado em lógica)

Misturar os dois dificulta rollback parcial.
```

---

## `deploy.mdc`

```
---
description: Mapa de portas, ambientes e sequência correta de deploy do FinUp
globs: docker-compose*.yml, scripts/deploy/**/*.sh, .env*
alwaysApply: false
---

# Deploy — FinUp

## Mapa de portas

| Serviço | Dev local | Prod (interno) | Prod (externo/Nginx) |
|---------|-----------|---------------|----------------------|
| Backend API | 8000 | 8000 | 8000 |
| Frontend app | 3000 | 3000 | **3003** → meufinup.com.br |
| Frontend admin | 3001 | 3000 | **3001** → admin |
| PostgreSQL | 5432 | — (interno) | não exposto |
| Redis | 6379 | — (interno) | não exposto |

⚠️ Frontend app usa porta **3003** no host em produção (não 3000).

## Arquivos docker-compose

| Arquivo | Uso |
|---------|-----|
| `docker-compose.yml` | Desenvolvimento local (hot reload) |
| `docker-compose.prod.yml` | Produção na VM (sem hot reload, build standalone) |
| `docker-compose.vm.yml` | Variante específica da VM |

NUNCA usar `docker-compose.prod.yml` localmente para desenvolvimento.

## Script canônico de deploy

```bash
# O único script correto para deploy em produção:
./scripts/deploy/deploy.sh

# Para desenvolvimento local:
./scripts/deploy/quick_start.sh   # subir
./scripts/deploy/quick_stop.sh    # parar
```

## Sequência obrigatória de deploy

1. Backup do banco ANTES de qualquer coisa
2. `git pull origin main`
3. Migrations (`alembic upgrade head`) ANTES de reiniciar serviços
4. Build e restart do backend
5. Verificar health check do backend
6. Build e restart dos frontends
7. Verificar health checks dos frontends

NUNCA reiniciar serviços antes de rodar as migrations.
NUNCA rodar migrations depois de reiniciar com código novo.

## Variáveis obrigatórias em .env.prod

Qualquer nova variável de ambiente adicionada ao código DEVE ser documentada em `.env.prod.example` antes do deploy.
```
