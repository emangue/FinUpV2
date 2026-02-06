# Budget Structure Analysis - Mobile Experience V1.0

**Data:** 31/01/2026  
**Versão:** 1.0  
**Status:** 🚨 CRÍTICO - Discrepância identificada

---

## 🚨 Problema Identificado

### Situação Atual

**PRD/API_SPEC assumiu:**
- Metas são por **GRUPO** (Alimentação, Moradia, Transporte, etc)
- Endpoint: `GET /budget/geral?mes_referencia=2026-02`
- Response: `[{ grupo: "Alimentação", valor_planejado: 2000.00 }, ...]`

**Backend real usa:**
- Tabela `budget_geral` tem coluna `categoria_geral` (NÃO `grupo`)
- Valores: "Casa", "Cartão de Crédito", "Doações", "Saúde", "Viagens", "Outros"
- Tabela `budget_categoria_config` mapeia categorias → grupos via `filtro_valor`

---

## 📊 Estrutura Real das Tabelas de Budget

### 1. `budget_geral` (Valores planejados)

```sql
CREATE TABLE budget_geral (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    categoria_geral VARCHAR(50) NOT NULL,  -- ⚠️ NÃO é "grupo"!
    mes_referencia VARCHAR(7) NOT NULL,     -- Formato: YYYY-MM
    valor_planejado FLOAT NOT NULL,
    total_mensal FLOAT,                     -- Budget geral (teto)
    created_at DATETIME,
    updated_at DATETIME
);
```

**Exemplo de dados:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "categoria_geral": "Casa",  // ⚠️ Não é "Alimentação"
    "mes_referencia": "2026-02",
    "valor_planejado": 3500.00,
    "total_mensal": 10000.00
  },
  {
    "id": 2,
    "user_id": 1,
    "categoria_geral": "Cartão de Crédito",
    "mes_referencia": "2026-02",
    "valor_planejado": 2500.00,
    "total_mensal": 10000.00
  }
]
```

---

### 2. `budget_categoria_config` (Mapeamento categorias → grupos)

```sql
CREATE TABLE budget_categoria_config (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    nome_categoria VARCHAR(100) NOT NULL,   -- Ex: "Casa"
    ordem INTEGER NOT NULL,                  -- Hierarquia
    fonte_dados VARCHAR(20) NOT NULL,        -- "GRUPO" ou "TIPO_TRANSACAO"
    filtro_valor VARCHAR(100) NOT NULL,      -- Valor a filtrar (ex: "Moradia")
    tipos_gasto_incluidos VARCHAR(1000),     -- JSON array de TipoGasto
    cor_visualizacao VARCHAR(7),             -- Hex color
    ativo INTEGER DEFAULT 1,
    created_at DATETIME,
    updated_at DATETIME
);
```

**Exemplo de dados:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "nome_categoria": "Casa",
    "ordem": 1,
    "fonte_dados": "GRUPO",
    "filtro_valor": "Moradia",  // ⚠️ Filtra journal_entries onde GRUPO="Moradia"
    "tipos_gasto_incluidos": null,
    "cor_visualizacao": "#DDD6FE",
    "ativo": 1
  },
  {
    "id": 2,
    "user_id": 1,
    "nome_categoria": "Cartão de Crédito",
    "ordem": 2,
    "fonte_dados": "TIPO_TRANSACAO",
    "filtro_valor": "Cartão",  // ⚠️ Filtra journal_entries onde tipo="Cartão"
    "tipos_gasto_incluidos": "[\"Alimentação\", \"Transporte\", \"Compras\"]",
    "cor_visualizacao": "#DBEAFE",
    "ativo": 1
  }
]
```

---

### 3. `budget_planning` (Planejamento granular por GRUPO)

```sql
CREATE TABLE budget_planning (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    grupo VARCHAR(100) NOT NULL,            -- ✅ Aqui sim usa GRUPO!
    mes_referencia VARCHAR(7) NOT NULL,
    valor_planejado FLOAT NOT NULL,
    valor_medio_3_meses FLOAT DEFAULT 0.0,
    created_at DATETIME,
    updated_at DATETIME
);
```

**Exemplo de dados:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "grupo": "Alimentação",  // ✅ Usa GRUPO como esperado
    "mes_referencia": "2026-02",
    "valor_planejado": 2000.00,
    "valor_medio_3_meses": 1850.00
  },
  {
    "id": 2,
    "user_id": 1,
    "grupo": "Moradia",
    "mes_referencia": "2026-02",
    "valor_planejado": 3500.00,
    "valor_medio_3_meses": 3400.00
  }
]
```

---

## 🔍 Análise: Qual Tabela Usar?

### Opção 1: `budget_planning` (RECOMENDADO ✅)

**Prós:**
- ✅ Usa `grupo` diretamente (Alimentação, Moradia, etc)
- ✅ Granularidade fina (1 meta por grupo)
- ✅ Alinha com PRD (tela "Trackers" mostra grupos)
- ✅ Já existe endpoint `GET /budget/planning`

**Contras:**
- ⚠️ Endpoint atual retorna estrutura diferente do PRD
- ⚠️ Precisará adaptar response para match com PRD

**Estrutura atual do endpoint:**
```python
# GET /budget/planning?mes_referencia=2026-02
[
  {
    "id": 1,
    "grupo": "Alimentação",
    "valor_planejado": 2000.00,
    "valor_medio_3_meses": 1850.00
  }
]
```

**Estrutura esperada pelo PRD (via /dashboard/budget-vs-actual):**
```python
{
  "year": 2026,
  "month": 2,
  "total_realizado": 8547.00,
  "total_planejado": 10000.00,
  "grupos": [
    {
      "grupo": "Alimentação",
      "realizado": 1850.00,
      "planejado": 2000.00,  # Vem de budget_planning
      "percentual": 92.5,
      "cor": "#60A5FA"
    }
  ]
}
```

---

### Opção 2: `budget_geral` (NÃO RECOMENDADO ❌)

**Prós:**
- ✅ Já tem endpoint `GET /budget/geral`
- ✅ Sistema hierárquico (categoria → grupos)

**Contras:**
- ❌ Usa `categoria_geral` ("Casa", "Cartão de Crédito") em vez de `grupo`
- ❌ Não alinha com PRD (tela mostra Alimentação, Moradia, etc)
- ❌ Requer JOIN complexo com `budget_categoria_config`
- ❌ Menos intuitivo para usuário mobile

---

## ✅ Solução Recomendada

### Usar `budget_planning` + Adaptar Endpoint

**1. Endpoint existente:** `GET /budget/planning`

**Path:** `app_dev/backend/app/domains/budget/router.py`

```python
@router.get("/planning")
async def get_budget_planning(
    mes_referencia: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Busca budget_planning
    budgets = db.query(BudgetPlanning).filter(
        BudgetPlanning.user_id == current_user['id'],
        BudgetPlanning.mes_referencia == mes_referencia
    ).all()
    
    return [
        {
            "id": b.id,
            "grupo": b.grupo,
            "valor_planejado": b.valor_planejado,
            "valor_medio_3_meses": b.valor_medio_3_meses
        }
        for b in budgets
    ]
```

**2. Criar/atualizar metas:** `POST /budget/planning/bulk-upsert`

**Path:** `app_dev/backend/app/domains/budget/router.py`

```python
@router.post("/planning/bulk-upsert")
async def bulk_upsert_budget_planning(
    payload: BudgetPlanningBulkUpsert,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mes_referencia = payload.mes_referencia
    budgets = payload.budgets  # [{ grupo: "Alimentação", valor_planejado: 2000 }, ...]
    
    results = []
    for budget in budgets:
        # Buscar existente
        existing = db.query(BudgetPlanning).filter(
            BudgetPlanning.user_id == current_user['id'],
            BudgetPlanning.grupo == budget.grupo,
            BudgetPlanning.mes_referencia == mes_referencia
        ).first()
        
        if existing:
            # Atualizar
            existing.valor_planejado = budget.valor_planejado
            existing.updated_at = datetime.now()
            db.commit()
            results.append(existing)
        else:
            # Criar
            novo = BudgetPlanning(
                user_id=current_user['id'],
                grupo=budget.grupo,
                mes_referencia=mes_referencia,
                valor_planejado=budget.valor_planejado,
                valor_medio_3_meses=0.0
            )
            db.add(novo)
            db.commit()
            results.append(novo)
    
    return [
        {
            "id": r.id,
            "grupo": r.grupo,
            "mes_referencia": r.mes_referencia,
            "valor_planejado": r.valor_planejado
        }
        for r in results
    ]
```

---

## 📝 Atualizações Necessárias no API_SPEC.md

### Endpoint de Listagem

**Antes (incorreto):**
```
GET /api/v1/budget/geral?mes_referencia=2026-02
```

**Depois (correto):**
```
GET /api/v1/budget/planning?mes_referencia=2026-02
```

**Response:**
```json
[
  {
    "id": 1,
    "grupo": "Alimentação",
    "valor_planejado": 2000.00,
    "valor_medio_3_meses": 1850.00
  },
  {
    "id": 2,
    "grupo": "Moradia",
    "valor_planejado": 3500.00,
    "valor_medio_3_meses": 3400.00
  }
]
```

---

### Endpoint de Criação/Atualização

**Antes (incorreto):**
```
POST /api/v1/budget/geral/bulk-upsert
Body: { mes_referencia: "2026-02", budgets: [...] }
```

**Depois (correto):**
```
POST /api/v1/budget/planning/bulk-upsert
Body: { mes_referencia: "2026-02", budgets: [...] }
```

**Request Body:**
```json
{
  "mes_referencia": "2026-02",
  "budgets": [
    {
      "grupo": "Alimentação",
      "valor_planejado": 2200.00
    }
  ]
}
```

**Response:**
```json
[
  {
    "id": 123,
    "grupo": "Alimentação",
    "mes_referencia": "2026-02",
    "valor_planejado": 2200.00
  }
]
```

---

## 🔄 Fluxo de Dados Correto

### Dashboard Mobile (Budget vs Actual)

```typescript
// 1. Buscar dados de budget vs actual
const response = await fetch('/api/v1/dashboard/budget-vs-actual?year=2026&month=2');
const data = await response.json();

// data.grupos já vem com:
// - grupo (nome)
// - realizado (calculado de journal_entries)
// - planejado (vem de budget_planning)
// - percentual
// - cor

console.log(data.grupos);
// [
//   { grupo: "Alimentação", realizado: 1850, planejado: 2000, percentual: 92.5, cor: "#60A5FA" },
//   { grupo: "Moradia", realizado: 3200, planejado: 3500, percentual: 91.4, cor: "#DDD6FE" }
// ]
```

### Editar Meta Individual

```typescript
// 1. Listar metas
const response1 = await fetch('/api/v1/budget/planning?mes_referencia=2026-02');
const metas = await response1.json();

// 2. Atualizar meta (usar bulk-upsert com 1 item)
const response2 = await fetch('/api/v1/budget/planning/bulk-upsert', {
  method: 'POST',
  body: JSON.stringify({
    mes_referencia: '2026-02',
    budgets: [
      { grupo: 'Alimentação', valor_planejado: 2200.00 }
    ]
  })
});

const resultado = await response2.json();
console.log(resultado); // [{ id: 123, grupo: "Alimentação", ... }]
```

---

## 🎯 Action Items

### 1. Atualizar API_SPEC.md
- [ ] Substituir `/budget/geral` por `/budget/planning`
- [ ] Atualizar exemplos de request/response
- [ ] Corrigir Seção 3 (Budget)
- [ ] Atualizar Seção 10 (Exemplos de integração)

### 2. Validar Backend Existente
- [ ] Verificar se `GET /budget/planning` existe
- [ ] Verificar se `POST /budget/planning/bulk-upsert` existe
- [ ] Se não, criar no Sprint 0

### 3. Atualizar BACKEND_VALIDATION.md
- [ ] Adicionar seção sobre discrepância budget_geral vs budget_planning
- [ ] Documentar estrutura de cada tabela
- [ ] Recomendar uso de budget_planning

---

## 📊 Comparação Final

| Aspecto | `budget_geral` | `budget_planning` ✅ |
|---------|----------------|---------------------|
| Campo usado | `categoria_geral` | `grupo` |
| Valores | "Casa", "Cartão de Crédito" | "Alimentação", "Moradia" |
| Alinha com PRD | ❌ Não | ✅ Sim |
| Complexidade | 🔴 Alta (JOIN) | 🟢 Baixa (direto) |
| Endpoint existe | ✅ Sim | ⚠️ Verificar |
| Recomendação | ❌ Não usar | ✅ Usar |

---

## ⚠️ IMPORTANTE

**NUNCA misturar `budget_geral` e `budget_planning` na mesma feature!**

- **Mobile V1.0:** Usar APENAS `budget_planning`
- **Desktop (se existir):** Pode usar `budget_geral` (categorias amplas)
- **Consistência:** 1 tela = 1 tabela de budget

---

**Data:** 31/01/2026  
**Status:** 🚨 CRÍTICO - Requer ação imediata  
**Próximo:** Atualizar API_SPEC.md e validar backend
