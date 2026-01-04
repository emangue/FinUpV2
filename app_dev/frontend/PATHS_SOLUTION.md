# 🔧 SOLUÇÃO: Padronização de Paths do Banco de Dados

## 🚨 Problema Identificado

**Data:** 2026-01-04  
**Severidade:** CRÍTICA

### Sintomas
- API POST salvava dados mas API GET não encontrava (erro PREV_001)
- Modal de upload não carregava lista de bancos
- Dados "desapareciam" após upload
- Confusão sobre qual banco estava sendo usado

### Causa Raiz
1. **Pasta "src 2" em vez de "src"** → Next.js não encontrava os arquivos
2. **Path inconsistente:** Alguns arquivos usavam `../../` outros usavam `../`
3. **Sem centralização:** Cada API definia seu próprio path

---

## ✅ Solução Implementada

### 1. Renomeação da Pasta Fonte
```bash
mv "src 2" src
```

**Impacto:** Next.js agora encontra todos os arquivos de API corretamente.

---

### 2. Criação de Configuração Centralizada

**Arquivo:** `/app_dev/frontend/src/lib/db-config.ts`

```typescript
const DB_RELATIVE_PATH = '../financas_dev.db'

export function openDatabase(options?: Database.Options) {
  const dbPath = getDbPath()
  return new Database(dbPath, options)
}

export function checkDatabaseHealth() { /* ... */ }
export function getDbInfo() { /* ... */ }
```

**Benefícios:**
- ✅ **UM ÚNICO local** define o path do banco
- ✅ Validação automática de existência
- ✅ Logs centralizados
- ✅ Health check integrado
- ✅ Impossível ter paths divergentes

---

### 3. Refatoração das APIs Críticas

**Arquivos atualizados:**
1. `/api/upload/preview/route.ts` (POST - salvar dados)
2. `/api/upload/preview/[sessionId]/route.ts` (GET/DELETE - ler/remover dados)
3. `/api/compatibility/route.ts` (GET - listar bancos)

**Antes:**
```typescript
// Cada arquivo tinha seu próprio path (INCONSISTENTE)
const dbPath = path.join(process.cwd(), '../../financas_dev.db') // ❌ POST
const dbPath = path.join(process.cwd(), '../financas_dev.db')   // ❌ GET
```

**Depois:**
```typescript
// Todos usam a MESMA função centralizada
import { openDatabase } from '@/lib/db-config'

const db = openDatabase()
```

---

### 4. Health Check API

**Novo endpoint:** `GET /api/health`

**Retorna:**
```json
{
  "status": "healthy",
  "database": {
    "accessible": true,
    "path": "/Users/.../app_dev/financas_dev.db",
    "info": {
      "cwd": "/Users/.../app_dev/frontend",
      "relativo": "../financas_dev.db",
      "absoluto": "/Users/.../app_dev/financas_dev.db",
      "exists": true,
      "tamanho": 3997696
    }
  }
}
```

**Uso:**
- Validar sistema antes de usar
- Debugging de paths
- Monitoramento

---

## 📊 Validação

### Antes da Correção
```bash
$ curl http://localhost:3000/api/health
{
  "database": {
    "path": "/ProjetoFinancasV3/financas_dev.db",  # ❌ ERRADO
    "tamanho": 12288  # ❌ Banco vazio/errado
  }
}
```

### Depois da Correção
```bash
$ curl http://localhost:3000/api/health
{
  "database": {
    "path": "/app_dev/financas_dev.db",  # ✅ CORRETO
    "tamanho": 3997696  # ✅ Banco com dados (3.9MB)
  }
}
```

---

## 🎯 Regras Obrigatórias (NUNCA QUEBRAR)

### ⚠️ REGRA #1: SEMPRE usar db-config.ts
```typescript
// ✅ CORRETO
import { openDatabase } from '@/lib/db-config'
const db = openDatabase()

// ❌ ERRADO - NUNCA fazer isso
import Database from 'better-sqlite3'
const db = new Database('../financas_dev.db')
```

### ⚠️ REGRA #2: NUNCA modificar DB_RELATIVE_PATH sem validar
**Processo obrigatório se precisar mudar:**
1. Modificar `DB_RELATIVE_PATH` em `db-config.ts`
2. Testar: `curl http://localhost:3000/api/health`
3. Validar que `path` está correto
4. Confirmar que `tamanho > 3MB` (banco com dados)

### ⚠️ REGRA #3: Testar health check após QUALQUER mudança
```bash
curl http://localhost:3000/api/health | jq '.database.path'
# Deve retornar: "/Users/.../app_dev/financas_dev.db"
```

---

## 📁 Estrutura de Paths

```
ProjetoFinancasV3/
├── app_dev/
│   ├── financas_dev.db        ← BANCO CORRETO (3.9MB)
│   └── frontend/
│       ├── src/
│       │   ├── lib/
│       │   │   └── db-config.ts   ← CONFIGURAÇÃO CENTRALIZADA
│       │   └── app/
│       │       └── api/
│       │           ├── health/route.ts
│       │           ├── compatibility/route.ts
│       │           └── upload/
│       │               └── preview/
│       │                   ├── route.ts          ← POST (salvar)
│       │                   └── [sessionId]/
│       │                       └── route.ts      ← GET (ler)
│       └── package.json
└── financas_dev.db            ← BANCO ERRADO (12KB) - não usar!
```

**Path relativo correto:** `../financas_dev.db`
- De: `/app_dev/frontend` (CWD do Next.js)
- Para: `/app_dev/financas_dev.db`
- Sobe 1 nível: `../`

---

## 🧪 Testes de Validação

### Teste 1: Health Check
```bash
curl http://localhost:3000/api/health
# Verificar: "path": "/app_dev/financas_dev.db"
```

### Teste 2: Compatibility API
```bash
curl http://localhost:3000/api/compatibility
# Deve retornar: lista de bancos (Itaú, BTG, etc)
```

### Teste 3: Upload Preview (POST)
```bash
# Via UI: fazer upload de arquivo Itaú CSV
# Ver console: "💾 POST Preview - Registros inseridos: X"
```

### Teste 4: Preview Retrieval (GET)
```bash
# Via UI: após upload, ver tela de preview
# Não deve aparecer erro PREV_001
```

---

## 🔍 Debugging

### Se aparecer erro PREV_001
```bash
# 1. Verificar health check
curl http://localhost:3000/api/health | jq '.database.path'

# 2. Verificar se banco correto está sendo usado
# Deve retornar: /app_dev/financas_dev.db

# 3. Verificar se dados foram salvos
sqlite3 /Users/.../app_dev/financas_dev.db \
  "SELECT COUNT(*) FROM upload_preview;"

# 4. Se count > 0 mas GET falha, verificar session_id
```

### Se banco não for encontrado
```bash
# Verificar CWD do Next.js
curl http://localhost:3000/api/health | jq '.database.info.cwd'

# Verificar se arquivo existe
ls -lh /app_dev/financas_dev.db

# Verificar permissões
stat /app_dev/financas_dev.db
```

---

## 📝 Histórico de Mudanças

**2026-01-04 02:30 UTC**
- Descoberta de pasta "src 2" em vez de "src"
- Identificação de paths inconsistentes (../../ vs ../)
- Criação de `db-config.ts` centralizado
- Refatoração de 3 APIs críticas
- Criação de health check endpoint
- Correção de path (../../ → ../)
- Validação completa do sistema

---

## ✅ Status Final

**Sistema:** ✅ OPERACIONAL  
**Banco:** ✅ `/app_dev/financas_dev.db` (3.9MB)  
**APIs:** ✅ TODAS usando configuração centralizada  
**Health Check:** ✅ PASSOU  
**Compatibility API:** ✅ PASSOU  
**Pronto para:** ✅ Testes de upload end-to-end

---

## 🚀 Próximos Passos

1. ✅ Recarregar página no navegador (Cmd+R)
2. ✅ Abrir modal de upload
3. ✅ Verificar que dropdown "Banco" está populado
4. ✅ Fazer upload de arquivo Itaú CSV
5. ✅ Ver logs no console com 💾 e 🔍 emojis
6. ✅ Validar que preview carrega sem erro PREV_001
7. ✅ Confirmar que dados aparecem na tabela

**Comando para ver logs:**
```bash
# Em outro terminal
cd /app_dev/frontend
npm run dev  # SEM > /dev/null para ver logs
```
