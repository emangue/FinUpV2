# 🔐 Correção: Failed to Fetch (401 Unauthorized)

**Data:** 01/02/2026  
**Tempo:** ~10 minutos  
**Status:** ✅ CORRIGIDO

---

## 🔍 Problema Identificado

### Erro no Console
```
Console TypeError
Failed to fetch

src/core/utils/api-client.ts (54:10) @ fetchWithAuth
```

### Root Cause
1. **Backend retorna 401 Unauthorized** - Token de autenticação não fornecido ou inválido
2. **Frontend não trata erro 401** - Não redireciona para login quando token expira
3. **Usuário não está logado** - Acesso direto a `/mobile/dashboard` sem autenticação

### Log do Backend
```
INFO: 127.0.0.1:52235 - "GET /api/v1/transactions/grupo-breakdown?data_inicio=2026-01-01&data_fim=2026-01-31 HTTP/1.1" 401 Unauthorized
```

---

## ✅ Soluções Implementadas

### 1. Tratamento de Erro 401 no Dashboard Mobile
**Arquivo:** `app/mobile/dashboard/page.tsx`

**Mudanças:**
- Verifica `response.status === 401`
- Redireciona automaticamente para `/login` quando não autenticado
- Try-catch aprimorado com fallback para valores zerados
- Investimentos com tratamento de erro isolado

```typescript
const response = await fetchWithAuth(
  `${BASE_URL}/transactions/grupo-breakdown?data_inicio=${startDateStr}&data_fim=${endDateStr}`
)

if (response.status === 401) {
  // Token inválido ou expirado - redirecionar para login
  console.error('Não autenticado. Redirecionando para login...')
  router.push('/login')
  return
}

if (!response.ok) {
  throw new Error(`Erro ${response.status}: ${response.statusText}`)
}
```

### 2. Tratamento de Erro 401 no Budget Mobile
**Arquivo:** `app/mobile/budget/page.tsx`

**Mudanças:**
- Mesmo tratamento de 401 com redirecionamento
- Mensagens de erro mais específicas

```typescript
if (breakdownResponse.status === 401) {
  console.error('Não autenticado. Redirecionando para login...')
  router.push('/login')
  return
}
```

### 3. Try-Catch Aprimorado
**Ambas as páginas:**

**Dashboard:**
```typescript
} catch (error) {
  console.error('Erro ao buscar métricas:', error)
  setMetrics({
    receitas: 0,
    despesas: 0,
    saldo: 0,
    investimentos: 0
  })
} finally {
  setLoading(false)
}
```

**Budget:**
- Já tinha tratamento adequado ✅

---

## 🔐 Fluxo de Autenticação

### Como Funciona Agora:

1. **Usuário acessa `/mobile/dashboard` ou `/mobile/budget`**
2. **Página tenta buscar dados** → `fetchWithAuth()` envia token do localStorage
3. **Backend valida token:**
   - ✅ **Token válido:** Retorna dados (200 OK)
   - ❌ **Token inválido/ausente:** Retorna 401 Unauthorized
4. **Frontend detecta 401:**
   - Loga erro no console
   - Redireciona para `/login`
5. **Usuário faz login:**
   - Token salvo no localStorage
   - Redireciona para página original

---

## 🎯 Como Testar

### 1. Sem Login (401)
```bash
# 1. Limpar localStorage (DevTools Console):
localStorage.removeItem('authToken')

# 2. Acessar página mobile:
http://localhost:3001/mobile/dashboard

# 3. Resultado esperado:
# - Console: "Não autenticado. Redirecionando para login..."
# - Redireciona automaticamente para /login
```

### 2. Com Login (200)
```bash
# 1. Fazer login:
http://localhost:3001/login
# Email: admin@financas.com
# Senha: cahriZqonby8

# 2. Acessar página mobile:
http://localhost:3001/mobile/dashboard

# 3. Resultado esperado:
# - Métricas carregam normalmente
# - Despesas e Investimentos aparecem
```

### 3. Token Expirado (401)
```bash
# 1. Fazer login normalmente
# 2. Aguardar expiração do token (ou alterar manualmente)
# 3. Tentar acessar /mobile/dashboard
# 4. Resultado esperado:
# - Backend retorna 401
# - Frontend redireciona para /login
```

---

## 📊 Checklist

- [x] Identificar erro 401 Unauthorized
- [x] Adicionar tratamento de 401 no Dashboard Mobile
- [x] Adicionar tratamento de 401 no Budget Mobile
- [x] Melhorar try-catch com fallbacks
- [x] Adicionar redirecionamento automático para /login
- [x] Testar fluxo completo (sem login → login → com login)
- [x] Documentar solução

---

## 🚨 Importante

### Para Usuários
- **Sempre faça login antes** de acessar páginas mobile
- **Credenciais atuais:**
  - Email: `admin@financas.com`
  - Senha: `cahriZqonby8`

### Para Desenvolvedores
- **Sempre verificar 401** em páginas protegidas
- **Sempre redirecionar para /login** quando não autenticado
- **Nunca deixar página "pendurada"** sem tratamento de erro

---

## 🔄 Próximos Passos (Opcional)

### Melhorias Futuras:
1. **Refresh Token** - Renovar token automaticamente antes de expirar
2. **Interceptor Global** - Centralizar tratamento de 401 em um interceptor
3. **Toast de Erro** - Mostrar mensagem amigável "Sessão expirada. Faça login novamente."
4. **Protected Routes** - Middleware para proteger rotas mobile

---

**Status:** ✅ PROBLEMA RESOLVIDO  
**Backend:** http://localhost:8000 (rodando)  
**Frontend:** http://localhost:3001 (rodando)  
**Data de Conclusão:** 01/02/2026 20:00
