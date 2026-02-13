# 🔐 Plano de Segurança e Limpeza de Código

**Data:** 09/02/2026  
**Versão:** 1.0  
**Status:** 📋 Planejamento Completo - Aguardando Execução

---

## 📊 Resumo Executivo

Auditoria identificou **3 áreas críticas** que precisam de atenção imediata:

| Área | Problemas Encontrados | Severidade | Tempo Estimado |
|------|----------------------|------------|----------------|
| 🔴 **Segurança** | 15 vulnerabilidades (5 críticas, 6 médias, 4 baixas) | ALTA | 6-10h |
| 🧹 **Debug Logs** | 250+ console.log/print() poluindo código | MÉDIA | 2-4h |
| ❌ **Erros Build** | 19 erros TypeScript (pastas vermelhas) | MÉDIA | 4-6h |

**Tempo Total Estimado:** 12-20 horas  
**Prioridade:** 🔴 Iniciar HOJE com Fase 1 (2-4h)

---

## 🎯 Objetivos

1. **Eliminar vulnerabilidades críticas de segurança** (hardcoded secrets, token exposure)
2. **Remover 250+ debug logs** que poluem o código e expõem dados sensíveis
3. **Corrigir 19 erros TypeScript** que causam pastas vermelhas no VS Code
4. **Estabelecer padrões de segurança** para desenvolvimento futuro

---

## 🔴 FASE 1: VULNERABILIDADES CRÍTICAS (FAZER HOJE)

**Tempo:** 2-4 horas  
**Prioridade:** 🔴 URGENTE - Risco de invasão

### 1.1 Corrigir JWT Secret Hardcoded ⚠️ CRÍTICO

**Problema:** `app_dev/backend/app/core/config.py:53`
```python
JWT_SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
```

**Risco:** Atacante pode forjar tokens JWT e se passar por qualquer usuário.

**Solução:**

**Passo 1:** Gerar secret seguro
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
python3 -c "import secrets; print(secrets.token_hex(32))" > .jwt_secret_temp
cat .jwt_secret_temp
```

**Passo 2:** Adicionar ao `.env` (NUNCA commitar)
```bash
# app_dev/backend/.env
JWT_SECRET_KEY=<colar_valor_gerado_acima>
DEBUG=false
```

**Passo 3:** Modificar `config.py`
```python
# ANTES (INSEGURO):
JWT_SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
DEBUG: bool = True

# DEPOIS (SEGURO):
JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")  # Obriga ter no .env
DEBUG: bool = Field(default=False, env="DEBUG")
```

**Passo 4:** Validar que `.env` está no `.gitignore`
```bash
grep -E "^\.env$|^\.env\.\*$" .gitignore
# Deve retornar: .env
```

**✅ Critério de sucesso:**
- Backend NÃO inicia sem `JWT_SECRET_KEY` no `.env`
- Comando `git status` NÃO mostra arquivo `.env`

---

### 1.2 Remover Tokens dos Console Logs ⚠️ ALTO

**Problema:** Tokens JWT visíveis no console do browser (F12 DevTools)

**Arquivos afetados:**
1. `app_dev/frontend/src/core/contexts/auth-context.tsx` (linhas 73-88)
2. `app_dev/frontend/src/core/utils/api-client.ts` (linhas 31-46)
3. `app_dev/frontend/src/app/mobile/profile/page.tsx` (linha 65-66)

**Passo 1:** Remover logs de autenticação
```typescript
// DELETAR estas linhas em auth-context.tsx (73-88):
console.log('[AuthContext] Login bem-sucedido:', {
  tokenPreview: `${access_token.substring(0, 20)}...`,
  userId: userData.id,
  userEmail: userData.email,
})

// DELETAR estas linhas em api-client.ts (31-46):
console.log('🔑 Token (primeiros 20 chars):', token ? token.substring(0, 20) + '...' : 'NENHUM')
```

**Passo 2:** Substituir por logging seguro (opcional)
```typescript
// Apenas em DEVELOPMENT, sem dados sensíveis
if (process.env.NODE_ENV === 'development') {
  console.log('[AUTH] Login successful')  // Sem token, sem email
}
```

**✅ Critério de sucesso:**
- Abrir DevTools (F12) → Console
- Fazer login
- NÃO deve aparecer token, email ou userId

---

### 1.3 Adicionar Rate Limiting no Login ⚠️ MÉDIO

**Problema:** Endpoint `/login` aceita tentativas ilimitadas (brute-force)

**Passo 1:** Abrir `app_dev/backend/app/domains/auth/router.py`

**Passo 2:** Adicionar rate limit
```python
# ANTES:
@router.post("/login")
def login(request: Request, ...):

# DEPOIS:
from slowapi import Limiter
from slowapi.util import get_remote_address

@router.post("/login")
@limiter.limit("5/minute")  # Apenas 5 tentativas por minuto
def login(request: Request, ...):
```

**Passo 3:** Reiniciar backend
```bash
./scripts/deploy/quick_stop.sh && sleep 2 && ./scripts/deploy/quick_start.sh
```

**✅ Critério de sucesso:**
- Tentar login errado 6 vezes em 1 minuto
- 6ª tentativa deve retornar HTTP 429 (Too Many Requests)

---

### 1.4 Proteger Rotas Admin (Backend + Frontend) ⚠️ MÉDIO

**Problema:** Endpoints de configuração sem verificar se é admin + Telas admin acessíveis para todos

**Solução em 2 camadas:**

#### Backend: Bloquear API

**Passo 1:** Criar dependency `require_admin`
```python
# app_dev/backend/app/shared/dependencies.py

from fastapi import HTTPException, Depends
from app.domains.users.models import User
from app.domains.auth.jwt_utils import get_current_user

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verifica se usuário é admin."""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas administradores."
        )
    return current_user
```

**Passo 2:** Aplicar nos endpoints admin
```python
# ANTES:
@router.post("/screens")
def update_screens(user_id: int = Depends(get_current_user_id)):

# DEPOIS:
from app.shared.dependencies import require_admin

@router.post("/screens")
def update_screens(admin: User = Depends(require_admin)):
    # Agora só admin consegue executar
```

#### Frontend: Esconder/Bloquear Rotas

**Passo 3:** Criar componente de proteção admin
```typescript
// app_dev/frontend/src/core/components/require-admin.tsx

'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/core/contexts/auth-context'

export function RequireAdmin({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  
  useEffect(() => {
    if (!isLoading && (!user || user.role !== 'admin')) {
      // Redireciona para 404 (usuário nem sabe que rota existe)
      router.push('/404')
    }
  }, [user, isLoading, router])
  
  // Não renderiza nada para não-admins
  if (!user || user.role !== 'admin') {
    return null
  }
  
  return <>{children}</>
}
```

**Passo 4:** Aplicar em rotas admin
```typescript
// app_dev/frontend/src/app/admin/screens/page.tsx

import { RequireAdmin } from '@/core/components/require-admin'

export default function AdminScreensPage() {
  return (
    <RequireAdmin>
      {/* Conteúdo admin só renderiza se for admin */}
      <div>Gestão de Telas (Admin Only)</div>
    </RequireAdmin>
  )
}
```

**Passo 5:** Esconder links admin no sidebar
```typescript
// app_dev/frontend/src/components/app-sidebar.tsx

const { user } = useAuth()

// Condicional: só mostra links admin se for admin
{user?.role === 'admin' && (
  <NavSection title="Administração">
    <NavItem icon={Settings} label="Gestão de Telas" href="/admin/screens" />
    <NavItem icon={Users} label="Usuários" href="/admin/users" />
  </NavSection>
)}
```

**✅ Critérios de sucesso:**
- ✅ **Backend:** Logar com user comum → POST /api/v1/screens → 403 Forbidden
- ✅ **Frontend:** User comum não vê links admin no sidebar
- ✅ **Frontend:** User comum tenta acessar `/admin/screens` → 404 Not Found
- ✅ **Frontend:** Admin vê links e consegue acessar normalmente

---

## 🟠 FASE 2: LIMPEZA DE DEBUG LOGS (FAZER ESTA SEMANA)

**Tempo:** 2-4 horas  
**Prioridade:** 🟠 ALTA - Poluição de código

### 2.1 Estatísticas Encontradas

| Tipo | Quantidade | Arquivos |
|------|-----------|----------|
| `console.log` | 200+ | 89 arquivos |
| `console.error` | 50+ | 45 arquivos |
| `console.warn` | 5 | 4 arquivos |
| `print()` (Python) | 73 | 10 arquivos |

### 2.2 Top 10 Arquivos Mais Poluídos

1. **auth-context.tsx** - 9 logs
2. **use-edit-goal.ts** - 10 logs
3. **upload/preview/[sessionId]/page.tsx** - 10 logs
4. **mobile/preview/[sessionId]/page.tsx** - 4 logs
5. **api-client.ts** - 7 logs
6. **use-goals.ts** - 5 logs
7. **use-goal-detail.ts** - 6 logs
8. **use-upload.ts** - 15 logs
9. **use-dashboard.ts** - 6 logs
10. **EditGoalModal.tsx** - 6 logs

### 2.3 Estratégia de Remoção

#### ✅ ESTRATÉGIA ESCOLHIDA: Remoção Manual (Segura e Controlada)

**Por quê manual?**
- ✅ Controle total sobre o que é removido
- ✅ Evita remover logs importantes por engano
- ✅ Permite melhorar código durante revisão
- ✅ Zero risco de quebrar funcionalidade

#### Opção B: Remoção Manual (RECOMENDADA)

**Processo Passo a Passo:**

**Passo 1:** Criar branch dedicada
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
git checkout -b cleanup/remove-debug-logs-manual
```

**Passo 2:** Abrir cada arquivo dos Top 10 (ordem de prioridade)

**Lista de trabalho:**
1. ✅ `auth-context.tsx` - 9 logs (CRÍTICO - tem tokens)
2. ✅ `api-client.ts` - 7 logs (CRÍTICO - tem tokens)
3. ✅ `use-edit-goal.ts` - 10 logs
4. ✅ `upload/preview/[sessionId]/page.tsx` - 10 logs
5. ✅ `mobile/preview/[sessionId]/page.tsx` - 4 logs
6. ✅ `use-upload.ts` - 15 logs
7. ✅ `EditGoalModal.tsx` - 6 logs
8. ✅ `use-goals.ts` - 5 logs
9. ✅ `use-goal-detail.ts` - 6 logs
10. ✅ `use-dashboard.ts` - 6 logs

**Passo 3:** Aplicar regras de remoção

**Regras de Classificação:**

| Tipo de Log | Ação | Exemplo |
|-------------|------|---------|
| 🔴 **Debug de dados** | DELETAR | `console.log('Goals:', goals)` |
| 🔴 **State tracking** | DELETAR | `console.log('FormData atualizado:', data)` |
| 🔴 **Token/credentials** | DELETAR | `console.log('Token:', token.substring(0,20))` |
| 🔴 **API responses** | DELETAR | `console.log('API response:', response)` |
| 🟡 **Error handling** | MANTER ou MELHORAR | `console.error('Erro:', error)` → usar wrapper |
| 🟡 **Warnings importantes** | MANTER | `console.warn('API deprecated')` |
| 🟢 **Production logs** | MANTER | `console.info('App initialized')` |

**Passo 4:** Para cada arquivo:

```typescript
// EXEMPLO: app_dev/frontend/src/core/contexts/auth-context.tsx

// ❌ REMOVER (linhas 73-88):
console.log('[AuthContext] Login bem-sucedido:', {
  tokenPreview: `${access_token.substring(0, 20)}...`,
  userId: userData.id,
  userEmail: userData.email,
})

// ❌ REMOVER (linha 95):
console.log('[AuthContext] Logout executado')

// ✅ MANTER (mas melhorar):
console.error('[AuthContext] Erro no login:', error)

// ⬇️ MELHORAR para:
if (process.env.NODE_ENV === 'development') {
  console.error('[AuthContext] Erro no login:', error)
} else {
  // TODO: Enviar para error tracking (Sentry)
}
```

**Passo 5:** Testar após cada arquivo
```bash
# Terminal 1: Backend rodando
./scripts/deploy/quick_start.sh

# Terminal 2: Testar funcionalidade
# - Fazer login
# - Criar meta
# - Upload arquivo
# - Navegar entre telas

# Verificar: Tudo funciona SEM os logs removidos
```

**Passo 6:** Commit incremental
```bash
git add app_dev/frontend/src/core/contexts/auth-context.tsx
git commit -m "cleanup: remove debug logs from auth-context (9 logs)"

git add app_dev/frontend/src/core/utils/api-client.ts
git commit -m "cleanup: remove token logs from api-client (7 logs)"

# ... continuar para cada arquivo
```

**Estimativa de Tempo:**
- 10 arquivos × 15 min cada = **2.5 horas**
- Testes entre arquivos = **0.5 hora**
- **TOTAL: 3 horas** (mais seguro que automático)

---

### 2.4 Logs que DEVEM ser mantidos (mas melhorados)

**Substituir `console.error` por serviço de tracking:**

```typescript
// ANTES:
console.error('Erro ao salvar meta:', error)

// DEPOIS (com Sentry ou similar):
import * as Sentry from '@sentry/nextjs'

Sentry.captureException(error, {
  tags: { feature: 'goals', action: 'save' }
})
```

**Ou, se não usar Sentry ainda:**
```typescript
// Wrapper para futuro migration
const logError = (message: string, error: unknown) => {
  if (process.env.NODE_ENV === 'production') {
    // TODO: Enviar para serviço de log (Sentry, LogRocket, etc)
    console.error(`[ERROR] ${message}`, error)
  } else {
    console.error(message, error)
  }
}

// Uso:
logError('Erro ao salvar meta', error)
```

---

## 🟡 FASE 3: CORRIGIR ERROS TYPESCRIPT (FAZER ESTA SEMANA)

**Tempo:** 4-6 horas  
**Prioridade:** 🟡 MÉDIA - Pastas vermelhas no VS Code

### 3.1 Resumo dos Erros

| Arquivo | Erros | Tipo | Severidade |
|---------|-------|------|------------|
| mobile/preview/[sessionId]/page.tsx | 2 | Missing property `occurrences` | Alta |
| features/goals/hooks/use-goal-detail.ts | 1 | Type mismatch | Alta |
| features/goals/components/EditGoalModal.tsx | 5 | Missing properties | Alta |
| features/goals/components/ManageGoalsListItem.tsx | 3 | Type mismatch number vs string | Média |
| mobile/budget/manage/page.tsx | 5 | Type mismatch | Média |
| mobile/budget/new/page.tsx | 1 | Invalid prop type | Baixa |
| mobile/budget/[goalId]/page.tsx | 2 | Invalid prop type | Baixa |

**Total:** 19 erros em 7 arquivos

---

### 3.2 Fix 1: Interface Goal Incompleta ⚠️ CRÍTICO

**Problema:** `Goal` interface faltam campos usados no código

**Arquivo:** `app_dev/frontend/src/features/goals/types/index.ts`

**Solução:**
```typescript
// ANTES (incompleto):
export interface Goal {
  id: number
  nome: string
  grupo: string
  valor_alvo: number
  ativo: boolean
}

// DEPOIS (completo):
export interface Goal {
  id: number
  nome: string
  grupo: string
  categoria?: string  // ✅ Adicionar
  valor_alvo: number
  valor_atual?: number  // ✅ Adicionar
  orcamento: number  // ✅ Adicionar
  valor_medio_3_meses?: number  // ✅ Adicionar
  mes_referencia: string  // ✅ Adicionar (YYYY-MM)
  prazo?: string  // ✅ Adicionar (YYYY-MM)
  ativo: boolean
  status?: 'on_track' | 'warning' | 'over_budget'  // ✅ Adicionar
  created_at?: string
  updated_at?: string
}
```

**Testar:**
```bash
cd app_dev/frontend
npm run type-check  # Deve reduzir erros de 19 para ~10
```

---

### 3.3 Fix 2: Transaction Missing `occurrences`

**Problema:** `mobile/preview/[sessionId]/page.tsx:131`
```typescript
.sort((a, b) => (b.occurrences || 0) - (a.occurrences || 0));
// Error: Property 'occurrences' does not exist
```

**Solução:**
```typescript
// Adicionar ao tipo Transaction (no mesmo arquivo ou em types/)
interface Transaction {
  id: string
  date: string
  description: string
  value: number
  grupo?: string
  subgrupo?: string
  origem?: string
  occurrences?: number  // ✅ Adicionar esta linha
}
```

---

### 3.4 Fix 3: Goal ID Type Mismatch (number vs string)

**Problema:** URL params retornam `string`, mas `Goal.id` é `number`

**Arquivos afetados:**
- `ManageGoalsListItem.tsx`
- `mobile/budget/manage/page.tsx`
- `mobile/budget/[goalId]/page.tsx`

**Solução 1: Converter ID para number ao buscar**
```typescript
// ANTES (erro):
const goal = goals.find((g) => g.id === goalId)  // goalId é string

// DEPOIS (correto):
const goal = goals.find((g) => g.id === parseInt(goalId, 10))
```

**Solução 2: Converter ao chamar funções**
```typescript
// ANTES (erro):
onToggle(goal.id, isActive)  // goal.id é number, onToggle espera string

// DEPOIS (correto):
onToggle(goal.id.toString(), isActive)
```

**OU mudar signature:**
```typescript
interface ManageGoalsListItemProps {
  onToggle: (goalId: number, isActive: boolean) => void  // Aceitar number
}
```

---

### 3.5 Fix 4: MobileHeader leftAction Type

**Problema:** `mobile/budget/[goalId]/page.tsx:75`
```typescript
leftAction={{
  icon: <ArrowLeft />,
  label: 'Voltar',
  onClick: () => router.back()
}}
// Error: Type not assignable to "back" | "logo" | null
```

**Solução:** Verificar definição do componente `MobileHeader`

**Opção A:** Se aceita apenas string literal:
```typescript
<MobileHeader 
  leftAction="back"  // ✅ String literal
  onLeftClick={() => router.back()}  // Callback separado
/>
```

**Opção B:** Se aceita objeto, corrigir tipos:
```typescript
// Em components/mobile/mobile-header.tsx
interface MobileHeaderProps {
  leftAction?: 
    | 'back' 
    | 'logo' 
    | { icon: ReactNode; label: string; onClick: () => void }  // ✅ Aceitar objeto
    | null
}
```

---

### 3.6 Checklist de Validação TypeScript

Após cada fix, executar:

```bash
cd app_dev/frontend

# 1. Type check
npm run type-check

# 2. Lint
npm run lint

# 3. Build (mais rigoroso)
npm run build

# 4. Contar erros restantes
npm run type-check 2>&1 | grep "error TS" | wc -l
```

**Meta:** 0 erros TypeScript

---

## 🟢 FASE 4: MELHORIAS DE SEGURANÇA LONG-TERM (BACKLOG)

**Tempo:** 8-12 horas  
**Prioridade:** 🟢 BAIXA - Fazer quando tiver tempo

### 4.1 Migrar JWT para httpOnly Cookies

**Problema atual:** Token em `localStorage` vulnerável a XSS

**Solução:**

**Backend** (`auth/router.py`):
```python
from fastapi import Response

@router.post("/login")
def login(response: Response, ...):
    # Gerar token
    access_token = create_access_token(...)
    
    # Definir cookie httpOnly (JS não consegue acessar)
    response.set_cookie(
        key="auth_token",
        value=access_token,
        httponly=True,  # ✅ Protege contra XSS
        secure=True,    # ✅ Apenas HTTPS
        samesite="strict",  # ✅ Protege contra CSRF
        max_age=86400  # 24 horas
    )
    
    return {"user": user_data}  # Token não vai no body
```

**Frontend** (remover localStorage):
```typescript
// ANTES:
localStorage.setItem('authToken', token)

// DEPOIS:
// Nada! Cookie é enviado automaticamente pelo browser
fetch('/api/endpoint')  // Cookie vai no header automaticamente
```

**Middleware** (ler do cookie):
```python
from fastapi import Cookie

async def get_current_user_id(
    auth_token: str = Cookie(None)  # Ler do cookie
) -> int:
    if not auth_token:
        raise HTTPException(status_code=401)
    # Validar token...
```

---

### 4.2 Implementar Security Headers

**Adicionar middleware** em `main.py`:

```python
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# 1. Force HTTPS em produção
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# 2. Content Security Policy
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Next.js precisa
        "style-src 'self' 'unsafe-inline';"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

### 4.3 Implementar Token Refresh

**Problema:** Token expira → usuário precisa fazer login novamente

**Solução:** Refresh tokens de longa duração

```python
# Gerar 2 tokens no login
access_token = create_access_token(data, expires_delta=timedelta(minutes=30))
refresh_token = create_refresh_token(data, expires_delta=timedelta(days=7))

# Endpoint para renovar- MANUAL (ESTA SEMANA)
- [ ] 2.1 - ✅ DECIDIDO: Remoção manual (mais segura)
- [ ] 2.2 - Criar branch cleanup/remove-debug-logs-manual
- [ ] 2.3 - Arquivo 1: auth-context.tsx (9 logs) + test + commit
- [ ] 2.4 - Arquivo 2: api-client.ts (7 logs) + test + commit
- [ ] 2.5 - Arquivo 3: use-edit-goal.ts (10 logs) + test + commit
- [ ] 2.6 - Arquivo 4: upload/preview/[sessionId]/page.tsx (10 logs) + test + commit
- [ ] 2.7 - Arquivo 5: mobile/preview/[sessionId]/page.tsx (4 logs) + test + commit
- [ ] 2.8 - Arquivo 6: use-upload.ts (15 logs) + test + commit
- [ ] 2.9 - Arquivo 7: EditGoalModal.tsx (6 logs) + test + commit
- [ ] 2.10 - Arquivo 8: use-goals.ts (5 logs) + test + commit
- [ ] 2.11 - Arquivo 9: use-goal-detail.ts (6 logs) + test + commit
- [ ] 2.12 - Arquivo 10: use-dashboard.ts (6 logs) + test + commit
- [ ] 2.13 - Converter console.error críticos para logError wrapper
- [ ] ✅ Testar: App funciona normalmente (todos fluxos)
- [ ] ✅ Testar: Console limpo (F12 DevTools sem logs)
- [ ] ✅ Testar: Erros ainda são capturados corretamenter
```typescript
// Interceptar 401 e tentar refresh automaticamente
if (response.status === 401) {
  const refreshed = await fetch('/api/auth/refresh', { method: 'POST' })
  if (refreshed.ok) {
    // Retry request original
    return fetch(originalUrl, originalOptions)
  }
}
```

---

### 4.4 Adicionar Input Validation Rigoroso

**Upload de arquivos:**
```python
from fastapi import UploadFile

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload")
async def upload(file: UploadFile):
    # 1. Validar tipo
    if file.content_type not in ['text/csv', 'application/vnd.ms-excel']:
        raise HTTPException(400, "Tipo de arquivo não permitido")
    
    # 2. Validar tamanho
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, f"Arquivo muito grande (max {MAX_FILE_SIZE/1024/1024}MB)")
    
    # 3. Validar nome (prevenir path traversal)
    import re
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '', file.filename)
    
    # 4. Escanear conteúdo (XSS em nomes de arquivos CSV)
    if '<script' in contents.decode('utf-8', errors='ignore').lower():
        raise HTTPException(400, "Conteúdo suspeito detectado")
```

---

## 📋 CHECKLIST DE EXECUÇÃO

### Fase 1: Segurança Crítica (HOJE) (backend)
- [ ] 1.4 - Aplicar require_admin nos endpoints de screen
- [ ] 1.4 - Criar componente RequireAdmin (frontend)
- [ ] 1.4 - Aplicar RequireAdmin em rotas admin
- [ ] 1.4 - Adicionar condicional no sidebar (esconder links admin)
- [ ] ✅ Testar: Backend exige JWT_SECRET_KEY
- [ ] ✅ Testar: Console não mostra tokens
- [ ] ✅ Testar: 6ª tentativa login retorna 429
- [ ] ✅ Testar: User comum não vê links admin no sidebar
- [ ] ✅ Testar: User comum acessa /admin/screens → 404
- [ ] ✅ Testar: User comum POST /screens → 403 Forbidden
- [ ] ✅ Testar: Admin consegue acessar tudo normalmente
- [ ] 1.2 - Remover console.log com tokens (profile/page.tsx)
- [ ] 1.3 - Adicionar rate limit 5/min no /login
- [ ] 1.4 - Criar dependency require_admin
- [ ] 1.4 - Aplicar require_admin nos endpoints de screen
- [ ] ✅ Testar: Backend exige JWT_SECRET_KEY
- [ ] ✅ Testar: Console não mostra tokens
- [ ] ✅ Testar: 6ª tentativa login retorna 429
- [ ] ✅ Testar: User comum não consegue POST /screens (403)

### Fase 2: Limpeza de Logs (ESTA SEMANA)
- [ ] 2.1 - Decidir: Remoção automática OU manual?
- [ ] 2.2 - Criar branch cleanup/remove-debug-logs
- [ ] 2.3 - Executar script de limpeza (se automático)
- [ ] 2.4 - Revisar diff completo
- [ ] 2.5 - Converter console.error críticos para logError wrapper
- [ ] ✅ Testar: App funciona normalmente
- [ ] ✅ Testar: Console limpo (sem logs de debug)
- [ ] ✅ Testar: Erros ainda são capturados

### Fase 3: Erros TypeScript (ESTA SEMANA)
- [ ] 3.1 - Atualizar interface Goal (9 campos novos)
- [ ] 3.2 - Adicionar occurrences? ao tipo Transaction
- [ ] 3.3 - Corrigir comparações de Goal.id (number vs string)
- [ ] 3.4 - Corrigir leftAction type no MobileHeader
- [ ] ✅ Testar: npm run type-check (0 erros)
- [ ] ✅ Testar: npm run build (sucesso)
- [ ] ✅ Testar: Pastas não aparecem vermelhas no VS Code

### Fase 4: Long-term (BACKLOG)
- [ ] 4.1 - Migrar JWT para httpOnly cookies
- [ ] 4.2 - Adicionar security headers middleware
- [ ] 4.3 - Implementar token refresh
- [ ] 4.4 - Adicionar input validation rigoroso

---

## 🚨 TROUBLESHOOTING

### Problema: Backend não inicia após mudar JWT_SECRET_KEY

**Erro:**
```
ValidationError: 1 validation error for Settings
JWT_SECRET_KEY
  field required
```

**Solução:**
```bash
# Verificar se .env existe
ls -la app_dev/backend/.env

# Se não existir, criar:
echo "JWT_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > app_dev/backend/.env
echo "DEBUG=false" >> app_dev/backend/.env
```

---

### Problema: Script de limpeza removeu logs importantes

**Solução:**
```bash
# Reverter mudanças
git checkout HEAD -- app_dev/frontend/src/path/to/file.tsx

# OU restaurar tudo
git checkout HEAD -- .
```

---

### Problema: TypeScript ainda mostra erros após fixes

**Solução:**
```bash
# Limpar cache do TypeScript
cd app_dev/frontend
rm -rf .next node_modules/.cache
npm run type-check

# Reiniciar VS Code
# Cmd+Shift+P → "Reload Window"
```

---

## 📊 MÉTRICAS DE SUCESSO

### Antes da Limpeza
- ❌ JWT secret hardcoded
- ❌ 15 vulnerabilidades de segurança
- ❌ 250+ console.log poluindo código
- ❌ 19 erros TypeScript
- ❌ Pastas vermelhas no VS Code
- ❌ Tokens visíveis no browser console

### Depois da Limpeza
- ✅ JWT secret em variável de ambiente
- ✅ 0 vulnerabilidades críticas
- ✅ <10 console.log (apenas essenciais)
- ✅ 0 erros TypeScript
- ✅ Todas as pastas verdes no VS Code
- ✅ Console limpo (sem dados sensíveis)

---

## 📚 REFERÊNCIAS

- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices (RFC 8725)](https://tools.ietf.org/html/rfc8725)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Next.js Security Headers](https://nextjs.org/docs/app/api-reference/next-config-js/headers)
- [TypeScript Strict Mode](https://www.typescriptlang.org/tsconfig#strict)

---

## 🎯 PRÓXIMOS PASSOS

1. **Ler este documento completamente** (15 min)
2. **Decidir prioridade:** Fazer tudo hoje? Ou dividir em 3 dias?
3. **Criar branch de trabalho:** `git checkout -b security/critical-fixes`
4. **Executar Fase 1** (2-4h)
5. **Commitar e fazer backup:** `git commit -am "security: fix critical vulnerabilities"`
6. **Validar que tudo funciona**
7. **Executar Fase 2 e 3** (6-10h)

---

**Última Atualização:** 09/02/2026  
**Responsável:** Emanuel  
**Status:** 📋 Documento criado - Aguardando início da execução
