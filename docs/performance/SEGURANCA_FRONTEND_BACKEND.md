# Segurança — Auditoria Completa Frontend + Backend

**Data:** 01/03/2026
**Escopo:** app_dev/frontend + app_dev/backend
**Filosofia:** proteger sem dificultar o desenvolvimento — cada fix tem esforço ≤ 30min e não adiciona fricção no dia a dia.

---

## Resumo Executivo

| Severidade | Qtd | Impacto principal |
|------------|-----|-------------------|
| Crítico | 4 | Dados vazando, servidor derrubável |
| Alto | 3 | Brute force, arquivo malicioso |
| Médio | 4 | Política de senhas, console, queries |
| Baixo | 3 | Headers, health check |

**Tempo total estimado para remediar tudo:** ~4-5h

---

## 1. Crítico

### 1.1 CORS com credenciais + wildcard — CSRF possível

**Arquivo:** `app_dev/backend/app/main.py`

```python
# PROBLEMA
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],   # ← aceita TRACE, CONNECT, qualquer método
    allow_headers=["*"],   # ← aceita qualquer header customizado
)
```

`allow_credentials=True` com `allow_methods=["*"]` e `allow_headers=["*"]` é a combinação mais perigosa possível em CORS. Permite CSRF: um site malicioso pode fazer requests autenticados em nome do usuário.

```python
# FIX — não tem impacto no desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)
```

**Esforço:** 5 min. Sem impacto no desenvolvimento.

---

### 1.2 Token JWT salvo em localStorage — roubável via XSS

**Arquivo:** `app_dev/frontend/src/features/auth/hooks/use-token.ts`

```typescript
// PROBLEMA
export function saveToken(token: string): void {
  localStorage.setItem('authToken', token)  // qualquer script na página lê isso
}
```

```typescript
// PROBLEMA também em api-client.ts
const token = localStorage.getItem('authToken')
```

localStorage é acessível por qualquer JavaScript na página. Se existir um XSS (injeção de script via dado do usuário), o atacante pega o token com uma linha: `localStorage.getItem('authToken')`.

O backend já configura `httpOnly cookie` — o token não precisa ficar no localStorage.

```typescript
// FIX — remover saveToken() e depender só do cookie httpOnly
// api-client.ts: retirar o localStorage.getItem, cookie é enviado automaticamente
// Se precisar saber se está logado no frontend, decodificar JWT apenas para expiração:

import { jwtDecode } from 'jwt-decode'

export function isTokenValid(token: string): boolean {
  try {
    const { exp } = jwtDecode<{ exp: number }>(token)
    return Date.now() < exp * 1000
  } catch {
    return false
  }
}
// Não armazenar o token — só verificar via cookie ou request ao backend
```

**Esforço:** 30 min. Requer ajuste coordenado frontend + backend (garantir que cookie está sendo setado corretamente).

---

### 1.3 Upload sem validação de tamanho — servidor derrubável

**Arquivo:** `app_dev/backend/app/domains/upload/router.py`

```python
# PROBLEMA — sem limite de tamanho
file_bytes = await file.read()  # alguém manda 10GB, servidor trava
```

```python
# FIX
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50MB

@router.post("/detect")
async def detect_arquivo(file: UploadFile = File(...), ...):
    file_bytes = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Arquivo muito grande. Máximo: 50MB")
```

Adicionar também em `settings.py`:
```python
MAX_UPLOAD_SIZE_MB: int = 50
```

**Esforço:** 15 min. Sem impacto no desenvolvimento normal.

---

### 1.4 Upload sem validação de tipo — arquivo malicioso aceito

**Arquivo:** `app_dev/backend/app/domains/upload/router.py`

O endpoint aceita `formato: str = Form(...)` do cliente sem verificar o conteúdo real do arquivo. Um usuário pode enviar um `.sh` ou `.py` com content-type `text/csv`.

```python
# FIX
EXTENSOES_PERMITIDAS = {'csv', 'xls', 'xlsx', 'pdf', 'ofx'}
MIME_TYPES_PERMITIDOS = {
    'text/csv', 'text/plain',
    'application/pdf',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/octet-stream',  # alguns browsers enviam isso para .ofx
}

def validar_arquivo(file: UploadFile) -> None:
    ext = (file.filename or '').rsplit('.', 1)[-1].lower()
    if ext not in EXTENSOES_PERMITIDAS:
        raise HTTPException(400, f"Extensão .{ext} não permitida. Use: {', '.join(EXTENSOES_PERMITIDAS)}")
    if file.content_type and file.content_type not in MIME_TYPES_PERMITIDOS:
        raise HTTPException(400, f"Tipo de arquivo não permitido: {file.content_type}")
```

**Esforço:** 20 min. Sem impacto no desenvolvimento.

---

## 2. Alto

### 2.1 Rate limiting no login muito permissivo — brute force possível

**Arquivo:** `app_dev/backend/app/domains/auth/router.py`

```python
# PROBLEMA — 5/min = 7.200 tentativas/dia por IP
@limiter.limit("5/minute")
def login(...):
```

```python
# FIX — mais restritivo + log de tentativas falhas
@router.post("/login")
@limiter.limit("3/minute")   # reduz para 3/min
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    try:
        ...
    except HTTPException:
        # Log tentativa falha (IP + email — sem senha)
        logger.warning("login_failed ip=%s email=%s", request.client.host, credentials.email)
        raise
```

Para o futuro (não urgente): implementar lockout progressivo após 10 tentativas falhas no mesmo email em 1h.

**Esforço:** 10 min.

---

### 2.2 dangerouslySetInnerHTML no componente de gráfico — CSS injection

**Arquivo:** `app_dev/frontend/src/components/ui/chart.tsx`

```typescript
// PROBLEMA
<style dangerouslySetInnerHTML={{ __html: `--color-${key}: ${color}` }} />
```

Se `color` vier de dados do usuário sem sanitização, pode injetar CSS arbitrário ou, em alguns navegadores, scripts via CSS.

```typescript
// FIX — validar que color é uma cor válida antes de usar
const isValidColor = (c: string): boolean =>
  /^#[0-9A-Fa-f]{3,8}$/.test(c) ||
  /^(rgb|hsl)a?\([\d\s,%.]+\)$/.test(c) ||
  /^var\(--[\w-]+\)$/.test(c)

const safeColor = isValidColor(color) ? color : 'transparent'
```

**Esforço:** 15 min.

---

### 2.3 `text()` do SQLAlchemy — padrão de risco

**Arquivo:** múltiplos (principalmente `dashboard/repository.py`, `plano/service.py`)

As queries com `text()` estão parametrizadas corretamente — não há SQL injection imediato. Mas o padrão é arriscado: um desenvolvedor que copiar e modificar o código pode esquecer a parametrização.

```python
# PADRÃO ATUAL — seguro mas frágil
db.execute(text("SELECT ... WHERE user_id = :uid"), {"uid": user_id})

# PADRÃO RECOMENDADO — ORM, impossível esquecer parametrização
db.query(Model).filter(Model.user_id == user_id).all()
```

**Regra:** só usar `text()` quando o ORM não suportar a query (window functions, CTEs complexas). Nunca concatenar strings em `text()`.

**Esforço:** migração gradual — não urgente, mas sinalizar no code review.

---

## 3. Médio

### 3.1 Console com dados financeiros reais

**Arquivo:** múltiplos hooks do frontend (ex: `use-dashboard.ts:170`)

```
// Console exibe em produção:
useExpenseSources – Total: 32016.43
useExpenseSources – Dados recebidos: {sources: Array(6), total_despesas: 32016.43}
```

Qualquer pessoa que abra o DevTools vê os valores reais. Extensões maliciosas podem capturar.

**Fix rápido — `next.config.js`:**
```javascript
const nextConfig = {
  compiler: {
    // Remove todos console.log e console.debug em produção
    // Mantém console.error e console.warn para monitoramento
    removeConsole: process.env.NODE_ENV === 'production'
      ? { exclude: ['error', 'warn'] }
      : false,
  },
}
```

**Fix estrutural — criar logger utilitário:**
```typescript
// src/lib/logger.ts
const isDev = process.env.NODE_ENV === 'development'

export const logger = {
  // Nunca logar valores financeiros — apenas contagens e status
  debug: (msg: string, meta?: Record<string, unknown>) => {
    if (isDev) console.log(msg, meta)
  },
  error: (msg: string, err?: unknown) => console.error(msg, err),
}

// Uso correto:
logger.debug('useExpenseSources: fetch ok', { count: sources.length }) // ✓ count, não valor
// logger.debug('total:', total_despesas)  // ✗ nunca valor financeiro
```

**Esforço:** `next.config.js` = 5 min (resolve imediatamente). Logger utilitário = 1h.

---

### 3.2 Chamadas duplicadas do `useExpenseSources`

**Arquivo:** `app_dev/frontend/src/features/dashboard` (use-dashboard.ts:170)

O hook aparece sendo chamado duas vezes com os mesmos parâmetros `{year: 2026, month: 3}`. Isso dobra as requests à API sem necessidade.

Causas comuns:
- `useEffect` com dependência instável (objeto recriado a cada render)
- Componente pai re-renderizando desnecessariamente
- Falta de `useMemo` nas dependências

```typescript
// PROBLEMA — objeto novo a cada render dispara o useEffect
const params = { year, month }  // nova referência sempre
useEffect(() => { fetch(params) }, [params])  // roda sempre

// FIX — primitivos como dependência, nunca objetos
useEffect(() => { fetch(year, month) }, [year, month])  // roda só quando year ou month mudam
```

**Esforço:** 30 min de investigação + fix.

---

### 3.3 JWT secret sem validação de comprimento mínimo

**Arquivo:** `app_dev/backend/app/core/config.py`

Se alguém configurar um `.env` com `JWT_SECRET_KEY=abc`, o app inicia normalmente com uma secret quebrável.

```python
# FIX — validar no startup
from pydantic import field_validator

class Settings(BaseSettings):
    JWT_SECRET_KEY: str

    @field_validator('JWT_SECRET_KEY')
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError('JWT_SECRET_KEY precisa ter no mínimo 32 caracteres')
        return v
```

Gerar uma secret segura: `openssl rand -hex 32`

**Esforço:** 10 min.

---

### 3.4 Queries sem `user_id` em grupos e marcações

**Já documentado em:** `docs/performance/PERFORMANCE_OPORTUNIDADES.md` (seção 2)

Isso é simultaneamente um bug de integridade e segurança: dados de um usuário podem aparecer para outro. Prioridade 1 no plano de ataque de performance.

---

## 4. Baixo

### 4.1 Security headers ausentes

**Arquivo:** `app_dev/backend/app/main.py`

Headers que protegem contra clickjacking, MIME sniffing e XSS no browser, mas são transparentes para o desenvolvimento:

```python
# Adicionar em main.py, após os middlewares existentes
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

**Esforço:** 10 min. Zero impacto no desenvolvimento.

---

### 4.2 Health check expõe status do banco

**Arquivo:** `app_dev/backend/app/main.py`

```python
# PROBLEMA — informa atacante que banco está online/offline
return {"status": "healthy", "database": "connected"}

# FIX — versão pública diz apenas ok/error
return {"status": "ok"}
```

**Esforço:** 5 min.

---

### 4.3 Swagger habilitado em dev — OK, só confirmar desabilitado em prod

**Arquivo:** `app_dev/backend/app/main.py`

```python
docs_url="/docs" if settings.DEBUG else None,  # ✅ correto
```

Confirmar que o `.env` de produção tem `DEBUG=false`. Se estiver `DEBUG=true` em produção, toda a documentação da API fica pública.

---

## 5. O Que Já Está Bem

| Item | Status |
|------|--------|
| Swagger desabilitado em produção | ✅ |
| Senha com bcrypt | ✅ |
| Rate limiting existe no login | ✅ (fraco, mas existe) |
| JWT com expiração | ✅ |
| Admin separado do usuário comum | ✅ |
| Logs de purge de usuário | ✅ |
| Endpoints autenticados por padrão | ✅ |
| `.env` para secrets (sem hardcode) | ✅ |

---

## 6. Plano de Ação

| # | Fix | Arquivo | Esforço | Prioridade |
|---|-----|---------|---------|------------|
| 1 | CORS: restringir methods e headers | `main.py` | 5 min | Crítico |
| 2 | Upload: validar tamanho máximo | `upload/router.py` | 15 min | Crítico |
| 3 | Upload: validar extensão e MIME type | `upload/router.py` | 20 min | Crítico |
| 4 | `next.config.js`: removeConsole em produção | `next.config.js` | 5 min | Alto |
| 5 | Security headers no backend | `main.py` | 10 min | Alto |
| 6 | JWT secret: validar comprimento mínimo | `config.py` | 10 min | Médio |
| 7 | Rate limiting: reduzir para 3/min + log | `auth/router.py` | 10 min | Médio |
| 8 | Chart: validar colors antes do style tag | `chart.tsx` | 15 min | Médio |
| 9 | Health check: resposta mínima pública | `main.py` | 5 min | Baixo |
| 10 | localStorage token → remover, só cookie | `use-token.ts` + `api-client.ts` | 30 min | Alto |
| 11 | useExpenseSources: corrigir dependências | `use-dashboard.ts` | 30 min | Médio |
| 12 | Queries sem user_id (grupos/marcações) | ver PERFORMANCE doc | 30 min | Crítico |

**Total estimado:** ~3h para os itens 1-9 + 12. Item 10 requer teste cuidadoso.

---

## 7. Regras para o Futuro

```python
# BACKEND

# ❌ text() com concatenação
db.execute(text(f"SELECT * FROM table WHERE campo = '{valor}'"))

# ✅ ORM ou text() parametrizado
db.query(Model).filter(Model.campo == valor).all()

# ❌ query sem user_id
db.query(JournalEntry).filter(GRUPO=grupo).count()

# ✅ user_id sempre obrigatório
db.query(JournalEntry).filter(user_id=uid, GRUPO=grupo).count()

# ❌ arquivo sem validação
file_bytes = await file.read()

# ✅ sempre validar antes de ler
if file.size > MAX_SIZE: raise HTTPException(413, ...)
```

```typescript
// FRONTEND

// ❌ dados financeiros no console
console.log('total:', total_despesas)
console.log('response:', apiData)

// ✅ apenas metadata no logger de dev
logger.debug('fetch ok', { count: items.length })

// ❌ token no localStorage
localStorage.setItem('authToken', token)

// ✅ depender do httpOnly cookie — não armazenar token no JS

// ❌ objeto como dependência do useEffect
useEffect(() => fetch(params), [params])  // params é novo a cada render

// ✅ primitivos como dependência
useEffect(() => fetch(year, month), [year, month])
```
