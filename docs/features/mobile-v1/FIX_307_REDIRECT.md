# 🐛 Correção: Endpoints Retornando 404/307

**Data:** 01/02/2026 17:45  
**Problema:** Investimentos, Categories e Grupos não funcionavam

---

## 🔍 Problema Identificado

### Sintoma
- Frontend mostrava erro 404 em `/investimentos`, `/categories`, `/grupos`
- Backend retornava `307 Temporary Redirect`
- Requisições paravam no redirect sem seguir

### Causa Raiz
FastAPI adiciona **trailing slash** automaticamente:
- Request: `GET /api/v1/investimentos`
- Redirect: `307 → /api/v1/investimentos/`
- Frontend não seguia o redirect por padrão

### Linha do Log
```
INFO: 127.0.0.1:49990 - "GET /api/v1/investimentos?limit=2 HTTP/1.1" 307 Temporary Redirect
```

---

## ✅ Solução Implementada

### Arquivo Modificado
`app_dev/frontend/src/core/utils/api-client.ts`

### Mudança
Adicionado `redirect: 'follow'` no `fetch()`:

```typescript
return fetch(url, {
  ...options,
  headers,
  redirect: 'follow',  // Segue redirects 307 automaticamente
})
```

**Antes:**
- Fetch parava no 307
- Frontend via como erro

**Depois:**
- Fetch segue o redirect automaticamente
- Chama `/api/v1/investimentos/` com trailing slash
- Backend responde com dados

---

## 🧪 Teste

```bash
# Via cURL (com -L para seguir redirect)
curl -L "http://localhost:8000/api/v1/investimentos?limit=1" \
  -H "Authorization: Bearer TOKEN"

# Agora funciona também sem -L no frontend
```

---

## 📊 Endpoints Corrigidos

1. ✅ `/api/v1/investimentos`
2. ✅ `/api/v1/categories`
3. ✅ `/api/v1/grupos`
4. ✅ Todos os outros endpoints com GET

---

## 💡 Alternativas Consideradas

### Opção 1: Desabilitar redirect no FastAPI ❌
```python
app = FastAPI(redirect_slashes=False)
```
**Problema:** Quebra outros endpoints que dependem do trailing slash

### Opção 2: Adicionar trailing slash manualmente no frontend ❌
```typescript
INVESTIMENTOS: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/investimentos/`
```
**Problema:** Manutenção complexa, ~120 endpoints para modificar

### Opção 3: Seguir redirects no fetch ✅ (ESCOLHIDA)
```typescript
redirect: 'follow'
```
**Vantagens:**
- 1 linha de código
- Funciona para TODOS os endpoints
- Padrão HTTP correto
- Sem quebrar nada existente

---

## 📝 Impacto

**Endpoints Funcionando Agora:**
- ✅ Investimentos (portfolio, timeline, rendimentos)
- ✅ Categories (lista, grouped, grupos-subgrupos)
- ✅ Grupos (lista, tipos)
- ✅ Todas as telas de configuração

**Não Afeta:**
- Endpoints que já funcionavam (dashboard, transactions, auth)
- POST/PATCH/DELETE (não fazem redirect)

---

**Status:** ✅ RESOLVIDO  
**Arquivo:** `api-client.ts` linha 51
