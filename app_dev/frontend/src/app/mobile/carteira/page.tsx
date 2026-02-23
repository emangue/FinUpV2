'use client'

/**
 * Carteira / Portfolio - Visão consolidada dos investimentos
 *
 * Design: fundo branco, donut fino (stroke 10), scroll livre (sem sticky).
 * Dados: PatrimonioMensal para PL correto do mês selecionado.
 *
 * Botões:
 *   - Aportar → /mobile/investimentos  (lista de investimentos, pode adicionar aporte)
 *   - Simular → /mobile/dashboard?tab=patrimonio  (plano de aposentadoria)
 *   - Novo    → /mobile/investimentos?action=new  (abre sheet de criar investimento)
 */

import * as React from 'react'
import { Suspense } from 'react'
import { useRouter } from 'next/navigation'
import { useRequireAuth } from '@/core/hooks/use-require-auth'
import {
  getInvestimentos,
  getDistribuicaoPorTipo,
  getPatrimonioTimeline,
} from '@/features/investimentos/services/investimentos-api'
import { fetchLastMonthWithData } from '@/features/dashboard/services/dashboard-api'
import type {
  InvestimentoPortfolio,
  DistribuicaoTipo,
  PatrimonioMensal,
} from '@/features/investimentos/types'
import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker'
import {
  TrendingUp,
  TrendingDown,
  Plus,
  BarChart3,
  ArrowDownToLine,
  Wallet,
  ChevronRight,
  Search,
  PiggyBank,
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

/* ───────────────── helpers ───────────────── */

function fmt(value: number | string | undefined | null): string {
  const n = typeof value === 'string' ? parseFloat(value) : (value ?? 0)
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function fmtCompact(value: number): string {
  if (Math.abs(value) >= 1_000_000) return `R$ ${(value / 1_000_000).toFixed(1)}M`
  if (Math.abs(value) >= 1_000) return `R$ ${(value / 1_000).toFixed(1)}K`
  return fmt(value)
}

function pct(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

function getValor(inv: InvestimentoPortfolio): number {
  const v = inv.valor_total_mes
  if (v != null) return typeof v === 'number' ? v : parseFloat(String(v)) || 0
  return parseFloat(inv.valor_total_inicial || '0') || 0
}

/* ──────────────── Donut Chart (SVG fino) ──────────────── */

interface DonutSlice { label: string; value: number; color: string }

const COLORS = [
  '#6366f1', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16',
]

function DonutChart({
  slices,
  total,
  centerLabel,
  centerValue,
  centerSub,
}: {
  slices: DonutSlice[]
  total: number
  centerLabel: string
  centerValue: string
  centerSub: string
}) {
  const size = 200
  const stroke = 10
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  let offset = 0

  return (
    <div className="relative flex items-center justify-center">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* bg ring */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="#f3f4f6" strokeWidth={stroke}
        />
        {slices.map((s, i) => {
          const pctValue = total > 0 ? s.value / total : 0
          const dash = circumference * pctValue
          const gap = circumference - dash
          const currentOffset = offset
          offset += dash
          return (
            <circle
              key={i}
              cx={size / 2} cy={size / 2} r={radius}
              fill="none"
              stroke={s.color}
              strokeWidth={stroke}
              strokeDasharray={`${dash} ${gap}`}
              strokeDashoffset={-currentOffset}
              strokeLinecap="round"
              className="transition-all duration-700"
              style={{ transform: 'rotate(-90deg)', transformOrigin: 'center' }}
            />
          )
        })}
      </svg>
      {/* center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center px-4">
        <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">
          {centerLabel}
        </span>
        <span className="text-lg font-bold text-gray-900 mt-0.5">{centerValue}</span>
        <span className="text-[10px] text-gray-400">{centerSub}</span>
      </div>
    </div>
  )
}

/* ──────────────── Asset Card ──────────────── */

function AssetCard({
  investment,
  onClick,
}: {
  investment: InvestimentoPortfolio
  onClick: () => void
}) {
  const valor = getValor(investment)
  const valorInicial = parseFloat(investment.valor_total_inicial || '0') || 0
  const variacao = valorInicial > 0 ? ((valor - valorInicial) / valorInicial) * 100 : 0
  const isPositive = variacao >= 0
  const classeAtivo = investment.classe_ativo || 'Ativo'

  const iconColors: Record<string, string> = {
    'CDB': 'bg-blue-500',
    'LCI': 'bg-emerald-500',
    'LCA': 'bg-green-500',
    'Ação': 'bg-purple-500',
    'FII': 'bg-orange-500',
    'Tesouro': 'bg-yellow-500',
    'Fundo': 'bg-indigo-500',
    'ETF': 'bg-cyan-500',
    'Crypto': 'bg-amber-500',
    'Previdência': 'bg-pink-500',
    'Previdência Privada': 'bg-pink-500',
    'Renda Fixa': 'bg-red-400',
    'Fundo Imobiliário': 'bg-orange-400',
    'Fundo de Investimento': 'bg-indigo-400',
    'Conta Corrente': 'bg-gray-400',
    'FGTS': 'bg-teal-500',
    'Apartamento': 'bg-indigo-600',
    'Casa': 'bg-amber-500',
    'Automóvel': 'bg-violet-500',
  }
  const iconBg = iconColors[investment.tipo_investimento] || 'bg-gray-500'
  const initials = investment.tipo_investimento.slice(0, 2).toUpperCase()

  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 py-3.5 px-1 border-b border-gray-100 last:border-0 active:bg-gray-50 transition-colors text-left"
    >
      {/* Icon */}
      <div className={cn('w-10 h-10 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0', iconBg)}>
        {initials}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <span className="text-sm font-semibold text-gray-900 truncate">
            {investment.nome_produto}
          </span>
          {investment.percentual_cdi != null && investment.percentual_cdi > 0 && (
            <Badge variant="secondary" className="text-[9px] px-1 py-0 h-4 shrink-0">
              {investment.percentual_cdi}% CDI
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className="text-xs text-gray-400">{investment.corretora}</span>
          <span className="text-gray-300">·</span>
          <Badge
            variant="outline"
            className={cn(
              'text-[9px] px-1 py-0 h-3.5',
              classeAtivo === 'Passivo' ? 'border-red-200 text-red-500' : 'border-emerald-200 text-emerald-600'
            )}
          >
            {classeAtivo}
          </Badge>
        </div>
      </div>

      {/* Valor + Variação */}
      <div className="text-right shrink-0">
        <div className="text-sm font-semibold text-gray-900">{fmt(valor)}</div>
        {variacao !== 0 && (
          <div className={cn(
            'text-xs font-medium flex items-center justify-end gap-0.5',
            isPositive ? 'text-emerald-600' : 'text-red-500'
          )}>
            {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {pct(variacao)}
          </div>
        )}
      </div>
    </button>
  )
}

/* ──────────────────── Main Page ──────────────────── */

function CarteiraContent() {
  const router = useRouter()
  const isAuth = useRequireAuth()

  const [selectedMonth, setSelectedMonth] = React.useState<Date>(new Date())
  const [investimentos, setInvestimentos] = React.useState<InvestimentoPortfolio[]>([])
  const [distribuicao, setDistribuicao] = React.useState<DistribuicaoTipo[]>([])
  const [patrimonioData, setPatrimonioData] = React.useState<PatrimonioMensal | null>(null)
  const [patrimonioAnterior, setPatrimonioAnterior] = React.useState<PatrimonioMensal | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [searchOpen, setSearchOpen] = React.useState(false)
  const [searchTerm, setSearchTerm] = React.useState('')

  const anomes = selectedMonth.getFullYear() * 100 + (selectedMonth.getMonth() + 1)

  // Default para último mês com dados
  React.useEffect(() => {
    if (!isAuth) return
    fetchLastMonthWithData('patrimonio')
      .then(({ year, month }) => setSelectedMonth(new Date(year, month - 1, 1)))
      .catch(() => {})
  }, [isAuth])

  // Carregar dados
  React.useEffect(() => {
    if (!isAuth) return
    setLoading(true)

    const currentYear = selectedMonth.getFullYear()
    const currentMonth = selectedMonth.getMonth() + 1

    // Buscar timeline incluindo ano anterior (para variação Jan vs Dez anterior)
    const anoInicio = currentMonth === 1 ? currentYear - 1 : currentYear

    Promise.all([
      getInvestimentos({ ativo: true, anomes, limit: 200 }),
      getDistribuicaoPorTipo().catch(() => []),
      getPatrimonioTimeline({ ano_inicio: anoInicio, ano_fim: currentYear }).catch(() => []),
    ])
      .then(([inv, dist, pat]) => {
        setInvestimentos(inv)
        setDistribuicao(dist)

        // PL do mês selecionado (fonte de verdade)
        const mesAtual = pat.find(p => p.anomes === anomes) ?? null
        setPatrimonioData(mesAtual)

        // Mês anterior para cálculo de variação
        const anomesAnterior = currentMonth === 1
          ? (currentYear - 1) * 100 + 12
          : currentYear * 100 + (currentMonth - 1)
        const mesAnterior = pat.find(p => p.anomes === anomesAnterior) ?? null
        setPatrimonioAnterior(mesAnterior)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [isAuth, anomes, selectedMonth])

  // PL do mês selecionado (fonte de verdade: timeline do backend)
  const patrimonioLiquido = patrimonioData?.patrimonio_liquido ?? 0
  const totalAtivos = patrimonioData?.ativos ?? 0
  const totalPassivos = patrimonioData?.passivos ?? 0

  // Variação vs mês anterior
  const variacaoMes = React.useMemo(() => {
    if (!patrimonioAnterior || patrimonioAnterior.patrimonio_liquido === 0) return null
    return ((patrimonioLiquido - patrimonioAnterior.patrimonio_liquido) / Math.abs(patrimonioAnterior.patrimonio_liquido)) * 100
  }, [patrimonioLiquido, patrimonioAnterior])

  // Donut slices por tipo de investimento
  const donutSlices = React.useMemo<DonutSlice[]>(() => {
    const byType = new Map<string, number>()
    investimentos.forEach(inv => {
      const tipo = inv.tipo_investimento || 'Outros'
      const valor = Math.abs(getValor(inv))
      byType.set(tipo, (byType.get(tipo) || 0) + valor)
    })
    return Array.from(byType.entries())
      .sort((a, b) => b[1] - a[1])
      .map(([label, value], i) => ({
        label,
        value,
        color: COLORS[i % COLORS.length],
      }))
  }, [investimentos])

  const donutTotal = donutSlices.reduce((s, d) => s + d.value, 0)

  // Filtro de busca
  const filtered = React.useMemo(() => {
    if (!searchTerm.trim()) return investimentos
    const term = searchTerm.toLowerCase()
    return investimentos.filter(i =>
      i.nome_produto.toLowerCase().includes(term) ||
      i.corretora.toLowerCase().includes(term) ||
      i.tipo_investimento.toLowerCase().includes(term)
    )
  }, [investimentos, searchTerm])

  // Deduplica por balance_id
  const deduped = React.useMemo(() => {
    const seen = new Set<string>()
    return filtered.filter(inv => {
      const key = inv.balance_id ?? String(inv.id)
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  }, [filtered])

  if (!isAuth) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-white overflow-hidden">
      <div className="flex-1 overflow-y-auto pb-24">

        {/* ───── Header ───── */}
        <div className="flex items-center justify-between px-5 pt-3 pb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center">
              <Wallet className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-sm text-gray-900">Minha Carteira</span>
          </div>
          <button
            onClick={() => setSearchOpen(!searchOpen)}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
            aria-label="Buscar"
          >
            <Search className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Search bar */}
        {searchOpen && (
          <div className="px-5 pb-3 animate-in slide-in-from-top-2 duration-200">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar investimento..."
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              autoFocus
            />
          </div>
        )}

        {/* Month picker */}
        <div className="pb-4">
          <MonthScrollPicker
            selectedMonth={selectedMonth}
            onMonthChange={setSelectedMonth}
          />
        </div>

        {/* Donut + PL */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
          </div>
        ) : (
          <div className="flex flex-col items-center px-5">
            <DonutChart
              slices={donutSlices}
              total={donutTotal}
              centerLabel="MEU PORTFÓLIO"
              centerValue={fmtCompact(donutTotal)}
              centerSub={`${donutSlices.length} tipos`}
            />

            {/* Patrimônio Líquido */}
            <div className="mt-4 text-center">
              <div className="text-2xl font-bold text-gray-900">{fmt(patrimonioLiquido)}</div>
              <div className="text-[11px] text-gray-400 mt-0.5">Patrimônio Líquido</div>
              {variacaoMes !== null && (
                <div className={cn(
                  'inline-flex items-center gap-1 text-xs font-medium mt-1.5 px-2.5 py-0.5 rounded-full',
                  variacaoMes >= 0 ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-500'
                )}>
                  {variacaoMes >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  {pct(variacaoMes)} vs mês anterior
                </div>
              )}
            </div>
          </div>
        )}

        {/* ───── Action buttons ───── */}
        <div className="flex items-center justify-center gap-3 py-5 px-5">
          <button
            onClick={() => router.push('/mobile/investimentos')}
            className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-full text-sm font-semibold shadow-sm active:scale-95 transition-transform"
          >
            <ArrowDownToLine className="w-4 h-4" />
            APORTAR
          </button>
          <button
            onClick={() => router.push('/mobile/dashboard?tab=patrimonio')}
            className="flex items-center gap-2 px-5 py-2.5 bg-white text-gray-700 rounded-full text-sm font-semibold border border-gray-200 active:scale-95 transition-transform"
          >
            <BarChart3 className="w-4 h-4" />
            SIMULAR
          </button>
          <button
            onClick={() => router.push('/mobile/investimentos?action=new')}
            className="flex items-center gap-2 px-5 py-2.5 bg-white text-gray-700 rounded-full text-sm font-semibold border border-gray-200 active:scale-95 transition-transform"
          >
            <Plus className="w-4 h-4" />
            NOVO
          </button>
        </div>

        {/* ───── KPI strip ───── */}
        {!loading && (
          <div className="grid grid-cols-3 divide-x divide-gray-100 border-y border-gray-100 mx-5">
            <div className="py-3 text-center">
              <div className="text-[10px] text-gray-400 uppercase tracking-wider">Ativos</div>
              <div className="text-sm font-bold text-emerald-600 mt-0.5">{fmtCompact(totalAtivos)}</div>
            </div>
            <div className="py-3 text-center">
              <div className="text-[10px] text-gray-400 uppercase tracking-wider">Passivos</div>
              <div className="text-sm font-bold text-red-500 mt-0.5">{fmtCompact(totalPassivos)}</div>
            </div>
            <div className="py-3 text-center">
              <div className="text-[10px] text-gray-400 uppercase tracking-wider">Produtos</div>
              <div className="text-sm font-bold text-gray-900 mt-0.5">{deduped.length}</div>
            </div>
          </div>
        )}

        {/* ───── Legenda donut ───── */}
        {!loading && donutSlices.length > 0 && (
          <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 px-5 pt-4 pb-2 max-w-[320px] mx-auto">
            {donutSlices.map((s, i) => (
              <div key={i} className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: s.color }} />
                <span className="text-[10px] text-gray-500 truncate">
                  {s.label} ({((s.value / donutTotal) * 100).toFixed(0)}%)
                </span>
              </div>
            ))}
          </div>
        )}

        {/* ───── Portfolio list header ───── */}
        <div className="flex items-center justify-between px-5 pt-5 pb-2">
          <h2 className="text-sm font-bold text-gray-900">Meu Portfólio</h2>
          <button
            onClick={() => router.push('/mobile/investimentos')}
            className="text-xs text-indigo-600 font-medium flex items-center gap-0.5"
          >
            Ver tudo <ChevronRight className="w-3 h-3" />
          </button>
        </div>

        {/* ───── Asset list ───── */}
        <div className="px-4">
          {loading ? (
            <div className="space-y-4 py-4">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="flex items-center gap-3 animate-pulse">
                  <div className="w-10 h-10 rounded-full bg-gray-200" />
                  <div className="flex-1">
                    <div className="h-3.5 bg-gray-200 rounded w-32 mb-1.5" />
                    <div className="h-2.5 bg-gray-100 rounded w-20" />
                  </div>
                  <div className="text-right">
                    <div className="h-3.5 bg-gray-200 rounded w-20 mb-1.5" />
                    <div className="h-2.5 bg-gray-100 rounded w-12 ml-auto" />
                  </div>
                </div>
              ))}
            </div>
          ) : deduped.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16">
              <PiggyBank className="w-16 h-16 text-gray-200 mb-4" />
              <p className="text-gray-600 font-medium mb-1">
                {searchTerm ? 'Nenhum resultado' : 'Nenhum investimento'}
              </p>
              <p className="text-gray-400 text-sm text-center mb-6">
                {searchTerm
                  ? `Nenhum investimento encontrado para "${searchTerm}"`
                  : 'Adicione seu primeiro investimento para começar'}
              </p>
              {!searchTerm && (
                <button
                  onClick={() => router.push('/mobile/investimentos?action=new')}
                  className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold flex items-center gap-2"
                >
                  <Plus className="w-5 h-5" />
                  Novo investimento
                </button>
              )}
            </div>
          ) : (
            <div>
              {deduped.map((inv, index) => (
                <AssetCard
                  key={inv.balance_id ?? `inv-${inv.id}-${index}`}
                  investment={inv}
                  onClick={() => router.push(`/mobile/investimentos/${inv.id}?anomes=${anomes}`)}
                />
              ))}
              {/* Add assets button */}
              <button
                onClick={() => router.push('/mobile/investimentos?action=new')}
                className="w-full py-4 text-center text-sm text-gray-400 font-medium border-t border-gray-50 mt-2"
              >
                + Adicionar investimento
              </button>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}

export default function CarteiraMobilePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-white flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
        </div>
      }
    >
      <CarteiraContent />
    </Suspense>
  )
}
