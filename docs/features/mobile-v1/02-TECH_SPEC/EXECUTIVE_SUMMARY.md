# 🚨 RESUMO EXECUTIVO - Correções Necessárias

**Data:** 31/01/2026  
**Tempo de leitura:** 3 minutos  
**Status:** CRÍTICO - Ação imediata necessária

---

## 📋 Situação

Após validação completa do backend, **2 problemas críticos** foram identificados:

### ❌ Problema 1: Falta Mapeamento de Deploy
O TECH_SPEC.md não especifica **paths absolutos** de onde criar cada arquivo.

### ❌ Problema 2: Estrutura de Metas Incorreta
- PRD/API_SPEC assumiu usar `budget_geral` (campo `categoria_geral`)
- Mas `budget_geral` usa valores: "Casa", "Cartão de Crédito", etc
- PRD mostra grupos: "Alimentação", "Moradia", "Transporte"
- **Tabela correta:** `budget_planning` (campo `grupo`)

---

## ✅ Soluções Criadas

### 1. DEPLOY_MAP.md ✅
**Path:** `/docs/features/mobile-v1/02-TECH_SPEC/DEPLOY_MAP.md`

**Conteúdo:**
- ✅ Paths absolutos de TODOS os arquivos (local + prod)
- ✅ Comandos para criar estrutura de pastas
- ✅ Workflow completo de deploy (local → git → servidor)
- ✅ Checklist de deploy (frontend + backend + infra)
- ✅ Comandos úteis (logs, status, restart)

---

### 2. BUDGET_STRUCTURE_ANALYSIS.md ✅
**Path:** `/docs/features/mobile-v1/02-TECH_SPEC/BUDGET_STRUCTURE_ANALYSIS.md`

**Conteúdo:**
- ✅ Análise detalhada das 3 tabelas de budget
- ✅ Comparação `budget_geral` vs `budget_planning`
- ✅ Recomendação: Usar `budget_planning` (campo `grupo`)
- ✅ Exemplos de código (service + repository + router)
- ✅ Fluxos de dados corretos

---

## 🎯 Action Items (Ordem de Prioridade)

### Sprint 0 - Backend (CRÍTICO)

#### 1. Criar Endpoint `/budget/planning` (2-3h)
**Path:** `app_dev/backend/app/domains/budget/router.py`

```python
@router.get("/budget/planning")
async def get_budget_planning(
    mes_referencia: str = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = BudgetService(db)
    budgets = service.get_budgets_by_month_planning(user_id, mes_referencia)
    return {"budgets": budgets, "total": len(budgets)}
```

**Adicionar método no service.py:**
```python
def get_budgets_by_month_planning(self, user_id: int, mes_referencia: str):
    from .models import BudgetPlanning
    from .repository import BudgetRepository
    
    repo = BudgetRepository(self.db)
    return repo.get_by_month(user_id, mes_referencia)
```

---

#### 2. Criar Endpoint `/budget/planning/bulk-upsert` (3-4h)
**Path:** `app_dev/backend/app/domains/budget/router.py`

```python
@router.post("/budget/planning/bulk-upsert")
async def bulk_upsert_budget_planning(
    data: dict,  # {mes_referencia: str, budgets: [{grupo, valor_planejado}, ...]}
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = BudgetService(db)
    return service.bulk_upsert_budget_planning(
        user_id, 
        data["mes_referencia"], 
        data["budgets"]
    )
```

**Adicionar método no service.py:**
```python
def bulk_upsert_budget_planning(self, user_id: int, mes_referencia: str, budgets: List[dict]):
    from .models import BudgetPlanning
    from .repository import BudgetRepository
    
    repo = BudgetRepository(self.db)
    return repo.bulk_upsert(user_id, mes_referencia, budgets)
```

---

#### 3. Criar Endpoint `/budget/geral/copy-to-year` (3-4h)
**Conforme BACKEND_VALIDATION.md**

---

#### 4. Criar Endpoint `/transactions/grupo-breakdown` (3-4h)
**Conforme BACKEND_VALIDATION.md**

---

### Sprint 0 - Documentação (URGENTE)

#### 5. Atualizar API_SPEC.md (30 min)
**Substituir:**
- ❌ `GET /budget/geral` → ✅ `GET /budget/planning`
- ❌ `POST /budget/geral/bulk-upsert` → ✅ `POST /budget/planning/bulk-upsert`
- ❌ Campo `categoria_geral` → ✅ Campo `grupo`

**Seções a atualizar:**
- Seção 3 (Budget)
- Seção 10.1 (Exemplo de integração)

---

#### 6. Atualizar BACKEND_VALIDATION.md (15 min)
**Adicionar:**
- Seção sobre `budget_planning` vs `budget_geral`
- Recomendação explícita de usar `budget_planning`
- Links para BUDGET_STRUCTURE_ANALYSIS.md

---

## 📊 Status dos Documentos

| Documento | Status | Ação Necessária |
|-----------|--------|-----------------|
| TECH_SPEC.md | ✅ Completo | Nenhuma |
| API_SPEC.md | ⚠️ Desatualizado | Atualizar endpoints budget |
| COMPONENTS.md | ✅ Completo | Nenhuma |
| TESTING_STRATEGY.md | ✅ Completo | Nenhuma |
| IMPLEMENTATION_GUIDE.md | ✅ Completo | Nenhuma |
| BACKEND_VALIDATION.md | ⚠️ Incompleto | Adicionar seção budget |
| **DEPLOY_MAP.md** | ✅ **NOVO** | Nenhuma |
| **BUDGET_STRUCTURE_ANALYSIS.md** | ✅ **NOVO** | Nenhuma |

---

## ⏱️ Estimativa de Tempo

### Backend (Sprint 0)
- Endpoint `/budget/planning` (GET): **2-3h**
- Endpoint `/budget/planning/bulk-upsert` (POST): **3-4h**
- Endpoint `/budget/geral/copy-to-year`: **3-4h**
- Endpoint `/transactions/grupo-breakdown`: **3-4h**
- Testes unitários backend: **2-3h**

**Total Backend:** ~13-18h (2 dias úteis)

---

### Documentação (Sprint 0)
- Atualizar API_SPEC.md: **30 min**
- Atualizar BACKEND_VALIDATION.md: **15 min**
- Revisar INDEX.md: **15 min**

**Total Documentação:** ~1h

---

### Frontend (Sprint 1-4)
- Conforme IMPLEMENTATION_GUIDE.md: **~88-114h**

---

## 🚀 Próximos Passos (Hoje)

1. ✅ **Ler DEPLOY_MAP.md** - Entender paths e workflow
2. ✅ **Ler BUDGET_STRUCTURE_ANALYSIS.md** - Entender estrutura de metas
3. ⏳ **Atualizar API_SPEC.md** - Corrigir endpoints budget
4. ⏳ **Atualizar BACKEND_VALIDATION.md** - Adicionar seção budget
5. ⏳ **Implementar 4 endpoints backend** - Sprint 0

---

## 📞 Documentos de Referência

| Documento | Path | Objetivo |
|-----------|------|----------|
| **DEPLOY_MAP.md** | `/docs/features/mobile-v1/02-TECH_SPEC/DEPLOY_MAP.md` | Paths absolutos e workflow deploy |
| **BUDGET_STRUCTURE_ANALYSIS.md** | `/docs/features/mobile-v1/02-TECH_SPEC/BUDGET_STRUCTURE_ANALYSIS.md` | Estrutura de metas (budget_planning) |
| **API_SPEC.md** | `/docs/features/mobile-v1/02-TECH_SPEC/API_SPEC.md` | Endpoints (ATUALIZAR!) |
| **BACKEND_VALIDATION.md** | `/docs/features/mobile-v1/02-TECH_SPEC/BACKEND_VALIDATION.md` | Validação backend (ATUALIZAR!) |
| **IMPLEMENTATION_GUIDE.md** | `/docs/features/mobile-v1/02-TECH_SPEC/IMPLEMENTATION_GUIDE.md` | Ordem de implementação frontend |

---

## ⚠️ IMPORTANTE

**NUNCA começar implementação frontend antes de:**
1. ✅ Corrigir API_SPEC.md (endpoints budget)
2. ✅ Implementar 4 endpoints backend (Sprint 0)
3. ✅ Testar endpoints com Postman/curl
4. ✅ Validar response schemas

**Começar frontend com backend errado = Retrabalho total!**

---

**Data:** 31/01/2026  
**Status:** 🚨 CRÍTICO - 2 problemas identificados, 2 soluções criadas  
**Próximo:** Atualizar API_SPEC.md e implementar Sprint 0
