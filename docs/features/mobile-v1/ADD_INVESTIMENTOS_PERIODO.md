# ✅ Adição: Investimentos no Dashboard

**Data:** 01/02/2026 21:35  
**Tempo:** ~5 minutos  
**Status:** ✅ IMPLEMENTADO

---

## 🎯 Objetivo

Adicionar **Investimentos do período** no endpoint `/receitas-despesas`, buscando da categoria `CategoriaGeral = 'Investimentos'`.

---

## 📊 Lógica de Investimentos

### Categorias no Banco:
```sql
SELECT DISTINCT CategoriaGeral FROM journal_entries;

-- Resultado:
-- Despesa
-- Transferência
-- Receita
-- Investimentos  ✅
```

### Lógica de Valores:
```
CategoriaGeral = 'Investimentos'

Valores NEGATIVOS = Aplicações (saídas de dinheiro)
  Ex: -5000 = Investiu R$ 5.000

Valores POSITIVOS = Resgates (entradas de dinheiro)
  Ex: +2000 = Resgatou R$ 2.000

Total Investido = ABS(SUM(Valor))
  Ex: (-5000) + (-3000) + (+1000) = -7000 → ABS = R$ 7.000 investidos
```

---

## ✅ Implementação

### 1. Atualização do Método Service
**Arquivo:** `app_dev/backend/app/domains/transactions/service.py`

**Adicionado:**
```python
# Buscar investimentos
# Valores negativos = aplicações (saídas)
# Valores positivos = resgates (entradas)
# Multiplicar por -1 para mostrar total investido como positivo
investimentos_result = self.repository.db.query(
    func.sum(JournalEntry.Valor).label('total')
).filter(
    JournalEntry.user_id == user_id,
    JournalEntry.MesFatura >= mes_fatura_inicio,
    JournalEntry.MesFatura <= mes_fatura_fim,
    JournalEntry.CategoriaGeral == 'Investimentos',  # ✅ Categoria correta
    JournalEntry.IgnorarDashboard == 0
).scalar()

receitas = float(receitas_result or 0)
despesas = abs(float(despesas_result or 0))
investimentos = abs(float(investimentos_result or 0))  # ✅ ABS para valores positivos
saldo = receitas - despesas - investimentos  # ✅ Saldo descontando investimentos
```

### 2. Atualização do Dashboard Mobile
**Arquivo:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx`

**Antes:**
```typescript
// ❌ Buscava investimentos de outro endpoint (/investimentos/resumo)
const invResponse = await fetchWithAuth(`${BASE_URL}/investimentos/resumo`)
const invData = await invResponse.json()
const investimentos = invData.patrimonio_total || 0
```

**Depois:**
```typescript
// ✅ Investimentos já vêm no endpoint /receitas-despesas
const data = await response.json()
const investimentos = data.investimentos || 0  // Investimentos do período!
```

### 3. Response do Endpoint
**Endpoint:** `GET /api/v1/transactions/receitas-despesas`

**Response:**
```json
{
  "receitas": 15000.00,
  "despesas": 22461.52,
  "investimentos": 5000.00,  // ✅ NOVO!
  "saldo": -12461.52,         // ✅ Já descontando investimentos
  "periodo": {
    "data_inicio": "2026-02-01",
    "data_fim": "2026-02-28"
  }
}
```

---

## 📊 Exemplo Prático

### Cenário:
```
Mês de Fevereiro/2026:

Receitas (salário):        + R$ 15.000,00
Despesas (contas):         - R$ 10.000,00
Investimentos (aplicação): - R$  3.000,00

Saldo = 15.000 - 10.000 - 3.000 = R$ 2.000,00
```

### Response do Endpoint:
```json
{
  "receitas": 15000.00,
  "despesas": 10000.00,
  "investimentos": 3000.00,
  "saldo": 2000.00
}
```

### No Dashboard Mobile:
```
Receitas:      R$ 15.000,00  (verde)
Despesas:      R$ 10.000,00  (vermelho)
Saldo:         R$  2.000,00  (azul)
Investimentos: R$  3.000,00  (roxo)
```

---

## 🔄 Comparação: Antes vs Depois

### Antes
**Investimentos:** Buscava patrimônio total de `/investimentos/resumo`
- ❌ Retornava valor ACUMULADO (todo o patrimônio)
- ❌ Não estava relacionado ao período selecionado
- ❌ Requisição extra (2 endpoints)

### Depois
**Investimentos:** Vem de `/receitas-despesas`
- ✅ Retorna investimentos do PERÍODO selecionado
- ✅ Consistente com receitas/despesas
- ✅ Tudo em 1 requisição (mais performático)

---

## 📈 Fórmulas

### Receitas:
```sql
SUM(ValorPositivo) 
WHERE CategoriaGeral = 'Receita'
```

### Despesas:
```sql
ABS(SUM(Valor))
WHERE CategoriaGeral = 'Despesa'
```

### Investimentos:
```sql
ABS(SUM(Valor))
WHERE CategoriaGeral = 'Investimentos'
```

### Saldo:
```
Receitas - Despesas - Investimentos
```

---

## ✅ Checklist

- [x] Adicionar query de investimentos no service
- [x] Usar `CategoriaGeral = 'Investimentos'`
- [x] Aplicar `abs()` para valores positivos
- [x] Atualizar cálculo do saldo (- investimentos)
- [x] Remover busca de `/investimentos/resumo` do frontend
- [x] Usar investimentos do endpoint `/receitas-despesas`
- [x] Atualizar documentação do endpoint
- [x] Reiniciar backend

---

## 🚀 Teste

### Como Testar:
```bash
# 1. Recarregar Dashboard Mobile:
http://localhost:3000/mobile/dashboard

# 2. Verificar métricas:
# - Receitas: R$ X,XX
# - Despesas: R$ X,XX
# - Saldo: R$ X,XX (receitas - despesas - investimentos)
# - Investimentos: R$ X,XX (investimentos do período)

# 3. Testar YTD:
# - Clicar em "Ano"
# - Investimentos devem mostrar total do ano até o mês atual
```

---

**Status:** ✅ IMPLEMENTADO  
**Backend:** Reiniciado com investimentos  
**Frontend:** Simplificado (1 endpoint em vez de 2)  
**Benefício:** Mais performático e consistente  
**Data de Conclusão:** 01/02/2026 21:35
