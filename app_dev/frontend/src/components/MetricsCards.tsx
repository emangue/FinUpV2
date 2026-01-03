import { TrendingDown, TrendingUp, Wallet, Receipt } from 'lucide-react'
import { formatCurrency } from '../lib/utils'

interface MetricsProps {
  metrics: {
    total_gastos: number
    total_receitas: number
    saldo: number
    total_transacoes: number
  }
}

export default function MetricsCards({ metrics }: MetricsProps) {
  const cards = [
    {
      title: 'Total Gastos',
      value: formatCurrency(metrics.total_gastos),
      icon: TrendingDown,
      iconColor: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      title: 'Total Receitas',
      value: formatCurrency(metrics.total_receitas),
      icon: TrendingUp,
      iconColor: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Saldo',
      value: formatCurrency(metrics.saldo),
      icon: Wallet,
      iconColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Transações',
      value: metrics.total_transacoes.toString(),
      icon: Receipt,
      iconColor: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card) => {
        const Icon = card.icon
        return (
          <div
            key={card.title}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">{card.title}</h3>
              <div className={`p-2 rounded-lg ${card.bgColor}`}>
                <Icon className={`w-5 h-5 ${card.iconColor}`} />
              </div>
            </div>
            <p className="text-2xl font-bold text-gray-900">{card.value}</p>
          </div>
        )
      })}
    </div>
  )
}
