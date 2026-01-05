'use client';

import React, { useState, useEffect } from 'react';
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
  
  // Estados de filtros
  const [selectedYear, setSelectedYear] = useState('2024');
  const [selectedMonth, setSelectedMonth] = useState('all');

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
      
      // Usar ano/mês atual se month='all'
      const now = new Date();
      const queryYear = year;
      const queryMonth = month === 'all' ? now.getMonth() + 1 : month;
      
      const params = new URLSearchParams({ 
        year: queryYear,
        month: queryMonth.toString()
      });
      const response = await fetch(`/api/dashboard/metrics?${params}`);
      
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
      
      // Para chart-data, sempre buscar o ano todo (ignora month)
      const params = new URLSearchParams({ 
        year: year,
        month: '1' // Pode ser qualquer mês, backend ignora e retorna o ano todo
      });
      const response = await fetch(`/api/dashboard/chart-data?${params}`);
      
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
      
      // Usar ano/mês atual se month='all'
      const now = new Date();
      const queryYear = year;
      const queryMonth = month === 'all' ? now.getMonth() + 1 : month;
      
      const params = new URLSearchParams({ 
        year: queryYear,
        month: queryMonth.toString()
      });
      const response = await fetch(`/api/dashboard/categories?${params}`);
      
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

  const fetchData = (year: string, month: string) => {
    fetchMetrics(year, month);
    fetchChartData(year, month);
    fetchCategoryData(year, month);
  };

  useEffect(() => {
    fetchData(selectedYear, selectedMonth);
  }, []);

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

      {/* Grid Layout Principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Coluna Esquerda - Gráfico Receitas vs Despesas */}
        <div className="lg:col-span-2">
          {/* Filtros de Data e Métricas na mesma linha */}
          <div className="flex justify-between items-center mb-4">
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
          
          <ChartAreaInteractive
            data={chartData}
            loading={loadingChart}
            error={chartError}
          />
        </div>

        {/* Coluna Direita - Realizado vs Planejado */}
        <div className="lg:col-span-1">
          <BudgetVsActual
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
        <CreditCardExpenses />
      </div>

      {/* Refresh Button */}
      <div className="mt-6 flex justify-center">
        <button
          onClick={() => fetchData(selectedYear, selectedMonth)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          disabled={loadingMetrics || loadingChart || loadingCategories}
        >
          {(loadingMetrics || loadingChart || loadingCategories) ? 'Carregando...' : 'Atualizar Dados'}
        </button>
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;