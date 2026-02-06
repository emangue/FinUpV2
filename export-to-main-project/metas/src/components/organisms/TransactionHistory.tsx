'use client';

import { Transaction } from '@/types';

interface TransactionHistoryProps {
  transactions: Transaction[];
}

export default function TransactionHistory({ transactions }: TransactionHistoryProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
  };

  if (transactions.length === 0) {
    return (
      <div className="py-6 text-center">
        <p className="text-gray-400 text-sm">Nenhuma transação registrada</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {transactions.map((transaction) => (
        <div
          key={transaction.id}
          className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
        >
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-gray-900">{transaction.description}</h4>
            <p className="text-xs text-gray-500">{formatDate(transaction.date)}</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-bold text-gray-900">
              R$ {transaction.amount.toLocaleString()}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
