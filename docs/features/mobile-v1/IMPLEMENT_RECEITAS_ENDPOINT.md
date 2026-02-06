# ✅ Implementação: Endpoint de Receitas

**Data:** 01/02/2026 21:30  
**Tempo:** ~5 minutos  
**Status:** ✅ IMPLEMENTADO

---

## 🎯 Objetivo

Buscar **Receitas** do backend para exibir no Dashboard Mobile, usando a coluna `CategoriaGeral = 'Receita'`.

---

## ✅ Implementação

### 1. Novo Endpoint Backend
**Arquivo:** `app_dev/backend/app/domains/transactions/router.py`

**Endpoint:** `GET /api/v1/transactions/receitas-despesas`

**Query Params:**
- `data_inicio` (YYYY-MM-DD)
- `data_fim` (YYYY-MM-DD)

**Response:**
```json
{
  "receitas": 15000.00,
  "despesas": 22461.52,
  "saldo": -7461.52,
  "periodo": {
    "data_inicio": "2026-02-01",
    "data_fim": "2026-02-28"
  }
}
```

### 2. Método Service
**Arquivo:** `app_dev/backend/app/domains/transactions/service.py`

**Método:** `get_receitas_despesas()`

**Lógica:**
```python
# Buscar RECEITAS (CategoriaGeral = 'Receita')
receitas_result = db.query(
    func.sum(JournalEntry.ValorPositivo)
).filter(
    JournalEntry.CategoriaGeral == 'Receita',  # ✅ Receitas
    JournalEntry.MesFatura >= mes_inicio,
    JournalEntry.MesFatura <= mes_fim,
    JournalEntry.IgnorarDashboard == 0
).scalar()

# Buscar DESPESAS (CategoriaGeral = 'Despesa')
despesas_result = db.query(
    func.sum(JournalEntry.Valor)
).filter(
    JournalEntry.CategoriaGeral == 'Despesa',  # ✅ Despesas
    JournalEntry.MesFatura >= mes_inicio,
    JournalEntry.MesFatura <= mes_fim,
    JournalEntry.IgnorarDashboard == 0
).scalar()

receitas = float(receitas_result or 0)
despesas = abs(float(despesas_result or 0))
saldo = receitas - despesas
```

**Observação:** 
- Receitas usam `ValorPositivo` (valores positivos)
- Despesas usam `Valor` (valores negativos) + `abs()` para converter para positivo

### 3. Atualização Frontend
**Arquivo:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx`

**Antes:**
```typescript
// ❌ Receitas zeradas (TODO)
const receitas = 0

// ❌ Despesas calculadas manualmente (soma de grupos)
let despesas = 0
if (data.grupos) {
  Object.values(data.grupos).forEach((grupo: any) => {
    despesas += grupo.total || 0
  })
}
```

**Depois:**
```typescript
// ✅ Buscar receitas e despesas do novo endpoint
const response = await fetchWithAuth(
  `${BASE_URL}/transactions/receitas-despesas?data_inicio=${startDateStr}&data_fim=${endDateStr}`
)

const data = await response.json()

const receitas = data.receitas || 0  // ✅ Receitas reais!
const despesas = data.despesas || 0  // ✅ Despesas reais!
const saldo = data.saldo || 0        // ✅ Saldo calculado!
```

---

## 📊 Comparação

### Antes (Endpoint Antigo)
**Endpoint:** `GET /transactions/grupo-breakdown`

**Retorno:**
```json
{
  "grupos": {
    "Alimentação": { "total": 5000, "transacoes": 10 },
    "Casa": { "total": 3000, "transacoes": 5 }
  }
}
```

**Problema:**
- ❌ Só retorna DESPESAS (por grupo)
- ❌ Não retorna RECEITAS
- ❌ Frontend precisa somar manualmente

### Depois (Endpoint Novo)
**Endpoint:** `GET /transactions/receitas-despesas`

**Retorno:**
```json
{
  "receitas": 15000.00,
  "despesas": 22461.52,
  "saldo": -7461.52
}
```

**Vantagens:**
- ✅ Retorna RECEITAS e DESPESAS
- ✅ Saldo já calculado
- ✅ Mais performático (1 query vs múltiplas)
- ✅ Mais simples no frontend

---

## 🔍 Por que usar `CategoriaGeral`?

### Estrutura do Banco
```sql
journal_entries
├── CategoriaGeral (String)  -- 'Receita' ou 'Despesa'
├── GRUPO (String)            -- Ex: 'Salário', 'Alimentação'
├── SUBGRUPO (String)         -- Ex: 'CLT', 'Supermercado'
├── ValorPositivo (Float)     -- Sempre positivo
└── Valor (Float)             -- Negativo para despesas
```

### Lógica
```python
# RECEITAS
CategoriaGeral = 'Receita'
ValorPositivo > 0  # Ex: +5000 (salário)

# DESPESAS
CategoriaGeral = 'Despesa'
Valor < 0          # Ex: -500 (supermercado)
```

---

## ✅ Checklist

- [x] Criar endpoint `/receitas-despesas` no router
- [x] Implementar método `get_receitas_despesas()` no service
- [x] Buscar receitas com `CategoriaGeral = 'Receita'`
- [x] Buscar despesas com `CategoriaGeral = 'Despesa'`
- [x] Calcular saldo (receitas - despesas)
- [x] Atualizar Dashboard Mobile para usar novo endpoint
- [x] Reiniciar backend

---

## 🚀 Teste

### Como Testar:
```bash
# 1. Backend direto (com token):
curl -H "Authorization: Bearer SEU_TOKEN" \
  "http://localhost:8000/api/v1/transactions/receitas-despesas?data_inicio=2026-02-01&data_fim=2026-02-28"

# 2. Dashboard Mobile:
http://localhost:3000/mobile/dashboard

# 3. Resultado esperado:
# - Receitas > R$ 0,00 (se houver receitas no banco)
# - Despesas > R$ 0,00
# - Saldo calculado corretamente
```

---

**Status:** ✅ IMPLEMENTADO  
**Backend:** Reiniciado com novo endpoint  
**Frontend:** Atualizado para usar `/receitas-despesas`  
**Próximo:** Testar no navegador  
**Data de Conclusão:** 01/02/2026 21:30
