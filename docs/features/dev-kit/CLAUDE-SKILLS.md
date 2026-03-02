# Claude Code Skills — Conteúdo Completo

Cada seção é o conteúdo exato de um arquivo a criar em `.claude/commands/`.
Após criar a pasta `.claude/commands/`, copiar cada bloco como um arquivo `.md`.

## Status de criação

| Skill | Arquivo | Status |
|-------|---------|--------|
| `/commit` | `.claude/commands/commit.md` | ✅ Criado |
| `/new-domain` | `.claude/commands/new-domain.md` | ⏳ Pendente |
| `/new-feature` | `.claude/commands/new-feature.md` | ⏳ Pendente |
| `/security-check` | `.claude/commands/security-check.md` | ⏳ Pendente |
| `/perf-check` | `.claude/commands/perf-check.md` | ⏳ Pendente |
| `/api-review` | `.claude/commands/api-review.md` | ⏳ Pendente |
| `/feature-status` | `.claude/commands/feature-status.md` | ⏳ Pendente |
| `/migration` | `.claude/commands/migration.md` | ⏳ Pendente |
| `/deploy` | `.claude/commands/deploy.md` | ⏳ Pendente |

---

## `new-domain.md`

```markdown
Cria um novo domínio backend seguindo a arquitetura DDD do projeto FinUp.

## Uso
/new-domain <nome-do-dominio>

Exemplo: /new-domain pagamentos

## O que fazer

1. Ler um domínio existente como referência de estrutura:
   - app_dev/backend/app/domains/budget/ (domínio médio, bom exemplo)

2. Perguntar ao usuário antes de criar qualquer arquivo:
   - Qual é a entidade principal? (ex: Pagamento)
   - Quais campos básicos a tabela precisa?
   - O domínio precisa de relacionamento com algum outro? (ex: cards, transactions)

3. Criar os arquivos em `app_dev/backend/app/domains/<nome>/`:

   **`__init__.py`** — vazio

   **`models.py`** — modelo SQLAlchemy com:
   - `user_id` como ForeignKey obrigatório com index=True
   - `created_at` e `updated_at` automáticos
   - Relacionamento com User

   **`schemas.py`** — schemas Pydantic com:
   - Schema de criação (campos obrigatórios)
   - Schema de resposta (inclui id e timestamps)
   - Schema de atualização (todos os campos opcionais)

   **`repository.py`** — classe Repository com:
   - `list_by_user(user_id)` — sempre com filtro de user_id
   - `get_by_id(id, user_id)` — sempre verifica que pertence ao usuário
   - `create(data, user_id)`
   - `update(id, data, user_id)`
   - `delete(id, user_id)`

   **`service.py`** — classe Service que:
   - Recebe `db: Session` no __init__
   - Instancia o Repository internamente
   - Contém as regras de negócio
   - Lança HTTPException com mensagens claras

   **`router.py`** — endpoints FastAPI com:
   - `Depends(get_current_user_id)` em TODOS os endpoints
   - `Depends(get_db)` em TODOS os endpoints
   - Prefix `/nome-do-dominio`
   - GET /, GET /{id}, POST /, PUT /{id}, DELETE /{id}

4. Registrar o router em `app_dev/backend/app/main.py`:
   - Adicionar import
   - Adicionar `app.include_router(...)`

5. Mostrar resumo do que foi criado e quais endpoints estão disponíveis.
```

---

## `new-feature.md`

```markdown
Cria uma nova feature frontend seguindo a arquitetura do projeto FinUp.

## Uso
/new-feature <nome-da-feature>

Exemplo: /new-feature pagamentos

## O que fazer

1. Ler uma feature existente como referência:
   - app_dev/frontend/src/features/budget/ (feature completa, bom exemplo)

2. Perguntar ao usuário antes de criar:
   - Qual é o domínio backend correspondente?
   - A feature tem página própria ou é componente de outra página?
   - Precisa de listagem, formulário, ou ambos?

3. Criar estrutura em `app_dev/frontend/src/features/<nome>/`:

   **`types/index.ts`** — interfaces TypeScript alinhadas com os schemas do backend

   **`services/<nome>-service.ts`** — funções de fetch:
   - Usar `credentials: 'include'` em TODOS os requests (cookie httpOnly)
   - Usar `process.env.NEXT_PUBLIC_API_URL` como base
   - Tratar erros HTTP (throw se !res.ok)

   **`hooks/use-<nome>.ts`** — custom hook com:
   - `data`, `loading`, `error` sempre expostos
   - `useEffect` com primitivos como dependências (nunca objetos)
   - Funções de mutação (create, update, delete) se necessário

   **`components/`** — componentes React:
   - Separar ListComponent, FormComponent, etc.
   - Sempre tratar loading e error states
   - Usar componentes do `src/components/ui/` (shadcn/radix)

   **`index.ts`** — re-exports públicos da feature

4. Se a feature tiver página própria, criar em `app_dev/frontend/src/app/<nome>/page.tsx`

5. Mostrar resumo da estrutura criada e próximos passos.
```

---

## `security-check.md`

```markdown
Realiza auditoria de segurança completa nos arquivos modificados ou em um domínio específico.
Combina os padrões do projeto com OWASP Top 10 e boas práticas de mercado.

## Uso
/security-check                     # audita arquivos com git diff (modificados)
/security-check <domínio>           # audita domínio específico (ex: upload, auth)
/security-check --full              # audita todo o projeto

## O que fazer

### 1. Determinar escopo
- Sem argumento: `git diff --name-only HEAD` para pegar arquivos modificados
- Com domínio: `app_dev/backend/app/domains/<dominio>/` + feature frontend correspondente
- Com --full: todos os domínios backend + features frontend

### 2. Para cada arquivo Python (.py), verificar:

**OWASP A01 — Broken Access Control**
- Endpoint sem `Depends(get_current_user_id)`?
- Query sem filtro `user_id`?
- Usuário consegue acessar dados de outro usuário (IDOR)?

**OWASP A02 — Cryptographic Failures**
- Secrets hardcoded no código?
- JWT com algoritmo fraco (`none`, HS256 com secret fraco)?
- Dados sensíveis sendo logados?

**OWASP A03 — Injection**
- `text()` com concatenação de string?
- Parâmetros de query não sanitizados?

**OWASP A04 — Insecure Design**
- Upload sem validação de extensão, MIME e tamanho?
- Endpoint sem rate limiting (especialmente auth)?
- Resposta expondo stack trace ou detalhes de infra?

**OWASP A05 — Security Misconfiguration**
- `DEBUG=True` em produção?
- CORS com wildcard + credentials?
- Swagger habilitado em produção?

**OWASP A07 — Auth Failures**
- Login sem rate limiting?
- Senha sem mínimo de complexidade?
- Token sem expiração?

**Padrões específicos do projeto (docs/performance/SEGURANCA_FRONTEND_BACKEND.md)**
- `text()` com string concatenation?
- Filtro em Python em vez de SQL?
- Upload sem `_validar_arquivo()`?

### 3. Para cada arquivo TypeScript (.ts/.tsx), verificar:

**OWASP A02 — Dados sensíveis**
- `localStorage.setItem` com token ou dados financeiros?
- `console.log` com valores financeiros reais?

**OWASP A03 — XSS**
- `dangerouslySetInnerHTML` sem validação do valor?
- `eval()` em dados vindos da API?

**OWASP A05 — Misconfiguration**
- `NEXT_PUBLIC_*` expondo secrets?
- Variável de ambiente de secret no bundle do cliente?

**Padrões específicos do projeto**
- `localStorage.getItem('authToken')`?
- `console.log` com dados do usuário ou valores?

### 4. Gerar relatório

Formato da saída:

```
## Auditoria de Segurança — <escopo>
Data: <hoje>

### 🔴 Crítico
| Arquivo | Linha | Problema | OWASP | Fix |
|---------|-------|---------|-------|-----|

### 🟠 Alto
| ... |

### 🟡 Médio
| ... |

### ✅ OK
Itens verificados sem problemas encontrados.

### Referências
- docs/performance/SEGURANCA_FRONTEND_BACKEND.md
- OWASP Top 10: https://owasp.org/Top10/
```

Se não encontrar problemas, confirmar explicitamente que cada categoria foi verificada.
```

---

## `perf-check.md`

```markdown
Valida performance de código Python/TypeScript contra padrões do projeto e boas práticas.
Deve ser chamado antes de entregar qualquer nova chamada de API ou query de banco.

## Uso
/perf-check                         # verifica arquivos modificados (git diff)
/perf-check <domínio>               # verifica domínio específico
/perf-check <arquivo>               # verifica arquivo específico

## O que fazer

### 1. Determinar escopo (igual ao security-check)

### 2. Para cada arquivo Python (.py), verificar:

**N+1 — query dentro de loop**
- Existe `db.query()` ou `db.execute()` dentro de `for`?
- Solução: pré-buscar tudo em 1 query, usar dict para lookup O(1)

**Filtro em Python em vez de SQL**
- `.all()` seguido de list comprehension com filtro?
- Solução: mover filtro para `.filter()` no SQLAlchemy

**Query sem paginação**
- `.all()` em listagem sem `.limit()`?
- Risco: retornar milhares de registros
- Exceção: queries internas que precisam de todos os dados

**SELECT * implícito**
- `db.query(Model)` quando só usa 2-3 campos?
- Solução: `db.query(Model.campo1, Model.campo2)`

**Múltiplas queries para mesmo período**
- Loop por meses/anos fazendo query a cada iteração?
- Solução: buscar todo o período em 1 query, agrupar em Python

**user_id ausente**
- Query sem filtro `user_id`?
- Isso é tanto bug de segurança quanto de performance (full table scan)

**Índices**
- Nova coluna usada em `.filter()` sem `index=True` no modelo?
- FK sem índice?

### 3. Para cada arquivo TypeScript (.ts/.tsx), verificar:

**Requests sequenciais que poderiam ser paralelos**
- `await fetch(A)` seguido de `await fetch(B)` sem dependência entre eles?
- Solução: `Promise.all([fetch(A), fetch(B)])`

**useEffect com objeto como dependência**
- `useEffect(..., [objeto])` onde objeto é recriado a cada render?
- Solução: desestruturar para primitivos

**Ausência de staleTime**
- `useQuery` sem `staleTime`?
- Dados financeiros raramente mudam em segundos — cache de 1-5 min é seguro

**Cálculo pesado sem useMemo**
- Reduce/map/filter em array grande fora de useMemo?
- Recalcula a cada render desnecessariamente

**Componente client desnecessário**
- `'use client'` em componente que só renderiza dados estáticos?
- Next.js App Router: preferir Server Components para dados

### 4. Gerar relatório

```
## Auditoria de Performance — <escopo>
Data: <hoje>

### 🔴 Crítico (impacto direto no usuário)
| Arquivo | Linha | Problema | Impacto estimado | Solução |
|---------|-------|---------|-----------------|---------|

### 🟠 Alto
| ... |

### 🟡 Sugestão
| ... |

### ✅ OK
Itens verificados sem problemas encontrados.

### Referências
- docs/performance/PERFORMANCE_OPORTUNIDADES.md
```
```

---

## `api-review.md`

```markdown
Lista todos os endpoints de um domínio em formato de tabela clara.
Útil para revisar cobertura, construir frontend ou documentar.

## Uso
/api-review <domínio>

Exemplos:
/api-review plano
/api-review upload
/api-review auth

## O que fazer

1. Ler `app_dev/backend/app/domains/<dominio>/router.py`

2. Para cada endpoint encontrado, extrair:
   - Método HTTP (GET, POST, PUT, DELETE, PATCH)
   - Path completo (prefixo do router + path do decorator)
   - Autenticado? (tem `Depends(get_current_user_id)`)
   - Descrição (docstring do endpoint ou descrição inferida)
   - Response model (se definido)

3. Gerar tabela no formato:

```
## API — /api/v1/<domínio>

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | /api/v1/plano/orcamento | ✅ | Retorna orçamento mensal consolidado |
| POST | /api/v1/plano/expectativas | ✅ | Cria gasto extraordinário |
| ... | | | |

**Total: X endpoints**
**Autenticados: X/X**
```

4. Se existir frontend correspondente em `src/features/<dominio>/services/`, verificar se todos
   os endpoints do backend têm chamada de client no frontend. Listar os que faltam.
```

---

## `feature-status.md`

```markdown
Mostra o estado atual da sessão de trabalho: branch, arquivos modificados, docs relevantes.
Use no início de uma sessão para retomar contexto rapidamente.

## O que fazer

1. Executar `git branch --show-current` para pegar branch atual

2. Executar `git status --short` para listar arquivos modificados

3. Executar `git log --oneline -10` para ver commits recentes

4. Para cada domínio backend modificado (em `app_dev/backend/app/domains/`):
   - Qual é o domínio? Qual arquivo foi alterado?
   - Existe doc em `docs/features/` relacionado?

5. Para cada feature frontend modificada (em `app_dev/frontend/src/features/`):
   - Qual é a feature? Qual arquivo foi alterado?

6. Verificar se existem migrations pendentes:
   - Ler arquivos em `app_dev/backend/alembic/versions/` adicionados recentemente

7. Gerar resumo no formato:

```
## Status da Sessão
Data: <hoje>
Branch: <branch>

### Arquivos modificados
- backend: <lista>
- frontend: <lista>
- docs: <lista>

### Contexto relevante
- Feature em andamento: <nome inferido>
- Doc relacionado: <path se existir>
- Migrations pendentes: <sim/não + lista>

### Próximos passos sugeridos
<inferir do contexto dos arquivos modificados>
```
```

---

## `migration.md`

```markdown
Cria uma nova migration Alembic seguindo as boas práticas do projeto FinUp para PostgreSQL.

## Uso
/migration <descrição>

Exemplos:
/migration add_expectativas_mes_table
/migration remove_cenario_projecao
/migration add_user_id_index_to_grupos

## O que fazer

1. Ler as últimas 3 migrations em `app_dev/backend/alembic/versions/` como referência de padrão

2. Perguntar ao usuário:
   - Quais tabelas/colunas serão afetadas?
   - É uma migration de schema (ADD/DROP/ALTER) ou de dados (UPDATE/INSERT)?
   - Tem operações destrutivas (DROP COLUMN, DROP TABLE, RENAME)?

3. Gerar o arquivo de migration com:

   **Nomenclatura:** `<ano>_<descricao_clara>.py` (ex: `2026_add_expectativas_mes.py`)

   **Estrutura obrigatória:**
   ```python
   """<descrição clara da migration>

   Revision ID: <gerado pelo alembic>
   Revises: <revision anterior>
   Create Date: <data>
   """
   from alembic import op
   import sqlalchemy as sa

   revision = '<hash>'
   down_revision = '<hash_anterior>'
   branch_labels = None
   depends_on = None

   def upgrade():
       # implementação

   def downgrade():
       # OBRIGATÓRIO — reverter o upgrade
   ```

4. Para operações específicas, usar padrão correto:

   - **Índice:** `op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS ...")`
   - **Coluna NOT NULL em tabela existente:** 3 passos (nullable → populate → alter)
   - **DROP:** adicionar comentário `# ⚠️ DESTRUTIVO` com aviso

5. Se for migration de dados, criar arquivo separado do schema

6. Mostrar preview da migration e perguntar se deve rodar `alembic upgrade head` localmente

7. Após confirmação, rodar localmente e mostrar output do alembic

## Referências
- docs/features/dev-kit/CURSOR-RULES.md (seção migration.mdc)
- app_dev/backend/alembic/versions/ (migrations existentes como exemplo)
```

---

## `deploy.md`

```markdown
Executa ou valida o processo canônico de deploy do FinUp.
Referência: docs/features/dev-kit/DEPLOY.md

## Uso
/deploy --check     # valida pré-condições sem fazer nada
/deploy --local     # testa build de produção localmente
/deploy             # executa deploy completo na VM

## O que fazer

### Modo --check (pré-voo)

1. `git status` — tem arquivos não commitados?
2. `git log origin/main..HEAD` — branch está à frente do main?
3. Verificar se existem migrations novas não aplicadas em prod
4. Verificar se novas variáveis de ambiente foram adicionadas ao código
   mas não documentadas em `.env.prod.example`
5. Verificar se `console.log` com dados financeiros foram deixados no frontend

Gerar relatório: ✅ pronto para deploy / ⚠️ atenção nos itens X / ❌ não deployar

### Modo --local (teste de build)

1. Rodar `docker-compose -f docker-compose.prod.yml build`
2. Subir serviços localmente na config de prod
3. Verificar health checks
4. Derrubar após verificação

### Modo padrão (deploy real)

Seguir sequência do `docs/features/dev-kit/DEPLOY.md`:

**Fase 1:** Pré-voo (executar --check primeiro)
**Fase 2:** Backup do banco (OBRIGATÓRIO antes de qualquer outra coisa)
**Fase 3:** Pull + migrations + restart backend
**Fase 4:** Restart frontends
**Fase 5:** Verificação de saúde

Para cada passo que envolva operação irreversível (backup, migration destrutiva),
pedir confirmação explícita do usuário antes de prosseguir.

## Mapa de portas (referência rápida)
- Backend: 8000 (dev e prod)
- Frontend app: 3000 (dev) / 3003 no host em prod
- Frontend admin: 3001 (dev e prod no host)
```
