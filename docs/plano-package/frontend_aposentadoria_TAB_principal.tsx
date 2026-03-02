'use client'

/**
 * Tab Plano Aposentadoria - Sprint H
 * Se existem cenários: mostra Central de Cenários (lista + criar/editar)
 * Se não: mostra card "Construa Seu Plano"
 */

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { getCenarios } from '@/features/investimentos/services/investimentos-api'
import type { InvestimentoCenario } from '@/features/investimentos/types'
import { CentralCenarios } from './central-cenarios'
import { PlanoChart } from './plano-chart'

function formatCurrency(value: number) {
  if (value >= 1_000_000) return `R$ ${(value / 1_000_000).toFixed(1)} mi`
  if (value >= 1_000) return `R$ ${Math.round(value / 1_000)} mil`
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

interface PlanoAposentadoriaTabProps {
  patrimonioLiquido?: number | null
  idadeAtual?: number | null
  onCreatePlan?: () => void
}

export function PlanoAposentadoriaTab({
  patrimonioLiquido,
  idadeAtual,
  onCreatePlan,
}: PlanoAposentadoriaTabProps) {
  const router = useRouter()
  const valor = patrimonioLiquido ?? 0
  const idade = idadeAtual ?? 35

  const [cenarios, setCenarios] = useState<InvestimentoCenario[]>([])
  const [loading, setLoading] = useState(true)

  const fetchCenarios = useCallback(async () => {
    try {
      const list = await getCenarios(true)
      setCenarios(list || [])
    } catch {
      setCenarios([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchCenarios()
  }, [fetchCenarios])

  const handleCreate = () => {
    if (onCreatePlan) onCreatePlan()
    else router.push('/mobile/personalizar-plano')
  }

  // Sprint H: Se existem cenários, mostrar Central
  if (loading) {
    return (
      <div className="rounded-2xl border border-gray-200 bg-white p-8 flex items-center justify-center min-h-[200px]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
      </div>
    )
  }

  if (cenarios.length > 0) {
    const cenarioPrincipal = cenarios.find((c) => c.principal) ?? cenarios[0]
    return (
      <div className="space-y-4">
        <PlanoChart cenarioId={cenarioPrincipal.id} />
        <div className="rounded-2xl border border-gray-200 bg-white p-6">
          <CentralCenarios cenarios={cenarios} onRefresh={fetchCenarios} />
        </div>
      </div>
    )
  }

  const steps = [
    { n: 1, label: 'Idade atual' },
    { n: 2, label: 'Meta' },
    { n: 3, label: 'Aportes' },
    { n: 4, label: 'Retorno' },
  ]

  return (
    <div className="space-y-4">
      {/* Gráfico PL Realizado vs Plano (só realizado quando não há cenário) */}
      <PlanoChart cenarioId={null} />
      {/* Card principal */}
      <div className="rounded-2xl border border-gray-200 bg-white px-6 pt-6 pb-5">
        {/* Header */}
        <div className="flex items-center justify-between gap-2 mb-7">
          <h3 className="text-lg font-bold text-gray-900">Construa Seu Plano</h3>
          <span className="shrink-0 px-3 py-1 rounded-full bg-emerald-50 text-emerald-600 text-xs font-semibold">
            em 5 minutos
          </span>
        </div>

        {/* Timeline horizontal (reta) */}
        <div className="flex items-start justify-between mb-0">
          <div className="flex flex-col items-center shrink-0">
            <div className="w-3 h-3 rounded-full bg-gray-900" />
            <p className="text-xs font-semibold text-gray-900 mt-1.5">Hoje</p>
            <p className="text-xs text-gray-500 font-medium">{idade} anos</p>
          </div>

          <div className="flex-1 flex items-center pt-[5px] px-2">
            <svg viewBox="0 0 200 6" className="w-full h-[6px]" preserveAspectRatio="none">
              <line x1="0" y1="3" x2="200" y2="3" stroke="#d1d5db" strokeWidth="1.2" strokeDasharray="5 4" />
              <circle cx="50" cy="3" r="2.5" fill="#e5e7eb" />
              <circle cx="100" cy="3" r="2.5" fill="#e5e7eb" />
              <circle cx="150" cy="3" r="2.5" fill="#e5e7eb" />
            </svg>
          </div>

          <div className="flex flex-col items-center shrink-0">
            <div className="w-3.5 h-3.5 rounded-full border-[1.5px] border-gray-300 bg-gray-100 flex items-center justify-center">
              <div className="w-1.5 h-1.5 rounded-full bg-gray-300" />
            </div>
            <p className="text-xs font-semibold text-gray-900 mt-1.5">Aposentadoria</p>
            <p className="text-xs text-gray-500 italic">definir idade</p>
          </div>
        </div>

        {/* Curva ascendente + pills */}
        <div className="relative w-full mb-5" style={{ height: 200 }}>
          <svg
            viewBox="0 0 380 200"
            fill="none"
            className="absolute inset-0 w-full h-full pointer-events-none"
            preserveAspectRatio="xMidYMid meet"
          >
            <path
              d="M -20 190 C 30 188, 80 180, 130 155 C 190 120, 250 60, 310 30 C 340 18, 360 12, 395 8"
              stroke="#d1d5db"
              strokeWidth="2"
              strokeDasharray="8 5"
              strokeLinecap="round"
            />
          </svg>

          {/* Pill R$ ??? — topo direito */}
          <div className="absolute top-0 right-0 flex flex-col items-end">
            <div className="px-2.5 py-1 rounded-lg border-[1.5px] border-dashed border-gray-300 bg-white">
              <span className="text-gray-500 text-xs font-bold">R$ ???</span>
            </div>
            <p className="text-[10px] text-gray-400 mt-0.5 italic">Sua meta</p>
          </div>

          {/* Pill patrimônio — base esquerdo */}
          <div className="absolute bottom-[18px] left-0 flex flex-col items-start">
            <div className="px-2.5 py-1 rounded-lg bg-gray-900">
              <span className="text-white text-xs font-bold">
                {valor > 0 ? formatCurrency(valor) : 'R$ 0'}
              </span>
            </div>
            <p className="text-[10px] text-gray-500 mt-0.5 ml-0.5">Patrimônio Atual</p>
          </div>
        </div>

        {/* Seção Descubra */}
        <div className="rounded-xl bg-gray-50 p-4 mb-5">
          <div className="flex gap-3">
            <div className="shrink-0 w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center mt-0.5">
              <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <div className="min-w-0 flex-1">
              <h4 className="text-sm font-bold text-gray-900">Descubra seu futuro financeiro</h4>
              <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">
                Responda 4 perguntas e veja quanto terá ao se aposentar
              </p>

              <div className="flex flex-wrap gap-2 mt-3">
                {steps.map((s) => (
                  <span
                    key={s.n}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-200 bg-white text-xs font-medium text-gray-700"
                  >
                    <span className="text-gray-400">{s.n}</span>
                    {s.label}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* CTA */}
        <button
          onClick={handleCreate}
          className="w-full py-4 bg-gray-900 text-white rounded-2xl text-sm font-semibold
                     hover:bg-gray-800 active:scale-[0.98] transition-all
                     flex items-center justify-center gap-2"
        >
          <span className="text-lg leading-none">+</span>
          Criar Meu Plano
        </button>
      </div>

      {/* Rodapé informativo */}
      <div className="rounded-2xl border border-gray-200 bg-white p-5">
        <p className="text-sm text-gray-500 leading-relaxed">
          O simulador usa a regra dos 4% para estimar o patrimônio necessário para sua
          renda passiva na aposentadoria. Ajuste idade, aportes, retorno e inflação para
          ver a projeção em valores nominais e reais.
        </p>
      </div>
    </div>
  )
}
