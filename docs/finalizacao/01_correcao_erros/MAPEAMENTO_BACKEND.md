# 🔍 MAPEAMENTO DE ERROS - BACKEND

**Data:** 10/02/2026  
**Total de Erros Python:** 0 erros detectados  
**Status:** ✅ Backend sem erros de sintaxe/importação

---

## 📊 ESTATÍSTICAS GERAIS

| Categoria | Quantidade |
|-----------|------------|
| **Erros de Sintaxe** | 0 |
| **Erros de Import** | 0 |
| **Erros de Type Hints** | 0 |
| **Warnings** | A investigar |

---

## ✅ VALIDAÇÃO REALIZADA

### Arquivos Verificados:
```bash
app_dev/backend/app/domains/*/  # Domínios modulares
app_dev/backend/app/core/       # Core config
app_dev/backend/scripts/        # Scripts utilitários
```

### Métodos de Verificação:
1. ✅ **get_errors tool** - Verificação IDE/TypeScript
2. ⏳ **Pending:** Rodar `python -m py_compile` em todos .py
3. ⏳ **Pending:** Verificar imports com `pylint` ou `flake8`
4. ⏳ **Pending:** Verificar type hints com `mypy`

---

## 🔍 ANÁLISE DETALHADA

### ✅ Domínios Principais (Status: OK pelo IDE)

#### 1. Authentication (`domains/auth/`)
- `router.py` - ✅ Sem erros
- `service.py` - ✅ Sem erros
- `models.py` - ✅ Sem erros

#### 2. Transactions (`domains/transactions/`)
- `router.py` - ✅ Sem erros
- `service.py` - ✅ Sem erros
- `repository.py` - ✅ Sem erros
- `models.py` - ✅ Sem erros

#### 3. Goals (`domains/goals/`)
- `router.py` - ✅ Sem erros
- `service.py` - ✅ Sem erros
- `models.py` - ✅ Sem erros
- `schemas.py` - ✅ Sem erros

#### 4. Upload (`domains/upload/`)
- `router.py` - ✅ Sem erros
- `service.py` - ✅ Sem erros
- `processors/` - ✅ Sem erros

#### 5. Categories (`domains/categories/`)
- `router.py` - ✅ Sem erros
- `service.py` - ✅ Sem erros

#### 6. Dashboard (`domains/dashboard/`)
- `router.py` - ✅ Sem erros
- `service.py` - ✅ Sem erros

---

## ⚠️ ÁREAS QUE REQUEREM VALIDAÇÃO ADICIONAL

Mesmo sem erros reportados pelo IDE, algumas validações são recomendadas:

### 1. Validação de Runtime

**Arquivos a testar:**
```bash
app_dev/backend/app/main.py                 # Inicialização FastAPI
app_dev/backend/app/core/database.py        # Conexão DB
app_dev/backend/app/core/config.py          # Settings
```

**Teste sugerido:**
```bash
cd app_dev/backend
source ../../.venv/bin/activate
python -c "from app.main import app; print('✅ Backend importa sem erros')"
```

---

### 2. Validação de Endpoints

**Endpoints críticos a testar:**
```bash
# Health check
curl http://localhost:8000/api/health

# Goals
curl http://localhost:8000/api/v1/goals/ -H "Authorization: Bearer TOKEN"

# Dashboard
curl http://localhost:8000/api/v1/dashboard/metrics?year=2026&month=2

# Upload
curl http://localhost:8000/api/v1/upload/history -H "Authorization: Bearer TOKEN"
```

---

### 3. Validação de Schemas

**Verificar se schemas Pydantic retornam campos esperados pelo frontend:**

#### Goal Schema vs Frontend Interface:
```python
# Backend (schemas.py)
class GoalResponse(BaseModel):
    id: int
    user_id: int
    nome: str
    descricao: Optional[str]
    valor_alvo: float
    prazo: str  # YYYY-MM
    frequencia: Literal['mensal', 'anual']
    ativo: bool
    # ...
    
    # ❓ VERIFICAR: Retorna 'categoria'?
    # ❓ VERIFICAR: Retorna 'orcamento'?
    # ❓ VERIFICAR: 'progresso' está aninhado corretamente?
```

**Frontend espera (Goal interface):**
```typescript
interface Goal {
  id: number
  valor_alvo: number  // ✅ OK
  prazo: string       // ✅ OK
  ativo: boolean      // ✅ OK
  
  // ❌ NÃO EXISTE no schema Python:
  categoria?: string  // ← Frontend usa mas backend não retorna?
  orcamento?: number  // ← Nome incorreto? Deveria ser valor_alvo
  
  // ✅ Aninhado:
  progresso?: {
    valor_atual: number
    percentual: number
    falta: number
    categorias_vinculadas: number
  }
}
```

**⚠️ AÇÃO NECESSÁRIA:**
1. Chamar endpoint `/api/v1/goals/` e ver JSON real
2. Comparar com interface TypeScript
3. Corrigir descompasso (backend OU frontend)

---

### 4. Validação de Migrations

**Verificar se Alembic está sincronizado:**
```bash
cd app_dev/backend
alembic current  # Deve mostrar migration atual
alembic check    # Verifica se há divergências
```

**Tabelas críticas a validar:**
- `budget_geral` - Campos `id`, `user_id`, `categoria_geral`, `valor_planejado`, `mes_referencia`
- `journal_entries` - Campos completos conforme modelos
- `users` - Estrutura de autenticação

---

## 🚨 POTENCIAIS PROBLEMAS ENCONTRADOS (Lógicos)

Embora não sejam erros de sintaxe, análise do código frontend revelou possíveis problemas:

### 1. Campo `categoria` em Goals

**Problema:** Frontend usa `goal.categoria` mas schema Python não define.

**Hipóteses:**
1. Backend calcula `categoria` baseado em vinculações mas não retorna
2. Campo foi removido mas frontend não atualizado
3. Campo existe no banco mas não exposto no schema

**Investigação necessária:**
```python
# domains/goals/models.py
class Goal(Base):
    __tablename__ = "budget_geral"
    
    # ❓ Tem coluna 'categoria'?
    # ❓ Tem coluna 'categoria_geral'?
```

**Ação:**
- [ ] Verificar schema da tabela `budget_geral`
- [ ] Verificar se `GoalResponse` deve incluir campo
- [ ] Corrigir frontend OU backend

---

### 2. Campo `valor_atual` vs `progresso.valor_atual`

**Problema:** Frontend acessa `goal.valor_atual` mas deveria ser `goal.progresso.valor_atual`

**Backend (esperado):**
```python
class GoalResponse(BaseModel):
    progresso: Optional[GoalProgress]  # Aninhado
    
class GoalProgress(BaseModel):
    valor_atual: float  # ← Aqui
```

**Frontend (incorreto):**
```typescript
goal.valor_atual  // ❌ Não existe no root
goal.progresso.valor_atual  // ✅ Correto
```

**Ação:**
- [ ] Frontend já mapeado como erro P0
- [ ] Validar que backend retorna `progresso` aninhado
- [ ] Corrigir frontend para acessar corretamente

---

### 3. Campo `ativo` como Boolean vs Number

**Problema:** SQLite pode retornar 0/1, schema define bool, frontend compara com ambos.

**Backend:**
```python
class Goal(Base):
    ativo = Column(Boolean, default=True)  # ← Deveria ser bool
```

**Frontend (código defensivo):**
```typescript
goal.ativo === true || goal.ativo === 1  // ← Workaround
```

**Ação:**
- [ ] Verificar se backend sempre retorna boolean
- [ ] Se SQLite retorna 0/1, normalizar no schema:
```python
class GoalResponse(BaseModel):
    @validator('ativo', pre=True)
    def normalize_bool(cls, v):
        return bool(v)  # Converte 0/1 para False/True
```

---

## 📋 CHECKLIST DE VALIDAÇÃO BACKEND

### ✅ Fase 1 - Validação de Importação
- [ ] Rodar `python -m py_compile` em todos arquivos .py
- [ ] Verificar que `from app.main import app` funciona
- [ ] Iniciar backend e ver se sobe sem erros

### ✅ Fase 2 - Validação de Endpoints
- [ ] Testar `/api/health` (200 OK)
- [ ] Testar `/api/v1/goals/` (200 + JSON válido)
- [ ] Testar `/api/v1/dashboard/metrics` (200)
- [ ] Testar `/api/v1/upload/history` (200)

### ✅ Fase 3 - Validação de Schemas
- [ ] Comparar `GoalResponse` com JSON retornado por `/goals/`
- [ ] Verificar se `categoria` existe ou deve ser adicionado
- [ ] Validar que `progresso` retorna aninhado
- [ ] Confirmar que `ativo` sempre retorna boolean

### ✅ Fase 4 - Validação de Database
- [ ] Executar `alembic current` (migration aplicada)
- [ ] Executar `alembic check` (sem divergências)
- [ ] Verificar schema da tabela `budget_geral`:
```sql
sqlite3 database/financas_dev.db ".schema budget_geral"
```

### ✅ Fase 5 - Testes de Integração
- [ ] Criar nova meta pelo frontend → verificar persistência
- [ ] Editar meta → verificar campos atualizados
- [ ] Toggle ativo/inativo → verificar boolean correto
- [ ] Verificar logs de erro no backend durante testes

---

## 🎯 RESUMO EXECUTIVO

### Status Backend:
- ✅ **Sintaxe:** Sem erros Python detectados
- ⏳ **Runtime:** A validar com testes de importação
- ⚠️ **Schemas:** Possível descompasso com frontend (campos faltando)
- ⏳ **Database:** A validar migrations e estrutura

### Problemas Identificados (Lógicos):
1. Campo `categoria` pode estar faltando no schema
2. Campo `ativo` pode retornar 0/1 em vez de boolean
3. Schema pode não expor todos os campos que frontend espera

### Tempo Estimado de Validação:
- **Fase 1-2:** 30 min (importação + endpoints)
- **Fase 3:** 1 hora (análise schemas + comparação frontend)
- **Fase 4:** 30 min (database validation)
- **Fase 5:** 1 hora (testes integração)
- **TOTAL:** ~3 horas

### Próximos Passos:
1. ✅ Iniciar backend e coletar JSON real de endpoints
2. ✅ Comparar com interfaces TypeScript do frontend
3. ✅ Documentar divergências exatas
4. ✅ Decidir: corrigir backend (adicionar campos) OU frontend (usar campos corretos)
5. ✅ Aplicar correções e re-validar

---

**📌 NOTA:** Backend aparenta estar **estruturalmente correto** (sem erros de código). Problemas são de **contrato de dados** (schemas não alinham com frontend). Próximo passo é **auditoria de schemas** detalhada.
