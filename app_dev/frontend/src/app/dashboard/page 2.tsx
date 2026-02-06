'use client';

import React, { useState, useEffect } from 'react';
import { fetchWithAuth } from '@/core/utils/api-client';
import {
  ChartAreaInteractive,
  DateFilters,
  CompactMetrics,
  CategoryExpenses,
  BudgetVsActual,
  CreditCardExpenses
} from '@/features/dashboard';
import DashboardLayout from '@/components/dashboard-layout';

interface Metrics {
  totalDespesas: number;
  totalReceitas: number;
  saldoAtual: number;
  totalTransacoes: number;
}

interface ChartDataItem {
  mes: string;
  receitas: number;
  despesas: number;
}

interface CategoryData {
  categoria: string;
  valor: number;
  percentual: number;
}

const DashboardPage = () => {
  // Estados para dados
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [chartData, setChartData] = useState<ChartDataItem[]>([]);
  const [categoryData, setCategoryData] = useState<CategoryData[]>([]);
  
  // Estados de loading
  const [loadingMetrics, setLoadingMetrics] = useState(true);
  const [loadingChart, setLoadingChart] = useState(true);
  const [loadingCategories, setLoadingCategories] = useState(true);
  
  // Estados de erro
  const [metricsError, setMetricsError] = useState<string | null>(null);
  const [chartError, setChartError] = useState<string | null>(null);
  const [categoriesError, setCategoriesError] = useState<string | null>(null);
  
  // Estados de filtros - Detectar último mês automaticamente
  const [selectedYear, setSelectedYear] = useState('2025'); // Usar 2025 onde há dados
  const [selectedMonth, setSelectedMonth] = useState('12'); // Último mês com dados
  const [chartDataYear, setChartDataYear] = useState('2026'); // Ano dos dados do gráfico
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  // Função para detectar último mês com dados
  const getLastMonthWithData = (data: ChartDataItem[]): { year: string; month: string } => {
    if (!data || data.length === 0) {
      return { year: '2026', month: '01' };
    }
    
    // Mapear meses para números
    const monthMap: { [key: string]: string } = {
      'Jan': '01', 'Fev': '02', 'Mar': '03', 'Abr': '04', 'Mai': '05', 'Jun': '06',
      'Jul': '07', 'Ago': '08', 'Set': '09', 'Out': '10', 'Nov': '11', 'Dez': '12'
    };
    
    // Criar array ordenado por data para encontrar o mais recente
    const dataWithDates = data.map((item, index) => {
      let year = chartDataYear;
      let month = monthMap[item.mes];
      
      // Se começamos de 2026 e temos 12 meses, os primeiros meses são de 2025
      if (chartDataYear === '2026') {
        // Jan na posição 0-1: 2025, Jan na posição 10-11: 2026
        if (item.mes === 'Jan' && index < 2) {
          year = '2025';
        } else if (index < 2) {
          year = '2025';
        }
      }
      
      return {
        ...item,
        year,
        month,
        sortKey: `${year}${month}`, // Para ordenação
        hasData: item.receitas > 0 || item.despesas > 0
      };
    });
    
    // Encontrar último mês com dados
    const monthsWithData = dataWithDates
      .filter(item => item.hasData)
      .sort((a, b) => b.sortKey.localeCompare(a.sortKey)); // Ordenar por data desc
    
    if (monthsWithData.length > 0) {
      const lastMonth = monthsWithData[0];
      return { year: lastMonth.year, month: lastMonth.month };
    }
    
    return { year: '2026', month: '01' };
  };

  // Dados mock para desenvolvimento
  const mockMetrics: Metrics = {
    totalDespesas: 8547.32,
    totalReceitas: 12450.00,
    saldoAtual: 3902.68,
    totalTransacoes: 245
  };

  const mockCategoryData: CategoryData[] = [
    { categoria: 'Alimentação', valor: 1850.40, percentual: 21.6 },
    { categoria: 'Transporte', valor: 950.20, percentual: 11.1 },
    { categoria: 'Moradia', valor: 2100.00, percentual: 24.5 },
    { categoria: 'Saúde', valor: 450.75, percentual: 5.3 },
    { categoria: 'Lazer', valor: 680.50, percentual: 8.0 },
    { categoria: 'Educação', valor: 320.00, percentual: 3.7 },
    { categoria: 'Compras', valor: 1210.85, percentual: 14.2 },
    { categoria: 'Outros', valor: 983.62, percentual: 11.5 }
  ];

  const fetchMetrics = async (year: string, month: string) => {
    try {
      setLoadingMetrics(true);
      setMetricsError(null);
      
      const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1` : 'http://localhost:8000/api/v1';
      // Se month='all', não enviar parâmetro month (backend retorna ano todo)
      const params = new URLSearchParams({ 
        year: year
      });
      
      if (month !== 'all') {
        params.append('month', month);
      }
      
      const response = await fetchWithAuth(`${apiUrl}/dashboard/metrics?${params}`);
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar métricas: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Mapear resposta do backend para o formato do frontend
      setMetrics({
        totalDespesas: data.total_despesas,
        totalReceitas: data.total_receitas,
        saldoAtual: data.saldo_periodo,
        totalTransacoes: data.num_transacoes
      });
      
    } catch (error) {
      console.error('Error fetching metrics:', error);
      setMetricsError(error instanceof Error ? error.message : 'Erro desconhecido');
    } finally {
      setLoadingMetrics(false);
    }
  };

  const fetchChartData = async (year: string, month: string) => {
    try {
      setLoadingChart(true);
      setChartError(null);
      
      const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1` : 'http://localhost:8000/api/v1';
      // Buscar 12 meses de histórico até o mês selecionado (ou último mês se 'all')
      const targetMonth = month === 'all' ? '12' : month;
      
      const params = new URLSearchParams({ 
        year: year,
        month: targetMonth
      });
      const response = await fetchWithAuth(`${apiUrl}/dashboard/chart-data?${params}`);
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar dados do gráfico: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Backend já retorna no formato correto: { date: "Jan", receitas: X, despesas: Y }
      const formattedData = data.data.map((item: any) => ({
        mes: item.date,  // Já vem como "Jan", "Fev", etc
        receitas: item.receitas,
        despesas: item.despesas
      }));
      
      setChartData(formattedData);
      setChartDataYear(year); // Armazenar o ano dos dados do gráfico
      
      // Se é carregamento inicial, detectar último mês com dados
      if (isInitialLoad && formattedData.length > 0) {
        const lastData = getLastMonthWithData(formattedData);
        if (lastData.month !== selectedMonth || lastData.year !== selectedYear) {
          setSelectedMonth(lastData.month);
          setSelectedYear(lastData.year); // Atualizar também o ano se detectado diferente
          // Recarregar dados com o ano e mês corretos, mas evitar loop
          setTimeout(() => {
            fetchMetrics(lastData.year, lastData.month);
            fetchCategoryData(lastData.year, lastData.month);
          }, 100);
        }
      }
      
    } catch (error) {
      console.error('Error fetching chart data:', error);
      setChartError(error instanceof Error ? error.message : 'Erro desconhecido');
    } finally {
      setLoadingChart(false);
    }
  };

  const fetchCategoryData = async (year: string, month: string) => {
    try {
      setLoadingCategories(true);
      setCategoriesError(null);
      
      const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1` : 'http://localhost:8000/api/v1';
      // Se month='all', não enviar parâmetro month (backend retorna ano todo)
      const params = new URLSearchParams({ 
        year: year
      });
      
      if (month !== 'all') {
        params.append('month', month);
      }
      
      const response = await fetchWithAuth(`${apiUrl}/dashboard/categories?${params}`);
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar dados de categorias: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Mapear resposta do backend para o formato do frontend
      const formattedData = data.map((item: any) => ({
        categoria: item.categoria,
        valor: item.total,
        percentual: item.percentual
      }));
      
      setCategoryData(formattedData);
      
    } catch (error) {
      console.error('Error fetching category data:', error);
      setCategoriesError(error instanceof Error ? error.message : 'Erro desconhecido');
    } finally {
      setLoadingCategories(false);
    }
  };

  const handleYearChange = (year: string) => {
    setSelectedYear(year);
    fetchData(year, selectedMonth);
  };

  const handleMonthChange = (month: string) => {
    setSelectedMonth(month);
    fetchData(selectedYear, month);
  };

  // Handler para click no gráfico - usar ano dos dados, não ano selecionado atual
  const handleChartMonthClick = (month: string) => {
    // Usar o ano dos dados do gráfico, não o ano selecionado atual
    const yearToUse = chartDataYear;
    
    setSelectedMonth(month);
    setSelectedYear(yearToUse); // Atualizar também o ano selecionado
    fetchData(yearToUse, month);
  };

  const fetchData = (year: string, month: string) => {
    fetchMetrics(year, month);
    fetchChartData(year, month);
    fetchCategoryData(year, month);
    setLastUpdate(new Date());
  };

  // Carregar dados no mount inicial - começar com janeiro 2026 e detectar último mês
  useEffect(() => {
    if (isInitialLoad) {
      // Iniciar com janeiro 2026 como estimativa, será ajustado após carregar dados
      fetchData(selectedYear, '01'); // Começar com janeiro do ano atual
      setIsInitialLoad(false);
    }
  }, [isInitialLoad]);

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Dashboard Financeiro
        </h1>
        <p className="text-gray-600">
          Visão geral das suas finanças pessoais
        </p>
      </div>

      {/* Filtros e Métricas Centralizados */}
      <div className="flex justify-center items-center gap-8 mb-6">
        <DateFilters 
          selectedYear={selectedYear}
          selectedMonth={selectedMonth}
          onYearChange={handleYearChange}
          onMonthChange={handleMonthChange}
        />
        
        <CompactMetrics 
          metrics={metrics || undefined}
          loading={loadingMetrics}
          error={metricsError}
        />
      </div>

      {/* Grid Layout Principal */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Coluna Esquerda - Gráfico Receitas vs Despesas */}
        <div className="lg:col-span-1">
          <ChartAreaInteractive
            data={chartData}
            loading={loadingChart}
            error={chartError}
            selectedMonth={selectedMonth}
            onMonthClick={handleChartMonthClick}
          />
        </div>

        {/* Coluna Direita - Realizado vs Planejado */}
        <div className="lg:col-span-1">
          <BudgetVsActual
            year={selectedYear}
            month={selectedMonth}
            loading={false}
            error={null}
          />
        </div>
      </div>

      {/* Grid Layout Inferior */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Esquerda Inferior - Gastos por Categoria */}
        <CategoryExpenses
          data={categoryData}
          loading={loadingCategories}
          error={categoriesError}
        />

        {/* Direita Inferior - Gastos com Cartões */}
        <CreditCardExpenses year={selectedYear} month={selectedMonth} />
      </div>

      {/* Refresh Button com indicação de última atualização */}
      <div className="mt-6 flex justify-center items-center gap-4">
        <button
          onClick={() => {
            console.log('🔄 Atualizando dashboard manualmente...');
            fetchData(selectedYear, selectedMonth);
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          disabled={loadingMetrics || loadingChart || loadingCategories}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {(loadingMetrics || loadingChart || loadingCategories) ? 'Carregando...' : 'Atualizar Dashboard'}
        </button>
        {lastUpdate && (
          <span className="text-sm text-muted-foreground">
            Última atualização: {lastUpdate.toLocaleTimeString('pt-BR')}
          </span>
        )}
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;