# 🔍 Diagnóstico - Upload 404 Mobile vs Desktop

**Data:** 06/02/2026  
**Status:** 🔴 Em investigação - NÃO FAZER MUDANÇAS SEM DIAGNÓSTICO

---

## 🎯 Objetivo

Entender **EXATAMENTE** por que o desktop funciona e o mobile retorna 404, sem fazer alterações no código.

---

## ✅ Fatos Conhecidos

### Desktop (/upload)
- ✅ **Funciona perfeitamente**
- ✅ POST `/api/v1/upload/preview` → 200 OK
- ✅ Usa `upload-dialog.tsx` component
- ✅ Usa `fetchWithAuth` wrapper
- ✅ FormData construído manualmente

### Mobile (/mobile/upload)
- ❌ **Erro 404 Not Found**
- ❌ POST `/api/v1/upload/preview` → 404 Not Found
- ❌ Usa `upload-api.ts` service
- ❌ Usa mesmo `fetchWithAuth` wrapper
- ❌ FormData construído idêntico?

### Backend
- ✅ **Endpoint existe** - verificado via OpenAPI
- ✅ Router registrado em main.py linha 63
- ✅ Curl direto funciona (retorna 401 sem token)
- ✅ OPTIONS request retorna 200 OK

---

## 🔬 Plano de Diagnóstico

### Etapa 1 - Capturar Request Desktop (BASELINE)

**Ação:** Usar desktop, fazer upload, capturar TUDO

**Dados a coletar:**
```
1. Network Tab (Chrome DevTools):
   - Request URL exata
   - Request Method
   - Status Code
   - Request Headers (TODOS)
   - Request Payload (FormData completo)
   - Response Headers
   - Response Body

2. Console (Chrome DevTools):
   - Todas as mensagens de log
   - Mensagens do api-client
   - Mensagens do upload-dialog

3. Backend Log:
   - Linha exata do log do request
   - Status code retornado
   - Tempo de processamento
```

### Etapa 2 - Capturar Request Mobile (COM ERRO)

**Ação:** Usar mobile, fazer upload, capturar TUDO (mesmos dados da Etapa 1)

### Etapa 3 - Comparação Lado-a-Lado

**Criar tabela:**

| Item | Desktop (✅ OK) | Mobile (❌ 404) | Diferença? |
|------|---------------|----------------|------------|
| URL exata | ? | ? | ? |
| Method | POST | POST | ✅ |
| Authorization header | Bearer ... | Bearer ... | ? |
| Content-Type | ? | ? | ? |
| FormData - file | ? | ? | ? |
| FormData - banco | ? | ? | ? |
| FormData - formato | ? | ? | ? |
| FormData - mesFatura | ? | ? | ? |
| FormData - tipoDocumento | ? | ? | ? |
| FormData - cartao | ? | ? | ? |

### Etapa 4 - Identificar Causa Raiz

**Após comparação, responder:**

1. Qual campo/header é diferente?
2. Por que essa diferença causa 404?
3. Onde no código essa diferença é gerada?

### Etapa 5 - Fix Cirúrgico

**Apenas após identificar causa:**

1. Modificar APENAS o ponto específico
2. Testar
3. Confirmar que funciona
4. Commitar com mensagem clara

---

## 🚫 O QUE NÃO FAZER

- ❌ Adicionar mais login automático
- ❌ Modificar estrutura de autenticação
- ❌ Criar novos middlewares
- ❌ Refatorar código que funciona
- ❌ Fazer múltiplas mudanças simultâneas

---

## 📊 Template de Captura

### Desktop Request (exemplo)
```
URL: http://localhost:8000/api/v1/upload/preview
Method: POST
Status: 200 OK

Headers:
  Authorization: Bearer eyJhbGciOiJIUz...
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...

FormData:
  file: [File] fatura-202601.csv (1234 bytes)
  banco: "Itau"
  formato: "CSV"
  mesFatura: "2026-01"
  tipoDocumento: "fatura"
  cartao: "Itaucard"
  final_cartao: "9266"
```

### Mobile Request (preencher)
```
URL: ?
Method: POST
Status: 404 Not Found

Headers:
  Authorization: ?
  Content-Type: ?

FormData:
  file: ?
  banco: ?
  formato: ?
  mesFatura: ?
  tipoDocumento: ?
  cartao: ?
```

---

## 💡 Próximos Passos

1. **PARAR** de fazer mudanças no código
2. Seguir plano de diagnóstico acima
3. Preencher tabela de comparação
4. Identificar diferença específica
5. Fazer fix cirúrgico pontual

---

**Última atualização:** 06/02/2026 - Emanuel  
**Status:** Aguardando coleta de dados
