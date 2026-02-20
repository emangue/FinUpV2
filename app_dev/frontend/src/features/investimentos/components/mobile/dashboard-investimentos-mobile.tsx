/**
 * Dashboard de Investimentos - Mobile
 * Adaptação mobile do dashboard de investimentos
 */

'use client'

import { useState, useMemo } from 'react'
import { PortfolioOverview } from '../portfolio-overview'
import { TimelineIndicators } from '../timeline-indicators'
import { DistribuicaoChart } from '../distribuicao-chart'
import { DistribuicaoPorTipo } from '../distribuicao-por-tipo'
import { EvolucaoTemporal } from '../evolucao-temporal'
import { VisaoPorCorretora } from '../visao-por-corretora'
import { useInvestimentos } from '../../hooks/use-investimentos'
import { useRendimentosTimeline } from '../../hooks/use-rendimentos-timeline'
import { DashboardSkeleton } from '../loading-states'
import { EmptyInvestimentos, EmptyFilterResults } from '../empty-states'
import { ApiErrorFallback } from '../error-boundary'
import { InvestmentFilters } from '../investment-filters'
import { PeriodFilter } from '../period-filter'
import { BottomNav } from '@/components/mobile/bottom-nav'

export function DashboardInvestimentosMobile() {
  const [addModalOpen, setAddModalOpen] = useState(false)
  // TODO: Adaptação mobile dos estados e filtros
  const currentYear = new Date().getFullYear()
  const currentMonth = new Date().getMonth() + 1

  const [startMonth, setStartMonth] = useState(currentMonth)
  const [startYear, setStartYear] = useState(currentYear - 1)
  const [endMonth, setEndMonth] = useState(currentMonth)
  const [endYear, setEndYear] = useState(currentYear)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedCorretora, setSelectedCorretora] = useState('all')

  const {
    investimentos,
    resumo,
    distribuicao,
    loading: loadingInvestimentos,
    error: errorInvestimentos,
    refresh,
  } = useInvestimentos({ limit: 100 })

  const {
    rendimentos,
    loading: loadingRendimentos,
  } = useRendimentosTimeline({
    ano_inicio: 2024,
    ano_fim: currentYear,
  })

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

  // Loading
  if (loadingInvestimentos || loadingRendimentos) {
    return <DashboardSkeleton />
  }
  // Error
  if (errorInvestimentos) {
    return <ApiErrorFallback error={errorInvestimentos} onRetry={refresh} />
  }
  // Empty
  if (investimentos.length === 0) {
    return <EmptyInvestimentos onAdd={() => setAddModalOpen(true)} />
  }
  const hasFilters = searchTerm || selectedType !== 'all' || selectedCorretora !== 'all'
  if (hasFilters && filteredInvestimentos.length === 0) {
    return <EmptyFilterResults onClearFilters={handleClearFilters} />
  }

  // Layout mobile: vertical, cards empilhados, scrollável
  return (
    <>
      <div className="min-h-screen bg-background pb-20 px-2 space-y-4 overflow-x-hidden">
        {/* Filtros mobile */}
        <div className="pt-4">
          <PeriodFilter
            startMonth={startMonth}
            startYear={startYear}
            endMonth={endMonth}
            endYear={endYear}
            onPeriodChange={handlePeriodChange}
          />
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
        </div>
        {/* Resumo do Portfólio */}
        {resumo && <PortfolioOverview resumo={resumo} />}
        {/* Gráficos principais */}
        {rendimentos.length > 0 && (
          <EvolucaoTemporal timeline={rendimentos} cenario={{ rendimento_mensal: 0.8, aporte_mensal: 0 }} />
        )}
        {distribuicao && <DistribuicaoChart distribuicao={distribuicao} />}
        {distribuicao && resumo && (
          <DistribuicaoPorTipo 
            distribuicao={distribuicao}
            totalGeral={parseFloat(resumo.total_investido)}
          />
        )}
        {resumo && (
          <VisaoPorCorretora 
            investimentos={filteredInvestimentos}
            totalGeral={parseFloat(resumo.total_investido)}
          />
        )}
        {/* Indicadores de linha do tempo */}
        <TimelineIndicators rendimentos={rendimentos} />
        {/* TODO: Cards de investimentos, botões, etc. */}
      </div>
      <BottomNav />
    </>
  )
}
