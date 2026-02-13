/**
 * WalletBalanceCard Component
 * Sprint 3.2 - Dashboard Mobile Redesign
 * 
 * Exibe saldo da carteira com variação percentual
 */

interface WalletBalanceCardProps {
  balance: number
  changePercentage?: number | null
}

export function WalletBalanceCard({ balance, changePercentage }: WalletBalanceCardProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2
    }).format(value)
  }

  const formatPercentage = (value: number) => {
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(1)}%`
  }

  return (
    <div className="mb-6">
      <p className="text-xs text-gray-500 mb-1">Saldo da Carteira</p>
      <div className="flex items-baseline gap-2 mb-3">
        <h2 className="text-3xl font-bold text-gray-900">
          {formatCurrency(balance)}
        </h2>
        {changePercentage !== null && changePercentage !== undefined && (
          <span className={`text-sm font-semibold ${changePercentage >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {formatPercentage(changePercentage)}
          </span>
        )}
      </div>
    </div>
  )
}
