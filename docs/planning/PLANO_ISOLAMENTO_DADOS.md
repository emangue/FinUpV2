# 🚨 PLANO DE ISOLAMENTO DE DADOS - MULTI-TENANCY

**Data:** 20 de janeiro de 2026  
**Status:** 🔴 CRÍTICO - Dados não isolados corretamente  
**Prioridade:** P0 (Bloqueador)

---

## 📋 PROBLEMA IDENTIFICADO

### Sintoma
Usuário `teste@email.com` (user_id=4) vê dados do usuário `admin` (user_id=1) em investimentos:
- Ativos: R$ 235.413,03 (deveria ser ~R$ 23k-70k)
- Passivos: -R$ 98.512,57
- Patrimônio: R$ 136.900,46
- 15 produtos (deveria ter 313 produtos com valores menores)

### Causa Raiz
**Frontend NÃO está enviando token JWT** no header `Authorization: Bearer <token>`

Fluxo atual:
```
Frontend (teste) → Backend (sem token) → get_current_user_id_optional() 
→ fallback user_id=1 → Retorna dados do admin
```

Fluxo esperado:
```
Frontend (teste) → Backend (com token) → get_current_user_id_optional() 
→ extrai user_id=4 do token → Retorna dados do teste
```

---

## ✅ O QUE JÁ ESTÁ CORRETO

### Backend - Isolamento Implementado Corretamente

**Todos os domínios têm filtro por user_id:**

1. ✅ **investimentos/** - Portfolio, cenários, histórico, planejamento
   - `InvestimentoRepository.get_portfolio_resumo(user_id)` ✅
   - `InvestimentoRepository.list_all(user_id)` ✅
   - Todos os endpoints filtram por `user_id` ✅

2. ✅ **transactions/** - Lançamentos financeiros
   - `JournalEntry.user_id == user_id` em todas as queries ✅

3. ✅ **budget/** - Orçamentos e categorias
   - `BudgetService.get_categorias_config(user_id)` ✅

4. ✅ **cards/** - Cartões
   - Filtro por `user_id` implementado ✅

5. ✅ **upload/** - Upload de arquivos
   - Associa `user_id` ao processar ✅

**Arquitetura de Dependências:**
```python
# app/shared/dependencies.py
def get_current_user_id_optional(authorization: Optional[str] = Header(None)) -> int:
    if not authorization:
        return 1  # ❌ FALLBACK PERIGOSO (mas necessário para transição)
    
    token = authorization.replace("Bearer ", "")
    user_id = extract_user_id_from_token(token)
    return user_id if user_id else 1
```

---

## ❌ O QUE ESTÁ QUEBRADO

### Frontend - Token JWT NÃO é Enviado

**Problema 1: Configuração de API**
```typescript
// app_dev/frontend/src/core/config/api.config.ts
export const API_CONFIG = {
  BACKEND_URL: 'http://localhost:8000',
  API_PREFIX: '/api/v1',
}

// ❌ FALTA: Configuração de headers padrão com token
```

**Problema 2: Fetch sem Autenticação**
```typescript
// Todas as chamadas de API fazem:
const response = await fetch(API_ENDPOINTS.INVESTIMENTOS.RESUMO)

// ❌ DEVERIA ser:
const token = getToken()
const response = await fetch(API_ENDPOINTS.INVESTIMENTOS.RESUMO, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

**Problema 3: AuthContext não expõe token**
```typescript
// app_dev/frontend/src/contexts/AuthContext.tsx
export const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  loading: true,
  login: async () => {},
  logout: () => {},
  // ❌ FALTA: token: string | null
})
```

---

## 🎯 PLANO DE AÇÃO - 3 FASES

### FASE 1: FIX URGENTE - Envio de Token (2-3 horas)

**Objetivo:** Fazer frontend enviar token JWT em TODAS as requisições

#### 1.1. Criar Utility de API com Auth
```typescript
// app_dev/frontend/src/core/utils/api-client.ts
export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('authToken')
  
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
}
```

#### 1.2. Atualizar AuthContext
```typescript
// Adicionar token ao contexto
const [token, setToken] = useState<string | null>(null)

const login = async (email: string, password: string) => {
  const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: email, password }),
  })
  
  const data = await response.json()
  localStorage.setItem('authToken', data.access_token)  // ✅ Salvar token
  setToken(data.access_token)
  setUser(data.user)
}
```

#### 1.3. Substituir fetch() por fetchWithAuth()
```bash
# Buscar todos os fetch() no código
grep -r "fetch(" app_dev/frontend/src --include="*.ts" --include="*.tsx" | wc -l
# Substituir por fetchWithAuth()
```

**Arquivos prioritários (investimentos):**
- `app_dev/frontend/src/features/investments/**/*.tsx`
- `app_dev/frontend/src/app/investimentos/**/*.tsx`

#### 1.4. Testar
```bash
# Login como teste
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "teste@email.com", "password": "teste123"}'

# Copiar token e testar resumo
curl http://localhost:8000/api/v1/investimentos/resumo \
  -H "Authorization: Bearer <TOKEN>"

# Deve retornar dados do teste (valores menores)
```

---

### FASE 2: AUDITORIA COMPLETA - Todos os Domínios (1 dia)

**Objetivo:** Garantir 100% de isolamento em todos os endpoints

#### 2.1. Auditoria de Routers
```bash
# Verificar todos os routers que NÃO usam user_id
cd app_dev/backend/app/domains
grep -r "@router" . | grep -v "user_id" | grep -v "__pycache__"
```

#### 2.2. Auditoria de Repositories
```bash
# Verificar queries que não filtram por user_id
grep -r "def get_" app/domains/*/repository.py | grep -v "user_id"
grep -r "def list_" app/domains/*/repository.py | grep -v "user_id"
```

#### 2.3. Criar Script de Validação
```python
# scripts/validate_user_isolation.py
"""
Testa se cada endpoint retorna dados APENAS do usuário autenticado
"""
import requests

def test_user_isolation():
    # Login como user 1
    token1 = login("admin@email.com", "admin123")
    data1 = fetch_investimentos(token1)
    
    # Login como user 4
    token4 = login("teste@email.com", "teste123")
    data4 = fetch_investimentos(token4)
    
    # Validar que são diferentes
    assert data1 != data4, "❌ Usuários vendo mesmos dados!"
    assert data4['total_investido'] < data1['total_investido'], "❌ Valores não randomizados!"
```

#### 2.4. Documentar Endpoints Auditados
```markdown
# RELATORIO_AUDITORIA_ISOLAMENTO.md

## Endpoints Validados
- [x] /api/v1/investimentos/resumo - ✅ Isolado
- [x] /api/v1/transactions/list - ✅ Isolado
- [x] /api/v1/budget/categorias - ✅ Isolado
...
```

---

### FASE 3: HARDENING - Segurança Reforçada (🚨 OBRIGATÓRIA - 1-2 dias)

**Objetivo:** **ELIMINAR COMPLETAMENTE** fallback para user_id=1 e tornar autenticação **OBRIGATÓRIA**

**⚠️ DECISÃO CRÍTICA DO USUÁRIO:**
> "não quero mais que o BAU seja ver os dados do admin"

**Sem token = Sem acesso** (401 Unauthorized)

#### 3.1. REMOVER get_current_user_id_optional COMPLETAMENTE

**ANTES (opcional, perigoso):**
```python
@router.get("/resumo")
def get_resumo(
    user_id: int = Depends(get_current_user_id_optional)  # ❌ Fallback para 1
):
    return service.get_resumo(user_id)
```

**DEPOIS (obrigatório, seguro):**
```python
@router.get("/resumo")
def get_resumo(
    user_id: int = Depends(get_current_user_from_jwt)  # ✅ Token OBRIGATÓRIO
):
    return service.get_resumo(user_id)
```

**Substituir em TODOS os 15 domínios:**
```bash
# Buscar todos os usos de get_current_user_id_optional
grep -r "get_current_user_id_optional" app_dev/backend/app/domains/

# Substituir por get_current_user_from_jwt
# Total estimado: ~50-100 endpoints
```

#### 3.2. DEPRECAR get_current_user_id_optional (Marcar como obsoleto)

```python
# app/shared/dependencies.py
@deprecated("Use get_current_user_from_jwt. Fallback será removido em breve.")
def get_current_user_id_optional(
    authorization: Optional[str] = Header(None)
) -> int:
    """
    ⚠️ DEPRECADO - NÃO USAR EM NOVOS ENDPOINTS
    
    Esta função será REMOVIDA após migração completa.
    Use get_current_user_from_jwt() para novos endpoints.
    """
    raise DeprecationWarning(
        "get_current_user_id_optional está obsoleto. "
        "Use get_current_user_from_jwt para autenticação obrigatória."
    )
```

#### 3.3. REMOVER COMPLETAMENTE get_current_user_id_optional

Após validar que todos os endpoints foram migrados:

```bash
# 1. Verificar que nenhum endpoint usa mais
grep -r "get_current_user_id_optional" app_dev/backend/app/domains/
# Resultado esperado: 0 matches

# 2. Deletar função
# Remover do app/shared/dependencies.py
```

#### 3.4. Adicionar Middleware de Logging
```python
# app/core/middleware/auth_logger.py
@app.middleware("http")
async def log_auth_requests(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    user_id = extract_user_id_from_token(auth_header) if auth_header else None
    
    logger.info(f"{request.method} {request.url.path} - user_id={user_id}")
    
    response = await call_next(request)
    return response
```

#### 3.5. Criar Testes de Segurança

```python
# tests/security/test_user_isolation.py
def test_cannot_access_other_user_data():
    """Usuário 4 não pode ver dados do usuário 1"""
    token_user4 = login("teste@email.com")
    
    # Tentar acessar investimento do user 1
    response = requests.get(
        "http://localhost:8000/api/v1/investimentos/1",  # ID do admin
        headers={"Authorization": f"Bearer {token_user4}"}
    )
    
    assert response.status_code == 404, "❌ Usuário consegue ver dados de outro!"

def test_no_token_returns_401():
    """🚨 CRÍTICO: Sem token = 401 Unauthorized"""
    response = requests.get("http://localhost:8000/api/v1/investimentos/resumo")
    
    assert response.status_code == 401, "❌ Endpoint aceita request sem token!"
    assert "Token" in response.json()["detail"], "❌ Mensagem de erro incorreta!"

def test_invalid_token_returns_401():
    Fallback para user_id=1 existe (RISCO DE SEGURANÇA)
- ❌ 0% de isolamento em produção

### Depois (Meta - TODAS AS FASES)
- ✅ 100% dos requests com token JWT
- ✅ Cada usuário vê APENAS seus dados
- ✅ Valores corretos: R$ 23k-70k para teste (10-30% do admin)
- ✅ **SEM token = 401 Unauthorized (ZERO fallback)**
- ✅ **get_current_user_id_optional DELETADO**
- ✅ Testes automatizados passando
- ✅ Auditoria completa documentada
- ✅ **BAU (Business As Usual) = Autenticação obrigatória**

#### 3.6. Validação Final - Garantir Zero Fallback

```bash
# Script de validação final
python scripts/validate_no_fallback.py

# Valida:
# 1. Nenhum endpoint usa get_current_user_id_optional
# 2. Todos os endpoints retornam 401 sem token
# 3. Função get_current_user_id_optional foi deletada
# 4. Todos os testes de segurança passam
```

**Output esperado:**
```
🔍 Validando eliminação de fallback...

✅ get_current_user_id_optional não encontrado no código
✅ 100% dos endpoints retornam 401 sem token
✅ 0 requests com fallback para user_id=1
✅ Todos os testes de segurança passando

🎉 VALIDAÇÃO COMPLETA: Zero fallback, autenticação obrigatória!
```

---

## 📊 MÉTRICAS DE SUCESSO

### Antes (Atual)
- ❌ Frontend não envia token
- ❌ Usuário teste vê dados do admin
- ❌ Valores na tela: R$ 235k (admin) em vez de ~R$ 23k-70k (teste)
- ❌ 0% de isolamento em produção

### Depois (Meta)
- ✅ 100% dos requests com token JWT
- ✅ Cada usuário vê APENAS seus dados
- ✅ Valores corretos: R$ 23k-70k para teste (10-30% do admin)
- ✅ Testes automatizados passando
- ✅ Auditoria completa documentada

---

## ⚠️ RISCOS E 
- FASE 1: Frontend passa a enviar token (preparação)
- FASE 2: Validar que todos os fluxos funcionam com token
- FASE 3: Remover fallback (breaking change controlado)
- **Comunicar mudança antes de FASE 3 ser executada**

### Risco 2: Performance
**Problema:** Validar JWT em cada request adiciona latência  
**Mitigação:** 
- Cachear user_id extraído por 5min (evita decode repetido)
- Validar apenas assinatura (rápido)
- Monitorar latência antes/depois

### Risco 3: Token Expiration
**Problema:** Token expira, usuário é deslogado  
**Mitigação:** 
- Implementar refresh token (exp: 7 dias)
- Renovação automática em background
- Interceptor no frontend para renovar antes de expirar

### ⚠️ Risco 4: Fallback Acidental
**Problema:** Alguém reintroduz fallback no futuro  
**Mitigação:**
- ✅ Adicionar lint rule proibindo `get_current_user_id_optional`
- ✅ Testes de segurança em CI/CD (falham se aceitar request sem token)
- ✅ Documentar em `.github/copilot-instructions.md`: "NUNCA usar fallback"
- ✅ Code review obrigatório para mudanças em `dependencies.py`tura

### Risco 3: Token Expiration
**Problema:*🚨 OBRIGATÓRIA - Eliminar Fallback)
- [ ] Deprecar `get_current_user_id_optional` (marcar como obsoleto)
- [ ] Substituir ALL 50-100 endpoints: `get_current_user_id_optional` → `get_current_user_from_jwt`
- [ ] **DELETAR** `get_current_user_id_optional` do código
- [ ] Validar que 0 endpoints aceitam request sem token
- [ ] Adicionar middleware de logging
- [ ] Criar testes de segurança (`tests/security/test_no_fallback.py`)
- [ ] Executar `validate_no_fallback.py` e garantir 100% sucesso
- [ ] Adicionar lint rule proibindo `get_current_user_id_optional`
- [ ] Documentar em `.github/copilot-instructions.md`: **"PROIBIDO usar fallback"**
- [ ] Atualizar `CONTRIBUTING.md` com guidelines de autenticação obrigatória
- [ ] **Confirmação final:** Testar que sem token = 401 em TODOS os endpoints

### FASE 1 (Urgente)
- [ ] Criar `api-client.ts` com `fetchWithAuth()`
- [ ] Atualizar `AuthContext` para expor token
- [ ] Salvar token no `localStorage` após login
- [ ] Substituir `fetch()` por `fetchWithAuth()` em investimentos
- [ ] Testar com curl que dados são diferentes por usuário
- [ ] Testar no browser que teste vê valores corretos

### FASE 2 (Importante)
- [ ] Auditar todos os 15 domínios
- [ ] Criar `scripts/validate_user_isolation.py`
- [ ] Executar validação e documentar resultados
- [ ] Corrigir endpoints que não filtram por `user_id`
- [ ] Criar `RELATORIO_AUDITORIA_ISOLAMENTO.md`

### FASE 3 (Reforço)
- [ ] Substituir `get_current_user_id_optional` → `get_current_user_from_jwt`
- [ ] Adicionar middleware de logging
- [ ] Criar testes de segurança (`tests/security/`)
- [ ] Documentar novos padrões em `.github/copilot-instructions.md`
- [ ] Atualizar `CONTRIBUTING.md` com guidelines de autenticação

---

## 🎯 PRÓXIMO PASSO IMEDIATO

**COMEÇAR PELA FASE 1 - Item 1.1:**

```bash
# Criar utility de API com auth
touch app_dev/frontend/src/core/utils/api-client.ts
```

**Conteúdo inicial:**
```typescript
// app_dev/frontend/src/core/utils/api-client.ts
/**
 * Cliente HTTP com autenticação JWT automática
 * Adiciona header Authorization em todas as requests
 */

export async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = localStorage.getItem('authToken')
  
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
}

export async function fetchJsonWithAuth<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetchWithAuth(url, options)
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
## 🎯 DECISÃO CRÍTICA TOMADA

**Requisito do usuário confirmado:**
> "você pode no final das fases tirar o fallback? não quero mais que o BAU seja ver os dados do admin"

**Resposta:** ✅ **SIM**

**Compromisso:**
- FASE 3 é **OBRIGATÓRIA** (não opcional)
- `get_current_user_id_optional` será **DELETADO**
- Sem token = **401 Unauthorized** (sem exceções)
- BAU (Business As Usual) = **Autenticação obrigatória**

**Impacto:**
- ✅ **Segurança maximizada** (zero vazamento de dados)
- ✅ **Multi-tenancy real** (cada usuário isolado)
- ⚠️ **Breaking change** (código que não envia token quebra)

**Validação final obrigatória:**
```bash
# NENHUM destes comandos pode funcionar sem token:
curl http://localhost:8000/api/v1/investimentos/resumo
# Esperado: {"detail": "Token de autenticação não fornecido"} (401)

curl http://localhost:8000/api/v1/transactions/list
# Esperado: {"detail": "Token de autenticação não fornecido"} (401)

# etc... (todos os endpoints)
```

---

**Documento criado:** 2026-01-20  
**Última atualização:** 2026-01-20 (Decisão de remover fallback confirmada)  
**Status:** 🔴 AGUARDANDO EXECUÇÃO FASE 1  
**Decisão:** 🚨 FASE 3 É OBRIGATÓRIA - Zero fallback após conclusão
```

**Executar:**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
# Criar arquivo
# Atualizar AuthContext
# Substituir fetch() em investimentos
# Testar!
```

---

## 📚 REFERÊNCIAS

- [FastAPI Security - OAuth2 JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Next.js Authentication Best Practices](https://nextjs.org/docs/authentication)
- [OWASP - Multi-Tenancy Security](https://owasp.org/www-project-multitenant-application-security/)

---

**Documento criado:** 2026-01-20  
**Última atualização:** 2026-01-20  
**Status:** 🔴 AGUARDANDO EXECUÇÃO FASE 1
