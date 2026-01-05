# 🤖 Instruções GitHub Copilot - Sistema Modular de Finanças v4

## ⚠️ REGRAS CRÍTICAS - SEMPRE SEGUIR

### 🗄️ BANCO DE DADOS ÚNICO - REGRA INVIOLÁVEL

**Path absoluto único para TODO o sistema:**
```
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db
```

**Arquivos de configuração:**
1. **Backend:** `app_dev/backend/app/core/config.py` → `DATABASE_PATH`
2. **Frontend:** `app_dev/frontend/src/lib/db-config.ts` → `DB_ABSOLUTE_PATH`

**🚫 NUNCA:**
- Criar outro banco de dados em QUALQUER local:
  * ❌ `app_dev/financas.db`
  * ❌ `app_dev/financas_dev.db`
  * ❌ `app_dev/backend/financas.db`
  * ❌ Qualquer variação de path
- Usar paths relativos diferentes
- Modificar apenas um dos arquivos
- Criar cópias do banco
- Fazer backup manual (usar scripts de backup)

**✅ SEMPRE:**
- Usar path absoluto completo: `app_dev/backend/database/financas_dev.db`
- Se mudar, mudar nos 2 arquivos simultaneamente
- Testar backend E frontend após mudanças
- Ver `DATABASE_CONFIG.md` para detalhes
- Verificar `.gitignore` para ignorar duplicados

**🔍 VERIFICAÇÃO PERIÓDICA:**
```bash
# DEVE retornar APENAS 1 arquivo
find app_dev -name "*.db" -type f | grep -v node_modules
# Resultado esperado: app_dev/backend/database/financas_dev.db
```

---

## 🧹 LIMPEZA E ORGANIZAÇÃO - LIÇÕES APRENDIDAS

### ⚠️ ARQUIVOS QUE NÃO DEVEM EXISTIR

**Após refatoração modular, estes arquivos/pastas foram REMOVIDOS e NÃO devem ser recriados:**

#### Backend - Rotas Antigas (REMOVIDAS):
```
❌ app_dev/backend/app/routers/          # Substituído por domains/*/router.py
   ├── auth.py
   ├── cartoes.py
   ├── compatibility.py
   ├── dashboard.py
   ├── exclusoes.py
   ├── marcacoes.py
   ├── transactions.py
   ├── upload.py
   ├── upload_classifier.py
   └── users.py

❌ app_dev/backend/app/models/           # Substituído por domains/*/models.py
❌ app_dev/backend/app/schemas/          # Substituído por domains/*/schemas.py
```

#### Backend - Configurações Duplicadas (REMOVIDAS):
```
❌ app_dev/backend/app/config.py         # Usar app/core/config.py
❌ app_dev/backend/app/database.py       # Usar app/core/database.py
❌ app_dev/backend/app/dependencies.py   # Usar app/shared/dependencies.py
```

#### Frontend - Rotas API Antigas (REMOVIDAS):
```
❌ app_dev/frontend/src/app/api/cartoes/
❌ app_dev/frontend/src/app/api/categories/
❌ app_dev/frontend/src/app/api/compatibility/
❌ app_dev/frontend/src/app/api/dashboard/
❌ app_dev/frontend/src/app/api/exclusoes/
❌ app_dev/frontend/src/app/api/grupos/
❌ app_dev/frontend/src/app/api/health/
❌ app_dev/frontend/src/app/api/marcacoes/
❌ app_dev/frontend/src/app/api/transactions/
❌ app_dev/frontend/src/app/api/upload/
❌ app_dev/frontend/src/app/api/users/

✅ ÚNICO permitido: app_dev/frontend/src/app/api/[...proxy]/
```

#### Databases Duplicados (REMOVIDOS):
```
❌ app_dev/financas.db
❌ app_dev/financas_dev.db
❌ app_dev/backend/financas.db
❌ *.db.backup_* (backups manuais na pasta database/)

✅ ÚNICO oficial: app_dev/backend/database/financas_dev.db
```

### 🚨 SE VOCÊ CRIAR ALGUM DESSES ARQUIVOS:

**PARE IMEDIATAMENTE e pergunte:**
1. Por que estou criando isso?
2. Já existe equivalente na nova arquitetura?
3. Devo usar domínio isolado ou proxy genérico?
4. Estou duplicando funcionalidade?

**LEMBRE-SE:**
- Backend: Use `domains/*/router.py` (NUNCA `app/routers/`)
- Frontend: Use proxy `[...proxy]` (NUNCA rotas individuais)
- Config: Use `app/core/` e `app/shared/` (NUNCA duplicar na raiz)
- Database: Use APENAS o path oficial (NUNCA criar outros)

---

## 🏗️ ARQUITETURA MODULAR - BACKEND

### Estrutura de Domínios (DDD - Domain-Driven Design)

```
app_dev/backend/app/
├── core/                      # ✅ Configurações globais (NUNCA lógica de negócio)
│   ├── config.py              # Settings (DATABASE_PATH aqui)
│   ├── database.py            # SQLAlchemy setup
│   └── __init__.py
│
├── domains/                   # ✅ Domínios de negócio ISOLADOS
│   ├── transactions/          # Domínio de transações
│   │   ├── models.py          # JournalEntry model
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── repository.py      # TODAS as queries SQL
│   │   ├── service.py         # TODA lógica de negócio
│   │   ├── router.py          # Endpoints FastAPI
│   │   └── __init__.py
│   │
│   ├── users/                 # Domínio de usuários
│   ├── categories/            # Domínio de categorias
│   ├── cards/                 # Domínio de cartões
│   └── upload/                # Domínio de upload
│
├── shared/                    # ✅ Compartilhado entre domínios
│   ├── dependencies.py        # get_current_user_id, etc
│   └── __init__.py
│
└── main.py                    # FastAPI app setup
```

### Princípios de Isolamento de Domínios

**1. CADA DOMÍNIO É AUTOCONTIDO:**
```python
# ✅ CORRETO - Domínio transactions isolado
from app.domains.transactions.models import JournalEntry
from app.domains.transactions.service import TransactionService

# ❌ ERRADO - Não importar de outros domínios
from app.domains.users.models import User  # NÃO fazer isso em transactions
```

**2. CAMADAS OBRIGATÓRIAS (Repository → Service → Router):**

**Repository (Queries SQL isoladas):**
```python
# domains/transactions/repository.py
class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, id: str, user_id: int):
        return self.db.query(JournalEntry).filter(...).first()
    
    # TODAS as queries SQL aqui
```

**Service (Lógica de negócio isolada):**
```python
# domains/transactions/service.py
class TransactionService:
    def __init__(self, db: Session):
        self.repository = TransactionRepository(db)
    
    def update_transaction(self, id: str, user_id: int, data):
        # Validações de negócio
        # Cálculos
        # Chamadas ao repository
```

**Router (Apenas validação HTTP):**
```python
# domains/transactions/router.py
@router.patch("/{id}")
def update(id: str, data: UpdateSchema, db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.update_transaction(id, 1, data)
```

**3. REGRAS DE IMPORTAÇÃO:**

```python
# ✅ CORRETO
from app.core.database import Base, get_db
from app.shared.dependencies import get_current_user_id
from .models import JournalEntry  # Mesmo domínio
from .repository import TransactionRepository  # Mesmo domínio

# ❌ ERRADO
from app.models import JournalEntry  # Modelo monolítico antigo
from ..users.models import User  # Import cruzado entre domínios
from app.domains.categories import *  # Import * é proibido
```

### Quando Modificar um Domínio

**Cenário:** Adicionar campo `categoria` em transações

**✅ Passos corretos:**
1. Modificar `domains/transactions/models.py` (adicionar coluna)
2. Atualizar `domains/transactions/schemas.py` (adicionar campo nos schemas)
3. Modificar `domains/transactions/repository.py` (queries se necessário)
4. Atualizar `domains/transactions/service.py` (validações/cálculos)
5. Testar `domains/transactions/router.py`
6. **PARAR:** Não precisa tocar em users, categories, cards, upload!

**Arquivos afetados:** ~5 arquivos (todos no mesmo domínio)
**Antes da modularização:** ~15 arquivos espalhados

---

## ⚠️ REGRAS OBRIGATÓRIAS - SEMPRE SEGUIR

### 1. Antes de Modificar Qualquer Código

**SEMPRE verificar a versão atual do arquivo/módulo antes de fazer mudanças:**

```bash
# Verificar versão global do projeto
cat VERSION.md

# Verificar versão de arquivo específico (docstring no topo)
head -20 app/models.py | grep -i version
```

### 2. Ao Iniciar Modificações em Arquivos Críticos

**Arquivos Críticos que requerem versionamento:**
- `app/models.py` (schema do banco)
- `app/utils/hasher.py` (lógica de hash)
- `app/utils/processors/*.py` (processadores)
- `app/blueprints/*/routes.py` (rotas e lógica de negócio)
- `app/config.py` (configurações)

**Procedimento Obrigatório:**

1. **Marcar como desenvolvimento:**
   ```bash
   python scripts/version_manager.py start <caminho_do_arquivo>
   ```
   - Atualiza versão para `-dev` (ex: `2.1.0` → `2.1.0-dev`)
   - Cria branch git automática (ex: `dev/models-2025-12-27`)
   - Registra início da mudança

2. **Fazer as modificações necessárias**

3. **Testar completamente** (marcar como `-test` se necessário)

4. **Finalizar mudança:**
   ```bash
   python scripts/version_manager.py finish <caminho_do_arquivo> "Descrição da mudança"
   ```
   - Remove sufixo `-dev`/`-test`
   - Gera documentação automática em `changes/`
   - Cria commit git
   - Merge na branch principal

### 3. Nunca Commitar Versões de Desenvolvimento

**🚫 BLOQUEADO via git hook pre-commit:**
- Versões terminando em `-dev`
- Versões terminando em `-test`
- Mudanças em arquivos críticos sem documentação em `changes/`

### 4. Documentação Obrigatória de Mudanças

**Toda mudança em arquivo crítico deve gerar arquivo em `changes/`:**

Formato: `YYYY-MM-DD_nome-arquivo_descricao-curta.md`

Exemplo: `2025-12-27_models_adiciona-campo-categoria.md`

**Template automático gerado pelo `version_manager.py finish`**

### 5. Rollback de Mudanças

**Para reverter mudanças mal feitas:**

```bash
# Ver versões disponíveis
git tag -l "v*"

# Rollback para versão específica
python scripts/version_manager.py rollback v2.1.0

# Ou rollback manual via git
git checkout v2.1.0 -- <arquivo_especifico>
```

### 6. Releases de Novas Versões

**Quando um conjunto de mudanças está completo e testado:**

```bash
# Release patch (2.1.0 → 2.1.1) - bug fixes
python scripts/version_manager.py release patch

# Release minor (2.1.0 → 2.2.0) - novas features
python scripts/version_manager.py release minor

# Release major (2.1.0 → 3.0.0) - breaking changes
python scripts/version_manager.py release major
```

**O script automaticamente:**
- Incrementa versão em `VERSION.md` e `app/__init__.py`
- Agrega todos os arquivos de `changes/` no `CHANGELOG.md`
- Cria commit de release
- Cria tag git semântica (ex: `v2.2.0`)
- Limpa pasta `changes/` (move para histórico)

---

## 📋 Workflow Completo - Checklist

### Ao Receber Pedido de Modificação

- [ ] 1. Ler `VERSION.md` para ver versão atual
- [ ] 2. Identificar se arquivo é crítico (lista acima)
- [ ] 3. Se crítico: rodar `version_manager.py start <arquivo>`
- [ ] 4. Fazer modificações no código
- [ ] 5. Testar mudanças
- [ ] 6. Rodar `version_manager.py finish <arquivo> "descrição"`
- [ ] 7. Verificar que documentação foi gerada em `changes/`
- [ ] 8. Confirmar com usuário se mudança está OK
- [ ] 9. Se conjunto completo: perguntar se quer fazer release

### Exemplo Prático

**Usuário pede:** "Adicionar campo 'Categoria' no modelo JournalEntry"

**Resposta do AI:**

```bash
# 1. Iniciar mudança
python scripts/version_manager.py start app/models.py

# 2. [AI faz modificações em models.py]

# 3. Finalizar mudança
python scripts/version_manager.py finish app/models.py "Adiciona campo Categoria ao modelo JournalEntry para melhor classificação de transações"
```

**AI confirma:**
- ✅ Versão atualizada: `2.1.0-dev` → `2.1.1`
- ✅ Documentação gerada: `changes/2025-12-27_models_adiciona-campo-categoria.md`
- ✅ Commit criado: "feat(models): Adiciona campo Categoria ao JournalEntry [v2.1.1]"

---

## 🎯 Regras de Versionamento Semântico

### MAJOR (X.0.0)
- Breaking changes no schema do banco
- Mudanças incompatíveis na API
- Refatorações massivas de domínios

### MINOR (x.Y.0)
- Novas funcionalidades em domínios
- Novos campos no banco (não-breaking)
- Novos domínios/módulos

### PATCH (x.y.Z)
- Bug fixes em domínios específicos
- Melhorias de performance
- Correções de typos

---

## 🚫 PROIBIÇÕES ABSOLUTAS

### 1. Imports Cruzados entre Domínios
```python
# ❌ PROIBIDO
# Em domains/transactions/service.py
from app.domains.users.models import User  # NÃO!

# ✅ CORRETO
# Use shared/ para funcionalidades compartilhadas
from app.shared.dependencies import get_current_user_id
```

### 2. Lógica de Negócio no Router
```python
# ❌ PROIBIDO
@router.post("/")
def create(data: Schema, db: Session = Depends(get_db)):
    # Cálculos complexos aqui
    valor_positivo = abs(data.valor)  # NÃO!
    # Validações aqui
    if not data.grupo:  # NÃO!
        raise HTTPException(...)
    
    transaction = Model(**data.dict())
    db.add(transaction)
    db.commit()
    return transaction

# ✅ CORRETO
@router.post("/")
def create(data: Schema, db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.create(data)  # Lógica no service
```

### 3. Queries SQL no Service
```python
# ❌ PROIBIDO
class TransactionService:
    def get_transaction(self, id: str):
        # Query SQL aqui
        return self.db.query(Model).filter(...).first()  # NÃO!

# ✅ CORRETO
class TransactionService:
    def __init__(self, db: Session):
        self.repository = TransactionRepository(db)
    
    def get_transaction(self, id: str):
        return self.repository.get_by_id(id)  # Query no repository
```

### 4. Modificar Modelos de Outros Domínios
```python
# ❌ PROIBIDO
# Em domains/transactions/models.py
from app.domains.categories.models import BaseMarcacao  # NÃO!

class JournalEntry(Base):
    categoria = relationship(BaseMarcacao)  # NÃO criar relationships cruzadas!
```

### 5. Usar Paths Relativos para Database
```python
# ❌ PROIBIDO
DATABASE_PATH = "../database/financas.db"
DATABASE_PATH = "./financas.db"
DB_PATH = Path(__file__).parent / "database" / "financas.db"

# ✅ CORRETO - Path absoluto único
DATABASE_PATH = Path("/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db")
```

---

## ✅ PADRÕES OBRIGATÓRIOS

### 1. Criar Novo Domínio

```bash
mkdir -p app_dev/backend/app/domains/novo_dominio
```

**Arquivos obrigatórios:**
1. `models.py` - Modelo SQLAlchemy
2. `schemas.py` - Pydantic schemas (Create, Update, Response)
3. `repository.py` - Queries SQL isoladas
4. `service.py` - Lógica de negócio
5. `router.py` - Endpoints FastAPI
6. `__init__.py` - Exports

**Template de `__init__.py`:**
```python
from .models import NovoModel
from .schemas import NovoCreate, NovoUpdate, NovoResponse
from .service import NovoService
from .repository import NovoRepository
from .router import router

__all__ = [
    "NovoModel",
    "NovoCreate",
    "NovoUpdate",
    "NovoResponse",
    "NovoService",
    "NovoRepository",
    "router",
]
```

**Registrar em `main.py`:**
```python
from app.domains.novo_dominio.router import router as novo_router
app.include_router(novo_router, prefix="/api/v1")
```

### 2. Adicionar Nova Funcionalidade a Domínio Existente

**Exemplo:** Adicionar endpoint de estatísticas em transactions

1. **Repository** - Adicionar query:
```python
# domains/transactions/repository.py
def get_statistics(self, user_id: int, filters):
    return self.db.query(
        func.count(JournalEntry.id),
        func.sum(JournalEntry.Valor)
    ).filter(JournalEntry.user_id == user_id).first()
```

2. **Service** - Adicionar lógica:
```python
# domains/transactions/service.py
def get_statistics(self, user_id: int, filters):
    count, total = self.repository.get_statistics(user_id, filters)
    return {
        "count": count or 0,
        "total": float(total or 0),
        "average": total / count if count else 0
    }
```

3. **Router** - Adicionar endpoint:
```python
# domains/transactions/router.py
@router.get("/statistics")
def get_stats(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.get_statistics(user_id, {})
```

**Arquivos modificados:** 3 (todos no mesmo domínio)
**Impacto:** Zero em outros domínios

---

## 🔍 Checklist de Modificação

Antes de fazer qualquer mudança, perguntar:

- [ ] ✅ Estou modificando apenas um domínio?
- [ ] ✅ Queries SQL estão no repository?
- [ ] ✅ Lógica de negócio está no service?
- [ ] ✅ Router só valida e chama service?
- [ ] ✅ Não estou importando de outros domínios?
- [ ] ✅ Database path é o absoluto único?
- [ ] ✅ Testei o domínio isoladamente?

---

## 🔧 FRONTEND - Configuração Centralizada

### URLs de API (api.config.ts)

**Path:** `app_dev/frontend/src/core/config/api.config.ts`

```typescript
// ✅ ÚNICO lugar onde URLs são definidas
export const API_CONFIG = {
  BACKEND_URL: 'http://localhost:8000',
  API_PREFIX: '/api/v1',
}

export const API_ENDPOINTS = {
  TRANSACTIONS: {
    LIST: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/list`,
    // ...
  }
}
```

**🚫 NUNCA:**
- Hardcoded URLs em componentes
- `fetch('http://localhost:8000/...')` direto
- URLs diferentes em arquivos diferentes

**✅ SEMPRE:**
- Importar de `@/core/config/api.config`
- Usar `API_ENDPOINTS.TRANSACTIONS.LIST`
- Mudar URL = 1 arquivo apenas

### Proxy Genérico

**Path:** `app_dev/frontend/src/app/api/[...proxy]/route.ts`

**Benefício:** Substitui 20+ rotas individuais por 1 arquivo

```typescript
// ✅ ANTES: 1 arquivo
// app/api/[...proxy]/route.ts

// ❌ DEPOIS: 20+ arquivos (não fazer)
// app/api/transactions/route.ts
// app/api/dashboard/route.ts
// app/api/upload/route.ts
// ...
```

---

## � FRONTEND - Arquitetura Feature-Based

### Estrutura de Features (Isolamento por Domínio)

```
app_dev/frontend/src/
├── core/                          # ✅ Configurações e utilitários globais
│   ├── config/
│   │   └── api.config.ts          # URLs centralizadas
│   └── types/
│       └── shared.types.ts        # Types compartilhados
│
├── features/                      # ✅ Domínios de negócio ISOLADOS
│   ├── transactions/              # Feature de transações
│   │   ├── components/            # Componentes específicos
│   │   │   ├── edit-transaction-modal.tsx
│   │   │   ├── transaction-filters.tsx
│   │   │   ├── add-group-modal.tsx
│   │   │   └── index.ts           # Export barrel
│   │   ├── hooks/                 # Hooks customizados
│   │   ├── services/              # Lógica de API
│   │   ├── types/                 # Types específicos
│   │   └── index.ts               # Export principal
│   │
│   ├── dashboard/                 # Feature de dashboard
│   │   ├── components/
│   │   │   ├── budget-vs-actual.tsx
│   │   │   ├── category-expenses.tsx
│   │   │   ├── chart-area-interactive.tsx
│   │   │   └── index.ts
│   │   └── index.ts
│   │
│   ├── upload/                    # Feature de upload
│   │   ├── components/
│   │   │   ├── upload-dialog.tsx
│   │   │   └── index.ts
│   │   └── index.ts
│   │
│   └── settings/                  # Feature de configurações
│       └── components/
│           └── index.ts
│
└── components/                    # ✅ Componentes COMPARTILHADOS apenas
    ├── dashboard-layout.tsx       # Layout global
    ├── app-sidebar.tsx            # Sidebar global
    ├── nav-main.tsx               # Navegação global
    └── ui/                        # Componentes UI base
        ├── button.tsx
        ├── card.tsx
        └── ...
```

### Princípios de Isolamento de Features

**1. CADA FEATURE É AUTOCONTIDA:**
```typescript
// ✅ CORRETO - Feature transactions isolada
import { EditTransactionModal, TransactionFilters } from '@/features/transactions'

// ❌ ERRADO - Não importar de outras features
import { UploadDialog } from '@/features/upload'  // NÃO fazer em transactions
```

**2. ESTRUTURA OBRIGATÓRIA (components → hooks → services):**

**Components (UI isolada):**
```typescript
// features/transactions/components/edit-transaction-modal.tsx
export function EditTransactionModal({ id, onClose }: Props) {
  const { updateTransaction } = useTransactionService()  // Hook local
  // ...
}
```

**Hooks (Estado e lógica):**
```typescript
// features/transactions/hooks/use-transaction-service.ts
export function useTransactionService() {
  const updateTransaction = async (id: string, data) => {
    // Chama service
  }
  return { updateTransaction }
}
```

**Services (API calls):**
```typescript
// features/transactions/services/transaction-api.ts
import { API_ENDPOINTS } from '@/core/config/api.config'

export async function updateTransaction(id: string, data) {
  const response = await fetch(API_ENDPOINTS.TRANSACTIONS.UPDATE(id), {
    method: 'PATCH',
    body: JSON.stringify(data)
  })
  return response.json()
}
```

**3. REGRAS DE IMPORTAÇÃO:**

```typescript
// ✅ CORRETO
import { API_CONFIG } from '@/core/config/api.config'
import { Button } from '@/components/ui/button'  // UI compartilhado
import { EditTransactionModal } from '@/features/transactions'  // Mesma feature

// ❌ ERRADO
import { EditTransactionModal } from '@/features/transactions/components/edit-transaction-modal'  // Path direto, usar index
import { UploadDialog } from '@/features/upload'  // Import cruzado entre features
```

### Quando Modificar uma Feature

**Cenário:** Adicionar filtro de "Categoria" em transações

**✅ Passos corretos:**
1. Modificar `features/transactions/components/transaction-filters.tsx` (adicionar campo)
2. Atualizar `features/transactions/types/` (adicionar tipo se necessário)
3. Modificar `features/transactions/services/` (adicionar parâmetro na API)
4. Testar `features/transactions/` isoladamente
5. **PARAR:** Não precisa tocar em dashboard, upload, settings!

**Arquivos afetados:** ~3 arquivos (todos na mesma feature)
**Antes da modularização:** ~10 arquivos espalhados

---

## 🚫 PROIBIÇÕES FRONTEND

### 1. Imports Cruzados entre Features
```typescript
// ❌ PROIBIDO
// Em features/transactions/components/list.tsx
import { UploadDialog } from '@/features/upload/components/upload-dialog'  // NÃO!

// ✅ CORRETO
// Criar componente compartilhado se usado por múltiplas features
import { SharedDialog } from '@/components/shared-dialog'
```

### 2. Componentes Compartilhados em Features
```typescript
// ❌ PROIBIDO
// features/transactions/components/button-primary.tsx
// Se usado por 2+ features, NÃO deve estar em nenhuma feature específica

// ✅ CORRETO
// components/ui/button-primary.tsx (compartilhado)
```

### 3. Lógica de API nos Componentes
```typescript
// ❌ PROIBIDO
export function TransactionsList() {
  const [data, setData] = useState([])
  
  useEffect(() => {
    fetch('http://localhost:8000/api/v1/transactions/list')  // NÃO!
      .then(res => res.json())
      .then(setData)
  }, [])
}

// ✅ CORRETO
export function TransactionsList() {
  const { transactions, loading } = useTransactions()  // Hook com service
}
```

### 4. URLs Hardcoded
```typescript
// ❌ PROIBIDO
const response = await fetch('http://localhost:8000/api/v1/transactions')

// ✅ CORRETO
import { API_ENDPOINTS } from '@/core/config/api.config'
const response = await fetch(API_ENDPOINTS.TRANSACTIONS.LIST)
```

---

## ✅ PADRÕES FRONTEND OBRIGATÓRIOS

### 1. Criar Nova Feature

```bash
mkdir -p src/features/nova_feature/{components,hooks,services,types}
```

**Arquivos obrigatórios:**
1. `components/index.ts` - Export barrel de componentes
2. `index.ts` - Export principal da feature

**Template de `components/index.ts`:**
```typescript
export { NovoComponente } from './novo-componente'
export { OutroComponente } from './outro-componente'
export type { NovoComponenteProps } from './novo-componente'
```

**Template de `index.ts` (raiz da feature):**
```typescript
// Components
export * from './components'

// Hooks (quando houver)
// export * from './hooks'

// Services (quando houver)
// export * from './services'

// Types (quando houver)
// export * from './types'
```

### 2. Adicionar Componente a Feature Existente

**Exemplo:** Adicionar modal de exclusão em transactions

1. **Criar componente:**
```typescript
// features/transactions/components/delete-transaction-modal.tsx
export function DeleteTransactionModal({ id, onClose }: Props) {
  // ...
}
```

2. **Adicionar ao index:**
```typescript
// features/transactions/components/index.ts
export { DeleteTransactionModal } from './delete-transaction-modal'
```

3. **Usar na página:**
```typescript
// app/transactions/page.tsx
import { DeleteTransactionModal } from '@/features/transactions'
```

**Arquivos modificados:** 2-3 (todos na mesma feature)
**Impacto:** Zero em outras features

---

## 🔍 Checklist de Modificação Frontend

Antes de fazer qualquer mudança, perguntar:

- [ ] ✅ Estou modificando apenas uma feature?
- [ ] ✅ Componente é específico desta feature (não compartilhado)?
- [ ] ✅ Calls de API estão em services/?
- [ ] ✅ Lógica de estado está em hooks/?
- [ ] ✅ Componentes só fazem UI?
- [ ] ✅ Não estou importando de outras features?
- [ ] ✅ URLs vêm de api.config.ts?
- [ ] ✅ Testei a feature isoladamente?

---

## �🎯 Regras de Versionamento Semântico

### MAJOR (X.0.0)
- Breaking changes no schema do banco
- Mudanças incompatíveis na API
- Refatorações massivas

### MINOR (x.Y.0)
- Novas funcionalidades
- Novos campos no banco (não-breaking)
- Novos blueprints/rotas

### PATCH (x.y.Z)
- Bug fixes em domínios específicos
- Melhorias de performance
- Correções de typos

---

## � CORREÇÕES OBRIGATÓRIAS APÓS REMOVER ARQUIVOS ANTIGOS

### Se você remover arquivos da arquitetura antiga, SEMPRE verificar:

**1. Imports em `app/main.py`:**
```python
# ❌ ERRADO (routers antigos)
from .routers import auth, dashboard, compatibility

# ✅ CORRETO (apenas domínios)
from .domains.transactions.router import router as transactions_router
from .domains.users.router import router as users_router
# ...
```

**2. Imports em `run.py`:**
```python
# ❌ ERRADO
from app.config import settings

# ✅ CORRETO
from app.core.config import settings
```

**3. Imports em scripts (`backend/scripts/*.py`):**
```python
# ❌ ERRADO
from app.database import engine, Base

# ✅ CORRETO
from app.core.database import engine, Base
```

**4. Verificar ausência de rotas antigas em `main.py`:**
```python
# ❌ REMOVER estas linhas se existirem:
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(compatibility.router)
# ...

# ✅ MANTER apenas domínios:
app.include_router(transactions_router, prefix="/api/v1", tags=["Transactions"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
# ...
```

**5. Testar após qualquer remoção:**
```bash
# Reiniciar servidores
./quick_stop.sh && ./quick_start.sh

# Verificar backend
curl http://localhost:8000/api/health

# Verificar logs
tail -30 backend.log | grep -i error
```

---

## �🚀 Iniciar/Parar Servidores (PROCESSO OTIMIZADO)

### ⚡ COMANDO ÚNICO - Quando usuário pedir "ligar servidores"

**SEMPRE usar este comando único:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4 && chmod +x quick_start.sh && ./quick_start.sh
```

**O que faz automaticamente:**
- ✅ Limpa portas 8000 e 3000
- ✅ Inicia Backend FastAPI (porta 8000) com venv
- ✅ Inicia Frontend Next.js (porta 3000)
- ✅ Roda em background com logs
- ✅ Salva PIDs para controle

**Parar servidores:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4 && chmod +x quick_stop.sh && ./quick_stop.sh
```

### URLs de Acesso

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/api/health

**Login padrão:** admin@email.com / admin123

### 🔄 Restart Automático Após Modificações

**OBRIGATÓRIO: Reiniciar servidores automaticamente após:**
- Modificação em domínios (models.py, routes.py, schemas)
- Finalização de mudanças com `version_manager.py finish`
- Instalação de novas dependências
- Mudanças em configurações (config.py)
- Atualizações no schema do banco

**Comando completo de restart:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4 && ./quick_stop.sh && ./quick_start.sh
```

### 📋 Monitoramento de Logs

```bash
# Backend
tail -f /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/backend.log

# Frontend
tail -f /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/frontend.log
```

### 🚨 Troubleshooting Rápido

**Portas ocupadas:**
```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
```

**Banco não inicializado:**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev
source venv/bin/activate
python init_db.py
```

---

## � Regras de Templates e Componentes Compartilhados

### ⚠️ REGRA CRÍTICA: Nunca Duplicar Templates

**Princípio fundamental:** Um template deve existir em **UM ÚNICO LUGAR**

**Templates COMPARTILHADOS** (usados por múltiplos blueprints):
- ✅ DEVEM ficar em `/templates/` (root)
- ✅ Exemplos: `transacoes.html`, `base.html`, `confirmar_upload.html`
- ✅ Qualquer blueprint pode renderizar: `render_template('transacoes.html')`

**Templates ESPECÍFICOS** (usados por apenas um blueprint):
- ✅ DEVEM ficar em `/app/blueprints/<nome>/templates/`
- ✅ Exemplo: `dashboard.html` (só usado pelo blueprint dashboard)
- ✅ Renderizar: `render_template('dashboard.html')`

**🚫 NUNCA DUPLICAR:**
- ❌ NUNCA ter o mesmo template em `/templates/` E em `/app/blueprints/*/templates/`
- ❌ Flask serve `/templates/` PRIMEIRO, causando bugs silenciosos
- ❌ Mudanças "desaparecem" porque Flask ignora a versão do blueprint

**✅ ESTRUTURA CORRETA:**
```
templates/
  ├── base.html                      # Layout compartilhado
  ├── transacoes.html                # ✅ Compartilhado (usado por dashboard, admin)
  ├── confirmar_upload.html          # ✅ Compartilhado
  ├── _macros/                       # Componentes reutilizáveis
  │   ├── transacao_filters.html     
  │   ├── transacao_modal_edit.html  
  │   └── ...
  └── _partials/                     # Seções compartilhadas
      └── ...

app/blueprints/
  ├── admin/templates/               
  │   └── admin_transacoes.html      # ✅ Específico do Admin
  ├── dashboard/templates/           
  │   └── dashboard.html             # ✅ Específico do Dashboard
  └── upload/templates/              
      └── validar.html               # ✅ Específico do Upload
```

**Regra de Ouro:**
- Se o template é usado por 2+ blueprints → `/templates/` (root)
- Se o template é usado por 1 blueprint → `/app/blueprints/<nome>/templates/`
- **NUNCA duplicar - apenas uma versão deve existir**

### Obrigações ao Modificar Templates

**SEMPRE que modificar um componente compartilhado (`_macros/` ou `_partials/`):**
1. ✅ Verificar TODOS os blueprints que usam esse componente
2. ✅ Testar em todos os contextos de uso
3. ✅ Documentar mudanças no cabeçalho do componente
4. ✅ Reiniciar servidor após mudanças

**SEMPRE que criar funcionalidade repetida entre blueprints:**
1. ✅ Avaliar se deve virar componente compartilhado
2. ✅ Extrair para `_macros/` ou `_partials/`
3. ✅ Documentar variáveis esperadas no cabeçalho Jinja
4. ✅ Atualizar todos os templates que podem usar o componente

**Princípio DRY (Don't Repeat Yourself):**
- ❌ NUNCA duplicar código HTML entre templates
- ✅ SEMPRE usar `{% include %}` para reutilização
- ✅ SEMPRE usar `{% extends %}` para herança de layout
- ✅ Preferir componentes compartilhados a cópias

### Componentes Compartilhados Existentes

1. **`_macros/transacao_filters.html`**
   - Filtros de pesquisa (estabelecimento, categoria, tipo)
   - Soma de valores filtrados
   - Variáveis: `mes_atual`, `filtro_*`, `grupos_lista`, `soma_filtrada`

2. **`_macros/transacao_modal_edit.html`**
   - Modal de edição de transações
   - JavaScript incluído (abrirModalEditar, salvarEdicaoTransacao)
   - Variáveis: `grupos_lista`

---

## �🔍 Comandos Úteis para o AI

```bash
# Ver status do versionamento
python scripts/version_manager.py status

# Listar mudanças pendentes
ls -la changes/

# Ver histórico de versões
git tag -l "v*" --sort=-version:refname | head -10

# Ver última versão commitada
git describe --tags --abbrev=0

# Verificar arquivos em modo -dev
grep -r "\-dev" app/ --include="*.py" | head -5
```

---

## ⚡ Atalhos Rápidos

**Mudança rápida (arquivo não-crítico):**
- Não requer `version_manager.py`
- Fazer mudança diretamente
- Commit normal

**Mudança em arquivo crítico:**
- `start` → modificar → testar → `finish`

**Bug fix urgente:**
- Usar branch hotfix
- Versionar mesmo assim
- Release patch imediato

---

## 🚨 Situações de Emergência

### Esqueci de rodar `start` antes de modificar

```bash
# Verificar diff
git diff app/models.py

# Se mudança é boa, criar documentação manualmente
cp changes/TEMPLATE.md changes/2025-12-27_models_<descricao>.md
# Editar arquivo com detalhes da mudança

# Atualizar versão manualmente no docstring
```

### Preciso desfazer mudança em -dev

```bash
# Descartar mudanças não commitadas
git checkout -- <arquivo>

# Ou reverter para versão estável anterior
python scripts/version_manager.py rollback <tag>
```

### Hook pre-commit está bloqueando commit válido

```bash
# Verificar o que está bloqueando
python scripts/version_manager.py status

# Se realmente precisa commitar (emergência), bypass (não recomendado)
git commit --no-verify -m "msg"
```

---

## 🚀 Iniciar/Parar Servidores (PROCESSO OTIMIZADO)

### ⚡ COMANDO ÚNICO - Quando usuário pedir "ligar servidores"

**SEMPRE usar este comando único:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4 && chmod +x quick_start.sh && ./quick_start.sh
```

**O que faz automaticamente:**
- ✅ Limpa portas 8000 e 3000
- ✅ Inicia Backend FastAPI (porta 8000) com venv
- ✅ Inicia Frontend Next.js (porta 3000)
- ✅ Roda em background com logs
- ✅ Salva PIDs para controle

**Parar servidores:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4 && chmod +x quick_stop.sh && ./quick_stop.sh
```

### URLs de Acesso

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/api/health

**Login padrão:** admin@email.com / admin123

### 🔄 Restart Automático Após Modificações

**OBRIGATÓRIO: Reiniciar servidores automaticamente após:**
- Modificação em arquivos críticos (models.py, routes.py, schemas)
- Finalização de mudanças com `version_manager.py finish`
- Instalação de novas dependências
- Mudanças em configurações (config.py)
- Atualizações no schema do banco

**Comando completo de restart:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4 && ./quick_stop.sh && ./quick_start.sh
```

### 📋 Monitoramento de Logs

```bash
# Backend
tail -f /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/backend.log

# Frontend
tail -f /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/frontend.log
```

### 🚨 Troubleshooting Rápido

**Portas ocupadas:**
```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
```

**Banco não inicializado:**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev
source venv/bin/activate
python init_db.py
```

### Integração com Workflow de Versionamento

**No `version_manager.py finish`, sempre incluir:**
1. Finalizar mudança e commit
2. **RESTART AUTOMÁTICO:** `./quick_stop.sh && ./quick_start.sh`
3. Validar que servidores estão operacionais (verificar logs)

---

## �📚 Referências Rápidas

- **Documentação completa:** `CONTRIBUTING.md`
- **Template de mudanças:** `changes/TEMPLATE.md`
- **Histórico de bugs:** `BUGS.md` (manter como referência histórica)
- **Status do projeto:** `STATUSPROJETO.md`
- **Arquitetura:** `ESTRUTURA_PROJETO.md`

---

## 💡 Lembrete Final

**Este sistema existe para:**
- ✅ Facilitar rollback de mudanças mal feitas
- ✅ Manter histórico detalhado de modificações
- ✅ Garantir rastreabilidade completa
- ✅ Proteger código em produção
- ✅ Permitir trabalho incremental seguro

**Sempre que começar a trabalhar no projeto, leia este arquivo primeiro!** 🎯
