# Plano de Ação — Segurança

**Origem:** Auditoria de Segurança `AUDITORIA_SEGURANCA.md` (2026-03-02)
**Branch de execução:** feature/security-hardening (novo) a partir de `main`

---

## Resumo dos problemas

| ID | Severidade | Problema | Status |
|---|---|---|---|
| C-01 | 🔴 CRÍTICO | Sem security headers no backend | pendente |
| A-01 | 🟠 ALTO | Token JWT em localStorage | pendente |
| A-02 | 🟠 ALTO | 46 `console.log` com dados financeiros | pendente |
| A-03 | 🟠 ALTO | CORS com métodos/headers irrestrito | pendente |
| M-01 | 🟡 MÉDIO | `print()` no backend em produção | pendente |
| M-02 | 🟡 MÉDIO | `.env` com secrets em texto puro | pendente |
| M-03 | 🟡 MÉDIO | `change-password` sem rate limit próprio | pendente |
| B-01 | 🔵 BAIXO | Três chaves diferentes para o mesmo token | pendente |
| B-02 | 🔵 BAIXO | `lib/api-client.ts` duplica `core/utils/api-client.ts` | pendente |

---

## Estratégia geral

Dividido em **4 sprints** em ordem de risco × facilidade de implementação:

- **Sprint 1 — Backend hardening** (C-01, A-03, M-01, M-03): zero risco de quebrar o frontend, todas mudanças no backend.
- **Sprint 2 — Remover token do localStorage** (A-01, B-01, B-02): elimina o risco principal de XSS, exige atenção nos arquivos que consomem o token.
- **Sprint 3 — Logger + console.log** (A-02): criar utilitário e substituir todos os 46 logs.
- **Sprint 4 — Hardening de produção** (M-02, CSP no Next.js): configurações de ambiente e Content-Security-Policy.

---

## Sprint 1 — Backend hardening

**Estimativa:** 1h
**Risco de regressão:** Baixo (mudanças exclusivamente no backend)
**Resolve:** C-01, A-03, M-01, M-03

---

### Tarefa 1.1 — SecurityHeadersMiddleware (C-01)

**Arquivo:** `app_dev/backend/app/main.py`

Criar middleware que adiciona os headers de segurança em todas as respostas.
Inserir **após** o bloco CORS (linha 59 atual).

```python
# Adicionar import no topo do arquivo
from starlette.middleware.base import BaseHTTPMiddleware

# Adicionar classe antes dos routers
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

**Verificação:** `curl -I http://localhost:8000/api/health` deve retornar os headers `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`.

---

### Tarefa 1.2 — Restringir CORS (A-03)

**Arquivo:** `app_dev/backend/app/main.py` linhas 57–58

Substituir os wildcards por listas explícitas:

```python
# Antes
allow_methods=["*"],
allow_headers=["*"],

# Depois
allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
```

**Verificação:** preflight OPTIONS com header customizado estranho deve retornar 403.

---

### Tarefa 1.3 — Rate limit em change-password (M-03)

**Arquivo:** `app_dev/backend/app/domains/auth/router.py`

Localizar o endpoint `change-password` e adicionar decorator de rate limit:

```python
@router.post("/change-password")
@limiter.limit("5/hour")   # ← adicionar esta linha
def change_password(request: Request, ...):
```

**Observação:** o `limiter` já existe na linha 23 do router.

**Verificação:** submeter 6 vezes o endpoint em sequência deve retornar 429 na 6ª tentativa.

---

### Tarefa 1.4 — Substituir `print()` por `logger` no backend (M-01)

**Arquivo:** `app_dev/backend/app/domains/transactions/service.py` linhas 672, 701, 922

Verificar se o módulo já tem `import logging` no topo. Se não, adicionar.

```python
# Adicionar no topo do arquivo (ou ajustar logger existente)
import logging
logger = logging.getLogger(__name__)

# Substituições:
# Linha 672: print(f"⚠️ AVISO: ...") → logger.debug("AVISO: ...")
# Linha 701: print(f"✅ Retornando ...") → logger.debug("Retornando %d grupos", len(grupos_com_media))
# Linha 922: print(f"➕ Nova marcação ...") → logger.debug("Nova marcação: %s > %s", grupo, subgrupo)
```

**Verificação:** iniciar o backend e verificar que o `stdout` não tem essas linhas em produção (DEBUG desligado).

---

## Sprint 2 — Remover token do localStorage

**Estimativa:** 2h
**Risco de regressão:** Médio — vários arquivos dependem do token em localStorage. Executar com testes manuais de login/logout ao final.
**Resolve:** A-01, B-01, B-02

### Contexto técnico

O backend já faz tudo correto:
- `POST /auth/login` retorna `access_token` no body **e** seta cookie `httpOnly`
- Todos os fetches do frontend que usam `credentials: 'include'` já enviam o cookie automaticamente
- O `AuthContext` (`src/contexts/AuthContext.tsx`) não usa localStorage — funciona via cookie

O problema: o `fetchWithAuth` e outras partes **paralelamente** leem localStorage, criando um segundo vetor de ataque.

O `AuthContext.login()` (linha 58) chama `setToken(data.access_token)` — isso salva o token em estado React (memória), não em localStorage. Esse comportamento está correto e pode ser mantido.

---

### Tarefa 2.1 — Limpar `core/utils/api-client.ts`

**Arquivo:** `app_dev/frontend/src/core/utils/api-client.ts`

O `fetchWithAuth` deve parar de ler localStorage e depender apenas do cookie.

```typescript
// ANTES (linhas 12–16):
const token = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null
const headers: HeadersInit = {
  ...(!isFormData && { 'Content-Type': 'application/json' }),
  ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  ...options.headers,
}

// DEPOIS:
const headers: HeadersInit = {
  ...(!isFormData && { 'Content-Type': 'application/json' }),
  ...options.headers,
}
```

Remover também (linhas 27, 77–87):
- `localStorage.removeItem('authToken')` no handler 401 — o logout já é feito pelo redirect
- As funções exportadas `isAuthenticated()`, `clearAuth()`, `setAuthToken()` — estão `@deprecated` e não são mais necessárias com cookies

**O que manter:** `credentials: 'include'` na linha 22 e o redirect para `/auth/login` no 401.

---

### Tarefa 2.2 — Remover `features/auth/hooks/use-token.ts`

**Arquivo:** `app_dev/frontend/src/features/auth/hooks/use-token.ts`

Este arquivo é um wrapper dedicado a `localStorage` para token. Com cookies, ele não tem mais uso.

Antes de deletar: verificar se algum arquivo importa de `use-token.ts`:

```bash
grep -r "use-token" app_dev/frontend/src --include="*.ts" --include="*.tsx"
```

Se não houver importações, deletar o arquivo. Se houver, substituir os usos por `useAuth()` do `AuthContext`.

---

### Tarefa 2.3 — Limpar `app-sidebar.tsx`

**Arquivo:** `app_dev/frontend/src/components/app-sidebar.tsx` linhas 387–388, 406

```typescript
// Linha 387–388: logout manual via localStorage
localStorage.removeItem('authToken')
localStorage.removeItem('user')

// Substituir por: chamar logout() do AuthContext
const { logout } = useAuth()
// ... no handler de logout:
await logout()  // já faz fetch para /auth/logout e limpa o estado
```

```typescript
// Linha 406: leitura do token para verificar autenticação
const token = localStorage.getItem('authToken')

// Substituir por: usar isAuthenticated do AuthContext
const { isAuthenticated } = useAuth()
```

---

### Tarefa 2.4 — Remover `access_token` de `mobile/profile/page.tsx`

**Arquivo:** `app_dev/frontend/src/app/mobile/profile/page.tsx` linha 197

```typescript
// Antes
localStorage.removeItem('access_token')

// Remover esta linha — o logout pelo AuthContext já invalida o cookie
```

---

### Tarefa 2.5 — Avaliar e consolidar `lib/api-client.ts`

**Arquivo:** `app_dev/frontend/src/lib/api-client.ts`

Este arquivo é um segundo cliente HTTP que:
- Usa chave `token` (diferente das outras duas: `authToken` e `access_token`)
- NÃO usa `credentials: 'include'` — ou seja, não envia o cookie httpOnly

Verificar quais arquivos importam de `src/lib/api-client.ts`:

```bash
grep -r "from.*lib/api-client" app_dev/frontend/src --include="*.ts" --include="*.tsx"
grep -r "from.*@/lib/api-client" app_dev/frontend/src --include="*.ts" --include="*.tsx"
```

**Opção A (preferida):** se houver poucos usos, migrar cada chamada `apiFetch`/`api.get` para `fetchWithAuth`/`fetchJsonWithAuth` de `core/utils/api-client.ts` e deletar `lib/api-client.ts`.

**Opção B:** se houver muitos usos, corrigir `lib/api-client.ts` para usar `credentials: 'include'` e remover a leitura de localStorage, sem consolidar os arquivos agora.

---

### Verificação do Sprint 2

Ao final, executar checklist manual:
- [ ] Login funciona e redireciona para `/dashboard`
- [ ] Reload da página mantém usuário logado (cookie persiste)
- [ ] Logout limpa o cookie (verificar em DevTools → Application → Cookies)
- [ ] Nenhuma chave `authToken`, `access_token` ou `token` aparece em `localStorage` após login
- [ ] Requisições autenticadas funcionam (dashboard carrega dados)

---

## Sprint 3 — Logger + remoção dos console.log

**Estimativa:** 1h30
**Risco de regressão:** Baixo — apenas substitui console.log por logger.log, comportamento idêntico em dev
**Resolve:** A-02

---

### Tarefa 3.1 — Criar `src/lib/logger.ts`

**Arquivo:** `app_dev/frontend/src/lib/logger.ts` (novo)

```typescript
/**
 * Logger utilitário — só emite em desenvolvimento
 * Substitui console.log diretos que expõem dados financeiros
 */
const isDev = process.env.NODE_ENV === 'development'

export const logger = {
  log: (...args: unknown[]): void => {
    if (isDev) console.log(...args)
  },
  warn: (...args: unknown[]): void => {
    if (isDev) console.warn(...args)
  },
  // console.error permanece ativo em produção — erros são úteis para monitoramento
  error: (...args: unknown[]): void => console.error(...args),
}
```

---

### Tarefa 3.2 — Substituir console.log nos arquivos de alto impacto

Prioridade: arquivos que expõem dados financeiros diretamente.

**Substituição:** `import { logger } from '@/lib/logger'` + trocar `console.log` → `logger.log`

| Arquivo | Linhas | O que expõe |
|---|---|---|
| `features/dashboard/hooks/use-dashboard.ts` | 170, 172, 176, 177 | Total de despesas, fontes, período |
| `features/investimentos/components/simulador-cenarios.tsx` | 360–376 | Patrimônio, aportes, rentabilidade |
| `app/upload/confirm/page.tsx` | 250 | Array de transações |
| `app/upload/confirm-ai/page.tsx` | 169, 189, 318 | Transações classificadas pela IA |
| `app/budget/page.tsx` | 72 | Grupos orçamentários |
| `app/budget/detalhada/page.tsx` | 176 | Categorias |
| `app/mobile/preview/[sessionId]/page.tsx` | 72–73, 134–135 | Payload + transações agrupadas |
| `app/mobile/upload/page.tsx` | 281, 346 | sessionId de upload |
| `app/settings/admin/page.tsx` | 95, 105, 123–124 | Dados de usuário admin |
| `features/upload/components/upload-dialog.tsx` | 268, 282, 291 | Cartões + compatibilidade |
| `features/preview/lib/constants.ts` | 29–30 | Estrutura de grupos (mapa interno) |
| `app/mobile/budget/edit/page.tsx` | 72 | Dados de orçamento |

---

### Tarefa 3.3 — Varredura final de console.log restantes

Após as substituições acima, executar:

```bash
grep -rn "console\.log" app_dev/frontend/src --include="*.ts" --include="*.tsx" | grep -v "logger.ts"
```

Revisar cada ocorrência restante. `console.error` pode permanecer. `console.warn` em código de produção deve ser avaliado caso a caso.

---

## Sprint 4 — Hardening de produção

**Estimativa:** 1h30
**Risco de regressão:** Baixo
**Resolve:** M-02, CSP no Next.js

---

### Tarefa 4.1 — Content-Security-Policy no Next.js

**Arquivo:** `app_dev/frontend/next.config.ts`

Adicionar headers CSP para o frontend:

```typescript
import type { NextConfig } from "next"
import path from "path"

const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

const cspHeader = [
  "default-src 'self'",
  `connect-src 'self' ${apiUrl}`,
  "script-src 'self' 'unsafe-inline'",   // unsafe-inline necessário para Next.js App Router
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self'",
  "frame-ancestors 'none'",              // equivalente a X-Frame-Options: DENY
  "form-action 'self'",
].join('; ')

const nextConfig: NextConfig = {
  devIndicators: false,
  outputFileTracingRoot: path.join(__dirname),
  output: 'standalone',
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'Content-Security-Policy', value: cspHeader },
        ],
      },
    ]
  },
}

export default nextConfig
```

**Atenção:** Após adicionar CSP, abrir o app e monitorar o console do browser por erros de violação (`Refused to load...`). Ajustar diretivas conforme necessário.

---

### Tarefa 4.2 — Separar `.env` de dev e produção (M-02)

**Arquivos:** `app_dev/backend/.env`, `app_dev/backend/.env.production` (novo)

**Passo 1:** Verificar se `docker-compose.yml` tem credenciais hardcoded:
```bash
grep -i "password\|secret\|jwt" app_dev/docker-compose*.yml 2>/dev/null
```

**Passo 2:** Gerar chave JWT dedicada para produção:
```bash
openssl rand -hex 32
```

**Passo 3:** Criar `.env.production.template` (sem valores reais, apenas estrutura) para documentar quais variáveis são necessárias em produção:

```
# Template — preencher com valores reais no servidor de produção
JWT_SECRET_KEY=<gerar com: openssl rand -hex 32>
DATABASE_URL=postgresql://user:password@host:5432/db
DEBUG=false
CORS_ORIGINS=https://seudominio.com
```

**Passo 4:** Confirmar que `.env.production` e `docker-compose.yml` estão no `.gitignore`.

---

### Tarefa 4.3 — Ajustar `DEBUG` no `.env` de desenvolvimento (B-02)

**Arquivo:** `app_dev/backend/.env`

```
# Antes
DEBUG=false

# Depois (habilita /docs no Swagger para desenvolvimento)
DEBUG=true
```

Isso permite inspecionar a API via `/docs` durante o desenvolvimento sem precisar alterar o arquivo toda vez.

---

## Critérios de conclusão por sprint

### Sprint 1 ✅ quando:
- [ ] `curl -I http://localhost:8000/` retorna `X-Frame-Options: DENY`
- [ ] `curl -I http://localhost:8000/` retorna `X-Content-Type-Options: nosniff`
- [ ] `curl -I http://localhost:8000/` retorna `Referrer-Policy`
- [ ] CORS não aceita métodos além da lista explícita
- [ ] 6ª tentativa em `/auth/change-password` retorna 429
- [ ] Nenhum `print()` em `transactions/service.py`

### Sprint 2 ✅ quando:
- [ ] Nenhum `localStorage.getItem/setItem` relacionado a `authToken`, `token` ou `access_token` no código de autenticação
- [ ] Login e logout funcionam via cookie httpOnly
- [ ] DevTools → Application → Local Storage não mostra token após login
- [ ] DevTools → Application → Cookies mostra `auth_token` como httpOnly após login

### Sprint 3 ✅ quando:
- [ ] `grep -rn "console.log" src --include="*.tsx" --include="*.ts"` retorna apenas chamadas que usam `logger.log` ou estão em comentários
- [ ] Console do browser em produção (build) não mostra dados financeiros do usuário

### Sprint 4 ✅ quando:
- [ ] Console do browser não exibe erros de violação de CSP
- [ ] `docker-compose.yml` confirmado no `.gitignore` ou sem credenciais hardcoded
- [ ] `.env` de dev usa `DEBUG=true`
- [ ] JWT_SECRET_KEY de produção é diferente da de desenvolvimento

---

## Ordem de execução recomendada

```
Sprint 1 (1h)   →   Sprint 3 (1h30)   →   Sprint 2 (2h)   →   Sprint 4 (1h30)
   backend              logs                  token               prod config
```

Motivo: Sprint 1 e 3 são independentes e têm risco mínimo. Sprint 2 tem o maior impacto no fluxo de autenticação — convém fazer com os logs já limpos para facilitar debug. Sprint 4 envolve configurações de ambiente que podem ser validadas por último.
