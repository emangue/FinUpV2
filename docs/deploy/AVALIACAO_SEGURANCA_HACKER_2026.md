# 🔐 Avaliação de Segurança - Perspectiva de Ataque

**Data:** 14/02/2026  
**Objetivo:** Análise como se fosse um atacante buscando vulnerabilidades  
**Escopo:** Frontend Next.js, Backend FastAPI, comunicação, dados expostos

---

## 1. RESUMO EXECUTIVO

| Severidade | Quantidade | Principais Riscos |
|------------|------------|-------------------|
| 🔴 Crítica | 2 | Credenciais em docs, Token em localStorage |
| 🟠 Alta | 3 | Cookie sem HttpOnly, API Docs em prod, Logs sensíveis |
| 🟡 Média | 4 | CORS, XSS potencial, Inconsistência cookie |
| 🟢 Baixa | 2 | Info leak em erros, Rate limit genérico |

---

## 2. VULNERABILIDADES CRÍTICAS

### 2.1 🔴 Credenciais em Documentação Versionada

**Local:** `docs/deploy/DEPLOY_MEUFINUP_ATUALIZACAO_2026.md`  
**Problema:** Senha do PostgreSQL em texto plano no repositório:
```
Password: FinUp2026SecurePass
Connection string: postgresql://finup_user:FinUp2026SecurePass@127.0.0.1:5432/finup_db
```

**Impacto:** Qualquer pessoa com acesso ao repositório (incluindo histórico Git) obtém credenciais de produção.

**Recomendação:**
- Remover imediatamente do arquivo
- Usar variáveis de ambiente e referenciar `.env.example` sem valores reais
- Rotacionar senha do PostgreSQL em produção
- Adicionar `docs/deploy/*.md` ao `.gitignore` para arquivos com credenciais OU usar secrets manager

---

### 2.2 🔴 Token JWT em localStorage (XSS → Roubo de Sessão)

**Local:** `app_dev/frontend/src/core/utils/api-client.ts`, `AuthContext.tsx`  
**Problema:** Token salvo em `localStorage.setItem('authToken', token)`.

**Por que é crítico:**
- localStorage é acessível via JavaScript
- Se um atacante injetar XSS (mesmo em dependência npm), pode executar `localStorage.getItem('authToken')` e exfiltrar o token
- Token JWT = sessão completa até expirar (1h)

**Impacto:** Roubo de sessão, acesso total aos dados financeiros do usuário.

**Recomendação:**
- Migrar para **httpOnly cookies** (não acessíveis via JS)
- Backend define cookie no login com flags: `HttpOnly; Secure; SameSite=Strict`
- Frontend não precisa ler o token; cookie é enviado automaticamente

---

## 3. VULNERABILIDADES ALTAS

### 3.1 🟠 Cookie de Autenticação sem HttpOnly/Secure

**Local:** `AuthContext.tsx` linha 74:
```javascript
document.cookie = `auth_token=${access_token}; path=/; max-age=3600; SameSite=Lax`
```

**Problemas:**
- Falta `HttpOnly` → JavaScript pode ler (XSS rouba)
- Falta `Secure` → Pode ser enviado em HTTP (MITM)
- `SameSite=Lax` é aceitável, mas `Strict` é mais seguro

**Recomendação:**
```javascript
// Backend deve setar o cookie na resposta do login:
Set-Cookie: auth_token=<token>; Path=/; Max-Age=3600; HttpOnly; Secure; SameSite=Strict
```

---

### 3.2 🟠 API Docs (Swagger/ReDoc) Expostos em Produção

**Local:** `app_dev/backend/app/main.py`:
```python
docs_url="/docs",  # Swagger UI
redoc_url="/redoc"  # ReDoc
```

**Problema:** Em produção, `https://meufinup.com.br/docs` expõe:
- Lista completa de endpoints
- Parâmetros esperados
- Possibilidade de testar APIs diretamente
- Facilita enumeração e ataques automatizados

**Recomendação:**
- Desabilitar em produção: `docs_url=None, redoc_url=None` quando `DEBUG=False`
- Ou proteger com autenticação básica
- Ou restringir por IP (apenas admin)

---

### 3.3 🟠 Logs Sensíveis no Código

**Locais:**
- `AuthContext 2.tsx`: `console.log('[AuthContext] Login bem-sucedido:', { tokenPreview, userId, userEmail })`
- `api/[...proxy]/route.ts`: `console.log('[Proxy] Added token from cookie')`
- `api/[...proxy]/route.ts`: `console.log('[Proxy] ${method} ${fullUrl}')`
- `mobile/upload/page.tsx`: `console.log('🔑 Token recebido (primeiros 30 chars):', ...)`

**Problema:** Em produção, logs podem ir para agregadores (Sentry, CloudWatch). Token (mesmo parcial), URLs com query params, e dados de usuário vazam.

**Recomendação:**
- Remover `AuthContext 2.tsx` (arquivo duplicado com debug)
- Remover ou condicionar logs a `process.env.NODE_ENV === 'development'`
- Nunca logar tokens, mesmo truncados

---

## 4. VULNERABILIDADES MÉDIAS

### 4.1 🟡 Inconsistência Cookie: `auth_token` vs `token`

**Problema:**
- AuthContext seta cookie `auth_token`
- Proxy (`api/[...proxy]/route.ts`) busca cookie `token`
- Nomes diferentes → proxy nunca encontra token no cookie para SSR

**Impacto:** Funcionalidade quebrada em SSR, mas cliente usa Authorization header. Risco médio de confusão e possíveis bypass se alguém corrigir errado.

**Recomendação:** Padronizar em um nome (ex: `auth_token`) e garantir que proxy e cliente usem o mesmo.

---

### 4.2 🟡 CORS - Verificar Configuração em Produção

**Local:** `app_dev/backend/app/core/config.py`  
**Default:** `BACKEND_CORS_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"`

**Verificar:** Em produção, `.env` deve ter:
```
BACKEND_CORS_ORIGINS=https://meufinup.com.br,https://www.meufinup.com.br
```

**Risco:** Se CORS estiver `*` ou incluir origens não confiáveis, um site malicioso pode fazer requisições autenticadas em nome do usuário (se token em cookie com SameSite=Lax).

---

### 4.3 🟡 dangerouslySetInnerHTML em Chart

**Local:** `app_dev/frontend/src/components/ui/chart.tsx` linha 83:
```tsx
dangerouslySetInnerHTML={{
  __html: Object.entries(THEMES).map(([theme, prefix]) => `
    ${prefix} [data-chart=${id}] { ... }
  `).join("\n"),
}}
```

**Análise:** O conteúdo vem de `THEMES` e `id` (prop do componente). Se `id` ou dados de tema vierem de input do usuário ou da API sem sanitização, há risco de XSS.

**Recomendação:** Garantir que `id` e dados de tema são sempre controlados (não vêm de usuário/API). Se vierem de fonte externa, sanitizar (ex: DOMPurify) ou usar alternativa sem innerHTML.

---

### 4.4 🟡 Proxy Repassa Headers do Cliente

**Local:** `api/[...proxy]/route.ts`:
```javascript
request.headers.forEach((value, key) => {
  if (!['host', 'connection', 'content-length'].includes(key.toLowerCase())) {
    headers.set(key, value);
  }
});
```

**Problema:** Headers arbitrários do cliente são repassados ao backend. Um atacante pode enviar `X-Forwarded-For`, `X-Real-IP` ou outros para tentar spoofing.

**Recomendação:** Whitelist de headers permitidos (Authorization, Content-Type, etc.) em vez de repassar todos.

---

## 5. VULNERABILIDADES BAIXAS

### 5.1 🟢 Detalhes de Erro no Proxy

**Local:** `api/[...proxy]/route.ts`:
```javascript
return NextResponse.json({
  detail: error instanceof Error ? error.message : 'Internal proxy error',
  code: 'PROXY_ERROR',
}, { status: 500 });
```

**Problema:** `error.message` pode expor stack traces ou caminhos internos em desenvolvimento.

**Recomendação:** Em produção, retornar mensagem genérica: `"Erro interno. Tente novamente."`

---

### 5.2 🟢 Rate Limit Genérico

**Local:** `app_dev/backend/app/main.py`:
```python
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
```

**Problema:** 200 req/min é alto. Login tem 5/min (bom), mas outros endpoints podem ser abusados (ex: enumeração, scraping).

**Recomendação:** Ajustar limites por endpoint (ex: 30/min para listagens, 10/min para operações pesadas).

---

## 6. PONTOS POSITIVOS (O que está bem)

| Item | Status |
|------|--------|
| JWT obrigatório em endpoints | ✅ `get_current_user_id` exige token |
| Sem user_id hardcoded | ✅ Corrigido (23/01/2026) |
| Rate limit no login | ✅ 5 tentativas/minuto |
| SQL parametrizado | ✅ Uso de `text()` com `:param` |
| Sem fallback inseguro de JWT | ✅ `JWT_SECRET_KEY` obrigatório |
| CORS com allow_credentials | ✅ Configurável por origem |
| 401 redireciona para login | ✅ Cliente trata 401 |

---

## 7. COMUNICAÇÃO FRONTEND ↔ BACKEND

### Fluxo atual
1. **Login:** Frontend chama `POST /api/v1/auth/login` (ou via proxy) com email/senha
2. **Resposta:** Backend retorna `{ access_token, user }`
3. **Armazenamento:** Token em `localStorage` + cookie `auth_token`
4. **Requisições:** `fetchWithAuth()` adiciona `Authorization: Bearer <token>`
5. **Proxy (se usado):** Repassa headers; busca cookie `token` (nome incorreto)

### Riscos na comunicação
- **HTTPS:** Garantir que produção use TLS (Nginx/Certbot)
- **Token em trânsito:** Se HTTPS, ok. Se HTTP, token visível.
- **Token em storage:** localStorage vulnerável a XSS (ver 2.2)

---

## 8. INFORMAÇÕES EXPOSTAS NO FRONTEND

| Dado | Risco |
|------|-------|
| `NEXT_PUBLIC_BACKEND_URL` | Baixo – URL pública |
| Dados do usuário (nome, email) | Baixo – esperado na UI |
| Valores financeiros | Médio – só após login; garantir isolamento por user_id |
| Mensagens de erro da API | Médio – não expor stack traces |
| `process.env` em build | Baixo – só NEXT_PUBLIC_* vai para o cliente |

---

## 9. CHECKLIST DE REMediaÇÃO (Prioridade)

1. [ ] **URGENTE:** Remover credenciais do `DEPLOY_MEUFINUP_ATUALIZACAO_2026.md` e rotacionar senha PostgreSQL
2. [ ] **ALTA:** Planejar migração de token para httpOnly cookie
3. [ ] **ALTA:** Desabilitar `/docs` e `/redoc` em produção
4. [ ] **ALTA:** Remover logs sensíveis e arquivo `AuthContext 2.tsx`
5. [ ] **MÉDIA:** Padronizar nome do cookie (auth_token) no proxy
6. [ ] **MÉDIA:** Adicionar flags Secure e HttpOnly ao cookie (quando backend setar)
7. [ ] **MÉDIA:** Whitelist de headers no proxy
8. [ ] **BAIXA:** Mensagem genérica de erro no proxy em produção
9. [ ] **BAIXA:** Revisar rate limits por endpoint

---

**Documento gerado em:** 14/02/2026  
**Próxima revisão:** Após implementação das correções críticas
