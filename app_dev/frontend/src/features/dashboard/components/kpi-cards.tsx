'use client'

/**
 * KpiCards - Grid estilo Atelie
 * Receitas | Despesas (top)
 * Patrimônio: Ativos, Passivos, PL + vs mês anterior (bottom, full width)
 */

import { DollarSign, TrendingDown, Wallet, TrendingUp, ArrowDownRight } from 'lucide-react'
import type { DashboardMetrics } from '../types'

interface KpiCardsProps {
  metrics: DashboardMetrics | null
}

function formatCurrency(v: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(v)
}

/** Formato compacto: 1,2M, 600 mil */
function formatCompactCurrency(v: number) {
  const abs = Math.abs(v)
  const sign = v < 0 ? '-' : ''
  if (abs >= 1_000_000) {
    const val = abs / 1_000_000
    return `${sign}R$ ${val.toFixed(1).replace('.', ',')}M`
  }
  if (abs >= 1_000) {
    const val = Math.round(abs / 1_000)
    return `${sign}R$ ${val} mil`
  }
  return formatCurrency(v)
}

function formatPct(v: number) {
  const sign = v >= 0 ? '+' : ''
  return `${sign}${v.toFixed(1)}%`
}

export function KpiCards({ metrics }: KpiCardsProps) {
  if (!metrics) return null

  return (
    <div className="grid grid-cols-2 gap-3 mb-6">
      {/* Receitas */}
      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
          <DollarSign className="w-4 h-4" />
          Receitas
        </div>
        <p className="text-lg font-semibold text-gray-900">
          {formatCurrency(metrics.total_receitas)}
        </p>
        <p className="text-xs mt-1 font-medium text-gray-500">
          {metrics.receitas_change_percentage != null ? (
            <span className={metrics.receitas_change_percentage >= 0 ? 'text-green-600' : 'text-red-600'}>
              {formatPct(metrics.receitas_change_percentage)} vs mês anterior
            </span>
          ) : (
            <span className="text-gray-400">— vs mês anterior</span>
          )}
        </p>
      </div>

      {/* Despesas */}
      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
          <TrendingDown className="w-4 h-4" />
          Despesas
        </div>
        <p className="text-lg font-semibold text-gray-900">
          {formatCurrency(metrics.total_despesas)}
        </p>
        <p className="text-xs mt-1 font-medium text-gray-500">
          {metrics.change_percentage != null ? (
            <span className={metrics.change_percentage >= 0 ? 'text-red-600' : 'text-green-600'}>
              {formatPct(metrics.change_percentage)} vs mês anterior
            </span>
          ) : (
            <span className="text-gray-400">— vs mês anterior</span>
          )}
        </p>
        <p className="text-xs mt-0.5 text-gray-500">
          {metrics.despesas_vs_plano_percent != null ? (
            <>{metrics.despesas_vs_plano_percent}% vs plano</>
          ) : (
            <span className="text-gray-400">— vs plano</span>
          )}
        </p>
      </div>

      {/* Patrimônio: Ativos, Passivos, PL - vs LM / vs Plan */}
      <div className="col-span-2 rounded-xl border border-gray-200 bg-white p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-gray-500 text-sm">
            <Wallet className="w-4 h-4" />
            Patrimônio
          </div>
          <span className="text-[10px] text-gray-400 font-medium">vs LM / vs Plan</span>
        </div>
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="min-w-0">
            <p className="text-xs text-gray-500 mb-1 flex items-center justify-center gap-1">
              <TrendingUp className="w-3 h-3 shrink-0" />
              Ativos
            </p>
            <p className={`text-sm font-semibold truncate ${(metrics.ativos_mes ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCompactCurrency(metrics.ativos_mes ?? 0)}
            </p>
            <p className="text-[10px] mt-0.5">
              {metrics.ativos_change_percentage != null ? (
                <span className={metrics.ativos_change_percentage >= 0 ? 'text-green-600' : 'text-red-600'}>
                  {formatPct(metrics.ativos_change_percentage)}
                </span>
              ) : (
                <span className="text-gray-400">—</span>
              )}
            </p>
          </div>
          <div className="min-w-0 border-x border-gray-100">
            <p className="text-xs text-gray-500 mb-1 flex items-center justify-center gap-1">
              <ArrowDownRight className="w-3 h-3 shrink-0" />
              Passivos
            </p>
            <p className={`text-sm font-semibold truncate ${(metrics.passivos_mes ?? 0) <= 0 ? 'text-red-600' : 'text-gray-900'}`}>
              {formatCompactCurrency(metrics.passivos_mes ?? 0)}
            </p>
            <p className="text-[10px] mt-0.5">
              {metrics.passivos_change_percentage != null ? (
                <span className={metrics.passivos_change_percentage >= 0 ? 'text-green-600' : 'text-red-600'}>
                  {formatPct(metrics.passivos_change_percentage)}
                </span>
              ) : (
                <span className="text-gray-400">—</span>
              )}
            </p>
          </div>
          <div className="min-w-0">
            <p className="text-xs text-gray-500 mb-1 flex items-center justify-center gap-1">
              <Wallet className="w-3 h-3 shrink-0" />
              PL
            </p>
            <p className={`text-sm font-bold truncate ${(metrics.patrimonio_liquido_mes ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCompactCurrency(metrics.patrimonio_liquido_mes ?? 0)}
            </p>
            <p className="text-[10px] mt-0.5">
              {metrics.patrimonio_change_percentage != null || metrics.patrimonio_vs_plano_percent != null ? (
                <>
                  {metrics.patrimonio_change_percentage != null && (
                    <span className={metrics.patrimonio_change_percentage >= 0 ? 'text-green-600' : 'text-red-600'}>
                      {formatPct(metrics.patrimonio_change_percentage)}
                    </span>
                  )}
                  {metrics.patrimonio_change_percentage != null && metrics.patrimonio_vs_plano_percent != null && (
                    <span className="text-gray-400 mx-0.5">/</span>
                  )}
                  {metrics.patrimonio_vs_plano_percent != null && (
                    <span className="text-gray-600">{metrics.patrimonio_vs_plano_percent}% plan</span>
                  )}
                </>
              ) : (
                <span className="text-gray-400">—</span>
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
