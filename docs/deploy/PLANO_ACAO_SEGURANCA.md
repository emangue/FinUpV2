# 📋 Plano de Ação - Correções de Segurança

**Data:** 14/02/2026  
**Referência:** [AVALIACAO_SEGURANCA_HACKER_2026.md](./AVALIACAO_SEGURANCA_HACKER_2026.md)  
**Objetivo:** Guia passo a passo para corrigir todas as vulnerabilidades identificadas

---

## Índice

1. [Fase 1 - Urgente (1-2 dias)](#fase-1---urgente-1-2-dias)
2. [Fase 2 - Alta Prioridade (3-5 dias)](#fase-2---alta-prioridade-3-5-dias)
3. [Fase 3 - Média Prioridade (2-3 dias)](#fase-3---média-prioridade-2-3-dias)
4. [Fase 4 - Baixa Prioridade (1 dia)](#fase-4---baixa-prioridade-1-dia)
5. [Cronograma e Dependências](#cronograma-e-dependências)

---

## Fase 1 - Urgente (1-2 dias)

### 1.1 Remover credenciais da documentação

| Item | Detalhe |
|------|---------|
| **Arquivo** | `docs/deploy/DEPLOY_MEUFINUP_ATUALIZACAO_2026.md` |
| **Esforço** | 30 min |
| **Referência** | Avaliação 2.1 |

**Passos:**

1. Abrir `docs/deploy/DEPLOY_MEUFINUP_ATUALIZACAO_2026.md`
2. Na seção 2.3 (PostgreSQL), substituir valores reais por placeholders:
   ```markdown
   | **Password** | `$POSTGRES_PASSWORD` (variável de ambiente) |
   | **Connection string** | `postgresql://finup_user:$POSTGRES_PASSWORD@127.0.0.1:5432/finup_db` |
   ```
3. Adicionar nota: *"Credenciais reais em `.env` no servidor. NUNCA commitar."*
4. Criar/atualizar `docs/deploy/.env.example` (se não existir) com variáveis sem valores:
   ```
   POSTGRES_PASSWORD=
   JWT_SECRET_KEY=
   ```

**Validação:** `git diff` não deve mostrar senhas. Buscar no arquivo por "FinUp" ou "SecurePass" → 0 resultados.

---

### 1.2 Rotacionar senha do PostgreSQL em produção

| Item | Detalhe |
|------|---------|
| **Local** | Servidor (VPS) |
| **Esforço** | 1h |
| **Pré-requisito** | 1.1 concluído (para não re-expor a nova senha) |

**Passos:**

1. SSH no servidor: `ssh minha-vps-hostinger`
2. Gerar nova senha forte: `openssl rand -base64 24`
3. Alterar senha no PostgreSQL:
   ```bash
   sudo -u postgres psql -c "ALTER USER finup_user WITH PASSWORD 'NOVA_SENHA_AQUI';"
   ```
4. Atualizar `.env` do backend no servidor com a nova senha
5. Reiniciar backend: `systemctl restart finup-backend`
6. Testar: `curl https://meufinup.com.br/api/health`
7. **Importante:** Remover a senha antiga do histórico Git (ver 1.3)

---

### 1.3 Limpar histórico Git (opcional, recomendado)

| Item | Detalhe |
|------|---------|
| **Esforço** | 1h |
| **Risco** | Alto - pode quebrar clones. Fazer em horário de baixo uso. |

**Passos:**

1. Usar `git filter-repo` ou `BFG Repo-Cleaner` para remover a senha do histórico
2. Alternativa mais simples: aceitar que a senha antiga está no histórico e garantir que a nova (após rotação) nunca foi commitada
3. Documentar no README: "Se você clonou antes de 14/02/2026, a senha antiga pode estar no histórico. Use sempre a senha atual do servidor."

---

## Fase 2 - Alta Prioridade (3-5 dias)

### 2.1 Desabilitar API Docs em produção

| Item | Detalhe |
|------|---------|
| **Arquivo** | `app_dev/backend/app/main.py` |
| **Esforço** | 15 min |
| **Referência** | Avaliação 3.2 |

**Passos:**

1. Abrir `app_dev/backend/app/main.py`
2. Importar `settings` (já importado)
3. Alterar criação do FastAPI:
   ```python
   app = FastAPI(
       title=settings.APP_NAME,
       version=settings.APP_VERSION,
       description="API REST para Sistema de Finanças Pessoais - Arquitetura Modular",
       docs_url="/docs" if settings.DEBUG else None,
       redoc_url="/redoc" if settings.DEBUG else None,
   )
   ```
4. Garantir que `DEBUG=False` no `.env` de produção

**Validação:** Em produção, `https://meufinup.com.br/docs` deve retornar 404.

---

### 2.2 Remover logs sensíveis e arquivo duplicado

| Item | Detalhe |
|------|---------|
| **Arquivos** | `AuthContext 2.tsx`, `api/[...proxy]/route.ts`, `mobile/upload/page.tsx` |
| **Esforço** | 45 min |
| **Referência** | Avaliação 3.3 |

**Passos:**

1. **Deletar** `app_dev/frontend/src/contexts/AuthContext 2.tsx` (duplicado com debug)
2. Verificar se algum import usa `AuthContext 2` → corrigir para `AuthContext`
3. Em `app_dev/frontend/src/app/api/[...proxy]/route.ts`:
   - Remover: `console.log('[Proxy] Added token from cookie');`
   - Remover ou condicionar: `console.log('[Proxy] ${method} ${fullUrl}');` → só em dev:
     ```javascript
     if (process.env.NODE_ENV === 'development') {
       console.log(`[Proxy] ${method} ${path}`);
     }
     ```
4. Em `app_dev/frontend/src/app/mobile/upload/page.tsx`:
   - Remover: `console.log('🔑 Token recebido (primeiros 30 chars):', ...)`
5. Buscar outros `console.log` com token, userId, userEmail: `rg "console.log.*token|userId|userEmail" app_dev/frontend`

**Validação:** Nenhum log com dados sensíveis em produção.

---

### 2.3 Migração: Token para httpOnly Cookie

| Item | Detalhe |
|------|---------|
| **Arquivos** | Backend: `auth/router.py`, `auth/service.py`; Frontend: `AuthContext.tsx`, `api-client.ts`, `api/[...proxy]/route.ts` |
| **Esforço** | 4-6h |
| **Referência** | Avaliação 2.2, 3.1 |

**Visão geral:** Backend seta cookie HttpOnly no login; frontend deixa de usar localStorage.

**Passos – Backend:**

1. Em `app_dev/backend/app/domains/auth/router.py` (ou service), no retorno do login:
   ```python
   from fastapi.responses import JSONResponse
   
   # No login, após gerar token:
   response = JSONResponse(content={
       "access_token": access_token,
       "token_type": "bearer",
       "user": user_data
   })
   response.set_cookie(
       key="auth_token",
       value=access_token,
       max_age=3600,
       path="/",
       secure=True,      # Apenas HTTPS
       httponly=True,    # Não acessível via JS
       samesite="strict"
   )
   return response
   ```
2. Criar endpoint `POST /auth/logout` que limpa o cookie:
   ```python
   response = JSONResponse(content={"message": "Logged out"})
   response.delete_cookie(key="auth_token", path="/")
   return response
   ```

**Passos – Frontend:**

3. Em `AuthContext.tsx`:
   - Remover `setAuthToken(access_token)` e `document.cookie = ...`
   - Manter apenas `setToken` em memória (para estado da UI) – opcional
   - O cookie será enviado automaticamente em requisições same-origin
4. Em `api-client.ts`:
   - Para requisições ao **mesmo domínio** (via proxy `/api/...`): não enviar Authorization manualmente; o cookie vai automaticamente
   - Para requisições **diretas ao backend** (se houver): o backend precisa aceitar cookie OU manter header para transição
5. **Estratégia de transição:** Manter suporte a header `Authorization` no backend por um período; frontend envia cookie (credentials: 'include') e backend prioriza cookie sobre header
6. Remover `localStorage.setItem/removeItem/getItem` de authToken em todo o frontend

**Passos – Proxy:**

7. Em `api/[...proxy]/route.ts`:
   - Garantir que `fetch` usa `credentials: 'include'` para enviar cookies
   - Buscar cookie `auth_token` (não `token`) para SSR quando o cliente não envia header

**Validação:**
- Login → cookie `auth_token` com HttpOnly e Secure
- Requisições autenticadas funcionam sem localStorage
- `localStorage.getItem('authToken')` retorna null após login
- Logout limpa o cookie

---

## Fase 3 - Média Prioridade (2-3 dias)

### 3.1 Padronizar nome do cookie no proxy

| Item | Detalhe |
|------|---------|
| **Arquivo** | `app_dev/frontend/src/app/api/[...proxy]/route.ts` |
| **Esforço** | 10 min |
| **Referência** | Avaliação 4.1 |

**Passos:**

1. Em `api/[...proxy]/route.ts`, linha ~97:
   ```javascript
   // ANTES
   const tokenCookie = request.cookies.get('token');
   
   // DEPOIS
   const tokenCookie = request.cookies.get('auth_token') || request.cookies.get('token');
   ```
2. Após migração para httpOnly (2.3), remover fallback `token` e usar apenas `auth_token`

**Validação:** Proxy encontra o cookie em requisições SSR.

---

### 3.2 Whitelist de headers no proxy

| Item | Detalhe |
|------|---------|
| **Arquivo** | `app_dev/frontend/src/app/api/[...proxy]/route.ts` |
| **Esforço** | 30 min |
| **Referência** | Avaliação 4.4 |

**Passos:**

1. Definir lista de headers permitidos:
   ```javascript
   const ALLOWED_HEADERS = [
     'authorization', 'content-type', 'accept', 'accept-language',
     'cache-control', 'pragma'
   ];
   ```
2. Substituir o `forEach` que repassa todos os headers:
   ```javascript
   const contentType = request.headers.get('content-type');
   ALLOWED_HEADERS.forEach(key => {
     const value = request.headers.get(key);
     if (value) headers.set(key, value);
   });
   // Content-Type para multipart: deixar fetch gerar (já tratado)
   ```
3. Manter a lógica especial para multipart/form-data (não enviar Content-Type manualmente)

**Validação:** Upload, login e requisições JSON continuam funcionando.

---

### 3.3 Sanitizar dangerouslySetInnerHTML no Chart

| Item | Detalhe |
|------|---------|
| **Arquivo** | `app_dev/frontend/src/components/ui/chart.tsx` |
| **Esforço** | 45 min |
| **Referência** | Avaliação 4.3 |

**Passos:**

1. Verificar origem de `id` no componente Chart – se vier de props de pai, rastrear até a fonte
2. Se `id` for sempre interno (ex: `useId()` ou string fixa): adicionar comentário de segurança e seguir
3. Se `id` puder vir de API/usuário:
   - Instalar: `npm install dompurify && npm install -D @types/dompurify`
   - Sanitizar: `import DOMPurify from 'dompurify'; __html: DOMPurify.sanitize(cssContent)`
   - Ou: gerar o CSS sem innerHTML (ex: usar `style` prop ou CSS-in-JS)
4. Para `id`, validar formato: apenas `[a-zA-Z0-9_-]`:
   ```javascript
   const safeId = /^[a-zA-Z0-9_-]+$/.test(id) ? id : 'chart-' + Math.random().toString(36).slice(2);
   ```

**Validação:** Nenhum XSS ao passar `id` malicioso (ex: `id="<script>alert(1)</script>"`).

---

### 3.4 Verificar CORS em produção

| Item | Detalhe |
|------|---------|
| **Arquivo** | `.env` no servidor |
| **Esforço** | 15 min |
| **Referência** | Avaliação 4.2 |

**Passos:**

1. SSH no servidor
2. Verificar `app_dev/backend/.env`:
   ```bash
   grep CORS /var/www/finup/app_dev/backend/.env
   ```
3. Deve conter:
   ```
   BACKEND_CORS_ORIGINS=https://meufinup.com.br,https://www.meufinup.com.br
   ```
4. Se estiver vazio ou com `*`, corrigir
5. Reiniciar backend: `systemctl restart finup-backend`

**Validação:** Frontend em meufinup.com.br consegue chamar a API. Origens não listadas recebem CORS error.

---

## Fase 4 - Baixa Prioridade (1 dia)

### 4.1 Mensagem genérica de erro no proxy

| Item | Detalhe |
|------|---------|
| **Arquivo** | `app_dev/frontend/src/app/api/[...proxy]/route.ts` |
| **Esforço** | 10 min |
| **Referência** | Avaliação 5.1 |

**Passos:**

1. No `catch` do `handleProxy`:
   ```javascript
   const isProduction = process.env.NODE_ENV === 'production';
   const message = isProduction 
     ? 'Erro interno. Tente novamente.' 
     : (error instanceof Error ? error.message : 'Internal proxy error');
   
   return NextResponse.json(
     { detail: message, code: 'PROXY_ERROR' },
     { status: 500 }
   );
   ```

**Validação:** Em produção, erro 500 não expõe stack trace.

---

### 4.2 Ajustar rate limits por endpoint

| Item | Detalhe |
|------|---------|
| **Arquivos** | `app_dev/backend/app/main.py`, routers (transactions, dashboard, upload, etc.) |
| **Esforço** | 1-2h |
| **Referência** | Avaliação 5.2 |

**Passos:**

1. Reduzir limite global em `main.py`:
   ```python
   limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
   ```
2. Adicionar limites específicos nos routers mais sensíveis:
   ```python
   @router.get("/list")
   @limiter.limit("30/minute")
   def list_transactions(...): ...
   
   @router.post("/process")
   @limiter.limit("10/minute")
   def process_upload(...): ...
   ```
3. Manter login em 5/min (já está)
4. Listar endpoints e definir limites:
   - Listagens (transactions, dashboard, etc.): 30/min
   - Escritas (create, update, delete): 20/min
   - Upload/processamento: 10/min

**Validação:** Abuso (ex: 100 req em 1 min) retorna 429 Too Many Requests.

---

## Cronograma e Dependências

```
Fase 1 (Urgente)     Fase 2 (Alta)           Fase 3 (Média)        Fase 4 (Baixa)
─────────────────────────────────────────────────────────────────────────────────

1.1 Remover creds ──► 2.1 API Docs
     │
1.2 Rotacionar senha  2.2 Logs sensíveis
     │
1.3 Histórico Git     2.3 httpOnly cookie ──► 3.1 Cookie proxy
                          │
                          └─────────────────► 3.2 Headers proxy
                                              3.3 Chart sanitize
                                              3.4 CORS prod
                                                              ──► 4.1 Erro proxy
                                                                  4.2 Rate limits
```

**Ordem sugerida:**

| Semana | Itens |
|--------|-------|
| 1 | 1.1, 1.2, 2.1, 2.2 |
| 2 | 2.3 (httpOnly cookie) |
| 3 | 3.1, 3.2, 3.3, 3.4 |
| 4 | 4.1, 4.2 |

---

## Checklist Final

- [ ] 1.1 Credenciais removidas do MD
- [ ] 1.2 Senha PostgreSQL rotacionada
- [ ] 2.1 API Docs desabilitados em prod
- [ ] 2.2 Logs sensíveis removidos
- [ ] 2.3 Token migrado para httpOnly cookie
- [ ] 3.1 Cookie padronizado no proxy
- [ ] 3.2 Whitelist de headers no proxy
- [ ] 3.3 Chart sanitizado
- [ ] 3.4 CORS verificado em prod
- [ ] 4.1 Erro genérico no proxy
- [ ] 4.2 Rate limits ajustados

---

**Documento:** Plano de Ação - Segurança  
**Última atualização:** 14/02/2026
