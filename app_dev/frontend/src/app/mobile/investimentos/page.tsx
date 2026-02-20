'use client'

/**
 * Investimentos Mobile - Tela de detalhamento de investimentos
 *
 * - Scroll de meses fixo no topo (filtra por anomes)
 * - Toggle Ativos / Passivos / Todos
 * - Filtro por tipo (com opção de desfiltrar)
 * - Lista de cards de investimentos
 * - Criar novo, editar, copiar do mês anterior
 */

import * as React from 'react'
import { Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker'
import { InvestmentCard } from '@/features/investimentos/components/mobile/investment-card'
import { CreateInvestmentSheet } from '@/features/investimentos/components/mobile/create-investment-sheet'
import { EditValorMesSheet } from '@/features/investimentos/components/mobile/edit-valor-mes-sheet'
import {
  getInvestimentos,
  copiarMesAnterior,
} from '@/features/investimentos/services/investimentos-api'
import { fetchLastMonthWithData } from '@/features/dashboard/services/dashboard-api'
import type { InvestimentoPortfolio } from '@/features/investimentos/types'
import { TrendingUp, Plus, Copy, ArrowLeft, Filter, X, Calculator } from 'lucide-react'
import { useRequireAuth } from '@/core/hooks/use-require-auth'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { cn } from '@/lib/utils'

type ClasseToggle = 'todos' | 'ativos' | 'passivos'

function getValorTotalMes(inv: InvestimentoPortfolio): number {
  const v = inv.valor_total_mes
  if (v == null) return parseFloat(inv.valor_total_inicial || '0') || 0
  return typeof v === 'number' ? v : parseFloat(String(v)) || 0
}

function InvestimentosMobileContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const isAuth = useRequireAuth()
  const anomesFromUrl = searchParams.get('anomes')
  const tipoFromUrl = searchParams.get('tipo')
  const [selectedMonth, setSelectedMonth] = React.useState<Date>(new Date())
  const [classeToggle, setClasseToggle] = React.useState<ClasseToggle>('todos')
  const [filterSheetOpen, setFilterSheetOpen] = React.useState(false)

  React.useEffect(() => {
    if (anomesFromUrl) {
      const a = parseInt(anomesFromUrl, 10)
      if (a >= 200001 && a <= 210012) {
        setSelectedMonth(new Date(Math.floor(a / 100), (a % 100) - 1))
      }
      return
    }
    let cancelled = false
    fetchLastMonthWithData('patrimonio')
      .then(({ year, month }) => {
        if (!cancelled) setSelectedMonth(new Date(year, month - 1, 1))
      })
      .catch(() => {})
    return () => { cancelled = true }
  }, [anomesFromUrl])
  const [investimentos, setInvestimentos] = React.useState<InvestimentoPortfolio[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [createOpen, setCreateOpen] = React.useState(false)
  const [copying, setCopying] = React.useState(false)
  const [editValorInvestment, setEditValorInvestment] = React.useState<InvestimentoPortfolio | null>(null)

  const anomes = selectedMonth.getFullYear() * 100 + (selectedMonth.getMonth() + 1)
  const ano = selectedMonth.getFullYear()

  // Sempre busca todos (filtros aplicados no client)
  const loadInvestimentos = React.useCallback(() => {
    if (!isAuth) return
    setLoading(true)
    setError(null)
    getInvestimentos({ ativo: true, anomes, limit: 200 })
      .then(setInvestimentos)
      .catch((err) => setError(err?.message || 'Erro ao carregar investimentos'))
      .finally(() => setLoading(false))
  }, [isAuth, anomes])

  React.useEffect(() => {
    loadInvestimentos()
  }, [loadInvestimentos])

  // Filtros client-side: tipo (da URL) + classe (ativos/passivos)
  // Deduplica por balance_id (evita "duplicate key" do React se API retornar duplicados)
  const filteredInvestimentos = React.useMemo(() => {
    const seen = new Set<string>()
    return investimentos.filter((inv) => {
      const valor = getValorTotalMes(inv)
      if (classeToggle === 'ativos' && valor <= 0) return false
      if (classeToggle === 'passivos' && valor >= 0) return false
      if (tipoFromUrl && inv.tipo_investimento !== tipoFromUrl) return false
      const key = inv.balance_id ?? String(inv.id)
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  }, [investimentos, classeToggle, tipoFromUrl])

  const tiposDisponiveis = React.useMemo(
    () => Array.from(new Set(investimentos.map((i) => i.tipo_investimento))).sort(),
    [investimentos]
  )

  const clearTipoFilter = () => {
    const params = new URLSearchParams(searchParams.toString())
    params.delete('tipo')
    router.push(`/mobile/investimentos${params.toString() ? `?${params.toString()}` : ''}`)
  }

  const selectTipoFilter = (tipo: string | null) => {
    const params = new URLSearchParams(searchParams.toString())
    if (tipo) params.set('tipo', tipo)
    else params.delete('tipo')
    router.push(`/mobile/investimentos${params.toString() ? `?${params.toString()}` : ''}`)
    setFilterSheetOpen(false)
  }

  const handleCopiarMesAnterior = async () => {
    setCopying(true)
    try {
      const { copiados } = await copiarMesAnterior(anomes)
      if (copiados > 0) loadInvestimentos()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao copiar')
    } finally {
      setCopying(false)
    }
  }

  if (!isAuth) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50 overflow-hidden">
      {/* Header: Voltar | Título | Filtrar | Novo */}
      <div className="sticky top-0 z-20 bg-white border-b border-gray-200 shrink-0">
        <div className="flex items-center gap-2 px-2 py-2">
          <button
            onClick={() => router.back()}
            className="p-2 rounded-full text-gray-600 hover:bg-gray-100 hover:text-gray-900 shrink-0"
            aria-label="Voltar"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="flex-1 text-base font-semibold text-gray-900 truncate">
            Meus Investimentos
          </h1>
          <Sheet open={filterSheetOpen} onOpenChange={setFilterSheetOpen}>
            <SheetTrigger asChild>
              <button
                className={cn(
                  'p-2 rounded-full shrink-0',
                  tipoFromUrl
                    ? 'text-indigo-600 bg-indigo-50'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                )}
                aria-label="Filtrar"
              >
                <Filter className="w-5 h-5" />
              </button>
            </SheetTrigger>
            <SheetContent side="bottom" className="rounded-t-2xl max-h-[70vh]">
              <SheetHeader>
                <SheetTitle>Filtrar por tipo</SheetTitle>
              </SheetHeader>
              <div className="mt-4 space-y-2 overflow-y-auto max-h-[50vh]">
                <button
                  onClick={() => selectTipoFilter(null)}
                  className={cn(
                    'w-full py-3 px-4 rounded-xl text-left font-medium transition-colors',
                    !tipoFromUrl
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  )}
                >
                  Todos os tipos
                </button>
                {tiposDisponiveis.map((tipo) => (
                  <button
                    key={tipo}
                    onClick={() => selectTipoFilter(tipo)}
                    className={cn(
                      'w-full py-3 px-4 rounded-xl text-left font-medium transition-colors',
                      tipoFromUrl === tipo
                        ? 'bg-indigo-100 text-indigo-700'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    )}
                  >
                    {tipo}
                  </button>
                ))}
              </div>
            </SheetContent>
          </Sheet>
          <button
            onClick={() => router.push('/mobile/investimentos/simulador')}
            className="p-2 rounded-full text-gray-600 hover:bg-gray-100 hover:text-gray-900 shrink-0"
            aria-label="Simulador"
          >
            <Calculator className="w-5 h-5" />
          </button>
          <button
            onClick={() => setCreateOpen(true)}
            className="p-2 rounded-full text-gray-600 hover:bg-gray-100 hover:text-gray-900 shrink-0"
            aria-label="Novo investimento"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>
        {/* Scroll de meses */}
        <div className="px-2 pb-2">
          <MonthScrollPicker
            selectedMonth={selectedMonth}
            onMonthChange={setSelectedMonth}
          />
        </div>
        {/* Toggle Ativos / Passivos / Todos */}
        <div className="flex gap-1 px-4 pb-3">
          <div className="flex rounded-lg bg-gray-100 p-1 w-full">
            {(['todos', 'ativos', 'passivos'] as const).map((opt) => (
              <button
                key={opt}
                onClick={() => setClasseToggle(opt)}
                className={cn(
                  'flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors',
                  classeToggle === opt
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                {opt === 'todos' ? 'Todos' : opt === 'ativos' ? 'Ativos' : 'Passivos'}
              </button>
            ))}
          </div>
        </div>
        {/* Chip filtro por tipo (quando ativo) */}
        {tipoFromUrl && (
          <div className="px-4 pb-3">
            <button
              onClick={clearTipoFilter}
              className="inline-flex items-center gap-1.5 py-1.5 px-3 rounded-full bg-indigo-100 text-indigo-700 text-sm font-medium hover:bg-indigo-200"
            >
              Filtrado: {tipoFromUrl}
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Conteúdo rolável */}
      <div className="flex-1 min-h-0 overflow-y-auto px-5 py-4">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mb-4" />
            <p className="text-gray-500 text-sm">Carregando investimentos...</p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-16">
            <p className="text-red-600 text-center mb-4">{error}</p>
            <button
              onClick={loadInvestimentos}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium"
            >
              Tentar novamente
            </button>
          </div>
        ) : filteredInvestimentos.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16">
            <TrendingUp className="w-16 h-16 text-gray-300 mb-4" />
            <p className="text-gray-600 font-medium mb-2">
              {investimentos.length === 0
                ? 'Nenhum investimento neste mês'
                : 'Nenhum resultado com os filtros aplicados'}
            </p>
            <p className="text-gray-500 text-sm text-center mb-6">
              {investimentos.length === 0
                ? 'Cadastre um novo ou copie do mês anterior'
                : 'Tente alterar os filtros ou limpar o filtro de tipo'}
            </p>
            <div className="flex flex-col gap-3 w-full max-w-xs">
              {(tipoFromUrl || classeToggle !== 'todos') && (
                <button
                  onClick={() => {
                    clearTipoFilter()
                    setClasseToggle('todos')
                  }}
                  className="w-full py-3 bg-gray-200 text-gray-800 rounded-xl font-semibold"
                >
                  Limpar filtros
                </button>
              )}
              {investimentos.length === 0 && (
                <>
                  <button
                    onClick={() => setCreateOpen(true)}
                    className="w-full py-3 bg-indigo-600 text-white rounded-xl font-semibold flex items-center justify-center gap-2"
                  >
                    <Plus className="w-5 h-5" />
                    Novo investimento
                  </button>
                  <button
                    onClick={handleCopiarMesAnterior}
                    disabled={copying}
                    className="w-full py-3 bg-gray-200 text-gray-800 rounded-xl font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    <Copy className="w-5 h-5" />
                    {copying ? 'Copiando...' : 'Copiar do mês anterior'}
                  </button>
                </>
              )}
            </div>
          </div>
        ) : (
          <>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-gray-900">Meus Investimentos</h2>
                <p className="text-sm text-gray-500 mt-0.5">
                  {filteredInvestimentos.length} investimento{filteredInvestimentos.length !== 1 ? 's' : ''} em{' '}
                  {selectedMonth.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {filteredInvestimentos.map((inv, index) => (
                <InvestmentCard
                  key={inv.balance_id ?? `inv-${inv.id}-${index}`}
                  investment={inv}
                  onClick={() => router.push(`/mobile/investimentos/${inv.id}?anomes=${anomes}`)}
                  onEditValor={() => setEditValorInvestment(inv)}
                />
              ))}
            </div>
          </>
        )}
      </div>

      <CreateInvestmentSheet
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onSuccess={loadInvestimentos}
        ano={ano}
        anomes={anomes}
      />

      <EditValorMesSheet
        open={!!editValorInvestment}
        onClose={() => setEditValorInvestment(null)}
        onSuccess={loadInvestimentos}
        investment={editValorInvestment}
        anomes={anomes}
        mesLabel={selectedMonth.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}
      />
    </div>
  )
}

export default function InvestimentosMobilePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
        </div>
      }
    >
      <InvestimentosMobileContent />
    </Suspense>
  )
}
