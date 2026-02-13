# 🚨 Breaking Changes - Budget Consolidation v2.0.0

**Data:** 13/02/2026  
**Sprint:** Sprint 1 - Consolidação Budget Tables  
**Impacto:** Alto - Mudanças massivas em API e Database

---

## 📊 Resumo das Mudanças

### Database
- **4 tabelas → 1 tabela** (75% redução)
- **Migration:** `635e060a2434_consolidate_budget_tables.py`
- **Dados:** 361 registros migrados, 0 perdidos

### API
- **~25 endpoints → ~12 endpoints** (52% redução)
- **Campo renomeado:** `categoria_geral` → `grupo`
- **Campo removido:** `total_mensal` (substituído por cálculo)
- **Campo novo:** `valor_medio_3_meses` (calculado automaticamente)

### Frontend
- **20+ arquivos TypeScript** atualizados
- **Interfaces:** Goal, GoalCreate, GoalUpdate modificadas
- **Components:** 6 componentes refatorados

---

## 🗄️ Database - Tabelas Removidas

### ANTES (4 tabelas):
```
budget_planning          → Orçamento mensal (planejado)
budget_geral            → Orçamento geral consolidado
budget_categoria_config → Configurações de categorias
budget_geral_historico  → Histórico de mudanças
```

### DEPOIS (1 tabela):
```
budget_planning → ÚNICA tabela, todos os dados consolidados
```

### Schema Final:
```sql
CREATE TABLE budget_planning (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    grupo VARCHAR(255) NOT NULL,               -- ✨ RENOMEADO: categoria_geral → grupo
    subgrupo VARCHAR(255),
    tipo_gasto VARCHAR(50),                    -- 'essencial', 'não_essencial', 'variavel'
    valor_planejado NUMERIC(10,2) NOT NULL,
    valor_medio_3_meses NUMERIC(10,2),         -- ✨ NOVO: média calculada automaticamente
    ativo BOOLEAN DEFAULT true,                -- ✨ NOVO: suporte soft-delete
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, ano, mes, grupo, subgrupo)
);
```

**Campos REMOVIDOS:**
- ❌ `total_mensal` (agora calculado via query em journal_entries)
- ❌ `categoria_geral` (renomeado para `grupo`)

---

## 🔗 API - Endpoints Modificados

### ❌ REMOVIDOS (HTTP 410 Gone):

```python
# 1. Bulk upsert geral (substituído)
POST /api/v1/budget/geral/bulk-upsert
→ MIGRAR PARA: POST /api/v1/budget/planning/bulk-upsert

# 2. Listar orçamento geral (substituído)
GET /api/v1/budget/geral
→ MIGRAR PARA: GET /api/v1/budget/planning

# 3. Grupos disponíveis geral (substituído)
GET /api/v1/budget/geral/grupos-disponiveis
→ MIGRAR PARA: GET /api/v1/budget/planning/grupos-disponiveis

# 4. Configuração de categorias (removido permanentemente)
POST /api/v1/budget/categorias-config/bulk-upsert
GET /api/v1/budget/categorias-config
→ SEM SUBSTITUTO (funcionalidade removida)

# 5. Copiar ano (removido temporariamente)
POST /api/v1/budget/geral/copy-to-year
→ SEM SUBSTITUTO (será reimplementado em Sprint futuro)
```

### ✅ ENDPOINTS MANTIDOS:

```python
# Planning (ATIVOS)
GET /api/v1/budget/planning
POST /api/v1/budget/planning/bulk-upsert
GET /api/v1/budget/planning/grupos-disponiveis
GET /api/v1/budget/planning/detalhamento-media
GET /api/v1/budget/planning/tipos-gasto-disponiveis

# Outros endpoints de budget
GET /api/v1/budget/grupos-with-types
GET /api/v1/budget/tipos-gasto-disponiveis
```

---

## 📝 API - Schema Changes

### Request Body - ANTES (v1.x):
```json
{
  "categoria_geral": "Alimentação",
  "subgrupo": "Supermercado",
  "valor_planejado": 1500.00,
  "ano": 2026,
  "mes": 2
}
```

### Request Body - DEPOIS (v2.0):
```json
{
  "grupo": "Alimentação",              // ✨ RENOMEADO
  "subgrupo": "Supermercado",
  "valor_planejado": 1500.00,
  "tipo_gasto": "essencial",           // ✨ NOVO (opcional)
  "ativo": true,                        // ✨ NOVO (opcional, default=true)
  "ano": 2026,
  "mes": 2
}
```

### Response Body - ANTES (v1.x):
```json
{
  "id": 123,
  "categoria_geral": "Alimentação",
  "total_mensal": 1450.00,             // ❌ REMOVIDO
  "valor_planejado": 1500.00
}
```

### Response Body - DEPOIS (v2.0):
```json
{
  "id": 123,
  "grupo": "Alimentação",              // ✨ RENOMEADO
  "valor_medio_3_meses": 1480.50,      // ✨ NOVO (calculado)
  "valor_planejado": 1500.00,
  "ativo": true                         // ✨ NOVO
}
```

---

## ⚛️ Frontend - TypeScript Interfaces

### ANTES (v1.x):
```typescript
interface Goal {
  id: number
  categoria_geral: string            // ❌ RENOMEADO
  subgrupo?: string
  total_mensal: number               // ❌ REMOVIDO
  valor_planejado: number
  ano: number
  mes: number
}
```

### DEPOIS (v2.0):
```typescript
interface Goal {
  id: number
  grupo: string                      // ✨ RENOMEADO: categoria_geral → grupo
  subgrupo?: string
  valor_medio_3_meses: number        // ✨ NOVO: total_mensal → valor_medio_3_meses
  valor_planejado: number
  tipo_gasto?: string                // ✨ NOVO (opcional)
  ativo?: boolean                    // ✨ NOVO (opcional)
  ano: number
  mes: number
}
```

---

## 🔄 Migration Path - Desenvolvedores

### 1. Backend - Atualizar Endpoints

**Substituir chamadas antigas:**
```python
# ❌ ANTES
response = requests.post(
    "http://localhost:8000/api/v1/budget/geral/bulk-upsert",
    json={"categoria_geral": "Alimentação"}
)

# ✅ DEPOIS
response = requests.post(
    "http://localhost:8000/api/v1/budget/planning/bulk-upsert",
    json={"grupo": "Alimentação"}
)
```

### 2. Frontend - Atualizar Interfaces

**Buscar e substituir (regex):**
```bash
# Campos TypeScript
find . -name "*.ts" -o -name "*.tsx" | xargs sed -i '' 's/categoria_geral:/grupo:/g'
find . -name "*.ts" -o -name "*.tsx" | xargs sed -i '' 's/total_mensal/valor_medio_3_meses/g'

# Props de componentes
find . -name "*.tsx" | xargs sed -i '' 's/{categoria_geral}/{grupo}/g'
```

### 3. Database - Aplicar Migration

**Local (dev):**
```bash
cd app_dev/backend
source ../../.venv/bin/activate
alembic upgrade head
```

**Produção (PostgreSQL):**
```bash
ssh user@servidor
cd /var/www/finup/app_dev/backend
source venv/bin/activate
alembic upgrade head
```

### 4. Rollback (se necessário)

**Reverter migration:**
```bash
# Ver migration atual
alembic current

# Downgrade
alembic downgrade -1  # Volta 1 migration
# ou
alembic downgrade 5f2c31234567  # Volta para migration específica
```

**Restaurar backup:**
```bash
# Backup criado automaticamente antes da migration
cp app_dev/backend/database/financas_dev.db.backup_pre_consolidation_* \
   app_dev/backend/database/financas_dev.db
```

---

## 🧪 Testing Checklist

Após atualizar código, validar:

### Backend:
- [ ] ✅ `alembic current` mostra migration 635e060a2434
- [ ] ✅ `GET /api/v1/budget/planning` retorna dados
- [ ] ✅ `POST /api/v1/budget/planning/bulk-upsert` aceita "grupo"
- [ ] ✅ `GET /api/v1/budget/geral` retorna HTTP 410 Gone
- [ ] ✅ Campos do response incluem `valor_medio_3_meses` e `ativo`

### Frontend:
- [ ] ✅ `npm run build` sem erros TypeScript
- [ ] ✅ Interface Goal não tem erros de tipo
- [ ] ✅ Componentes usam `goal.grupo` (não `categoria_geral`)
- [ ] ✅ Componentes usam `valor_medio_3_meses` (não `total_mensal`)
- [ ] ✅ Forms enviam campo "grupo" na criação/edição

### Database:
- [ ] ✅ Apenas 1 tabela `budget_planning` existe
- [ ] ✅ Total de registros: ~1200+ (após migration)
- [ ] ✅ Coluna `grupo` contém valores (não NULL)
- [ ] ✅ Coluna `valor_medio_3_meses` calculada para registros migrados

---

## 📞 Suporte

**Problemas com migration?**
- Slack: #financas-dev
- Email: dev@finup.com
- Backup: `financas_dev.db.backup_pre_consolidation_*`

**Precisa de ajuda com frontend?**
- Ver exemplos: `app_dev/frontend/src/features/goals/`
- Documentação TypeScript: `docs/frontend/TYPESCRIPT_MIGRATION.md`

**Rollback urgente?**
- Script: `scripts/migration/rollback_budget_consolidation.sh`
- Manual: Restaurar backup + `alembic downgrade -1`

---

## 📚 Referências

- **Migration:** `migrations/versions/635e060a2434_consolidate_budget_tables.py`
- **Planning Doc:** `docs/features/budget-consolidation/PLANO_IMPLEMENTACAO.md`
- **Sprint Report:** `docs/features/budget-consolidation/SPRINT1_COMPLETE.md`
- **Commit:** `a1293910` (153 files, +30425/-1829 lines)
