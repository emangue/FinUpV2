# Auditoria de Segurança v2 — app_dev + app admin

**Data:** 2026-03-02 (atualização da auditoria de 2026-03-02)
**Branch:** feature/merge-plano-aposentadoria
**Método:** Análise estática — backend + frontend + app admin

---

## Sumário executivo

### Status da auditoria anterior

| ID | Severidade | Título | Status |
|---|---|---|---|
| C-01 | 🔴 CRÍTICO | Security headers ausentes | ✅ **CORRIGIDO** |
| A-03 | 🟠 ALTO | CORS com métodos/headers irrestrito | ✅ **CORRIGIDO** |
| A-01 | 🟠 ALTO | Token JWT em localStorage | ✅ **CORRIGIDO** |
| M-03 | 🟡 MÉDIO | `change-password` sem rate limit | ✅ **CORRIGIDO** |
| A-02 | 🟠 ALTO | 46+ `console.log` com dados financeiros | ⬜ **REDUZIDO** (logger.ts criado, uso parcial) |
| M-01 | 🟡 MÉDIO | `print()` no backend | ⬜ **PENDENTE** (verificar service.py) |
| M-02 | 🟡 MÉDIO | JWT_SECRET_KEY dev ≠ prod | ⬜ **VERIFICAR** em produção |

### Novos achados — app admin

| Severidade | Qtd | Itens |
|---|---|---|
| 🔴 CRÍTICO | 2 | ADM-01 · ADM-03 |
| 🟠 ALTO | 2 | ADM-02 · ADM-04 |
| 🟡 MÉDIO | 2 | ADM-05 · ADM-06 |
| 🔵 BAIXO | 1 | ADM-07 |

---

## Achados da auditoria anterior — revisão

### ✅ C-01 — Security Headers — CORRIGIDO

`SecurityHeadersMiddleware` implementado em `main.py:16-30`. Todos os headers esperados presentes:
`X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `HSTS` (prod).

---

### ✅ A-03 — CORS restrito — CORRIGIDO

`main.py:75-76` — métodos e headers agora explícitos:
```python
allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
```

---

### ✅ A-01 — Token removido do localStorage — CORRIGIDO

`admin/page.tsx:4` usa `fetchWithAuth` para a listagem de usuários. Funções `@deprecated` mantidas
como no-op em `api-client.ts`. Cookie httpOnly é o único mecanismo de sessão.

---

### ⬜ A-02 — console.log — REDUZIDO, não concluído

`logger.ts` criado com guard `isDev`. Admin page já usa `logger.log()`.
Restam `console.error()` sem guard nos handlers de erro (`admin/page.tsx:80, 150, 169, 195, 233`).
`console.error` é intencional em produção para erros, mas alguns expostos em contextos admin
devem ser guardados também.

---

## Novos achados — app admin

---

### 🔴 [ADM-01] `GET /users/{user_id}` sem autenticação — IDOR

**Severidade:** CRÍTICO
**Arquivo:** `app_dev/backend/app/domains/users/router.py` linhas 88–97

```python
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)   # ← sem require_admin, sem get_current_user_id
):
    service = UserService(db)
    return service.get_user(user_id)
```

Todos os outros endpoints do mesmo router têm `admin = Depends(require_admin)`.
Este é o único sem autenticação — provavelmente omissão durante desenvolvimento.

**Impacto:** Qualquer requisição não autenticada consegue enumerar todos os usuários do sistema:
```bash
for i in {1..100}; do
  curl http://meu-app.com/api/v1/users/$i
done
# Retorna: id, nome, email, role, ativo, created_at de cada usuário
```

**Correção:**
```python
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin),  # ← adicionar
):
```

---

### 🔴 [ADM-02] Senha exposta em query string no reset-password

**Severidade:** CRÍTICO
**Arquivo:** `app_dev/backend/app/domains/users/router.py` linha 138–139

```python
@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: int,
    nova_senha: str,           # ← query parameter, NÃO body
    db: Session = Depends(get_db),
    admin = Depends(require_admin),
):
```

Quando `nova_senha` é um parâmetro de query (não body), a URL gerada é:
```
POST /api/v1/users/5/reset-password?nova_senha=MinhaNovaS3nh@
```

A senha nova aparece em texto puro em:
- Logs do servidor nginx/uvicorn (access log)
- Histórico de rede do browser (DevTools → Network)
- Logs de proxy reverso
- Qualquer ferramenta de observabilidade (Datadog, Grafana, etc.)

**Correção — mover para body:**
```python
# Schema novo:
class ResetPasswordRequest(BaseModel):
    nova_senha: str

# Endpoint corrigido:
@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: int,
    body: ResetPasswordRequest,  # ← body, não query param
    db: Session = Depends(get_db),
    admin = Depends(require_admin),
):
    return UserService(db).reset_password(user_id, body.nova_senha)
```

**Frontend correspondente** (`admin/page.tsx:219-223`) também precisa ser atualizado
— atualmente usa `fetch()` sem `credentials: 'include'` (ver ADM-03), então a
operação já está quebrando silenciosamente.

---

### 🟠 [ADM-03] Frontend admin usa `fetch()` sem autenticação em 3 operações

**Severidade:** ALTO
**Arquivo:** `app_dev/frontend/src/app/settings/admin/page.tsx`

Três das quatro operações admin usam `fetch()` puro em vez de `fetchWithAuth()`,
e apontam para URLs incorretas (sem `/v1/`):

| Operação | Linha | Problema |
|---|---|---|
| Criar/editar usuário (`handleSave`) | 138 | `fetch('/api/users/...')` — sem `credentials: 'include'`, URL incorreta |
| Desativar usuário (`handleDelete`) | 184 | `fetch('/api/users/...')` — sem `credentials: 'include'`, URL incorreta |
| Alterar senha (`handleSalvarNovaSenha`) | 219 | `fetch('/api/users/...')` — sem `credentials: 'include'`, URL incorreta |

Apenas `fetchUsuarios()` (linha 74) usa `fetchWithAuth()` com URL correta.

**Efeito prático:** As três operações de escrita estão provavelmente **falhando silenciosamente**
(cookie não enviado → 401 Unauthorized), mas o código não trata o status 401 nesses handlers —
mostra mensagem de erro genérica do `response.json()` ou simplesmente não atualiza a lista.

**URL correta:** `${apiUrl}/users/...` (onde `apiUrl` = `http://localhost:8000/api/v1`)

**Correção:**
```typescript
// handleSave — linha 138:
const response = await fetchWithAuth(`${apiUrl}/users${editingUsuario ? `/${editingUsuario.id}` : ''}`, {
  method,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body)
})

// handleDelete — linha 184:
const response = await fetchWithAuth(`${apiUrl}/users/${id}`, {
  method: 'DELETE'
})

// handleSalvarNovaSenha — linha 219:
const response = await fetchWithAuth(`${apiUrl}/users/${senhaUsuarioId}/reset-password`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ nova_senha: novaSenha })  // após corrigir ADM-02
})
```

---

### 🟠 [ADM-04] `GET /screens/list` aceita `is_admin=true` de qualquer usuário

**Severidade:** ALTO
**Arquivo:** `app_dev/backend/app/domains/screen_visibility/router.py` linhas 21–33

```python
@router.get("/list", response_model=List[ScreenVisibilityResponse])
def list_screens(
    is_admin: bool = False,  # TODO: Pegar do token/session do usuário ← NUNCA implementado
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    service = ScreenVisibilityService(db)
    return service.list_for_user(is_admin=is_admin)  # ← usa o parâmetro da query
```

Qualquer usuário autenticado pode chamar:
```
GET /api/v1/screens/list?is_admin=true
```
e ver **todas** as telas em desenvolvimento/alpha (status A e D), não apenas as de produção.

Isso expõe features em desenvolvimento que ainda não deveriam ser visíveis para usuários regulares.

**Correção:**
```python
@router.get("/list", response_model=List[ScreenVisibilityResponse])
def list_screens(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # busca user completo
):
    is_admin = current_user.role == 'admin'   # extrai role do token, não do query param
    return ScreenVisibilityService(db).list_for_user(is_admin=is_admin)
```

---

### 🟡 [ADM-05] Sem audit log em operações admin críticas

**Severidade:** MÉDIO
**Arquivo:** `app_dev/backend/app/domains/users/service.py`

Apenas `purge_user()` registra log de auditoria:
```python
logger.warning("PURGE user_id=%s por admin_id=%s", user_id, executado_por)
```

As seguintes operações não têm registro de quem fez o quê e quando:

| Operação | Impacto |
|---|---|
| `update_user()` — alterar role/email/ativo | Promoção de usuário para admin não é auditada |
| `delete_user()` — desativar usuário | Desativação não tem rastro de quem executou |
| `reset_password()` — resetar senha | Reset de senha não registra admin responsável |
| `create_user()` — criar usuário | Criação não registra quem criou |

**Recomendação:**
```python
# Em cada operação crítica, adicionar:
logger.warning(
    "ADMIN_ACTION action=%s target_user_id=%s executado_por=%s",
    "update_role", user_id, admin_id
)
```

---

### 🟡 [ADM-06] Validação de senha só no frontend (mínimo 6 chars)

**Severidade:** MÉDIO
**Arquivo:** `admin/page.tsx:213-216` + `users/service.py` (ausência de validação)

Frontend valida apenas comprimento ≥ 6. Backend (`reset_password`, `create_user`) não valida
complexidade de senha. Um admin pode criar usuários com senha `"123456"`.

**Recomendação:** adicionar validação no backend:
```python
# Em service.py, antes do hash:
if len(nova_senha) < 12:
    raise HTTPException(400, "Senha deve ter no mínimo 12 caracteres")
```

---

### 🔵 [ADM-07] Proteção do user_id=1 apenas no frontend

**Severidade:** BAIXO
**Arquivo:** `admin/page.tsx:176-178`

```typescript
if (id === 1) {
  alert('Não é possível deletar o usuário administrador principal')
  return
}
```

O backend **também** protege o `user_id=1` em `delete_user()` e `purge_user()`.
A proteção frontend é apenas UX. Correto como está.
Documentado aqui apenas para ciência — não há risco real pois o backend é a fonte da verdade.

---

## O que está correto no app admin ✅

| Item | Localização | Detalhe |
|---|---|---|
| `require_admin` em todos endpoints de escrita | `users/router.py` | Todos PUT, POST, DELETE têm verificação de role |
| `purge_user` com dupla confirmação | `users/router.py:77-84` | Exige string literal + email do usuário |
| Proteção do user_id=1 no backend | `users/service.py` | Admin principal não pode ser deletado/desativado |
| RBAC com role no JWT | `dependencies.py` | `require_admin()` usa role do token, não parâmetro externo |
| Frontend envolvido em `<RequireAdmin>` | `admin/page.tsx:239` | Proteção client-side alinhada com backend |
| `fetchWithAuth` na listagem | `admin/page.tsx:74` | Listagem usa cookie corretamente |
| Audit log no purge | `users/service.py` | `logger.warning("PURGE ...")` presente |

---

## Plano de correção — app admin

### Fase 1 — Imediata (críticos, baixo risco de quebra)

| # | Ação | Arquivo | Esforço |
|---|---|---|---|
| 1.1 | Adicionar `admin = Depends(require_admin)` em `GET /users/{user_id}` | `users/router.py:91` | 2 min |
| 1.2 | Mover `nova_senha` de query param para request body em `reset-password` | `users/router.py:136-147` | 15 min |
| 1.3 | Substituir `fetch()` por `fetchWithAuth()` nos 3 handlers admin | `admin/page.tsx:138,184,219` | 20 min |
| 1.4 | Corrigir URLs de `/api/users/` para `${apiUrl}/users/` nos handlers | `admin/page.tsx:119-122,184,219` | 10 min |

**Validação fase 1:**
```bash
# ADM-01: endpoint deve retornar 401 sem autenticação
curl http://localhost:8000/api/v1/users/1
# Esperado: 401 Unauthorized

# ADM-02: senha não deve aparecer na URL (verificar logs do uvicorn)
# ADM-03/1.4: operações admin devem funcionar na interface (criar/editar/deletar usuário)
```

### Fase 2 — Curto prazo

| # | Ação | Arquivo | Esforço |
|---|---|---|---|
| 2.1 | Corrigir `GET /screens/list` para extrair `is_admin` do token | `screen_visibility/router.py:22-23` | 15 min |
| 2.2 | Adicionar audit log em `update_user`, `delete_user`, `reset_password`, `create_user` | `users/service.py` | 30 min |
| 2.3 | Aumentar validação de senha para 12 chars no backend | `users/service.py` | 5 min |

### DAG de dependências

```
ADM-01 — independente ──► Fase 1 (30 min total)
ADM-02 + ADM-03 — dependentes entre si (frontend chama o endpoint)
ADM-04 — independente ──► Fase 2 (50 min total)
ADM-05 — independente
ADM-06 — independente
```

---

## Score geral de segurança

| Dimensão | Antes | Depois fase 1 |
|---|---|---|
| Autenticação de API | 🟠 Bom (1 endpoint sem auth) | ✅ Sólido |
| Autorização admin | 🟡 Parcial (frontend admin quebrado) | ✅ Funcional |
| Exposição de senhas | 🔴 Crítico (query string) | ✅ Seguro |
| Visibilidade de telas | 🟠 Bypassável | ✅ Protegida |
| Audit trail | 🟡 Parcial (só purge) | 🟡 Melhorado (fase 2) |
| Security headers | ✅ Completo | ✅ Mantido |
| Token storage | ✅ Cookie httpOnly | ✅ Mantido |

---

## Achados encerrados (não requerem ação)

- **ADM-07**: Proteção do user_id=1 só no frontend — backend também protege, sem risco.
- **M-02**: JWT_SECRET_KEY em .env dev — fora do git, processo documentado.
- **B-02**: DEBUG=false no .env de dev — cosmético, não é risco de segurança.

---

*Referência: auditoria original em `AUDITORIA_SEGURANCA.md`*
*Plano de ação original em `PLANO_ACAO_SEGURANCA.md`*
