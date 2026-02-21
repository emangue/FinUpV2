'use client'

import { useState, useCallback, useMemo } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import type { AporteExtraordinario, PlanoProfile } from '../types'
import { planProfiles } from '../lib/plan-profiles'

const MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

function fC(v: number): string {
  if (v >= 1e6) return 'R$ ' + (v / 1e6).toFixed(1).replace('.', ',') + 'M'
  if (v >= 1e3) return 'R$ ' + Math.round(v / 1e3).toLocaleString('pt-BR') + ' mil'
  return 'R$ ' + Math.round(v).toLocaleString('pt-BR')
}
function fF(v: number): string {
  return 'R$ ' + Math.round(v).toLocaleString('pt-BR')
}

export function PersonalizarPlanoLayout() {
  const router = useRouter()
  const [age, setAge] = useState(35)
  const [retire, setRetire] = useState(65)
  const [aporte, setAporte] = useState(5000)
  const [retorno, setRetorno] = useState(10)
  const [inflacao, setInflacao] = useState(4.5)
  const [patrimonio, setPatrimonio] = useState(760000)
  const [rendaMensal, setRendaMensal] = useState(25000)
  const [extras, setExtras] = useState<AporteExtraordinario[]>([])
  const [activeProfile, setActiveProfile] = useState<PlanoProfile>('moderado')
  const [showSuccess, setShowSuccess] = useState(false)

  const years = Math.max(1, retire - age)
  const months = years * 12
  const retornoReal = ((1 + retorno / 100) / (1 + inflacao / 100) - 1) * 100
  const patrimonioNecessario = (rendaMensal * 12) / 0.04

  const expandExtras = useCallback((totalMonths: number) => {
    const monthlyMap = new Map<number, number>()
    extras.forEach((e) => {
      const intervalMap: Record<string, number> = {
        unico: 0,
        trimestral: 3,
        semestral: 6,
        anual: 12,
      }
      const interval = intervalMap[e.recorrencia]
      if (interval === 0) {
        const m = e.mesAno - 1
        if (m < totalMonths) monthlyMap.set(m, (monthlyMap.get(m) || 0) + e.valor)
      } else {
        let ocorrencia = 0
        for (let m = e.mesAno - 1; m < totalMonths; m += interval) {
          let val = e.valor
          if (e.evoluir && e.evolucaoValor && ocorrencia > 0) {
            if (e.evolucaoTipo === 'percentual') {
              val = e.valor * Math.pow(1 + e.evolucaoValor / 100, ocorrencia)
            } else {
              val = e.valor + e.evolucaoValor * ocorrencia
            }
          }
          monthlyMap.set(m, (monthlyMap.get(m) || 0) + val)
          ocorrencia++
        }
      }
    })
    return monthlyMap
  }, [extras])

  const projection = useMemo(() => {
    const extraMap = expandExtras(months)
    const monthlyRateNom = Math.pow(1 + retorno / 100, 1 / 12) - 1
    let pNom = patrimonio
    let totalExtras = 0
    for (let m = 0; m < months; m++) {
      const extra = extraMap.get(m) || 0
      totalExtras += extra
      pNom = (pNom + aporte + extra) * (1 + monthlyRateNom)
    }
    const totalAportes = patrimonio + aporte * months + totalExtras
    const rendimentosNom = pNom - totalAportes

    const monthlyRateReal = Math.pow(1 + retornoReal / 100, 1 / 12) - 1
    let pReal = patrimonio
    for (let m = 0; m < months; m++) {
      const extra = extraMap.get(m) || 0
      pReal = (pReal + aporte + extra) * (1 + monthlyRateReal)
    }

    const rendaPassivaNom = (pNom * 0.04) / 12
    const rendaPassivaReal = (pReal * 0.04) / 12
    const perdaInflacao = pNom - pReal
    const multiplier = pReal / Math.max(totalAportes, 1)

    return {
      pNom,
      pReal,
      totalAportes,
      rendimentosNom,
      rendaPassivaNom,
      rendaPassivaReal,
      perdaInflacao,
      multiplier,
    }
  }, [age, retire, aporte, retorno, inflacao, patrimonio, rendaMensal, months, retornoReal, expandExtras])

  const curvePaths = useMemo(() => {
    const maxVal = projection.pNom * 1.05
    const startY = 115
    const endY = 8
    const startX = 10
    const endX = 310

    const y1 = startY - (projection.pNom / maxVal) * (startY - endY)
    const cp1x = startX + (endX - startX) * 0.35
    const cp1y = startY - ((projection.pNom * 0.15) / maxVal) * (startY - endY)
    const cp2x = startX + (endX - startX) * 0.7
    const cp2y = startY - ((projection.pNom * 0.55) / maxVal) * (startY - endY)
    const nomPath = `M ${startX} ${startY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${endX} ${y1}`
    const nomArea = `${nomPath} L ${endX} 125 L ${startX} 125 Z`

    const yReal = startY - (projection.pReal / maxVal) * (startY - endY)
    const cpR1y = startY - ((projection.pReal * 0.15) / maxVal) * (startY - endY)
    const cpR2y = startY - ((projection.pReal * 0.55) / maxVal) * (startY - endY)
    const realPath = `M ${startX} ${startY} C ${cp1x} ${cpR1y}, ${cp2x} ${cpR2y}, ${endX} ${yReal}`
    const realArea = `${realPath} L ${endX} 125 L ${startX} 125 Z`

    return { nomPath, nomArea, realPath, realArea }
  }, [projection])

  const sentiment = useMemo(() => {
    if (projection.rendaPassivaReal >= rendaMensal) {
      return {
        emoji: '😊',
        text: 'Seu plano está excelente! Meta batida em valores reais.',
        bg: 'bg-emerald-50',
        textColor: 'text-emerald-700',
      }
    }
    if (projection.rendaPassivaReal >= rendaMensal * 0.7) {
      return {
        emoji: '😐',
        text: 'Quase lá! Considere aumentar aportes ou prazo.',
        bg: 'bg-amber-50',
        textColor: 'text-amber-700',
      }
    }
    return {
      emoji: '😟',
      text: 'Aportes insuficientes considerando a inflação.',
      bg: 'bg-red-50',
      textColor: 'text-red-700',
    }
  }, [projection.rendaPassivaReal, rendaMensal])

  const addExtra = () => {
    setExtras((prev) => [
      ...prev,
      {
        id: 'e' + Date.now(),
        mesAno: 12,
        valor: 30000,
        descricao: '13º Salário',
        recorrencia: 'anual',
        evoluir: false,
        evolucaoValor: 5,
        evolucaoTipo: 'percentual',
      },
    ])
  }

  const removeExtra = (id: string) => {
    setExtras((prev) => prev.filter((e) => e.id !== id))
  }

  const updateExtra = (
    id: string,
    field: keyof AporteExtraordinario,
    val: string | number | boolean
  ) => {
    setExtras((prev) =>
      prev.map((e) => (e.id === id ? { ...e, [field]: val } : e))
    )
  }

  const setProfile = (profile: PlanoProfile) => {
    const data = planProfiles[profile]
    setRetorno(data.retorno)
    setInflacao(data.inflacao)
    setActiveProfile(profile)
  }

  const quickPicks = [1000, 2000, 3000, 5000, 7000, 10000]

  const formatPatrimonioInput = (v: string) => {
    const raw = v.replace(/\D/g, '')
    if (raw) setPatrimonio(parseInt(raw))
  }

  const formatRendaInput = (v: string) => {
    const raw = v.replace(/\D/g, '')
    if (raw) setRendaMensal(parseInt(raw))
  }

  if (showSuccess) {
    return (
      <div className="fixed inset-0 z-50 bg-white flex items-center justify-center max-w-[430px] mx-auto">
        <div className="text-center px-8 animate-fade-in">
          <div className="w-20 h-20 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-6">
            <svg
              className="w-10 h-10 text-emerald-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Plano Salvo! 🎉</h2>
          <p className="text-sm text-gray-500 mb-8">
            Seu plano de aposentadoria está configurado.
          </p>
          <Link
            href="/mobile/dashboard"
            className="inline-flex items-center gap-2 px-8 py-3.5 bg-gray-900 text-white rounded-xl text-sm font-semibold hover:bg-gray-800 transition-colors no-underline"
          >
            Voltar ao Dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-50 min-h-screen max-w-[430px] mx-auto relative">
      <div className="sticky top-0 z-20 bg-white border-b border-gray-200">
        <div className="flex items-center gap-3 px-4 py-3">
          <button
            onClick={() => router.push('/mobile/dashboard')}
            className="p-2 rounded-full text-gray-600 hover:bg-gray-100 -ml-2"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>
          <h1 className="text-base font-semibold text-gray-900 flex-1">
            Personalizar Meu Plano
          </h1>
          <span className="text-xs text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full font-medium">
            Simulador
          </span>
        </div>
      </div>

      <div className="px-5 pb-6 scrollbar-hide overflow-y-auto">
        {/* Idade */}
        <div className="mt-5">
          <div className="section-label text-[11px] font-bold uppercase tracking-[0.08em] text-gray-400 mb-3 flex items-center gap-2">
            <svg
              className="w-3.5 h-3.5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            Idade
            <span className="flex-1 h-px bg-gray-200" />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-3">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-xs text-gray-500">Sua idade atual</p>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-3xl font-bold text-gray-900">{age}</span>
                <span className="text-sm text-gray-400">anos</span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">Aposentadoria</p>
              <div className="flex items-baseline gap-1 mt-1 justify-end">
                <span className="text-3xl font-bold text-emerald-600">{retire}</span>
                <span className="text-sm text-gray-400">anos</span>
              </div>
            </div>
          </div>

          {/* Sprint A: Idade atual editável via slider */}
          <div className="mb-4">
            <label className="text-[10px] text-gray-400 uppercase tracking-wide mb-1.5 block">
              Idade atual
            </label>
            <input
              type="range"
              min={18}
              max={70}
              value={age}
              className="w-full"
              onChange={(e) => setAge(parseInt(e.target.value))}
            />
            <div className="flex justify-between text-[10px] text-gray-300 mt-0.5">
              <span>18</span>
              <span>30</span>
              <span>40</span>
              <span>50</span>
              <span>60</span>
              <span>70</span>
            </div>
          </div>

          <div className="mb-2">
            <label className="text-[10px] text-gray-400 uppercase tracking-wide mb-1.5 block">
              Idade de aposentadoria
            </label>
            <input
              type="range"
              min={40}
              max={80}
              value={retire}
              className="w-full"
              onChange={(e) => setRetire(parseInt(e.target.value))}
            />
            <div className="flex justify-between text-[10px] text-gray-300 mt-0.5">
              <span>40</span>
              <span>50</span>
              <span>60</span>
              <span>70</span>
              <span>80</span>
            </div>
          </div>

          <div className="flex items-center justify-center gap-2 mt-3 py-2 bg-gray-50 rounded-lg">
            <svg
              className="w-3.5 h-3.5 text-amber-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="text-xs text-gray-600">
              Faltam <strong className="text-gray-900">{Math.max(0, retire - age)}</strong> anos
            </span>
          </div>
        </div>

        {/* Meta Financeira */}
        <div className="mt-5">
          <div className="section-label text-[11px] font-bold uppercase tracking-[0.08em] text-gray-400 mb-3 flex items-center gap-2">
            <svg
              className="w-3.5 h-3.5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Meta Financeira
            <span className="flex-1 h-px bg-gray-200" />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-[10px] text-gray-400 uppercase tracking-wide mb-1 block">
                Patrimônio atual
              </label>
              <div className="flex items-center gap-1 border-b-2 border-gray-200 pb-1 focus-within:border-gray-900 transition-colors">
                <span className="text-gray-400 text-sm">R$</span>
                <input
                  type="text"
                  value={patrimonio.toLocaleString('pt-BR')}
                  className="text-lg font-bold text-gray-900 w-full outline-none bg-transparent"
                  onChange={(e) => formatPatrimonioInput(e.target.value)}
                />
              </div>
              <p className="text-[9px] text-gray-300 mt-1">💡 Auto dos investimentos</p>
            </div>
            <div>
              <label className="text-[10px] text-gray-400 uppercase tracking-wide mb-1 block">
                Renda desejada/mês
              </label>
              <div className="flex items-center gap-1 border-b-2 border-emerald-200 pb-1 focus-within:border-emerald-500 transition-colors">
                <span className="text-gray-400 text-sm">R$</span>
                <input
                  type="text"
                  value={rendaMensal.toLocaleString('pt-BR')}
                  className="text-lg font-bold text-emerald-600 w-full outline-none bg-transparent"
                  onChange={(e) => formatRendaInput(e.target.value)}
                />
              </div>
              <p className="text-[9px] text-gray-300 mt-1">Na aposentadoria</p>
            </div>
          </div>
          <div className="mt-3 py-2 px-3 bg-amber-50 rounded-lg border border-amber-100">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-amber-700">
                Patrimônio necessário (regra 4%)
              </span>
              <span className="text-xs font-bold text-amber-900">
                {fF(patrimonioNecessario)}
              </span>
            </div>
          </div>
        </div>

        {/* Aporte Mensal */}
        <div className="mt-5">
          <div className="section-label text-[11px] font-bold uppercase tracking-[0.08em] text-gray-400 mb-3 flex items-center gap-2">
            <svg
              className="w-3.5 h-3.5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
            Aporte Mensal
            <span className="flex-1 h-px bg-gray-200" />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-1">
          <div className="flex items-center justify-center gap-2 mb-4">
            <span className="text-gray-400 text-lg">R$</span>
            <span className="text-4xl font-bold text-gray-900">
              {aporte.toLocaleString('pt-BR')}
            </span>
            <span className="text-gray-400 text-sm">/mês</span>
          </div>
          <input
            type="range"
            min={500}
            max={50000}
            step={500}
            value={aporte}
            className="w-full"
            onChange={(e) => setAporte(parseInt(e.target.value))}
          />
          <div className="flex justify-between text-[10px] text-gray-300 mt-0.5">
            <span>R$ 500</span>
            <span>R$ 10k</span>
            <span>R$ 25k</span>
            <span>R$ 50k</span>
          </div>
        </div>
        <div className="flex gap-1.5 mb-3 px-1">
          {quickPicks.map((v) => (
            <button
              key={v}
              onClick={() => setAporte(v)}
              className={`flex-1 py-1.5 rounded-lg border text-[10px] font-semibold transition-all ${
                aporte === v
                  ? 'bg-gray-900 text-white border-gray-900'
                  : 'border-gray-200 bg-white text-gray-500 hover:bg-gray-50'
              }`}
            >
              {v >= 1000 ? `${v / 1000}k` : v}
            </button>
          ))}
        </div>

        {/* Retorno & Inflação */}
        <div className="mt-5">
          <div className="section-label text-[11px] font-bold uppercase tracking-[0.08em] text-gray-400 mb-3 flex items-center gap-2">
            <svg
              className="w-3.5 h-3.5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
              />
            </svg>
            Retorno & Inflação
            <span className="flex-1 h-px bg-gray-200" />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-3">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-xs text-gray-500">Retorno nominal (a.a.)</p>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-3xl font-bold text-gray-900">{retorno}</span>
                <span className="text-sm text-gray-400">%</span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">Inflação (IPCA)</p>
              <div className="flex items-baseline gap-1 mt-1 justify-end">
                <span className="text-3xl font-bold text-orange-500">
                  {inflacao.toFixed(1).replace('.', ',')}
                </span>
                <span className="text-sm text-gray-400">%</span>
              </div>
            </div>
          </div>

          <div className="mb-4">
            <label className="text-[10px] text-gray-400 uppercase tracking-wide mb-1.5 block">
              Retorno nominal anual
            </label>
            <input
              type="range"
              min={4}
              max={20}
              step={0.5}
              value={retorno}
              className="w-full"
              onChange={(e) => setRetorno(parseFloat(e.target.value))}
            />
            <div className="flex justify-between text-[10px] text-gray-300 mt-0.5">
              <span>4%</span>
              <span>8%</span>
              <span>12%</span>
              <span>16%</span>
              <span>20%</span>
            </div>
          </div>

          <div className="mb-2">
            <label className="text-[10px] text-gray-400 uppercase tracking-wide mb-1.5 block">
              Inflação anual esperada (IPCA)
            </label>
            <input
              type="range"
              min={2}
              max={10}
              step={0.5}
              value={inflacao}
              className="w-full"
              onChange={(e) => setInflacao(parseFloat(e.target.value))}
            />
            <div className="flex justify-between text-[10px] text-gray-300 mt-0.5">
              <span>2%</span>
              <span>4%</span>
              <span>6%</span>
              <span>8%</span>
              <span>10%</span>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 mt-3">
            {(['conservador', 'moderado', 'arrojado'] as PlanoProfile[]).map((p) => {
              const d = planProfiles[p]
              const realP =
                ((1 + d.retorno / 100) / (1 + d.inflacao / 100) - 1) * 100
              const isActive = activeProfile === p
              const colorMap: Record<PlanoProfile, string> = {
                conservador: 'text-blue-600',
                moderado: 'text-white',
                arrojado: 'text-orange-600',
              }
              return (
                <button
                  key={p}
                  onClick={() => setProfile(p)}
                  className={`py-2.5 px-2 rounded-xl border text-center transition-colors ${
                    isActive ? 'border-gray-900 bg-gray-900' : 'border-gray-200 bg-white hover:bg-gray-50'
                  }`}
                >
                  <span
                    className={`text-xs font-bold block ${
                      isActive ? 'text-white' : colorMap[p]
                    }`}
                  >
                    {d.retorno}%
                  </span>
                  <span
                    className={`text-[9px] block ${
                      isActive ? 'text-gray-300' : 'text-gray-400'
                    }`}
                  >
                    {p.charAt(0).toUpperCase() + p.slice(1)}
                  </span>
                  <span
                    className={`text-[8px] block ${
                      isActive ? 'text-gray-400' : 'text-gray-300'
                    }`}
                  >
                    Real: {realP.toFixed(0)}%
                  </span>
                </button>
              )
            })}
          </div>

          <div className="mt-3 py-2 px-3 bg-blue-50 rounded-lg border border-blue-100">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-blue-700">
                Retorno real (descontada inflação)
              </span>
              <span className="text-xs font-bold text-blue-900">
                {retornoReal.toFixed(1).replace('.', ',')}% a.a.
              </span>
            </div>
          </div>
        </div>

        {/* Aportes Extraordinários */}
        <div className="mt-5">
          <div className="section-label text-[11px] font-bold uppercase tracking-[0.08em] text-gray-400 mb-3 flex items-center gap-2">
            <svg
              className="w-3.5 h-3.5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Aportes Extraordinários
            <span className="flex-1 h-px bg-gray-200" />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-3">
          {extras.length > 0 && (
            <div className="space-y-3 mb-3">
              {extras.map((e) => (
                <div
                  key={e.id}
                  className="border border-gray-100 rounded-xl p-3.5 relative"
                >
                  <button
                    onClick={() => removeExtra(e.id)}
                    className="absolute top-2 right-2 p-1 text-gray-300 hover:text-red-500 transition-colors"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>

                  <div className="grid grid-cols-2 gap-3 mb-3">
                    <div>
                      <label className="text-[9px] text-gray-400 uppercase tracking-wide block mb-1">
                        Descrição
                      </label>
                      <input
                        type="text"
                        value={e.descricao}
                        className="w-full text-xs font-medium text-gray-900 bg-gray-50 rounded-lg px-2.5 py-2 outline-none border border-gray-100 focus:border-gray-300"
                        onChange={(ev) =>
                          updateExtra(e.id, 'descricao', ev.target.value)
                        }
                      />
                    </div>
                    <div>
                      <label className="text-[9px] text-gray-400 uppercase tracking-wide block mb-1">
                        Valor (R$)
                      </label>
                      <input
                        type="number"
                        value={e.valor}
                        className="w-full text-xs font-bold text-gray-900 bg-gray-50 rounded-lg px-2.5 py-2 outline-none border border-gray-100 focus:border-gray-300"
                        onChange={(ev) =>
                          updateExtra(e.id, 'valor', parseFloat(ev.target.value) || 0)
                        }
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 mb-3">
                    <div>
                      <label className="text-[9px] text-gray-400 uppercase tracking-wide block mb-1">
                        Mês
                      </label>
                      <select
                        className="w-full text-xs text-gray-700 bg-gray-50 rounded-lg px-2.5 py-2 outline-none border border-gray-100"
                        value={e.mesAno}
                        onChange={(ev) =>
                          updateExtra(e.id, 'mesAno', parseInt(ev.target.value))
                        }
                      >
                        {MESES.map((m, i) => (
                          <option key={i} value={i + 1}>
                            {m}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-[9px] text-gray-400 uppercase tracking-wide block mb-1">
                        Recorrência
                      </label>
                      <select
                        className="w-full text-xs text-gray-700 bg-gray-50 rounded-lg px-2.5 py-2 outline-none border border-gray-100"
                        value={e.recorrencia}
                        onChange={(ev) =>
                          updateExtra(e.id, 'recorrencia', ev.target.value)
                        }
                      >
                        <option value="unico">Único</option>
                        <option value="trimestral">Trimestral</option>
                        <option value="semestral">Semestral</option>
                        <option value="anual">Anual</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex items-center justify-between py-2 px-2 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={e.evoluir}
                        className="w-4 h-4 rounded accent-gray-900"
                        onChange={(ev) =>
                          updateExtra(e.id, 'evoluir', ev.target.checked)
                        }
                      />
                      <label className="text-xs text-gray-600">Evoluir valor</label>
                    </div>
                    {e.evoluir && (
                      <div className="flex items-center gap-1.5">
                        <input
                          type="number"
                          value={e.evolucaoValor}
                          className="w-14 text-xs font-semibold text-gray-900 bg-white rounded px-2 py-1 outline-none border border-gray-200 text-center"
                          onChange={(ev) =>
                            updateExtra(
                              e.id,
                              'evolucaoValor',
                              parseFloat(ev.target.value) || 0
                            )
                          }
                        />
                        <div className="flex rounded-lg overflow-hidden border border-gray-200">
                          <button
                            onClick={() =>
                              updateExtra(e.id, 'evolucaoTipo', 'percentual')
                            }
                            className={`px-2 py-1 text-[10px] font-bold ${
                              e.evolucaoTipo === 'percentual'
                                ? 'bg-gray-900 text-white'
                                : 'bg-white text-gray-500'
                            }`}
                          >
                            %
                          </button>
                          <button
                            onClick={() =>
                              updateExtra(e.id, 'evolucaoTipo', 'nominal')
                            }
                            className={`px-2 py-1 text-[10px] font-bold ${
                              e.evolucaoTipo === 'nominal'
                                ? 'bg-gray-900 text-white'
                                : 'bg-white text-gray-500'
                            }`}
                          >
                            R$
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  {e.evoluir && (
                    <div className="mt-2 py-1.5 px-2.5 bg-blue-50 rounded-lg">
                      <p className="text-[9px] text-blue-600">
                        {e.evolucaoTipo === 'percentual'
                          ? `Ano 1: R$ ${e.valor.toLocaleString('pt-BR')} → Ano 2: R$ ${Math.round(
                              e.valor * (1 + e.evolucaoValor / 100)
                            ).toLocaleString('pt-BR')} → Ano 3: R$ ${Math.round(
                              e.valor * Math.pow(1 + e.evolucaoValor / 100, 2)
                            ).toLocaleString('pt-BR')}`
                          : `Ano 1: R$ ${e.valor.toLocaleString('pt-BR')} → Ano 2: R$ ${(
                              e.valor + e.evolucaoValor
                            ).toLocaleString('pt-BR')} → Ano 3: R$ ${(
                              e.valor +
                              e.evolucaoValor * 2
                            ).toLocaleString('pt-BR')}`}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {extras.length === 0 && (
            <div className="text-center py-4">
              <p className="text-xs text-gray-400 mb-3">
                Adicione aportes extras como 13º, bônus, vendas, etc.
              </p>
            </div>
          )}

          <button
            onClick={addExtra}
            className="w-full py-2.5 border-2 border-dashed border-gray-200 rounded-xl text-xs font-semibold text-gray-500 hover:border-gray-400 hover:text-gray-700 transition-colors flex items-center justify-center gap-1.5 mt-2"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Adicionar Aporte Extraordinário
          </button>
        </div>

        {/* Projeção */}
        <div className="mt-5">
          <div className="section-label text-[11px] font-bold uppercase tracking-[0.08em] text-gray-400 mb-3 flex items-center gap-2">
            <svg
              className="w-3.5 h-3.5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            Projeção
            <span className="flex-1 h-px bg-gray-200" />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-4">
          <div className="relative mb-5">
            <div className="flex items-center justify-between">
              <div className="flex flex-col items-center">
                <div className="w-3 h-3 rounded-full bg-gray-900 z-10" />
                <span className="text-[10px] text-gray-500 mt-1">Hoje</span>
                <span className="text-[10px] font-semibold text-gray-900">
                  {age} anos
                </span>
              </div>
              <div className="flex-1 relative mx-2">
                <div className="h-0.5 bg-gray-200 w-full absolute top-1.5" />
                <div className="h-0.5 bg-gradient-to-r from-gray-900 to-emerald-500 w-full absolute top-1.5" />
              </div>
              <div className="flex flex-col items-center">
                <div className="w-3 h-3 rounded-full bg-emerald-500 z-10" />
                <span className="text-[10px] text-gray-500 mt-1">
                  Aposentadoria
                </span>
                <span className="text-[10px] font-semibold text-emerald-600">
                  aos {retire}
                </span>
              </div>
            </div>
          </div>

          <div className="relative mb-4" style={{ height: 140 }}>
            <svg
              viewBox="0 0 320 130"
              className="w-full h-full"
              preserveAspectRatio="none"
            >
              <defs>
                <linearGradient id="areaGrad2" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity={0.12} />
                  <stop offset="100%" stopColor="#10b981" stopOpacity={0.02} />
                </linearGradient>
                <linearGradient id="areaGradReal" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f97316" stopOpacity={0.08} />
                  <stop offset="100%" stopColor="#f97316" stopOpacity={0.01} />
                </linearGradient>
              </defs>
              <path d={curvePaths.nomArea} fill="url(#areaGrad2)" />
              <path d={curvePaths.realArea} fill="url(#areaGradReal)" />
              <path
                d={curvePaths.nomPath}
                stroke="#111827"
                strokeWidth="2"
                fill="none"
              />
              <path
                d={curvePaths.realPath}
                stroke="#f97316"
                strokeWidth="2"
                strokeDasharray="4 4"
                fill="none"
              />
              <circle cx={10} cy={110} r={5} fill="white" stroke="#111827" strokeWidth={2} />
              <circle cx={10} cy={110} r={2} fill="#111827" />
            </svg>
            <div className="absolute left-[1%] bottom-[5%]">
              <div className="bg-gray-900 text-white text-[10px] font-semibold px-2 py-0.5 rounded-md shadow whitespace-nowrap">
                {fC(patrimonio)}
              </div>
            </div>
            <div className="absolute right-[1%] top-[0%]">
              <div className="bg-emerald-500 text-white text-[10px] font-semibold px-2 py-0.5 rounded-md shadow whitespace-nowrap">
                {fC(projection.pNom)}
              </div>
              <div className="text-[9px] text-gray-400 text-right mt-0.5">
                Meta {new Date().getFullYear() + years}
              </div>
            </div>
            <div className="absolute right-[1%] top-[35%]">
              <div className="bg-orange-400 text-white text-[10px] font-semibold px-2 py-0.5 rounded-md shadow whitespace-nowrap">
                {fC(projection.pReal)}
              </div>
              <div className="text-[9px] text-orange-400 text-right mt-0.5">
                Valor real
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4 mb-4 justify-center">
            <div className="flex items-center gap-1.5">
              <div className="w-5 h-0.5 bg-gradient-to-r from-gray-900 to-emerald-500 rounded-full" />
              <span className="text-[10px] text-gray-500">Nominal</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-5 h-0.5 border-t-2 border-dashed border-orange-400" />
              <span className="text-[10px] text-gray-500">Real (- IPCA)</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-emerald-50 rounded-xl p-3 text-center">
              <p className="text-[10px] text-emerald-700 font-medium uppercase tracking-wide">
                Patrimônio Nominal
              </p>
              <p className="text-lg font-bold text-emerald-700 mt-1">
                {fC(projection.pNom)}
              </p>
            </div>
            <div className="bg-orange-50 rounded-xl p-3 text-center">
              <p className="text-[10px] text-orange-700 font-medium uppercase tracking-wide">
                Valor Real (hoje)
              </p>
              <p className="text-lg font-bold text-orange-700 mt-1">
                {fC(projection.pReal)}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-blue-50 rounded-xl p-3 text-center">
              <p className="text-[10px] text-blue-700 font-medium uppercase tracking-wide">
                Renda Passiva
              </p>
              <p className="text-lg font-bold text-blue-700 mt-1">
                ~{fC(projection.rendaPassivaReal)}/mês
              </p>
              <p className="text-[9px] text-blue-500 mt-0.5">
                Nominal: ~{fC(projection.rendaPassivaNom)}
              </p>
            </div>
            <div className="bg-gray-50 rounded-xl p-3 text-center">
              <p className="text-[10px] text-gray-500 font-medium uppercase tracking-wide">
                Poder de compra
              </p>
              <p className="text-lg font-bold text-gray-900 mt-1">
                ≈ {fC(projection.rendaPassivaReal)}
              </p>
              <p className="text-[9px] text-gray-400 mt-0.5">Em reais de hoje</p>
            </div>
          </div>

          <div className="space-y-0 divide-y divide-gray-100 mb-4">
            <div className="flex items-center justify-between py-2.5">
              <span className="text-xs text-gray-500">Total aportado</span>
              <span className="text-xs font-semibold text-gray-900">
                {fF(projection.totalAportes)}
              </span>
            </div>
            <div className="flex items-center justify-between py-2.5">
              <span className="text-xs text-gray-500">Rendimentos nominais</span>
              <span className="text-xs font-semibold text-emerald-600">
                {fF(projection.rendimentosNom)}
              </span>
            </div>
            <div className="flex items-center justify-between py-2.5">
              <span className="text-xs text-gray-500">Perda com inflação</span>
              <span className="text-xs font-semibold text-orange-500">
                - {fF(projection.perdaInflacao)}
              </span>
            </div>
            <div className="flex items-center justify-between py-2.5">
              <span className="text-xs text-gray-500">Multiplicador real</span>
              <span className="text-xs font-semibold text-gray-900">
                {projection.multiplier.toFixed(1)}x
              </span>
            </div>
          </div>

          <div
            className={`flex items-center justify-center gap-2 py-3 rounded-xl ${sentiment.bg}`}
          >
            <span className="text-2xl">{sentiment.emoji}</span>
            <span className={`text-sm font-medium ${sentiment.textColor}`}>
              {sentiment.text}
            </span>
          </div>
        </div>

        <div className="sticky bottom-0 -mx-5 px-5 py-4 bg-gradient-to-t from-gray-50 via-gray-50 to-transparent">
          <button
            onClick={() => setShowSuccess(true)}
            className="w-full py-3.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 transition-colors flex items-center justify-center gap-2 shadow-lg shadow-emerald-200"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            Salvar Meu Plano
          </button>
        </div>
      </div>
    </div>
  )
}
