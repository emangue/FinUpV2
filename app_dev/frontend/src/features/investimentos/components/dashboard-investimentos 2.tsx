/**
 * Componente principal - Dashboard de Investimentos
 */

'use client'

import { useState, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Calculator } from 'lucide-react'
import { PortfolioOverview } from './portfolio-overview'
import { TimelineIndicators } from './timeline-indicators'
import { InvestmentsTable } from './investments-table'
import { DistribuicaoChart } from './distribuicao-chart'
import { DistribuicaoPorTipo } from './distribuicao-por-tipo'
import { EvolucaoTemporal } from './evolucao-temporal'
import { VisaoPorCorretora } from './visao-por-corretora'
import { ExportInvestimentos } from './export-investimentos'
import { PeriodFilter } from './period-filter'
import { InvestmentFilters } from './investment-filters'
import { AddInvestmentModal } from './add-investment-modal'
import { useInvestimentos } from '../hooks/use-investimentos'
import { useRendimentosTimeline } from '../hooks/use-rendimentos-timeline'
import { DashboardSkeleton } from './loading-states'
import { EmptyInvestimentos, EmptyFilterResults } from './empty-states'
import { ApiErrorFallback } from './error-boundary'
import type { InvestimentoPortfolio } from '../types'

export function DashboardInvestimentos() {
  const currentYear = new Date().getFullYear()
  const currentMonth = new Date().getMonth() + 1
  
  // Estados dos filtros
  const [startMonth, setStartMonth] = useState(currentMonth)
  const [startYear, setStartYear] = useState(currentYear - 1)
  const [endMonth, setEndMonth] = useState(currentMonth)
  const [endYear, setEndYear] = useState(currentYear)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedCorretora, setSelectedCorretora] = useState('all')
  const [addModalOpen, setAddModalOpen] = useState(false)
  
  const {
    investimentos,
    resumo,
    distribuicao,
    loading: loadingInvestimentos,
    error: errorInvestimentos,
    refresh,
  } = useInvestimentos({ limit: 100 })

  // Buscar histórico completo desde maio/2024 para o gráfico
  const {
    rendimentos,
    loading: loadingRendimentos,
  } = useRendimentosTimeline({
    ano_inicio: 2024,  // Início do histórico
    ano_fim: currentYear,
  })

  // Calcular tipos e corretoras únicos para os filtros
  const { types, corretoras } = useMemo(() => {
    const typesSet = new Set<string>()
    const corretorasSet = new Set<string>()
    
    investimentos.forEach(inv => {
      typesSet.add(inv.tipo_investimento)
      corretorasSet.add(inv.corretora)
    })
    
    return {
      types: Array.from(typesSet).sort(),
      corretoras: Array.from(corretorasSet).sort(),
    }
  }, [investimentos])

  // Filtrar investimentos baseado nos filtros ativos
  const filteredInvestimentos = useMemo(() => {
    return investimentos.filter(inv => {
      const matchesSearch = !searchTerm || 
        inv.nome_produto.toLowerCase().includes(searchTerm.toLowerCase()) ||
        inv.emissor?.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesType = selectedType === 'all' || inv.tipo_investimento === selectedType
      const matchesCorretora = selectedCorretora === 'all' || inv.corretora === selectedCorretora
      
      return matchesSearch && matchesType && matchesCorretora
    })
  }, [investimentos, searchTerm, selectedType, selectedCorretora])

  const handlePeriodChange = (sMonth: number, sYear: number, eMonth: number, eYear: number) => {
    setStartMonth(sMonth)
    setStartYear(sYear)
    setEndMonth(eMonth)
    setEndYear(eYear)
  }

  const handleClearFilters = () => {
    setSearchTerm('')
    setSelectedType('all')
    setSelectedCorretora('all')
  }

  // Loading state
  if (loadingInvestimentos || loadingRendimentos) {
    return <DashboardSkeleton />
  }

  // Error state
  if (errorInvestimentos) {
    return <ApiErrorFallback error={errorInvestimentos} onRetry={refresh} />
  }

  // Empty state - nenhum investimento cadastrado
  if (investimentos.length === 0) {
    return <EmptyInvestimentos onAdd={() => setAddModalOpen(true)} />
  }

  // Empty state - filtros sem resultado
  const hasFilters = searchTerm || selectedType !== 'all' || selectedCorretora !== 'all'
  if (hasFilters && filteredInvestimentos.length === 0) {
    return (
      <div className="space-y-6">
        {/* Header e filtros ainda visíveis */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Meus Investimentos</h1>
            <p className="text-muted-foreground">Acompanhe seu portfólio e rentabilidade</p>
          </div>
        </div>
        
        <InvestmentFilters
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          selectedType={selectedType}
          onTypeChange={setSelectedType}
          selectedCorretora={selectedCorretora}
          onCorretoraChange={setSelectedCorretora}
          types={types}
          corretoras={corretoras}
          onClearFilters={handleClearFilters}
        />
        
        <EmptyFilterResults onClearFilters={handleClearFilters} />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Meus Investimentos</h1>
          <p className="text-muted-foreground">
            Acompanhe seu portfólio e rentabilidade
          </p>
        </div>
        <div className="flex gap-2">
          <ExportInvestimentos 
            investimentos={filteredInvestimentos}
            filtrosAtivos={{
              searchTerm,
              selectedType,
              selectedCorretora
            }}
          />
          <Button 
            variant="outline" 
            className="flex items-center gap-2"
            onClick={() => window.location.href = '/investimentos/simulador'}
          >
            <Calculator className="h-4 w-4" />
            Simulador
          </Button>
          <Button onClick={() => setAddModalOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Adicionar
          </Button>
        </div>
      </div>

      {/* Filtro de Período */}
      <PeriodFilter
        startMonth={startMonth}
        startYear={startYear}
        endMonth={endMonth}
        endYear={endYear}
        onPeriodChange={handlePeriodChange}
      />

      {/* Resumo do Portfólio */}
      {resumo && <PortfolioOverview resumo={resumo} />}

      {/* Evolução Temporal do Patrimônio - Logo após as caixas */}
      {rendimentos.length > 0 && (
        <EvolucaoTemporal 
          timeline={rendimentos}
          cenario={{
            rendimento_mensal: 0.8,
            aporte_mensal: 5000
          }}
        />
      )}

      {/* Timeline de Indicadores */}
      {rendimentos.length > 0 && (
        <TimelineIndicators rendimentos={rendimentos} />
      )}

      {/* Filtros de Investimentos */}
      <InvestmentFilters
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        selectedType={selectedType}
        onTypeChange={setSelectedType}
        selectedCorretora={selectedCorretora}
        onCorretoraChange={setSelectedCorretora}
        types={types}
        corretoras={corretoras}
        onClearFilters={handleClearFilters}
      />

      {/* Grid com Tabela e Gráficos */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Tabela de Investimentos */}
        <div className="lg:col-span-2">
          <InvestmentsTable 
            investimentos={filteredInvestimentos}
            onRefresh={refresh}
          />
        </div>

        {/* Gráficos */}
        <div className="space-y-6">
          {distribuicao.length > 0 && (
            <DistribuicaoChart distribuicao={distribuicao} />
          )}
        </div>
      </div>

      {/* Distribuição por Classe de Ativo */}
      {distribuicao.length > 0 && resumo && (
        <DistribuicaoPorTipo 
          distribuicao={distribuicao}
          totalGeral={parseFloat(resumo.total_investido)}
        />
      )}

      {/* Visão por Corretora */}
      {investimentos.length > 0 && resumo && (
        <VisaoPorCorretora 
          investimentos={investimentos}
          totalGeral={parseFloat(resumo.total_investido)}
        />
      )}

      {/* Modal de Adicionar */}
      <AddInvestmentModal
        open={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        onSuccess={refresh}
      />
    </div>
  )
}
