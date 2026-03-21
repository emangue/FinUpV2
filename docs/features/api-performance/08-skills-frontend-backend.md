# Skills: Frontend e Backend

> Skills criados em `.claude/commands/` para guiar desenvolvimento consistente no FinUpV2.
> Ativar com `/backend` ou `/frontend` em qualquer sessão do Claude Code.

---

## `/backend` — FastAPI + SQLAlchemy

**Arquivo:** `.claude/commands/backend.md`

### O que o skill cobre

- Estrutura DDD de 5 arquivos por domínio (models, schemas, router, service, repository)
- Regras de segurança: isolamento por `user_id`, dependências obrigatórias, admin check
- Boilerplate completo de cada camada com exemplos reais do projeto
- Registro de router em `main.py`
- Workflow de migrations Alembic dentro do Docker

### Decisões de design documentadas

| Padrão | Justificativa |
|--------|--------------|
| Repository isola todas as queries | Testabilidade + não vazar SQL para service |
| Service instancia repository via `__init__` | Sem injeção global, escopo por request |
| `user_id` em todo WHERE | Segurança: usuários não podem ver dados alheios |
| Schemas Response com `from_attributes=True` | Conversão ORM → Pydantic sem `.model_validate()` manual |
| HTTPException em vez de exceções customizadas | FastAPI converte automaticamente para JSON |
| PostgreSQL only (guard no Alembic) | Evita divergências de comportamento SQLite/Postgres |

### O que NÃO fazer (principais)

- SQL no service ou router
- Query sem filtro `user_id`
- `alembic upgrade` fora do container
- `async def` em endpoints sem necessidade real (projeto é síncrono)
- Retornar objeto ORM direto sem schema Response

---

## `/frontend` — Next.js + React

**Arquivo:** `.claude/commands/frontend.md`

### O que o skill cobre

- Estrutura de feature (types → services → hooks → components → barrel export)
- Regras de API: `api.config.ts` como única fonte de URLs, helpers `apiGet/apiPost/etc.`
- Padrão de hook com cancellation token e estado (loading/error/data)
- Routing: desktop `/app/` vs mobile `/app/mobile/`, proteção com `useRequireAuth`
- Styling: `cn()`, CSS variables do tema, tokens mobile de `/config/`
- Performance: `useMemo`, `useCallback`, `Promise.all`, cancellation em useEffect

### Decisões de design documentadas

| Padrão | Justificativa |
|--------|--------------|
| Endpoints centralizados em `api.config.ts` | Evita URLs hardcoded espalhadas; 1 lugar para mudar em caso de refactor |
| `fetchWithAuth` obrigatório | httpOnly cookie é enviado automaticamente; raw `fetch` não funciona |
| Estado via hooks customizados (sem Zustand/RQ) | Projeto estabelecido — não introduzir novas dependências sem consenso |
| Cancellation token em useEffect | Evita memory leaks e state updates após unmount |
| `/components/ui/` não editável | shadcn gerencia esses arquivos; edições são sobrescritas |
| Separação desktop/mobile em rotas distintas | Layouts muito diferentes; componentes compartilhados ficam em `ui/` e `atoms/` |
| AuthContext para estado de auth | Único ponto de verdade; evita re-fetch de usuário em cada página |

### O que NÃO fazer (principais)

- `fetch()` direto ou URL hardcoded fora de `api.config.ts`
- Lógica de negócio ou chamada de API dentro do componente
- Token em localStorage (backend usa httpOnly cookie)
- Editar `/components/ui/`
- Criar `page 2.tsx` (duplicatas históricas — não perpetue o padrão)
- `window.xxx` sem guard SSR

---

## Como os Skills Se Complementam

```
Sessão de desenvolvimento:

/backend → Crio novo domínio FastAPI
           Gera boilerplate + migration + registro em main.py

/frontend → Crio feature que consome esse domínio
            Gera types + serviço + hook + componente + barrel export
```

Os dois skills foram construídos a partir de análise real do código existente —
não são guias genéricos. Refletem as decisões já tomadas no projeto.
