'use client';

/**
 * F.01: Formulário de declaração de renda mensal líquida
 * Sprint 6 - Plano Financeiro
 */
import { useState, useEffect } from 'react';
import { DollarSign } from 'lucide-react';
import { getRenda, postRenda } from '../api';

export function RendaDeclaracaoForm() {
  const [renda, setRenda] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getRenda()
      .then((r) => setRenda(r.renda != null ? String(r.renda) : ''))
      .catch(() => setRenda(''))
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const valor = parseFloat(renda.replace(',', '.'));
    if (isNaN(valor) || valor < 0) {
      setError('Informe um valor válido');
      return;
    }
    setError('');
    setSaving(true);
    try {
      await postRenda(valor);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Erro ao salvar');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="h-12 bg-gray-200 rounded" />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <h3 className="text-[17px] font-semibold text-black mb-3 flex items-center gap-2">
        <DollarSign className="w-5 h-5 text-indigo-600" />
        Renda mensal líquida
      </h3>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <input
            type="text"
            inputMode="decimal"
            value={renda}
            onChange={(e) => setRenda(e.target.value.replace(/[^0-9,.]/g, ''))}
            placeholder="Ex: 8000"
            className="w-full px-4 py-3 border border-gray-300 rounded-xl text-[17px] font-semibold focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            aria-label="Renda mensal líquida em reais"
          />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={saving}
          className="w-full py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 disabled:opacity-50"
        >
          {saving ? 'Salvando...' : 'Salvar'}
        </button>
      </form>
    </div>
  );
}
