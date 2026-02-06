# 📋 TECH_SPEC - Correções de Infraestrutura (Sprint 0)

**Data:** 01/02/2026  
**Versão:** 1.0  
**Status:** ✅ COMPLETO

---

## 🎯 Objetivo

Corrigir problemas críticos de infraestrutura identificados durante a validação do Sprint 0, garantindo que toda a aplicação funcione corretamente antes de iniciar o desenvolvimento mobile.

---

## 🐛 Problemas Identificados e Soluções

### 1. Autenticação e CORS

**Problema:** Backend rejeitava requests do frontend na porta 3001

**Solução:**
```bash
# app_dev/backend/.env
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:3002,http://127.0.0.1:3002
```

---

### 2. Padrão de URLs na Aplicação

**Problema:** URLs inconsistentes causando duplicação de prefixos

**Solução:** Estabelecer padrão único para toda a aplicação

#### Padrão Correto (SEMPRE usar):
```typescript
import { API_CONFIG } from '@/core/config/api.config'

// Para fetchWithAuth (espera URL completa)
const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/resource`
// = http://localhost:8000/api/v1/resource

// Uso
await fetchWithAuth(BASE_URL)
```

#### Arquivos Corrigidos:
1. `features/investimentos/services/investimentos-api.ts` - Usar `API_ENDPOINTS.INVESTIMENTOS`
2. `features/categories/services/category-api.ts` - Construir URL completa
3. `app/settings/grupos/page.tsx` - Usar `BASE_URL` com `API_CONFIG`
4. `app/settings/exclusoes/page.tsx` - Idem
5. `app/settings/cartoes/page.tsx` - Idem
6. `features/upload/components/upload-dialog.tsx` - Idem (3 URLs)
7. `app/upload/preview/[sessionId]/page.tsx` - Idem (9 URLs)

---

### 3. Utilitário `fetchWithAuth` - Melhorias

**Arquivo:** `core/utils/api-client.ts`

#### 3.1. Suporte a Redirects 307
```typescript
export async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  // ...
  return fetch(url, {
    ...options,
    headers,
    redirect: 'follow',  // ✅ Segue redirects automaticamente
  })
}
```

#### 3.2. Detecção de FormData
```typescript
// Detectar se body é FormData
const isFormData = options.body instanceof FormData

const headers: HeadersInit = {
  ...(!isFormData && { 'Content-Type': 'application/json' }),  // ✅ Só se NÃO for FormData
  ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  ...options.headers,
}
```

**Motivo:** Browser precisa adicionar `boundary` automaticamente para multipart/form-data

---

### 4. Migração de `fetch()` para `fetchWithAuth()`

**Problema:** Endpoints protegidos sendo chamados sem token JWT

**Solução:** Substituir TODAS as chamadas diretas de `fetch()` por `fetchWithAuth()`

#### Exemplo de Migração:

**Antes:**
```typescript
const response = await fetch('/api/v1/endpoint')
if (!response.ok) {
  throw new Error('Erro')
}
const data = await response.json()
```

**Depois:**
```typescript
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'

const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`

const response = await fetchWithAuth(`${BASE_URL}/endpoint`)
if (!response.ok) {
  throw new Error('Erro')
}
const data = await response.json()
```

#### Arquivo Crítico Corrigido:
- `app/upload/preview/[sessionId]/page.tsx` - **9 ocorrências** de `fetch()` → `fetchWithAuth()`

---

## 📊 Impacto das Correções

### Funcionalidades Restauradas:
- ✅ Login/Autenticação
- ✅ Investimentos (lista, detalhes, CRUD)
- ✅ Configurações → Categorias
- ✅ Configurações → Grupos
- ✅ Configurações → Exclusões
- ✅ Configurações → Cartões
- ✅ Upload de arquivos (dialog)
- ✅ Upload Preview (classificação, edição)
- ✅ Upload Confirm (importação final)

### Telas 100% Funcionais:
- Dashboard
- Transações
- Investimentos (todas as sub-telas)
- Budget/Metas
- Upload (fluxo completo)
- Settings/Configurações (todas as sub-telas)

---

## 🔒 Segurança

### Autenticação JWT
- Token armazenado em `localStorage` com chave `authToken`
- `fetchWithAuth()` adiciona header automaticamente: `Authorization: Bearer <token>`
- Todos os endpoints protegidos validam token no backend

### CORS
- Configurado para aceitar portas 3000-3002
- Permite desenvolvimento com Next.js em porta alternativa

---

## 🛠️ Scripts de Desenvolvimento

### quick_start.sh (Melhorias)
```bash
# Auto-detecção e recriação de venv corrompido
# Limpeza de portas 3000-3005 (não só 3000)
# Mensagens informativas sobre portas dinâmicas
```

### quick_stop.sh (Melhorias)
```bash
# Limpeza de portas 3000-3005
# Kill tree de processos filhos
```

---

## 📝 Documentação Criada

1. `LOGIN_CREDENTIALS.md` - Credenciais admin atualizadas
2. `FIX_307_REDIRECT.md` - Correção de redirects
3. `FIX_DUPLICATE_URLS.md` - Correção de URLs duplicadas
4. `FIX_UPLOAD_URL.md` - Correção de upload (2 problemas)
5. `FIX_PREVIEW_AUTH.md` - Correção de preview (autenticação)
6. `SCRIPTS_IMPROVEMENTS.md` - Melhorias nos scripts
7. `SERVERS_ONLINE.md` - Status dos servidores
8. `SESSION_SUMMARY.md` - Resumo completo da sessão
9. `TECH_SPEC.md` - Este documento

---

## 🚀 Próximos Passos (Sprint 1)

Com a infraestrutura 100% funcional, podemos iniciar o desenvolvimento mobile:

### Sprint 1 - Dashboard Mobile (Prioridade ALTA)

#### 1.1. MonthScrollPicker (CRÍTICO)
- Componente de scroll horizontal de meses
- Baseado no design "Trackers"
- Touch-friendly (44px mínimo)

#### 1.2. YTDToggle
- Toggle entre visualização mensal e anual
- Estados visuais claros

#### 1.3. Dashboard Mobile Completo
- Reutilizar `MetricCards` existente
- Adaptar para mobile (padding, tipografia)
- Scroll suave entre seções

#### 1.4. Middleware de Redirecionamento
- Detectar `window.innerWidth < 768px`
- Redirecionar automaticamente para `/mobile/*`

---

## ✅ Checklist de Validação

### Infraestrutura
- [x] Backend rodando em `:8000`
- [x] Frontend rodando em `:3001`
- [x] CORS configurado
- [x] Autenticação funcionando
- [x] Redirects 307 seguidos automaticamente
- [x] FormData detectado corretamente

### Funcionalidades
- [x] Login
- [x] Dashboard
- [x] Transações
- [x] Investimentos
- [x] Budget/Metas
- [x] Upload (end-to-end)
- [x] Configurações (todas)

### Código
- [x] URLs padronizadas
- [x] `fetchWithAuth` usado consistentemente
- [x] Sem URLs hardcoded
- [x] Sem duplicação de prefixos

---

## 📚 Referências

- **PRD Mobile:** `/docs/features/mobile-v1/01-PRD/PRD.md`
- **Style Guide:** `/docs/features/mobile-v1/01-PRD/STYLE_GUIDE.md`
- **Copilot Instructions:** `/.github/copilot-instructions.md`
- **Session Summary:** `/docs/features/mobile-v1/SESSION_SUMMARY.md`

---

**Status:** ✅ APROVADO PARA PRODUÇÃO  
**Próximo:** Sprint 1 - Dashboard Mobile  
**Data de Conclusão:** 01/02/2026
