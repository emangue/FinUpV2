# 🎯 BUG #10 - Upload Dialog URL Incorreta

**Data:** 01/02/2026 17:58  
**Prioridade:** CRÍTICA  
**Status:** ✅ CORRIGIDO

---

## 🐛 Problema

Upload não funcionava - erro 422 "Unprocessable Entity".

**Frontend enviava:**
- `Content-Type: application/json` (ERRADO para FormData)

**Backend esperava:**
- `Content-Type: multipart/form-data` (com boundary)

---

## 🔍 Causa Raiz

`fetchWithAuth` estava adicionando `Content-Type: application/json` **sempre**, mesmo para FormData.

**Problema:**
```typescript
const headers = {
  'Content-Type': 'application/json',  // ❌ SOBRESCREVE multipart/form-data
  ...token,
  ...options.headers
}
```

Quando enviamos FormData, o **browser deve definir o Content-Type automaticamente** com o `boundary` correto:
```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...
```

---

## ✅ Correções Aplicadas

### 1. URL de Upload (Correção #1)

**Arquivo:** `/features/upload/components/upload-dialog.tsx`

**Antes:**
```typescript
const response = await fetchWithAuth('/api/upload/preview', {
  method: 'POST',
  body: formData
})
```

**Depois:**
```typescript
const BASE_URL_UPLOAD_PREVIEW = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/preview`

const response = await fetchWithAuth(BASE_URL_UPLOAD_PREVIEW, {
  method: 'POST',
  body: formData
})
```

---

### 2. Content-Type para FormData (Correção #2) ✨

**Arquivo:** `/core/utils/api-client.ts`

**Antes:**
```typescript
const headers = {
  'Content-Type': 'application/json',  // ❌ Sempre
  ...token,
  ...options.headers
}
```

**Depois:**
```typescript
// Detectar se body é FormData
const isFormData = options.body instanceof FormData

const headers: HeadersInit = {
  ...(!isFormData && { 'Content-Type': 'application/json' }),  // ✅ Só se NÃO for FormData
  ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  ...options.headers,
}
```

---

## 📋 Arquivos Modificados

1. `upload-dialog.tsx` - Adicionado `BASE_URL_UPLOAD_PREVIEW` (linha 140)
2. `api-client.ts` - Detectar FormData e não adicionar Content-Type (linhas 24-56) ✨

---

## ⚠️ Lição Aprendida

### Sobre URLs:
**SEMPRE verificar que a URL usa o padrão completo:**
```typescript
`${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/resource`
// = http://localhost:8000/api/v1/resource ✅
```

### Sobre Content-Type:
**NUNCA definir Content-Type manualmente para FormData:**
```typescript
// ❌ ERRADO
headers: {
  'Content-Type': 'application/json',  // Sobrescreve multipart/form-data
}

// ✅ CORRETO - Detectar FormData
const isFormData = options.body instanceof FormData
const headers = {
  ...(!isFormData && { 'Content-Type': 'application/json' }),
}
```

**Browser adiciona automaticamente:**
```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
```

---

## 🔍 Outros Problemas Encontrados (Não Críticos)

Encontrados 4 arquivos adicionais com URLs incompletas (sem `/v1`):

1. `add-group-modal.tsx` - `/api/grupos` (deveria ser `/api/v1/grupos`)
2. `edit-transaction-modal.tsx` - `/api/categories/grupos-subgrupos`

**Ação:** Corrigir em Sprint futuro (não estão causando erros ativos).

---

**Status:** ✅ CORRIGIDO  
**Requer:** Reload da página (F5)
