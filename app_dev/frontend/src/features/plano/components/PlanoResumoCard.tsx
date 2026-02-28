'use client';

/**
 * PlanoResumoCard — Renda | Gastos | Disponível | Saldo
 * Reutiliza lógica do resumo (restrição orçamentária)
 */
import { useState, useEffect } from 'react';
import { getResumoPlano } from '../api';

function formatCurrency(v: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  }).format(v);
}

interface PlanoResumoCardProps {
  year: number;
  month: number;
}

export function PlanoResumoCard({ year, month }: PlanoResumoCardProps) {
  const [resumo, setResumo] = useState<{
    renda: number | null;
    total_budget: number;
    disponivel_real: number | null;
  } | null>(null);

  useEffect(() => {
    getResumoPlano(year, month)
      .then(setResumo)
      .catch(() => setResumo(null));
  }, [year, month]);

  if (!resumo || resumo.renda == null) return null;
  if (resumo.total_budget === 0) return null;

  return (
    <div className="bg-indigo-50 border border-indigo-100 rounded-2xl p-4">
      <p className="text-[13px] font-medium text-indigo-900 mb-2">
        Restrição orçamentária (metas)
      </p>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div>
          <p className="text-[11px] text-indigo-600 uppercase">Renda</p>
          <p className="text-[14px] font-semibold text-indigo-900">
            {formatCurrency(resumo.renda)}
          </p>
        </div>
        <div>
          <p className="text-[11px] text-indigo-600 uppercase">Planejado</p>
          <p className="text-[14px] font-semibold text-indigo-900">
            {formatCurrency(resumo.total_budget)}
          </p>
        </div>
        <div>
          <p className="text-[11px] text-indigo-600 uppercase">Disponível</p>
          <p
            className={`text-[14px] font-semibold ${
              (resumo.disponivel_real ?? 0) >= 0 ? 'text-emerald-700' : 'text-red-700'
            }`}
          >
            {resumo.disponivel_real != null
              ? formatCurrency(resumo.disponivel_real)
              : '—'}
          </p>
        </div>
      </div>
      <p className="text-[12px] text-indigo-700 mt-2">
        Disponível = Renda − total das metas por grupo
      </p>
    </div>
  );
}
