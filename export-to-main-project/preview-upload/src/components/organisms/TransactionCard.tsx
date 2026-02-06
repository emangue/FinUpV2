'use client';

import { useState } from 'react';
import { Transaction } from '@/types';
import { formatCurrency, GRUPOS, SUBGRUPOS } from '@/lib/constants';
import { CLASSIFICATION_SOURCE_LABELS, CLASSIFICATION_SOURCE_COLORS } from '@/types';
import Badge from '../atoms/Badge';
import IconButton from '../atoms/IconButton';

interface TransactionCardProps {
  transaction: Transaction;
  onEdit?: (transaction: Transaction) => void;
  onBatchUpdate?: (transactionId: string, grupo: string, subgrupo: string) => void;
}

export default function TransactionCard({ transaction, onEdit, onBatchUpdate }: TransactionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedGrupo, setSelectedGrupo] = useState(transaction.grupo || '');
  const [selectedSubgrupo, setSelectedSubgrupo] = useState(transaction.subgrupo || '');
  
  const isGrouped = transaction.items && transaction.items.length > 0;
  const isClassified = Boolean(transaction.grupo && transaction.subgrupo);

  const borderColor = isClassified ? 'border-green-200' : 'border-gray-200';

  const handleGrupoChange = (value: string) => {
    setSelectedGrupo(value);
    setSelectedSubgrupo('');
    if (onBatchUpdate && value && !isGrouped) {
      // Auto-save para transações únicas quando mudar grupo
      onBatchUpdate(transaction.id, value, '');
    }
  };

  const handleSubgrupoChange = (value: string) => {
    setSelectedSubgrupo(value);
    if (onBatchUpdate && selectedGrupo && value) {
      // Auto-save quando selecionar subgrupo completo
      onBatchUpdate(transaction.id, selectedGrupo, value);
    }
  };

  return (
    <div className={`bg-white border ${borderColor} rounded-xl overflow-hidden hover:shadow-md transition-all`}>
      {/* Header */}
      <div
        className={`p-4 ${isGrouped ? 'cursor-pointer' : ''}`}
        onClick={() => isGrouped && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start gap-3">
          {isGrouped && (
            <button
              className={`text-gray-400 mt-1 transform transition-transform duration-200 ${
                isExpanded ? 'rotate-90' : ''
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          )}

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-1">
              <div>
                {isGrouped && <Badge className="mb-1">{transaction.occurrences}×</Badge>}
                <h3 className="font-semibold text-gray-900 text-sm">{transaction.description}</h3>
                {isGrouped && (
                  <p className="text-xs text-gray-500 mt-0.5">{transaction.occurrences} ocorrências</p>
                )}
                {!isGrouped && <p className="text-xs text-gray-500 mt-0.5">{transaction.date}</p>}
              </div>

              <div className="flex items-center gap-2">
                {isClassified && <Badge variant="success">✓</Badge>}
                <p className="font-semibold text-red-600 text-sm whitespace-nowrap">
                  {formatCurrency(transaction.value)}
                </p>
                {!isClassified && !isGrouped && onEdit && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit(transaction);
                    }}
                    className="text-gray-400 hover:text-blue-600 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                      />
                    </svg>
                  </button>
                )}
              </div>
            </div>

            {/* Classification Fields - Always visible */}
            <div className="mt-2 space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500 w-20">Grupo:</span>
                {isClassified ? (
                  <span className="text-sm text-gray-900 bg-green-50 border border-green-200 px-2 py-1 rounded-md font-medium">
                    {transaction.grupo}
                  </span>
                ) : (
                  <select
                    value={selectedGrupo}
                    onChange={(e) => {
                      e.stopPropagation();
                      handleGrupoChange(e.target.value);
                    }}
                    onClick={(e) => e.stopPropagation()}
                    className="flex-1 text-sm border border-gray-300 rounded-lg px-2 py-1 bg-white text-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none"
                  >
                    <option value="">Selecione grupo</option>
                    {GRUPOS.map((g) => (
                      <option key={g} value={g}>
                        {g}
                      </option>
                    ))}
                  </select>
                )}
              </div>
              
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500 w-20">Subgrupo:</span>
                {isClassified ? (
                  <span className="text-sm text-gray-900 bg-green-50 border border-green-200 px-2 py-1 rounded-md font-medium">
                    {transaction.subgrupo}
                  </span>
                ) : (
                  <select
                    value={selectedSubgrupo}
                    onChange={(e) => {
                      e.stopPropagation();
                      handleSubgrupoChange(e.target.value);
                    }}
                    onClick={(e) => e.stopPropagation()}
                    disabled={!selectedGrupo}
                    className="flex-1 text-sm border border-gray-300 rounded-lg px-2 py-1 bg-white text-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
                  >
                    <option value="">Selecione subgrupo</option>
                    {selectedGrupo &&
                      SUBGRUPOS[selectedGrupo]?.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                  </select>
                )}
              </div>

              
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500 w-20">Origem:</span>
                <span className={`text-xs px-2 py-1 rounded-md ${CLASSIFICATION_SOURCE_COLORS[transaction.source]}`}>
                  {!isClassified && '⚠️ '}{CLASSIFICATION_SOURCE_LABELS[transaction.source]}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Expanded Items */}
      {isGrouped && isExpanded && transaction.items && (
        <div className="bg-gray-50 border-t border-gray-200">
          {transaction.items.map((item, index) => (
            <div
              key={item.id}
              className={`px-4 py-3 hover:bg-white transition-colors ${
                index > 0 ? 'border-t border-gray-200' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-xs text-gray-500 mb-0.5">{item.date}</p>
                  <p className="text-sm text-gray-900 font-medium">{item.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  <p className="font-semibold text-red-600 text-sm">{formatCurrency(item.value)}</p>
                  {onEdit && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onEdit(item);
                      }}
                      className="text-gray-400 hover:text-blue-600 transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                        />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
