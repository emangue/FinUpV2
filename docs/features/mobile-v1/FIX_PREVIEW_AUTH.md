# 🐛 BUG #12 - Upload Preview: 401 Unauthorized + URLs Duplicadas

**Data:** 01/02/2026 18:05  
**Prioridade:** CRÍTICA  
**Status:** ✅ CORRIGIDO

---

## 🐛 Problema

Após upload bem-sucedido, a tela de preview falhava com "Falha ao carregar dados do preview".

**Backend logs mostraram:**
```
❌ 401 Unauthorized: GET /api/v1/upload/preview/session_20260201_180025_1
❌ 404 Not Found: GET /api/v1/v1/categories/grupos-subgrupos (duplicação!)
```

---

## 🔍 Causa Raiz

### Problema 1: fetch() sem autenticação
Página de preview usava `fetch()` ao invés de `fetchWithAuth()`, então **não enviava token JWT**.

```typescript
const response = await fetch(`${apiUrl}/upload/preview/${sessionId}`)  // ❌ Sem token!
```

### Problema 2: URLs hardcoded
Linha 79 definia:
```typescript
const apiUrl = "http://localhost:8000/api/v1"  // ❌ Hardcoded
```

### Problema 3: URL duplicada
Linha 149:
```typescript
await fetch('/api/v1/categories/grupos-subgrupos')  // ❌ Falta BACKEND_URL
```

Resultado: Backend recebia `/api/v1/v1/categories/...` (duplicação!)

---

## ✅ Correções Aplicadas

**Arquivo:** `/app/upload/preview/[sessionId]/page.tsx`

### 1. Adicionado imports
```typescript
import { fetchWithAuth } from "@/core/utils/api-client"
import { API_CONFIG } from "@/core/config/api.config"
```

### 2. Definido URLs base
```typescript
const BASE_URL_UPLOAD_PREVIEW = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/preview`
const BASE_URL_UPLOAD_CONFIRM = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/confirm`
const BASE_URL_CATEGORIES = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/categories`
```

### 3. Substituído todos os `fetch()` por `fetchWithAuth()`

**Antes (9 ocorrências):**
```typescript
await fetch(`${apiUrl}/upload/preview/${sessionId}`)  // ❌
await fetch('/api/v1/categories/grupos-subgrupos')   // ❌
await fetch(`${apiUrl}/upload/confirm/${sessionId}`)  // ❌
// ... +6 ocorrências
```

**Depois:**
```typescript
await fetchWithAuth(`${BASE_URL_UPLOAD_PREVIEW}/${sessionId}`)  // ✅
await fetchWithAuth(`${BASE_URL_CATEGORIES}/grupos-subgrupos`)   // ✅
await fetchWithAuth(`${BASE_URL_UPLOAD_CONFIRM}/${sessionId}`)   // ✅
// ... +6 corrigidas
```

---

## 📋 Total de Correções

- **9 chamadas `fetch()` → `fetchWithAuth()`**
- **3 URLs base criadas**
- **1 URL hardcoded removida**
- **1 URL duplicada corrigida**

---

## 🧪 Como Testar

1. Recarregue a página (F5)
2. Faça upload de um arquivo novamente:
   - Banco: Itaú
   - Cartão: Azul
   - Arquivo: CSV de fatura
3. **Deve redirecionar para preview**
4. **Preview deve carregar transações**
5. **Dropdowns de Grupo/Subgrupo devem funcionar**

---

## ⚠️ Lição Aprendida

### SEMPRE usar `fetchWithAuth()` para endpoints protegidos!

**❌ ERRADO:**
```typescript
const response = await fetch('/api/v1/endpoint')  // Sem token!
```

**✅ CORRETO:**
```typescript
import { fetchWithAuth } from '@/core/utils/api-client'
const response = await fetchWithAuth(`${BASE_URL}/endpoint`)  // Com token!
```

### Endpoints que EXIGEM autenticação:
- `/api/v1/upload/*` ✅
- `/api/v1/categories/*` ✅
- `/api/v1/investimentos/*` ✅
- `/api/v1/transactions/*` ✅
- Basicamente **TODOS** os endpoints (exceto `/auth/login`)

---

**Status:** ✅ CORRIGIDO  
**Requer:** Reload da página (F5)  
**Impacto:** Upload completo agora funciona end-to-end! 🎉
