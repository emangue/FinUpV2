'use client'

import { useEffect, useState } from 'react'
import { fetchWithAuth } from '@/core/utils/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { TrendingUp, TrendingDown, ChevronDown, ChevronUp } from 'lucide-react'

interface BudgetItem {
  grupo: string
  realizado: number
  planejado: number
  percentual: number
  diferenca: number
}

interface BudgetData {
  items: BudgetItem[]
  total_realizado: number
  total_planejado: number
  percentual_geral: number
}

interface BudgetMobileProps {
  year: string
  month: string
}

export function BudgetMobile({ year, month }: BudgetMobileProps) {
  const [data, setData] = useState<BudgetData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isExpanded, setIsExpanded] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL 
          ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1` 
          : 'http://localhost:8000/api/v1'
        
        const url = month === 'all' 
          ? `${apiUrl}/dashboard/budget-vs-actual?year=${year}&ytd=true`
          : `${apiUrl}/dashboard/budget-vs-actual?year=${year}&month=${month}`
        
        const response = await fetchWithAuth(url)

        if (!response.ok) {
          throw new Error(`Erro ao buscar orçamento: ${response.statusText}`)
        }

        const result = await response.json()
        setData(result)
      } catch (err) {
        console.error('Error fetching budget:', err)
        setError(err instanceof Error ? err.message : 'Erro desconhecido')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [year, month])

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  if (loading) {
    return (
      <Card className="rounded-2xl shadow-md">
        <CardHeader>
          <CardTitle className="text-base">Realizado vs Planejado</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-200 animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !data) {
    return (
      <Card className="rounded-2xl shadow-md bg-red-50 border-red-200">
        <CardContent className="pt-6">
          <p className="text-sm text-red-600">
            {error || 'Erro ao carregar orçamento'}
          </p>
        </CardContent>
      </Card>
    )
  }

  // Filtrar top 5 grupos (excluir "Demais")
  const topGroups = data.items
    .filter(item => item.grupo !== 'Demais')
    .slice(0, 5)
  
  // Calcular "Demais" - soma de tudo que não está no top 5
  const demaisItems = data.items
    .filter(item => item.grupo !== 'Demais')
    .slice(5)
  
  const demais = demaisItems.length > 0 ? {
    grupo: 'Demais',
    realizado: demaisItems.reduce((sum, item) => sum + item.realizado, 0),
    planejado: demaisItems.reduce((sum, item) => sum + item.planejado, 0),
    percentual: 0,
    diferenca: 0
  } : null
  
  if (demais) {
    demais.percentual = demais.planejado > 0 
      ? (demais.realizado / demais.planejado) * 100 
      : 0
    demais.diferenca = demais.realizado - demais.planejado
  }

  return (
    <Card className="rounded-2xl shadow-md">
      {/* Header com título */}
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Realizado vs Planejado</CardTitle>
        <p className="text-xs text-gray-500 mt-1">
          Principais categorias de gasto
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Total geral - SEMPRE VISÍVEL */}
        <div className="bg-muted/50 p-4 rounded-lg border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Total Geral</span>
            <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
              data.percentual_geral <= 100 
                ? 'bg-green-100 text-green-700' 
                : 'bg-red-100 text-red-700'
            }`}>
              {data.percentual_geral.toFixed(0)}%
            </span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-xl font-bold">
              {formatCurrency(data.total_realizado)}
            </span>
            <span className="text-sm text-muted-foreground">
              de {formatCurrency(data.total_planejado)}
            </span>
          </div>
          <Progress 
            value={Math.min(data.percentual_geral, 100)} 
            className="h-2 mt-2"
          />
        </div>

        {/* Botão de expansão */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg border bg-card hover:bg-accent/5 transition-colors"
        >
          <span className="text-sm font-medium text-muted-foreground">
            {isExpanded ? 'Ver menos' : 'Ver detalhes'}
          </span>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
        </button>

        {/* Conteúdo expansível - Lista de categorias (top 5) */}
        {isExpanded && (
          <div className="space-y-3">
            {topGroups.map((item) => {
              const isOverBudget = item.percentual > 100
              const emoji = getEmojiForCategory(item.grupo)

              return (
                <div
                  key={item.grupo}
                  className="bg-card border rounded-lg p-3 hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{emoji}</span>
                      <span className="text-sm font-medium text-gray-700">
                        {item.grupo}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      {isOverBudget ? (
                        <TrendingUp className="h-3 w-3 text-red-500" />
                      ) : (
                        <TrendingDown className="h-3 w-3 text-green-500" />
                      )}
                      <span className={`text-xs font-semibold ${
                        isOverBudget ? 'text-red-600' : 'text-green-600'
                      }`}>
                        {item.percentual.toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="flex items-baseline justify-between text-xs mb-2">
                    <span className="font-semibold text-gray-900">
                      {formatCurrency(item.realizado)}
                    </span>
                    <span className="text-gray-500">
                      / {formatCurrency(item.planejado)}
                    </span>
                  </div>

                  <Progress
                    value={Math.min(item.percentual, 100)}
                    className="h-1.5"
                    indicatorClassName={isOverBudget ? 'bg-red-500' : 'bg-green-500'}
                  />
                </div>
              )
            })}

            {/* Item "Demais" se existir */}
            {demais && demais.realizado > 0 && (
              <div className="bg-card border border-dashed rounded-lg p-3 hover:shadow-sm transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">📦</span>
                    <span className="text-sm font-medium text-gray-600 italic">
                      Demais
                    </span>
                    <span className="text-xs text-gray-400">
                      ({demaisItems.length} categorias)
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    {demais.percentual > 100 ? (
                      <TrendingUp className="h-3 w-3 text-red-500" />
                    ) : (
                      <TrendingDown className="h-3 w-3 text-green-500" />
                    )}
                    <span className={`text-xs font-semibold ${
                      demais.percentual > 100 ? 'text-red-600' : 'text-green-600'
                    }`}>
                      {demais.percentual.toFixed(0)}%
                    </span>
                  </div>
                </div>

                <div className="flex items-baseline justify-between text-xs mb-2">
                  <span className="font-semibold text-gray-900">
                    {formatCurrency(demais.realizado)}
                  </span>
                  <span className="text-gray-500">
                    / {formatCurrency(demais.planejado)}
                  </span>
                </div>

                <Progress
                  value={Math.min(demais.percentual, 100)}
                  className="h-1.5"
                  indicatorClassName={demais.percentual > 100 ? 'bg-red-500' : 'bg-green-500'}
                />
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Helper para emoji por categoria
function getEmojiForCategory(categoria: string): string {
  const emojiMap: { [key: string]: string } = {
    'Alimentação': '🍔',
    'Transporte': '🚗',
    'Moradia': '🏠',
    'Saúde': '💊',
    'Educação': '📚',
    'Lazer': '🎮',
    'Vestuário': '👕',
    'Outros': '📦',
    'Fixa': '📌',
    'Variável': '📊',
  }
  return emojiMap[categoria] || '💰'
}
