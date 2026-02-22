# Plano de Reversão - Dashboard Mês/YTD/Ano

**Data:** 20/02/2026  
**Contexto:** Alterações perdidas após commit 0f3ba79a (restaura). Este documento registra o que foi implementado na sessão e o plano para reaplicar.

---

## Resumo do que foi implementado

### 1. Toggle 3 opções
- **Mês:** Dados do mês selecionado
- **YTD:** Comparar anos até o último mês com dado (ex: Jan-Fev 2024 vs Jan-Fev 2025)
- **Ano:** Comparar anos completos (Jan-Dez)

### 2. Backend
- `GET /dashboard/chart-data-ytd?years=2024,2025&last_month=2` - YTD por ano
- `GET /dashboard/years-with-data` - Anos com dados
- `GET /dashboard/chart-data-by-years?years=2024,2025` - Ano completo por ano
- `through_month` em: metrics, budget-vs-actual, income-sources, orcamento-investimentos, credit-cards
- `_build_date_filter(year, month, through_month)` no repository
- Python 3.9: `Optional[int]` em vez de `int | None`

### 3. Frontend
- **YearScrollPicker** - Scroll de anos (criar, baseado em MonthScrollPicker)
- **dashboard-api.ts:** fetchChartDataYtd, fetchChartDataByYears, fetchYearsWithData, throughMonth em todas as funções
- **use-dashboard.ts:** useChartDataYtd, useChartDataByYears, useYearsWithData, throughMonth nos hooks, remover console.logs
- **Dashboard page:** lastMonthWithData state, YearScrollPicker para ytd/year, chartDataToUse por período
- **OrcamentoTab:** period, throughMonth, fetchBudgetVsActual/fetchOrcamentoInvestimentos com throughParam
- **BarChart:** period 'month'|'ytd'|'year', legendas diferentes
- **GastosPorCartaoBox:** useMemo filters (evitar useEffect deps size change), throughMonth

### 4. Estrutura do Dashboard (versão restaurada)
- 2 tabs: Resultado, Patrimônio
- OrcamentoTab dentro de Resultado (Resumo + Gráfico + Orçamento + Cartões)
- KpiCards no topo

---

## Ordem de execução

1. YTDToggle (3 opções)
2. YearScrollPicker
3. Backend (router, service, repository)
4. dashboard-api.ts
5. use-dashboard.ts
6. OrcamentoTab
7. BarChart
8. GastosPorCartaoBox
9. Dashboard page
