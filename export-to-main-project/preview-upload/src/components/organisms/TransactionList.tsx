'use client';

import { Transaction, TabFilter } from '@/types';
import TransactionCard from './TransactionCard';

interface TransactionListProps {
  transactions: Transaction[];
  activeTab: TabFilter;
  onEdit: (transaction: Transaction) => void;
  onBatchUpdate: (transactionId: string, grupo: string, subgrupo: string) => void;
}

export default function TransactionList({ transactions, activeTab, onEdit, onBatchUpdate }: TransactionListProps) {
  const filteredTransactions = transactions.filter((tx) => {
    if (activeTab === 'all') return true;
    if (activeTab === 'classificadas') return tx.grupo && tx.subgrupo;
    if (activeTab === 'not_classified') return !tx.grupo || !tx.subgrupo;
    return tx.source === activeTab;
  });

  return (
    <div className="space-y-2 px-4 pb-24">
      {filteredTransactions.map((transaction) => (
        <TransactionCard
          key={transaction.id}
          transaction={transaction}
          onEdit={onEdit}
          onBatchUpdate={onBatchUpdate}
        />
      ))}

      {filteredTransactions.length === 0 && (
        <div className="text-center py-12">
          <svg
            className="mx-auto w-12 h-12 text-gray-300 mb-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p className="text-gray-500 text-sm">Nenhuma transação encontrada nesta categoria</p>
        </div>
      )}
    </div>
  );
}
