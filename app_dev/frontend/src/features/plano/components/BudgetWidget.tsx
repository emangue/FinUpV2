'use client';

/**
 * F.04: Widget de orçamento no dashboard
 * Nudge se renda não declarada; mostra Renda | Gasto | Poupança ou Disponível (A.07)
 * Sprint 6 - Plano Financeiro
 */
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Target, ChevronRight } from 'lucide-react';
import { getRenda, getResumoPlano } from '../api';

interface BudgetWidgetProps {
  totalDespesas?: number;
  totalReceitas?: number;
  year: number;
  month?: number;
}

function formatCurrency(v: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  }).format(v);
}

export function BudgetWidget({
  totalDespesas = 0,
  totalReceitas = 0,
  year,
  month,
}: BudgetWidgetProps) {
  const [renda, setRenda] = useState<number | null>(null);
  const [resumo, setResumo] = useState<{ total_budget: number; disponivel_real: number | null } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRenda()
      .then((r) => setRenda(r.renda))
      .catch(() => setRenda(null))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!month || month < 1 || month > 12) return;
    getResumoPlano(year, month)
      .then((r) => setResumo({ total_budget: r.total_budget, disponivel_real: r.disponivel_real }))
      .catch(() => setResumo(null));
  }, [year, month]);

  if (loading) return null;

  // Nudge: renda não declarada
  if (renda == null || renda === 0) {
    return (
      <Link
        href="/mobile/perfil/financeiro"
        className="block bg-indigo-50 border border-indigo-200 rounded-2xl p-4 mb-4"
      >
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center">
            <Target className="w-6 h-6 text-indigo-600" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-indigo-900">Configure seu plano financeiro</p>
            <p className="text-sm text-indigo-700">
              Declare sua renda para acompanhar gastos e metas
            </p>
          </div>
          <ChevronRight className="w-5 h-5 text-indigo-500" />
        </div>
      </Link>
    );
  }

  const poupanca = renda - totalDespesas;
  const pctPoupanca = renda > 0 ? Math.round((poupanca / renda) * 100) : 0;
  const disp = resumo?.disponivel_real;
  const temDisponivel = disp !== undefined && disp !== null;

  return (
    <Link
      href="/mobile/perfil/financeiro"
      className="block bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mb-4 hover:bg-gray-50"
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-[15px] font-semibold text-black flex items-center gap-2">
          <Target className="w-4 h-4 text-indigo-600" />
          Plano do mês
        </h3>
        <ChevronRight className="w-4 h-4 text-gray-400" />
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div>
          <p className="text-[11px] text-gray-500 uppercase">Renda</p>
          <p className="text-[13px] font-semibold text-black">{formatCurrency(renda)}</p>
        </div>
        <div>
          <p className="text-[11px] text-gray-500 uppercase">Gasto</p>
          <p className="text-[13px] font-semibold text-black">{formatCurrency(totalDespesas)}</p>
        </div>
        <div>
          <p className="text-[11px] text-gray-500 uppercase">
            {temDisponivel ? 'Disponível' : 'Poupança'}
          </p>
          <p
            className={`text-[13px] font-semibold ${
              temDisponivel
                ? (disp >= 0 ? 'text-emerald-600' : 'text-red-600')
                : (pctPoupanca >= 0 ? 'text-emerald-600' : 'text-red-600')
            }`}
          >
            {temDisponivel ? formatCurrency(disp) : `${pctPoupanca}%`}
          </p>
        </div>
      </div>
    </Link>
  );
}
