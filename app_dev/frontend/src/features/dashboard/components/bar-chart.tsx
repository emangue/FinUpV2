/**
 * BarChart Component
 * Sprint 3.2 - Dashboard Mobile Redesign
 * 
 * Gráfico de barras para receitas vs despesas
 * ATUALIZADO: Seguindo protótipo de referência com alturas fixas
 */

'use client'

import { useState } from 'react'
import type { ChartDataPoint } from '../types'

interface BarChartProps {
  data: ChartDataPoint[]
  title: string
  totalValue: number
  selectedMonth: Date  // Mês selecionado no scroll
}

export function BarChart({ data, title, totalValue, selectedMonth }: BarChartProps) {
  const [hoveredBar, setHoveredBar] = useState<number | null>(null)

  // Alturas FIXAS em pixels (como no protótipo de referência)
  // Garante visualização consistente independente dos valores reais
  const fixedHeights = [
    { despesas: 50, receitas: 65 },   // Mês 1
    { despesas: 62, receitas: 80 },   // Mês 2
    { despesas: 75, receitas: 95 },   // Mês 3
    { despesas: 58, receitas: 72 },   // Mês 4
    { despesas: 88, receitas: 110 },  // Mês 5
    { despesas: 98, receitas: 125 },  // Mês 6
    { despesas: 70, receitas: 88 },   // Mês 7
  ]

  // Calcular últimos 7 meses baseado no mês selecionado
  const generateLast7Months = () => {
    const months = []
    const current = new Date(selectedMonth)
    
    // Começar 6 meses antes do selecionado
    for (let i = 6; i >= 0; i--) {
      const date = new Date(current.getFullYear(), current.getMonth() - i, 1)
      const yearStr = date.getFullYear()
      const monthStr = String(date.getMonth() + 1).padStart(2, '0')
      const dateKey = `${yearStr}-${monthStr}-01`
      
      // Buscar dados reais da API pelo formato YYYY-MM-01
      const apiData = data.find(d => d.date === dateKey)
      
      months.push({
        date: dateKey,
        receitas: apiData?.receitas || 0,
        despesas: apiData?.despesas || 0
      })
    }
    
    return months
  }

  // Calcular os últimos 7 meses dinamicamente (com dados da API quando disponíveis)
  const displayData = generateLast7Months()
  
  // Debug: ver dados da API
  console.log('📊 BarChart - Dados da API:', data)
  console.log('📊 BarChart - displayData gerado:', displayData)

  // ⚡ NOVO: Calcular alturas proporcionais baseadas nos valores reais
  const calculateProportionalHeights = () => {
    // Encontrar o valor máximo entre todas receitas e despesas
    const allValues = displayData.flatMap(d => [d.receitas, d.despesas])
    const maxValue = Math.max(...allValues, 1) // Evitar divisão por 0
    
    const maxHeight = 150 // Altura máxima em pixels (deixa 10px de margem do container h-40=160px)
    const minHeight = 20  // Altura mínima para visibilidade (mesmo se valor for 0)
    
    return displayData.map(item => ({
      despesas: item.despesas > 0 
        ? Math.max(minHeight, (item.despesas / maxValue) * maxHeight)
        : minHeight,
      receitas: item.receitas > 0
        ? Math.max(minHeight, (item.receitas / maxValue) * maxHeight)
        : minHeight
    }))
  }
  
  const proportionalHeights = calculateProportionalHeights()

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0
    }).format(value)
  }

  const formatDate = (dateStr: string) => {
    // dateStr format: YYYY-MM-DD
    const [year, month, day] = dateStr.split('-')
    const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    return monthNames[parseInt(month) - 1]
  }

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-bold text-gray-900">{title}</h3>
        <p className="text-lg font-bold text-gray-900">{formatCurrency(totalValue)}</p>
      </div>
      <p className="text-xs text-gray-400 mb-4">Comparação Mensal</p>

      {/* Bar Chart */}
      <div className="relative">
        {/* Chart Container - Altura fixa h-40 (160px) */}
        <div className="flex items-end justify-between gap-4 h-40 px-2">
          {displayData.map((item, index) => (
            <div
              key={`${item.date}-${index}`}
              className="flex items-end gap-1 flex-1 relative group"
              onMouseEnter={() => setHoveredBar(index)}
              onMouseLeave={() => setHoveredBar(null)}
            >
              {/* ORDEM CRÍTICA: Despesas PRIMEIRO (cinza), Receitas DEPOIS (preto) */}
              
              {/* Despesas (cinza) - w-2 (8px fixo), altura proporcional */}
              <div
                className="w-2 bg-gray-400 rounded-t-sm cursor-pointer transition-opacity hover:opacity-80"
                style={{
                  height: `${proportionalHeights[index]?.despesas || 20}px`
                }}
              />
              
              {/* Receitas (preto) - w-2 (8px fixo), altura proporcional */}
              <div
                className="w-2 bg-gray-900 rounded-t-sm cursor-pointer transition-opacity hover:opacity-80"
                style={{
                  height: `${proportionalHeights[index]?.receitas || 20}px`
                }}
              />

              {/* Tooltip */}
              {hoveredBar === index && (
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-gray-900 text-white text-xs px-3 py-2 rounded-lg shadow-lg whitespace-nowrap z-10">
                  <div className="font-semibold mb-1">{formatDate(item.date)}</div>
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-sm"></div>
                    <span className="text-[11px]">Despesas: {formatCurrency(item.despesas)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-white rounded-sm"></div>
                    <span className="text-[11px]">Receitas: {formatCurrency(item.receitas)}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Month Labels - FORA do container de barras */}
        <div className="flex justify-between px-2 mt-2">
          {displayData.map((item, index) => (
            <span 
              key={`label-${item.date}-${index}`}
              className="text-[9px] text-gray-400 flex-1 text-center"
            >
              {formatDate(item.date)}
            </span>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-6">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-gray-400"></div>
          <span className="text-xs text-gray-600">Despesas</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-gray-900"></div>
          <span className="text-xs text-gray-600">Receitas</span>
        </div>
      </div>
    </div>
  )
}
