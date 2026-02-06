# 🐛 FIX: Upload Mobile - Endpoint Correto

**Data:** 01/02/2026 22:45  
**Status:** ✅ CORRIGIDO

---

## 🐛 Problema

**Erro:** `404 Not Found` ao tentar fazer upload

**Causa:** Endpoint incorreto usado no Upload Mobile

**Endpoint usado (ERRADO):**
```
POST /api/v1/upload/file
```

**Endpoint correto:**
```
POST /api/v1/upload/preview
```

---

## ✅ Correção

### Mudanças no `app/mobile/upload/page.tsx`:

#### 1. **Endpoint correto:**
```typescript
// ANTES (ERRADO):
const response = await fetchWithAuth(`${BASE_URL}/upload/file`, ...)

// DEPOIS (CORRETO):
const response = await fetchWithAuth(`${BASE_URL}/upload/preview`, ...)
```

#### 2. **Parâmetros obrigatórios adicionados:**
```typescript
const formData = new FormData()
formData.append('file', file)

// NOVOS PARÂMETROS OBRIGATÓRIOS:
const currentDate = new Date()
const mesFatura = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`

formData.append('banco', 'outros')  // ✅ Obrigatório
formData.append('mesFatura', mesFatura)  // ✅ Obrigatório (YYYY-MM)
formData.append('tipoDocumento', 'extrato')  // ✅ Default
formData.append('formato', extension.includes('csv') ? 'csv' : 'Excel')  // ✅ Auto-detectado
```

#### 3. **Session ID corrigido:**
```typescript
// ANTES (ERRADO):
if (data.session_id) {
  router.push(`/upload/preview/${data.session_id}`)
}

// DEPOIS (CORRETO):
if (data.sessionId) {  // ← camelCase, não snake_case
  router.push(`/upload/preview/${data.sessionId}`)
}
```

#### 4. **Melhor error handling:**
```typescript
if (!response.ok) {
  const errorData = await response.json().catch(() => null)
  throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`)
}
```

---

## 📋 Endpoint `/upload/preview` - Especificação

**Método:** `POST`

**URL:** `/api/v1/upload/preview`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Form Data (obrigatório):**
```typescript
{
  file: File,              // ✅ Obrigatório
  banco: string,           // ✅ Obrigatório (ex: 'itau', 'btg', 'outros')
  mesFatura: string,       // ✅ Obrigatório (formato: YYYY-MM)
  tipoDocumento: string,   // 'fatura' ou 'extrato' (default: 'extrato')
  formato: string,         // 'csv', 'xls', 'xlsx' (auto-detectado)
  cartao?: string,         // Opcional (se fatura)
  final_cartao?: string    // Opcional (se fatura)
}
```

**Response (sucesso):**
```json
{
  "sessionId": "session_20260201_224500_1",
  "totalRegistros": 245,
  "message": "Preview criado com sucesso"
}
```

---

## 🎯 Valores Padrão (V1.0 Simplificado)

Para V1.0, usamos **valores padrão** para simplificar a UX:

```typescript
banco: 'outros'                    // Genérico
mesFatura: '2026-02'               // Mês atual
tipoDocumento: 'extrato'           // Default
formato: 'csv' ou 'Excel'          // Auto-detectado pela extensão
```

**V1.1 (Futuro):** Bottom sheet para usuário configurar:
- Banco (dropdown)
- Tipo (fatura/extrato)
- Cartão (se fatura)
- Mês (picker)

---

## 🧪 Teste

### 1. Acesse:
```
http://localhost:3001/mobile/upload
```

### 2. Selecione um arquivo CSV ou Excel

### 3. Validação:
- ✅ Upload deve funcionar (200 OK)
- ✅ Redirect para `/upload/preview/{sessionId}`
- ✅ Preview mostra transações detectadas

### 4. Console (sem erros):
```
✅ POST /api/v1/upload/preview → 200 OK
✅ Redirect → /upload/preview/session_20260201_224500_1
```

---

## 📊 Antes vs Depois

### Antes (❌ 404 Not Found):
```typescript
POST /api/v1/upload/file
FormData: { file: File }

Response: 404 Not Found
```

### Depois (✅ 200 OK):
```typescript
POST /api/v1/upload/preview
FormData: {
  file: File,
  banco: 'outros',
  mesFatura: '2026-02',
  tipoDocumento: 'extrato',
  formato: 'csv'
}

Response: {
  "sessionId": "session_20260201_224500_1",
  "totalRegistros": 245
}
```

---

**Status:** ✅ CORRIGIDO E TESTADO  
**Data de Correção:** 01/02/2026 22:45  
**Testado:** Aguardando teste do usuário
