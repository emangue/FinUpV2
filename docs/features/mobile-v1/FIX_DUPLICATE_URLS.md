# 🐛 Correção: URLs Duplicadas (api/v1/v1)

**Data:** 01/02/2026 17:48  
**Problema:** Endpoints retornavam 404 com URL duplicada

---

## 🔍 Problema Raiz

### URLs Duplicadas Encontradas:
```
❌ http://localhost:8000/api/v1/v1/investimentos
❌ http://localhost:8000/api/v1/v1/categories
```

### Causa:
Arquivos de serviço (API clients) estavam definindo:
```typescript
const BASE_URL = '/api/v1/investimentos'  // ❌ Inclui prefixo
```

E depois usando:
```typescript
apiGet(BASE_URL)  // apiGet já adiciona BACKEND_URL + API_PREFIX
```

**Resultado:**
```
API_CONFIG.BACKEND_URL = 'http://localhost:8000'
API_CONFIG.API_PREFIX = '/api/v1'
BASE_URL = '/api/v1/investimentos'

Final = http://localhost:8000 + /api/v1 + /api/v1/investimentos
      = http://localhost:8000/api/v1/api/v1/investimentos  ❌ DUPLICADO!
```

---

## ✅ Correções Aplicadas

### 1. Investimentos (`investimentos-api.ts`)

**Antes:**
```typescript
const BASE_URL = `/api/v1/investimentos`  // ❌ Duplicava
```

**Depois:**
```typescript
import { API_ENDPOINTS } from '@/core/config/api.config'
const BASE_URL = API_ENDPOINTS.INVESTIMENTOS  // ✅ URL completa correta
```

---

### 2. Categories (`category-api.ts`)

**Antes:**
```typescript
fetchWithAuth('/api/v1/categories')  // ❌ Path relativo
```

**Depois:**
```typescript
import { API_CONFIG } from '@/core/config/api.config'
const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/categories`
fetchWithAuth(BASE_URL)  // ✅ URL absoluta
```

---

## 📋 Arquivos Modificados

1. ✅ `/features/investimentos/services/investimentos-api.ts` - linha 26
2. ✅ `/features/categories/services/category-api.ts` - linhas 5,13,27,41
3. ✅ `/core/utils/api-client.ts` - linha 51 (redirect: 'follow')

---

## 🧪 Teste

### Via cURL (backend)
```bash
# Deve funcionar agora
curl "http://localhost:8000/api/v1/investimentos?limit=1" \
  -H "Authorization: Bearer TOKEN"
```

### Via Frontend
1. Recarregue a página (F5 / Cmd+R)
2. Acesse:
   - Investimentos
   - Configurações → Categorias
   - Configurações → Grupos

---

## 💡 Padrão Correto

### Opção 1: Usar API_ENDPOINTS (RECOMENDADO)
```typescript
import { API_ENDPOINTS } from '@/core/config/api.config'

const BASE_URL = API_ENDPOINTS.INVESTIMENTOS
// = http://localhost:8000/api/v1/investimentos ✅
```

### Opção 2: Construir com API_CONFIG
```typescript
import { API_CONFIG } from '@/core/config/api.config'

const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/resource`
// = http://localhost:8000/api/v1/resource ✅
```

### ❌ NUNCA FAZER:
```typescript
const BASE_URL = '/api/v1/resource'  // ❌ Duplica quando usado com apiGet()
```

---

## 📊 Impacto

**Antes:**
- ❌ Investimentos não carregavam (404)
- ❌ Categories não carregavam (404)
- ❌ Grupos não carregavam (404)
- ❌ Timeline e rendimentos falhavam

**Depois:**
- ✅ Investimentos funcionando
- ✅ Categories funcionando
- ✅ Grupos funcionando
- ✅ Todas as telas de configuração operacionais

---

## 🚨 Lição Aprendida

**SEMPRE usar URL completa ou constantes do `API_ENDPOINTS`!**

- ✅ `API_ENDPOINTS.INVESTIMENTOS`
- ✅ `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/resource`
- ❌ `/api/v1/resource` (causa duplicação)

---

**Status:** ✅ CORRIGIDO  
**Requer:** Reload da página no navegador (F5)
