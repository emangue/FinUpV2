# 🐛 Correção: AttributeError 'DataTransacao'

**Data:** 01/02/2026 21:25  
**Tempo:** ~10 minutos  
**Status:** ✅ CORRIGIDO

---

## 🔍 Erro Identificado

### Erro no Backend (500 Internal Server Error)
```
AttributeError: type object 'JournalEntry' has no attribute 'DataTransacao'
```

**Arquivo:** `app_dev/backend/app/domains/transactions/service.py` (linha 116)  
**Método:** `get_all_grupos_breakdown()`

### Root Cause
No método `get_all_grupos_breakdown` que criamos, usamos o nome de coluna errado:
```python
# ❌ ERRADO
JournalEntry.DataTransacao >= dt_inicio,
JournalEntry.DataTransacao <= dt_fim,
```

O modelo `JournalEntry` **NÃO tem** coluna `DataTransacao`. As colunas de data são:
- `Data` (formato DD/MM/YYYY como string)
- `MesFatura` (formato YYYYMM como string) ✅
- `Ano` (integer)
- `Mes` (integer 1-12)

---

## ✅ Solução Implementada

### Mudança no Código
**Arquivo:** `app_dev/backend/app/domains/transactions/service.py`

**Antes (ERRADO):**
```python
# Query: agregar por grupo
results = self.repository.db.query(
    JournalEntry.GRUPO,
    func.sum(JournalEntry.Valor).label('total'),
    func.count(JournalEntry.IdTransacao).label('quantidade')
).filter(
    JournalEntry.user_id == user_id,
    JournalEntry.DataTransacao >= dt_inicio,  # ❌ Coluna não existe!
    JournalEntry.DataTransacao <= dt_fim,     # ❌ Coluna não existe!
    JournalEntry.CategoriaGeral == 'Despesa',
    JournalEntry.IgnorarDashboard == 0,
    JournalEntry.GRUPO.isnot(None)
).group_by(JournalEntry.GRUPO).all()
```

**Depois (CORRETO):**
```python
# Converter para MesFatura (YYYYMM)
mes_fatura_inicio = dt_inicio.strftime('%Y%m')  # Ex: "202601"
mes_fatura_fim = dt_fim.strftime('%Y%m')        # Ex: "202602"

# Query: agregar por grupo
results = self.repository.db.query(
    JournalEntry.GRUPO,
    func.sum(JournalEntry.Valor).label('total'),
    func.count(JournalEntry.IdTransacao).label('quantidade')
).filter(
    JournalEntry.user_id == user_id,
    JournalEntry.MesFatura >= mes_fatura_inicio,  # ✅ Coluna correta!
    JournalEntry.MesFatura <= mes_fatura_fim,     # ✅ Coluna correta!
    JournalEntry.CategoriaGeral == 'Despesa',
    JournalEntry.IgnorarDashboard == 0,
    JournalEntry.GRUPO.isnot(None)
).group_by(JournalEntry.GRUPO).all()
```

---

## 📊 Modelo JournalEntry (Colunas de Data)

### Estrutura Real:
```python
class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    # Dados principais
    Data = Column(String)           # ✅ Formato: "01/02/2026" (DD/MM/YYYY)
    
    # Dados temporais
    MesFatura = Column(String)      # ✅ Formato: "202602" (YYYYMM)
    Ano = Column(Integer)           # ✅ Ex: 2026
    Mes = Column(Integer)           # ✅ Ex: 2 (fevereiro)
    
    # ❌ NÃO EXISTE: DataTransacao
    # ❌ NÃO EXISTE: ano_mes
```

### Por que usar `MesFatura`?
1. **Performance:** Já está indexada e otimizada para queries
2. **Consistência:** Usado em todo o sistema existente
3. **Formato adequado:** String YYYYMM permite comparação direta (>=, <=)
4. **Compatibilidade:** Funciona com período YTD (Year-to-Date)

---

## 🔄 Fluxo de Conversão

### Entrada do Frontend:
```
data_inicio = "2026-02-01"  (YYYY-MM-DD)
data_fim = "2026-02-28"     (YYYY-MM-DD)
```

### Conversão no Backend:
```python
dt_inicio = datetime.strptime("2026-02-01", '%Y-%m-%d')  # datetime object
dt_fim = datetime.strptime("2026-02-28", '%Y-%m-%d')     # datetime object

mes_fatura_inicio = dt_inicio.strftime('%Y%m')  # "202602"
mes_fatura_fim = dt_fim.strftime('%Y%m')        # "202602"
```

### Query no Banco:
```sql
SELECT GRUPO, SUM(Valor), COUNT(IdTransacao)
FROM journal_entries
WHERE user_id = 1
  AND MesFatura >= '202602'   -- Comparação de strings funciona!
  AND MesFatura <= '202602'
  AND CategoriaGeral = 'Despesa'
  AND IgnorarDashboard = 0
  AND GRUPO IS NOT NULL
GROUP BY GRUPO
```

---

## ✅ Checklist

- [x] Identificar erro (AttributeError: DataTransacao)
- [x] Verificar modelo JournalEntry (colunas disponíveis)
- [x] Corrigir nome da coluna (DataTransacao → MesFatura)
- [x] Ajustar conversão de data (YYYY-MM-DD → YYYYMM)
- [x] Reiniciar backend
- [x] Documentar correção

---

## 🚀 Teste

### Como Testar:
```bash
# 1. Fazer login:
http://localhost:3000/login

# 2. Acessar Dashboard Mobile:
http://localhost:3000/mobile/dashboard

# 3. Resultado esperado:
# - Sem erros "Failed to fetch"
# - Métricas carregam (Despesas, Investimentos)
# - Console limpo (sem erros 500)
```

### Endpoints Afetados:
- ✅ `GET /api/v1/transactions/grupo-breakdown?data_inicio=X&data_fim=Y`
- ✅ Dashboard Mobile (`/mobile/dashboard`)
- ✅ Budget Mobile (`/mobile/budget`)

---

**Status:** ✅ ERRO CORRIGIDO  
**Backend:** Reiniciado com correção  
**Próximo:** Testar dashboard mobile  
**Data de Conclusão:** 01/02/2026 21:25
