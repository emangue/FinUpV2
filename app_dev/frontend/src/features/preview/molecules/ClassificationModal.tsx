'use client';

import { useState } from 'react';
import Button from '../atoms/Button';
import { GRUPOS, SUBGRUPOS, formatCurrency } from '../lib/constants';
import { ClassificationData, Transaction } from '../types';

interface ClassificationModalProps {
  transaction: Transaction;
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: ClassificationData) => void;
}

export default function ClassificationModal({
  transaction,
  isOpen,
  onClose,
  onSave,
}: ClassificationModalProps) {
  const [grupo, setGrupo] = useState('');
  const [subgrupo, setSubgrupo] = useState('');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSave = () => {
    if (!grupo || !subgrupo) {
      setError('Por favor, selecione grupo e subgrupo');
      return;
    }
    setError('');
    onSave({ grupo, subgrupo });
    setGrupo('');
    setSubgrupo('');
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl animate-fade-in">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900">Classificar Transação</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="bg-gray-50 p-3 rounded-lg mb-4">
          <p className="text-xs text-gray-500 mb-1">{transaction.date}</p>
          <p className="font-semibold text-gray-900">{transaction.description}</p>
          <p className="text-red-600 font-bold mt-1">{formatCurrency(transaction.value)}</p>
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Grupo</label>
            <select
              value={grupo}
              onChange={(e) => {
                setGrupo(e.target.value);
                setSubgrupo('');
              }}
              className="w-full text-sm border-2 border-gray-300 rounded-lg px-3 py-2.5 bg-white text-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all"
            >
              <option value="">Selecione grupo</option>
              {GRUPOS.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Subgrupo</label>
            <select
              value={subgrupo}
              onChange={(e) => setSubgrupo(e.target.value)}
              disabled={!grupo}
              className="w-full text-sm border-2 border-gray-300 rounded-lg px-3 py-2.5 bg-white text-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">Selecione subgrupo</option>
              {grupo &&
                SUBGRUPOS[grupo]?.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
            </select>
          </div>
        </div>

        {error && (
          <p className="text-sm text-red-600 flex items-center gap-1 mt-1">
            <span>⚠️</span>
            {error}
          </p>
        )}

        <Button
          onClick={handleSave}
          variant="primary"
          fullWidth
          className="mt-6 py-3 font-bold shadow-lg"
        >
          💾 Salvar Classificação
        </Button>
      </div>
    </div>
  );
}
