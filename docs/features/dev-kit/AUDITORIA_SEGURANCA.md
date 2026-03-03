# Auditoria de Segurança — app_dev

**Data:** 2026-03-02
**Branch:** feature/merge-plano-aposentadoria
**Método:** Análise estática de código — frontend + backend

---

## Resumo executivo

| Severidade | Qtd | Itens |
|---|---|---|
| 🔴 CRÍTICO | 1 | Ausência total de security headers no backend |
| 🟠 ALTO | 3 | Token em localStorage · 46 console.log com dados financeiros · CORS permissivo |
| 🟡 MÉDIO | 3 | `print()` no backend · .env com credenciais em texto puro · Sem rate limit em change-password |
| 🔵 BAIXO | 2 | Credencial de DB no .env dev · `access_token` duplicado em localStorage |
| ✅ OK | 5 | httpOnly cookie · bcrypt · ORM · Rate limit no login · Validação de upload |

---

## Achados Críticos e Altos

---

### 🔴 [C-01] Sem security headers no backend

**Severidade:** CRÍTICO
**Arquivo:** `app_dev/backend/app/main.py`

O backend não define nenhum header de segurança HTTP. Qualquer resposta da API — incluindo o frontend que a consome — fica sem proteção de camada de transporte.

| Header ausente | Risco |
|---|---|
| `Content-Security-Policy` | XSS — injeção de scripts maliciosos |
| `X-Frame-Options` | Clickjacking — iframe invisível sobre a tela |
| `X-Content-Type-Options` | MIME sniffing — navegador interpreta arquivo de forma incorreta |
| `Strict-Transport-Security` | Downgrade de HTTPS para HTTP em produção |
| `Referrer-Policy` | Vazamento da URL da API em cabeçalhos de requisição |

**Correção:**
```python
# app/main.py — adicionar após o CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

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

---

### 🟠 [A-01] Token JWT armazenado em localStorage

**Severidade:** ALTO
**Arquivo:** `app_dev/frontend/src/core/utils/api-client.ts` linhas 12, 27, 77, 81, 86

O `fetchWithAuth` foi escrito para usar cookies httpOnly (correto), mas **também** lê e escreve o token em `localStorage` como mecanismo paralelo:

```typescript
// linha 12 — lê token do localStorage e coloca em Authorization header
const token = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null

// linha 86 — funções @deprecated ainda ativas
export function setAuthToken(token: string): void {
  localStorage.setItem('authToken', token)  // ← expõe o token a qualquer JS da página
}
```

**Outros arquivos afetados:**

| Arquivo | Linha | Problema |
|---|---|---|
| `features/auth/hooks/use-token.ts` | 13, 22, 32 | Hook dedicado a persistir token em localStorage |
| `components/app-sidebar.tsx` | 387, 406 | Lê `authToken` de localStorage antes de requisições |
| `app/mobile/profile/page.tsx` | 197 | Remove `access_token` (chave diferente!) de localStorage |
| `lib/api-client.ts` | 9, 15 | Segundo cliente HTTP lendo chave `token` de localStorage |

**Por que é perigoso:** Qualquer script rodando na mesma origem (extensão de browser, widget, script injetado por XSS) consegue ler `localStorage.getItem('authToken')` e impersonar o usuário. O cookie `httpOnly` é imune a isso.

**Situação atual:** o backend seta o cookie httpOnly corretamente **e** retorna o token no body do JSON (`access_token`). O frontend então grava esse token no localStorage — anulando a proteção do cookie.

**Correção:**
- Remover toda leitura/escrita de `authToken` em localStorage
- Manter apenas `credentials: 'include'` no fetch (cookie httpOnly é enviado automaticamente)
- Marcar `setAuthToken`, `clearAuth`, `isAuthenticated` de `api-client.ts` como removidos (já estão como `@deprecated`)
- Consolidar os dois `api-client.ts` (`core/utils/` e `lib/`) — existem dois arquivos com mesmo propósito

---

### 🟠 [A-02] 46 `console.log` com dados financeiros ativos em produção

**Severidade:** ALTO
**Visibilidade:** Qualquer pessoa que abra o DevTools (F12) no browser do usuário vê todos esses dados

Total: **46 `console.log`** no frontend, dos quais os seguintes expõem dados sensíveis:

#### Dados financeiros diretos (alto impacto)

| Arquivo | Linha | O que expõe |
|---|---|---|
| `features/dashboard/hooks/use-dashboard.ts` | 170 | `{ year, month }` — período consultado |
| `features/dashboard/hooks/use-dashboard.ts` | 172 | Objeto completo de despesas do usuário |
| `features/dashboard/hooks/use-dashboard.ts` | 176 | Array de fontes de despesa com valores |
| `features/dashboard/hooks/use-dashboard.ts` | 177 | Total de despesas do mês |
| `features/investimentos/components/simulador-cenarios.tsx` | 360–376 | Valores de simulação de investimento (patrimônio, aportes, rentabilidade) |
| `app/upload/confirm/page.tsx` | 250 | Array de transações selecionadas para salvar |
| `app/upload/confirm-ai/page.tsx` | 169, 189, 318 | Transações processadas e classificadas pela IA |
| `app/budget/page.tsx` | 72 | Array completo de grupos orçamentários |
| `app/budget/detalhada/page.tsx` | 176 | Array de categorias com estrutura interna |

#### Dados de sessão/estrutura (médio impacto)

| Arquivo | Linha | O que expõe |
|---|---|---|
| `app/mobile/preview/[sessionId]/page.tsx` | 72–73 | Payload completo do backend + primeiro registro |
| `app/mobile/preview/[sessionId]/page.tsx` | 134–135 | Todas as transações agrupadas |
| `app/mobile/upload/page.tsx` | 281, 346 | `sessionId` de upload (pode ser reutilizado) |
| `app/settings/admin/page.tsx` | 95, 105, 123–124 | Dados de usuário + URL/método de requisição admin |
| `features/upload/components/upload-dialog.tsx` | 268, 282, 291 | Mapa de compatibilidade + cartões carregados |
| `features/preview/lib/constants.ts` | 29–30 | Estrutura completa de grupos/subgrupos (mapa interno da aplicação) |
| `app/mobile/budget/edit/page.tsx` | 72 | Dados de orçamento recebidos da API |

**Estes são os logs visíveis no screenshot enviado** — o console mostrando `useExpenseSources – Dados recebidos`, `Sources`, `Total: 32016.43` está originado no `use-dashboard.ts:172–177`.

**Correção:** Remover todos os `console.log` de produção. Padrão recomendado:

```typescript
// Criar utility em src/lib/logger.ts
const isDev = process.env.NODE_ENV === 'development'

export const logger = {
  log: (...args: unknown[]) => isDev && console.log(...args),
  warn: (...args: unknown[]) => isDev && console.warn(...args),
  // console.error pode permanecer — erros são úteis em prod
  error: console.error,
}

// Uso: substituir console.log → logger.log em todo o projeto
```

---

### 🟠 [A-03] CORS com métodos e headers irrestrito

**Severidade:** ALTO
**Arquivo:** `app_dev/backend/app/main.py` linhas 53–59

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # ✅ Origins específicas — OK
    allow_credentials=True,
    allow_methods=["*"],   # ❌ Permite DELETE, PATCH, OPTIONS, PUT — qualquer método
    allow_headers=["*"],   # ❌ Permite qualquer header customizado
)
```

**Origins está correto** (lista específica de localhost), mas métodos e headers irrestrito é desnecessário.

**Correção:**
```python
allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
```

---

## Achados Médios

---

### 🟡 [M-01] `print()` no backend — dados vazando nos logs do servidor

**Severidade:** MÉDIO
**Arquivo:** `app_dev/backend/app/domains/transactions/service.py` linhas 672, 701, 922

```python
# linha 672
print(f"⚠️ AVISO: Nenhum valor pré-calculado para {mes_referencia}. Buscar grupos únicos...")

# linha 701 — expõe contagem interna
print(f"✅ Retornando {len(grupos_com_media)} grupos com médias pré-calculadas")

# linha 922 — expõe subgrupo criado
print(f"➕ Nova marcação criada: {grupo} > {subgrupo}")
```

`print()` em Python vai para `stdout`, que em Docker vai para os logs do container. Em produção, logs de stdout podem ser expostos via ferramentas de observabilidade, dashboards de infra, ou acesso indevido ao container.

**Correção:** Substituir `print()` por `logging.getLogger(__name__).debug(...)` e configurar o nível de log para `WARNING` em produção.

---

### 🟡 [M-02] `.env` com JWT_SECRET_KEY e senha do banco em texto puro

**Severidade:** MÉDIO
**Arquivo:** `app_dev/backend/.env`

O arquivo **não está commitado no git** (confirmado via `git ls-files`, está no `.gitignore`). Porém:

```
JWT_SECRET_KEY=75a9adcc3479e410f304cbce982887692c208a5540d535a5bb80579f6bd4363a
DATABASE_URL=postgresql://finup_user:finup_password_dev_2026@localhost:5432/finup_db
```

- O arquivo existe no disco com credenciais em texto puro
- O próprio comentário diz que é "apenas para scripts Python standalone" e que o backend real usa `docker-compose.yml` — verificar se o docker-compose também tem credenciais hardcoded
- A chave JWT deve ser diferente entre dev e produção (atualmente pode ser a mesma)

**Recomendação:**
- Garantir que `JWT_SECRET_KEY` de produção seja gerada independentemente: `openssl rand -hex 32`
- Jamais reutilizar a chave do `.env` de dev em produção
- Verificar se `docker-compose.yml` também está no `.gitignore` caso contenha credenciais

---

### 🟡 [M-03] Endpoint `change-password` sem rate limiting próprio

**Severidade:** MÉDIO
**Arquivo:** `app_dev/backend/app/domains/auth/router.py` linha 151

O login tem rate limit dedicado de 3/minuto (correto). Mas `POST /auth/change-password` cai apenas no rate limit global de **60/minuto** — alto o suficiente para um ataque de força bruta contra a senha atual.

**Correção:**
```python
@router.post("/change-password")
@limiter.limit("5/hour")  # ← adicionar
def change_password(...):
```

---

## Achados Baixos

---

### 🔵 [B-01] Duas chaves de token distintas em localStorage

**Arquivo:** `api-client.ts` usa `authToken`; `mobile/profile/page.tsx` usa `access_token`; `lib/api-client.ts` usa `token`

Três chaves diferentes para o mesmo propósito. Se a autenticação migrar completamente para cookies (recomendado em A-01), esse problema é resolvido automaticamente. Caso contrário, unificar as três chaves em uma constante centralizada.

---

### 🔵 [B-02] `DEBUG=false` hardcoded no `.env` dev

**Arquivo:** `app_dev/backend/.env` linha 4: `DEBUG=false`

O `DEBUG=false` no `.env` de dev desativa o `/docs` (swagger). Em desenvolvimento isso dificulta a inspeção da API. Considerar `DEBUG=true` no `.env.dev` e `DEBUG=false` apenas no `.env.production`.

---

## O que está correto ✅

| Item | Localização | Detalhe |
|---|---|---|
| Cookie httpOnly + SameSite=strict | `auth/router.py:54-62` | Configuração correta de cookie de sessão |
| bcrypt com 12 rounds | `auth/password_utils.py` | Hashing seguro de senhas |
| ORM (sem raw SQL) | Todos os `repository.py` | Proteção automática contra SQL injection |
| Rate limit no login | `auth/router.py:27` | 3 tentativas/minuto por IP |
| Validação de upload | `upload/router.py:23-29` | Whitelist de extensões + MIME + 50MB max |
| JWT sem fallback fraco | `config.py:45-50` | Valida tamanho mínimo da chave (32 chars) |
| Docs desabilitados em prod | `main.py:43-44` | `/docs` e `/redoc` só no `DEBUG=true` |
| Rate limit global | `main.py:48` | 60/minuto (poderia ser menor, mas existe) |

---

## Plano de melhoria por prioridade

### Fase 1 — Imediata (proteção básica, baixo risco de quebrar algo)

| # | Ação | Arquivo | Esforço |
|---|---|---|---|
| 1.1 | Adicionar `SecurityHeadersMiddleware` no backend | `app/main.py` | 30 min |
| 1.2 | Restringir `allow_methods` e `allow_headers` no CORS | `app/main.py` | 10 min |
| 1.3 | Remover os 4 `console.log` de `use-dashboard.ts` | `features/dashboard/hooks/use-dashboard.ts` | 5 min |
| 1.4 | Remover `console.log` de `mobile/preview/[sessionId]/page.tsx` | `app/mobile/preview/` | 5 min |
| 1.5 | Substituir `print()` por `logger.debug()` no `transactions/service.py` | `domains/transactions/service.py` | 15 min |

### Fase 2 — Curto prazo (elimina o risco principal de XSS)

| # | Ação | Arquivo | Esforço |
|---|---|---|---|
| 2.1 | Criar `src/lib/logger.ts` com guard de `NODE_ENV` | novo arquivo | 15 min |
| 2.2 | Substituir todos os `console.log` de dados financeiros por `logger.log` | ~15 arquivos | 1h |
| 2.3 | Remover leitura/escrita de token em `localStorage` de `core/utils/api-client.ts` | `api-client.ts` | 30 min |
| 2.4 | Remover `use-token.ts` (hook dedicado a persistir token em localStorage) | `features/auth/hooks/` | 20 min |
| 2.5 | Auditar e remover todos os `localStorage.getItem/setItem` relacionados a `authToken` | `app-sidebar.tsx`, `profile/page.tsx`, `lib/api-client.ts` | 30 min |

### Fase 3 — Médio prazo (hardening de produção)

| # | Ação | Arquivo | Esforço |
|---|---|---|---|
| 3.1 | Adicionar `@limiter.limit("5/hour")` em `change-password` | `auth/router.py` | 5 min |
| 3.2 | Gerar nova `JWT_SECRET_KEY` exclusiva para produção | `.env` prod | 5 min |
| 3.3 | Configurar `Content-Security-Policy` completo no `next.config.js` | `next.config.js` | 1h |
| 3.4 | Consolidar `core/utils/api-client.ts` e `lib/api-client.ts` (dois arquivos com mesmo propósito) | ambos | 30 min |
| 3.5 | Verificar se `docker-compose.yml` está no `.gitignore` e sem credenciais hardcoded | `docker-compose.yml` | 10 min |

---

## Impacto esperado após Fase 1 + 2

- Console do browser **limpo** — nenhum dado financeiro visível via DevTools
- Token do usuário **não acessível via JavaScript** (apenas cookie httpOnly)
- Backend com headers básicos de proteção contra clickjacking e MIME sniffing
- Logs do servidor sem dados de negócio em `stdout`

O projeto já tem uma base sólida (httpOnly cookie, bcrypt, ORM, rate limit no login). As melhorias acima fecham as lacunas que ficaram abertas durante o desenvolvimento iterativo.
