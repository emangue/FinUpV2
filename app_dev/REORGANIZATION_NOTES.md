# 📋 Reorganização do Projeto - Janeiro 2026

## ✅ Mudanças Implementadas

### 1. **Consolidação da Estrutura**
- ❌ **Removido**: `app_dev` (versão Flask/React antiga)
- ✅ **Mantido**: `app_dev_nextjs` → renomeado para `app_dev` (versão Next.js)
- 🎯 **Resultado**: Estrutura única e clara, sem duplicação confusa

### 2. **Filtro Dashboard - IgnorarDashboard = 0**
Implementado em **TODAS** as APIs do dashboard:

#### APIs Atualizadas:
- ✅ `/api/dashboard/metrics` - Métricas financeiras
- ✅ `/api/dashboard/chart-data` - Dados do gráfico receitas vs despesas
- ✅ `/api/dashboard/categories` - Categorias de gasto

#### Exemplo de Filtro:
```sql
-- Antes
WHERE TipoTransacao = 'Receitas'

-- Depois
WHERE TipoTransacao = 'Receitas' AND IgnorarDashboard = 0
```

### 3. **Gráfico de Categorias - TipoGasto vs Receita**

#### Mudança Fundamental:
- ❌ **Antes**: Baseado em `GRUPO` 
- ✅ **Agora**: Baseado em `TipoGasto`

#### Query Implementada:
```sql
SELECT 
  TipoGasto as categoria,
  SUM(ValorPositivo) as valor,
  (SUM(ValorPositivo) / [receita_total] * 100) as percentual
FROM journal_entries
WHERE TipoTransacao IN ('Despesas', 'Cartão de Crédito')
  AND IgnorarDashboard = 0
  AND TipoGasto NOT IN (...)
  AND TipoGasto IS NOT NULL
GROUP BY TipoGasto
```

### 4. **Exclusões do Dashboard**

#### Tipos de Gasto Excluídos:
1. **Investimento - Ajustável**
2. **Investimento - Fixo**
3. **Pagamento Fatura**
4. **Receita - Outras**
5. **Receita - Salário**
6. **Salário**
7. **Transferência**

#### Justificativa:
- 🏦 **Investimentos**: Não são gastos operacionais
- 💳 **Pagamento Fatura**: Evita dupla contabilização
- 💰 **Receitas/Salário**: Estão na categoria errada (devem ser receitas)
- 🔄 **Transferências**: Movimentação interna, não gasto real

### 5. **Dados Filtrados**

#### Estatísticas (2025):
- **Total com filtro**: 1,400 transações ignoradas
- **Categorias exibidas**: Top 10 tipos de gasto válidos
- **Exemplo top 3**:
  1. Ajustável - Carro (275 transações)
  2. Ajustável - Assinaturas (172 transações) 
  3. Ajustável - Uber (148 transações)

## 🚀 Como Utilizar

### Estrutura Final:
```
ProjetoFinancasV3/
├── app/           # Versão produção (Flask)
├── app_dev/       # Versão desenvolvimento (Next.js) ✅
└── app_dev_old_*  # Backup da versão anterior
```

### Executar Dashboard:
```bash
cd app_dev
npm run dev
# Servidor: http://localhost:3000
```

### APIs Disponíveis:
- `GET /api/dashboard/metrics?year=2025&month=all`
- `GET /api/dashboard/chart-data?year=2025&month=all`  
- `GET /api/dashboard/categories?year=2025&month=all`

---

**📅 Data**: 03/01/2026  
**👨‍💻 Implementado por**: Sistema de Versionamento Automático  
**✅ Status**: Concluído e testado