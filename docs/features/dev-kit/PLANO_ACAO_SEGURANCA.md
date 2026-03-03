# Plano de Ação — Segurança (Auditoria 2026-03-02)

**Baseado em:** [AUDITORIA_SEGURANCA.md](./AUDITORIA_SEGURANCA.md)  
**Criado em:** 2026-03-02  
**Responsável:** Dev  
**Status:** 🔴 Pendente

---

## Visão Geral

| ID | Severidade | Título | Sprint | Status |
|----|------------|--------|--------|--------|
| C-01 | 🔴 CRÍTICO | Security headers ausentes no backend | 1 | ⬜ |
| A-03 | 🟠 ALTO | CORS com métodos/headers irrestrito | 1 | ⬜ |
| M-01 | 🟡 MÉDIO | `print()` no backend em produção | 1 | ⬜ |
| M-03 | 🟡 MÉDIO | `change-password` sem rate limit | 1 | ⬜ |
| A-02 | 🟠 ALTO | 46+ `console.log` com dados financeiros | 2 | ⬜ |
| A-01 | 🟠 ALTO | Token JWT em localStorage | 3 | ⬜ |
| B-01 | 🔵 BAIXO | Três chaves de token distintas em localStorage | 3 | ⬜ |
| M-02 | 🟡 MÉDIO | JWT_SECRET_KEY dev ≠ prod (verificar) | 3 | ⬜ |
| B-02 | 🔵 BAIXO | `DEBUG=false` no `.env` de dev | 3 | ⬜ |

**Estimativa total:** ~5h distribuídas em 3 sprints

---

## DAG — Dependências entre tarefas

```
C-01 ──┐
A-03 ──┤──► Sprint 1 (independente, sem risco de quebra)
M-01 ──┤
M-03 ──┘

         A-02 (criar logger.ts primeiro)
          │
          └──► Sprint 2 (substitui console.log em ~15 arquivos)

                    A-01 (remover localStorage)
                     │
                     ├── B-01 (unificar chaves, depende de A-01)
                     ├── M-02 (verificar JWT prod, independente)
                     └── B-02 (ajustar DEBUG, independente)
                          │
                          └──► Sprint 3 (maior risco, validar autenticação)
```

---

## Sprint 1 — Proteções imediatas (backend)

**Tempo estimado:** 1h  
**Risco:** 🟢 Baixo — nenhuma mudança de lógica de negócio  
**Validação:** `curl -I http://localhost:8000/api/health` e testar login

---

### Tarefa 1.1 — Security Headers Middleware

**Arquivo:** `app_dev/backend/app/main.py`  
**Onde inserir:** após o bloco `CORSMiddleware`, antes dos `include_router`

**Código a adicionar:**

```python
# --- Inserir após as importações existentes ---
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adiciona headers HTTP de segurança em todas as respostas.
    Proteções: clickjacking, MIME sniffing, HSTS (prod), referrer.
    """
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # HSTS apenas em produção (HTTPS obrigatório)
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response
```

**E registrar o middleware — após o CORSMiddleware:**

```python
# Adicionar APÓS app.add_middleware(CORSMiddleware, ...)
app.add_middleware(SecurityHeadersMiddleware)
```

**Posição exata no arquivo atual (linha ~53):**
```python
# ANTES (linha 53):
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers Modularizados...
```

```python
# DEPOIS:
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

app.add_middleware(SecurityHeadersMiddleware)   # ← novo

# Routers Modularizados...
```

**Validação:**
```bash
curl -I http://localhost:8000/api/health
# Deve retornar:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Referrer-Policy: strict-origin-when-cross-origin
# Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

### Tarefa 1.2 — CORS: restringir métodos e headers

**Arquivo:** `app_dev/backend/app/main.py`  
**Mudança:** já incluída na tarefa 1.1 acima (bloco CORS)

```python
# DE:
allow_methods=["*"],
allow_headers=["*"],

# PARA:
allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
```

**Notas:**
- `allow_origins` já está correto (lista específica) — não alterar
- `allow_credentials=True` permanece (necessário para cookie httpOnly)
- `OPTIONS` é necessário para preflight CORS

**Validação:**
```bash
# Testar preflight com método proibido
curl -X OPTIONS http://localhost:8000/api/v1/transactions/list \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: CONNECT" \
  -v 2>&1 | grep "Access-Control-Allow-Methods"
# Deve retornar apenas os métodos listados, não "*"
```

---

### Tarefa 1.3 — Substituir `print()` por `logging` no backend

**Arquivo:** `app_dev/backend/app/domains/transactions/service.py`  
**Linhas afetadas:** 672, 701, 922

**Mudanças:**

```python
# LINHA 672 — DE:
print(f"⚠️ AVISO: Nenhum valor pré-calculado para {mes_referencia}. Buscar grupos únicos...")

# PARA:
logger.debug("Nenhum valor pré-calculado para %s — buscando grupos únicos", mes_referencia)
```

```python
# LINHA 701 — DE:
print(f"✅ Retornando {len(grupos_com_media)} grupos com médias pré-calculadas")

# PARA:
logger.debug("Retornando %d grupos com médias pré-calculadas", len(grupos_com_media))
```

```python
# LINHA 922 — DE:
print(f"➕ Nova marcação criada: {grupo} > {subgrupo}")

# PARA:
logger.debug("Nova marcação criada: %s > %s", grupo, subgrupo)
```

**Verificar se `logger` já está importado no topo do arquivo:**
```python
# Se não existir, adicionar após as importações no topo de service.py:
import logging
logger = logging.getLogger(__name__)
```

**Validação:**
```bash
# Os prints NÃO devem mais aparecer nos logs do container
docker-compose logs -f backend | grep -E "AVISO|Retornando|Nova marcação"
# Deve retornar vazio durante uso normal (level DEBUG desativado em prod)
```

---

### Tarefa 1.4 — Rate limit em `change-password`

**Arquivo:** `app_dev/backend/app/domains/auth/router.py`  
**Linha:** ~151 (endpoint `change-password`)

```python
# DE:
@router.post("/change-password")
def change_password(
    ...

# PARA:
@router.post("/change-password")
@limiter.limit("5/hour")  # Protege contra força bruta na senha atual
def change_password(
    request: Request,   # ← parâmetro obrigatório para o limiter funcionar
    ...
```

**Atenção:** verificar se `request: Request` já é parâmetro da função. Se não for, adicionar como primeiro parâmetro. O decorador `@limiter.limit` exige o objeto `request` no handler.

**Validação:**
```bash
# Testar rate limit (6ª chamada deve retornar 429)
for i in {1..6}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST http://localhost:8000/api/v1/auth/change-password \
    -H "Content-Type: application/json" \
    -d '{"current_password":"x","new_password":"y"}'
done
# Primeiras 5: 401 ou 422 (credenciais inválidas) — OK
# 6ª: 429 Too Many Requests — ✅
```

---

## Sprint 2 — Eliminar vazamento de dados no console

**Tempo estimado:** 1h 15min  
**Risco:** 🟢 Baixo — apenas remove logs de debug  
**Validação:** abrir DevTools (F12) e navegar pelo app — console deve estar limpo

---

### Tarefa 2.1 — Criar `src/lib/logger.ts`

**Arquivo novo:** `app_dev/frontend/src/lib/logger.ts`

```typescript
/**
 * Logger condicional — só emite em NODE_ENV=development.
 * Substitui console.log em todo o projeto para evitar vazamento
 * de dados financeiros no browser em produção.
 *
 * Uso:
 *   import { logger } from '@/lib/logger'
 *   logger.log('Dados:', data)   // só aparece em dev
 *   logger.error('Erro:', err)  // sempre aparece (útil em prod)
 */

const isDev = process.env.NODE_ENV === 'development'

export const logger = {
  log: (...args: unknown[]): void => {
    if (isDev) console.log(...args)
  },
  warn: (...args: unknown[]): void => {
    if (isDev) console.warn(...args)
  },
  debug: (...args: unknown[]): void => {
    if (isDev) console.debug(...args)
  },
  // error sempre ativo — erros em prod são necessários para diagnóstico
  error: (...args: unknown[]): void => {
    console.error(...args)
  },
}
```

---

### Tarefa 2.2 — Substituir `console.log` com dados financeiros

Lista completa de mudanças por arquivo. Usar `logger.log` importado de `@/lib/logger`.

#### `features/dashboard/hooks/use-dashboard.ts` (linhas 170, 172, 176, 177)

```typescript
// Adicionar no topo do arquivo:
import { logger } from '@/lib/logger'

// DE (4 linhas):
console.log('🔍 useExpenseSources - Buscando despesas:', { year, month })
console.log('✅ useExpenseSources - Dados recebidos:', data)
console.log('📊 useExpenseSources - Sources:', data.sources)
console.log('💰 useExpenseSources - Total:', data.total_despesas)

// PARA:
logger.log('🔍 useExpenseSources - Buscando despesas:', { year, month })
logger.log('✅ useExpenseSources - Dados recebidos:', data)
logger.log('📊 useExpenseSources - Sources:', data.sources)
logger.log('💰 useExpenseSources - Total:', data.total_despesas)
```

#### `features/investimentos/components/simulador-cenarios.tsx` (linhas 360, 376)

```typescript
import { logger } from '@/lib/logger'

// DE:
console.log('📊 Valores da Simulação:', { ... })
console.log('💰 Cálculo Rentabilidade:', { ... })

// PARA:
logger.log('📊 Valores da Simulação:', { ... })
logger.log('💰 Cálculo Rentabilidade:', { ... })
```

#### `app/upload/confirm/page.tsx` (linha 250)

```typescript
// DE:
console.log('Salvando transações:', selectedTransactions)
// PARA:
logger.log('Salvando transações:', selectedTransactions)
```

#### `app/upload/confirm-ai/page.tsx` (linhas 169, 189, 318)

```typescript
// DE:
console.log('Dados processados:', processData)
console.log('Dados classificados:', classifyData)
console.log('Transações confirmadas:', result)
// PARA:
logger.log('Dados processados:', processData)
logger.log('Dados classificados:', classifyData)
logger.log('Transações confirmadas:', result)
```

#### `app/mobile/preview/[sessionId]/page.tsx` (linhas 72, 73, 134, 135)

```typescript
// DE:
console.log('🔍 DEBUG - Dados recebidos do backend:', data);
console.log('🔍 DEBUG - Primeiro registro:', data.dados?.[0]);
console.log('🔍 DEBUG - Transações agrupadas:', transactions);
console.log('🔍 DEBUG - Total de grupos/transações:', transactions.length);
// PARA:
logger.log('🔍 DEBUG - Dados recebidos do backend:', data);
logger.log('🔍 DEBUG - Primeiro registro:', data.dados?.[0]);
logger.log('🔍 DEBUG - Transações agrupadas:', transactions);
logger.log('🔍 DEBUG - Total de grupos/transações:', transactions.length);
```

#### `app/mobile/upload/page.tsx` (linhas 281, 346)

```typescript
// DE:
console.log('✅ [MOBILE-UPLOAD] Upload bem-sucedido! SessionId:', result.sessionId);
console.log('✅ [MOBILE-UPLOAD] Upload com senha bem-sucedido! SessionId:', result.sessionId);
// PARA:
logger.log('✅ [MOBILE-UPLOAD] Upload bem-sucedido! SessionId:', result.sessionId);
logger.log('✅ [MOBILE-UPLOAD] Upload com senha bem-sucedido! SessionId:', result.sessionId);
```

#### `app/budget/page.tsx` (linhas 72, 111)

```typescript
// DE:
console.log('Grupos carregados da API:', grupos.length, grupos);
console.log('Budget carregado:', Object.keys(budgetMap).length, 'grupos');
// PARA:
logger.log('Grupos carregados da API:', grupos.length, grupos);
logger.log('Budget carregado:', Object.keys(budgetMap).length, 'grupos');
```

#### `app/budget/detalhada/page.tsx` (linha 176)

```typescript
// DE:
console.log('Categorias carregadas:', result.categorias?.length, result.categorias);
// PARA:
logger.log('Categorias carregadas:', result.categorias?.length, result.categorias);
```

#### `app/budget/simples/page.tsx` (linhas 110, 111)

```typescript
// DE:
console.log('Grupos carregados:', grupos.length);
console.log('Médias calculadas:', Object.keys(medias).length);
// PARA:
logger.log('Grupos carregados:', grupos.length);
logger.log('Médias calculadas:', Object.keys(medias).length);
```

#### `app/settings/admin/page.tsx` (linhas 95, 105, 123, 124)

```typescript
// DE:
console.log('Editando usuário:', usuario)
console.log('Salvando usuário. Modo edição:', !!editingUsuario)
console.log('URL:', url)
console.log('Method:', method)
// PARA:
logger.log('Editando usuário:', usuario)
logger.log('Salvando usuário. Modo edição:', !!editingUsuario)
logger.log('URL:', url)
logger.log('Method:', method)
```

#### `features/upload/components/upload-dialog.tsx` (linhas 268, 282, 291)

```typescript
// DE:
console.log('🔍 Compatibilidade carregada:', data)
console.log('📊 Compatibilidade processada:', compatibilityMap)
console.log('💳 Cartões carregados:', data)
// PARA:
logger.log('🔍 Compatibilidade carregada:', data)
logger.log('📊 Compatibilidade processada:', compatibilityMap)
logger.log('💳 Cartões carregados:', data)
```

#### `features/preview/lib/constants.ts` (linhas 29, 30)

```typescript
// DE:
console.log('✅ Grupos carregados:', GRUPOS.length);
console.log('✅ Subgrupos por grupo:', Object.keys(SUBGRUPOS).length, 'grupos');
// PARA:
logger.log('✅ Grupos carregados:', GRUPOS.length);
logger.log('✅ Subgrupos por grupo:', Object.keys(SUBGRUPOS).length, 'grupos');
```

#### `features/preview/templates/PreviewLayout.tsx` (linha 245)

```typescript
// DE:
console.log('✅ Upload confirmado:', data);
// PARA:
logger.log('✅ Upload confirmado:', data);
```

#### `features/investimentos/components/export-investimentos.tsx` (linhas 178, 199)

```typescript
// DE:
console.log(`✅ ${investimentos.length} investimentos exportados para CSV`)
console.log(`✅ ${investimentos.length} investimentos exportados para Excel`)
// PARA:
logger.log(`✅ ${investimentos.length} investimentos exportados para CSV`)
logger.log(`✅ ${investimentos.length} investimentos exportados para Excel`)
```

#### `features/investimentos/hooks/use-toast-notifications.ts` (linha 19)

```typescript
// DE:
console.log(`[${type.toUpperCase()}] ${options.title}`, options.description)
// PARA:
logger.log(`[${type.toUpperCase()}] ${options.title}`, options.description)
```

#### `app/mobile/budget/manage/page.tsx` (linhas 55, 78)

```typescript
// DE:
console.log(`✅ Meta ${goal.grupo} ${!currentState ? 'ativada' : 'desativada'}`)
console.log(`✅ Valor da meta ${goal.grupo} atualizado: R$ ${novoValor}...`)
// PARA:
logger.log(`✅ Meta ${goal.grupo} ${!currentState ? 'ativada' : 'desativada'}`)
logger.log(`✅ Valor da meta ${goal.grupo} atualizado: R$ ${novoValor}...`)
```

#### `app/mobile/budget/edit/page.tsx` (linha 72)

```typescript
// DE:
console.log('Dados recebidos:', data)
// PARA:
logger.log('Dados recebidos:', data)
```

#### `app/dashboard/page.tsx` (linha 360)

```typescript
// DE:
console.log('🔄 Atualizando dashboard manualmente...');
// PARA:
logger.log('🔄 Atualizando dashboard manualmente...');
```

#### `components/app-sidebar.tsx` (linha 408)

```typescript
// DE:
console.log('[AppSidebar] Sem token, não carregando status de telas')
// PARA:
logger.log('[AppSidebar] Sem token, não carregando status de telas')
```

---

### Validação Sprint 2

```bash
# 1. Build de produção local (simula NODE_ENV=production)
cd app_dev/frontend && NODE_ENV=production npm run build

# 2. Buscar console.log remanescentes nos arquivos de produção
grep -r "console\.log" src/app src/features src/components \
  --include="*.ts" --include="*.tsx" \
  | grep -v "__tests__" \
  | grep -v "// " \
  | grep -v "Mock console"
# Deve retornar apenas linhas dentro de comentários ou arquivos de teste

# 3. Verificar no browser (após npm run dev):
# - Abrir DevTools → Console
# - Navegar no dashboard, uploads, investimentos
# - Console deve estar limpo (sem dados financeiros)
```

---

## Sprint 3 — Remover token do localStorage e hardening

**Tempo estimado:** 2h 30min  
**Risco:** 🟡 Médio — autenticação é crítica; testar fluxo completo  
**Validação:** fluxo de login → navegação → logout deve funcionar sem `authToken` no localStorage

---

### Tarefa 3.1 — Limpar `localStorage` de `core/utils/api-client.ts`

**Arquivo:** `app_dev/frontend/src/core/utils/api-client.ts`

O arquivo já tem cookie `credentials: 'include'` — correto. O que precisa ser removido é a leitura paralela do localStorage.

```typescript
// DE (arquivo atual):
export async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const isFormData = options.body instanceof FormData
  const token = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null
  const headers: HeadersInit = {
    ...(!isFormData && { 'Content-Type': 'application/json' }),
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',
    redirect: 'follow',
  })

  if (response.status === 401 && typeof window !== 'undefined') {
    localStorage.removeItem('authToken')
    window.location.href = '/auth/login'
  }

  return response
}

/** @deprecated Use useAuth() from AuthContext. Cookie httpOnly não é legível via JS. */
export function isAuthenticated(): boolean {
  return !!localStorage.getItem('authToken')
}

export function clearAuth(): void {
  localStorage.removeItem('authToken')
}

/** @deprecated Backend seta cookie httpOnly. Mantido para compatibilidade. */
export function setAuthToken(token: string): void {
  localStorage.setItem('authToken', token)
}
```

```typescript
// PARA (arquivo limpo):
/**
 * Cliente HTTP com autenticação via cookie httpOnly.
 * Autenticação é gerenciada exclusivamente pelo cookie `auth_token`
 * setado pelo backend — não há leitura/escrita em localStorage.
 */

export async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const isFormData = options.body instanceof FormData
  const headers: HeadersInit = {
    ...(!isFormData && { 'Content-Type': 'application/json' }),
    ...options.headers,
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',  // cookie httpOnly enviado automaticamente
    redirect: 'follow',
  })

  if (response.status === 401 && typeof window !== 'undefined') {
    window.location.href = '/auth/login'
  }

  return response
}

export async function fetchJsonWithAuth<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetchWithAuth(url, options)

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`HTTP ${response.status}: ${response.statusText}\n${errorText}`)
  }

  return response.json()
}

/**
 * @deprecated Removido — autenticação via cookie httpOnly não é detectável via JS.
 * Use AuthContext para verificar estado de autenticação.
 */
export function isAuthenticated(): boolean {
  // Mantido apenas para compatibilidade de tipos — sempre retorna false
  // Migrar chamadores para AuthContext.isAuthenticated
  return false
}

/**
 * @deprecated Removido — cookie httpOnly é limpo pelo backend no logout.
 * Chame POST /api/v1/auth/logout em vez disso.
 */
export function clearAuth(): void {
  // no-op intencional
}

/**
 * @deprecated Removido — backend seta cookie httpOnly automaticamente no login.
 * Não armazenar token em localStorage.
 */
export function setAuthToken(_token: string): void {
  // no-op intencional
}
```

---

### Tarefa 3.2 — Remover `use-token.ts`

**Arquivo:** `app_dev/frontend/src/features/auth/hooks/use-token.ts`

**Antes de remover:** verificar todos os lugares que importam este hook:

```bash
grep -r "use-token\|useToken" app_dev/frontend/src \
  --include="*.ts" --include="*.tsx" \
  | grep -v "__tests__"
```

**Se não houver chamadores ativos:** deletar o arquivo.

**Se houver chamadores:** substituir chamadas por `useAuth()` do `AuthContext` antes de deletar.

---

### Tarefa 3.3 — Limpar `localStorage` em arquivos remanescentes

**`components/app-sidebar.tsx` (linhas 387, 406)**

```bash
# Verificar contexto exato:
grep -n "localStorage\|authToken" app_dev/frontend/src/components/app-sidebar.tsx
```

Substituir qualquer leitura de `localStorage.getItem('authToken')` por verificação via `AuthContext`:

```typescript
// DE:
const token = localStorage.getItem('authToken')
if (!token) { ... }

// PARA:
const { isAuthenticated } = useAuth()  // importar AuthContext
if (!isAuthenticated) { ... }
```

**`app/mobile/profile/page.tsx` (linha 197)**

```bash
grep -n "access_token\|localStorage" app_dev/frontend/src/app/mobile/profile/page.tsx
```

Substituir `localStorage.removeItem('access_token')` pela chamada ao endpoint de logout do backend.

**`lib/api-client.ts` (linhas 9, 15 — arquivo duplicado)**

```bash
# Verificar se este arquivo ainda é importado em algum lugar:
grep -r "lib/api-client\|from.*lib/api" app_dev/frontend/src \
  --include="*.ts" --include="*.tsx" \
  | grep -v "core/utils/api-client"
```

Se não tiver importadores ativos → **deletar** `lib/api-client.ts` (duplicata do `core/utils/api-client.ts`).  
Se tiver importadores → migrar para `@/core/utils/api-client` e então deletar.

---

### Tarefa 3.4 — Verificar JWT_SECRET_KEY prod ≠ dev

```bash
# Verificar chave atual no .env de dev:
grep JWT_SECRET_KEY app_dev/backend/.env

# Verificar no servidor de prod (SSH):
ssh minha-vps-hostinger "grep JWT_SECRET_KEY /var/www/finup/app_dev/backend/.env"

# Se forem iguais, gerar nova chave para prod:
ssh minha-vps-hostinger "openssl rand -hex 32"
# Substituir no servidor:
ssh minha-vps-hostinger "sed -i 's/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=<nova_chave>/' /var/www/finup/app_dev/backend/.env"
# Reiniciar backend no servidor após mudança
```

**⚠️ Consequência:** trocar JWT_SECRET_KEY em produção invalida todos os tokens ativos. Usuários serão deslogados e precisarão fazer login novamente. Executar em horário de baixo tráfego.

---

### Tarefa 3.5 — Corrigir `DEBUG` no `.env` de dev

**Arquivo:** `app_dev/backend/.env`

```bash
# DE:
DEBUG=false

# PARA:
DEBUG=true
```

**Efeito:** habilita `/docs` e `/redoc` localmente para inspeção da API.  
**Em produção:** manter `DEBUG=false` (já correto no servidor).

---

### Tarefa 3.6 — Verificar `docker-compose.yml` no `.gitignore`

```bash
# Verificar se contém credenciais:
grep -E "password|secret|key" docker-compose.yml | grep -v "#"

# Se contiver credenciais hardcoded, verificar se está no .gitignore:
cat .gitignore | grep docker-compose

# Se não estiver e tiver credenciais → adicionar ao .gitignore
# (ou usar variáveis de ambiente no compose com arquivo .env separado)
```

---

### Validação Sprint 3

```bash
# 1. Verificar que localStorage está limpo após login
# - Login no app
# - DevTools → Application → Local Storage → localhost:3000
# - NÃO deve existir: authToken, access_token, token

# 2. Verificar que cookie httpOnly está presente
# - DevTools → Application → Cookies → localhost:3000
# - Deve existir: auth_token (HttpOnly ✅, SameSite: Strict ✅)

# 3. Testar fluxo completo
# - Login → navegar dashboard → transactions → upload → logout
# - Todas as páginas devem carregar dados normalmente

# 4. Testar expiração de sessão
# - Aguardar 1h ou deletar manualmente o cookie
# - Deve redirecionar para /auth/login automaticamente

# 5. Buscar localStorage remanescente no frontend:
grep -r "localStorage" app_dev/frontend/src \
  --include="*.ts" --include="*.tsx" \
  | grep -v "__tests__" \
  | grep -v "// "
# Deve retornar vazio ou apenas comentários
```

---

## Checklist de conclusão por sprint

### ✅ Sprint 1 concluído quando:
- [ ] `curl -I http://localhost:8000/api/health` retorna `X-Frame-Options: DENY`
- [ ] `curl -I http://localhost:8000/api/health` retorna `X-Content-Type-Options: nosniff`
- [ ] CORS não inclui `*` em métodos ou headers (verificar com DevTools → Network → preflight)
- [ ] `docker-compose logs backend` não mostra `print()` durante uso normal
- [ ] 6ª chamada a `change-password` retorna `429`
- [ ] Login, logout e navegação funcionam normalmente

### ✅ Sprint 2 concluído quando:
- [ ] `grep -r "console\.log" src/app src/features src/components | grep -v "// \|__tests__"` retorna vazio
- [ ] Console do browser está limpo ao navegar em dashboard, upload e investimentos
- [ ] `logger.ts` criado em `src/lib/logger.ts`
- [ ] Build de produção (`npm run build`) passa sem erros

### ✅ Sprint 3 concluído quando:
- [ ] `localStorage.getItem('authToken')` retorna `null` em qualquer página do app
- [ ] Cookie `auth_token` presente com `HttpOnly: true` e `SameSite: Strict`
- [ ] `use-token.ts` removido (ou todos os seus usos migrados para `AuthContext`)
- [ ] `lib/api-client.ts` (duplicata) removido
- [ ] JWT_SECRET_KEY de dev ≠ prod (verificado via SSH)
- [ ] `DEBUG=true` no `.env` local, `DEBUG=false` no servidor
- [ ] Fluxo completo de autenticação testado sem regressão

---

## Matriz de risco

| Tarefa | Probabilidade de quebra | O que pode quebrar | Mitigação |
|--------|------------------------|-------------------|-----------|
| 1.1 Security Headers | Muito baixa | Nenhuma | Testar com curl |
| 1.2 CORS | Baixa | Upload de arquivo (multipart) | Testar upload após mudança |
| 1.3 print → logging | Muito baixa | Nenhuma | Verificar `logger` importado |
| 1.4 Rate limit pwd | Muito baixa | Nenhuma | Testar com loop de curl |
| 2.1/2.2 Logger | Muito baixa | Nenhuma | Build + DevTools |
| 3.1 localStorage | **Alta** | Login, sessão, redirect | Testar fluxo completo |
| 3.2 use-token.ts | Média | Componentes que usam hook | Grep de importadores primeiro |
| 3.3 api-client.ts | Média | Páginas que usam lib duplicada | Grep antes de deletar |
| 3.4 JWT prod | Média | Sessões ativas (logout forçado) | Executar fora do horário de pico |

---

## Ordem de execução recomendada

```
Dia 1 (Sprint 1 — ~1h):
  1. git checkout -b fix/security-sprint1
  2. Editar main.py (1.1 + 1.2 juntos — mesmo arquivo)
  3. Editar transactions/service.py (1.3)
  4. Editar auth/router.py (1.4)
  5. docker-compose restart backend
  6. Validar com curl
  7. git commit -m "security: security headers, CORS restriction, logging, rate limit"

Dia 2 (Sprint 2 — ~1h 15min):
  1. git checkout -b fix/security-sprint2
  2. Criar src/lib/logger.ts (2.1)
  3. Substituir console.log em todos os arquivos (2.2) — usar sed ou Find & Replace no VS Code
  4. npm run build (validar)
  5. Testar no browser (DevTools Console)
  6. git commit -m "security: replace console.log with conditional logger"

Dia 3 (Sprint 3 — ~2h 30min):
  1. git checkout -b fix/security-sprint3
  2. Grep de importadores de use-token e lib/api-client antes de mexer
  3. Editar core/utils/api-client.ts (3.1)
  4. Migrar/remover use-token.ts (3.2)
  5. Limpar localStorage em app-sidebar e profile/page (3.3)
  6. Deletar lib/api-client.ts se sem importadores (3.3)
  7. Testar fluxo de login/logout/navegação completo
  8. SSH: verificar JWT_SECRET_KEY (3.4)
  9. Ajustar DEBUG no .env local (3.5)
  10. Verificar docker-compose.yml (3.6)
  11. git commit -m "security: remove token from localStorage, clean up auth"
  12. PR + merge após validação
```

---

## Referências

- Auditoria original: [AUDITORIA_SEGURANCA.md](./AUDITORIA_SEGURANCA.md)
- OWASP Top 10 2021 — A02 Cryptographic Failures, A05 Security Misconfiguration
- MDN: [Set-Cookie HttpOnly](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#httponly)
- FastAPI: [Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- Next.js: [environment variables](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables)
