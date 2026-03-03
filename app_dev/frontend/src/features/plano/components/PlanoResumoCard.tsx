'use client';

/**
 * PlanoResumoCard — Restrição orçamentária
 * Com realizado: Receitas | Despesas | Investidos (valor real + comparação com plano), igual Resumo do Mês
 * Sem realizado: Renda | Planejado | Disponível
 */
import { useState, useEffect } from 'react';
import { getResumoPlano } from '../api';
import { fetchIncomeSources } from '@/features/dashboard/services/dashboard-api';
import { fetchGoals } from '@/features/goals/services/goals-api';
import { fetchAporteInvestimentoDetalhado } from '@/features/dashboard/services/dashboard-api';

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
  const [receitas, setReceitas] = useState<{ total_receitas: number } | null>(null);
  const [goals, setGoals] = useState<Array<{ categoria_geral?: string; valor_realizado?: number; valor_planejado?: number }>>([]);
  const [aportePrincipal, setAportePrincipal] = useState<number>(0);

  useEffect(() => {
    const selectedMonth = new Date(year, month - 1, 1);
    Promise.all([
      getResumoPlano(year, month),
      fetchIncomeSources(year, month),
      fetchGoals(selectedMonth),
      fetchAporteInvestimentoDetalhado(year, month),
    ])
      .then(([r, inc, g, aporteDetalhe]) => {
        setResumo(r);
        setReceitas(inc && 'total_receitas' in inc ? inc : null);
        setGoals(Array.isArray(g) ? g : []);
        // Nova API: fixo (perfil) + extras (base_expectativas creditos) para o mês
        const aporte = aporteDetalhe?.mes?.aporte_total ?? 0
        setAportePrincipal(aporte);
      })
      .catch(() => {
        setResumo(null);
        setReceitas(null);
        setGoals([]);
        setAportePrincipal(0);
      });
  }, [year, month]);

  if (!resumo || resumo.renda == null) return null;
  if (resumo.total_budget === 0) return null;

  const goalsDespesas = goals.filter((g) => g.categoria_geral !== 'Investimentos');
  const goalsInvestimentos = goals.filter((g) => g.categoria_geral === 'Investimentos');
  const totalDespesas = goalsDespesas.reduce((s, g) => s + (g.valor_realizado ?? 0), 0);
  const totalInvestido = goalsInvestimentos.reduce((s, g) => s + (g.valor_realizado ?? 0), 0);
  const totalPlanejadoDesp = goalsDespesas.reduce((s, g) => s + (g.valor_planejado ?? 0), 0);
  const totalReceitas = receitas?.total_receitas ?? 0;

  const temRealizado = totalReceitas > 0 || totalDespesas > 0 || totalInvestido > 0;

  if (temRealizado) {
    const diffDesp = totalPlanejadoDesp - totalDespesas;
    const totalPlanejadoInv = aportePrincipal;
    const investidoOk = totalPlanejadoInv > 0 && totalInvestido >= totalPlanejadoInv;
    const pctInvestidoVsPlano = totalPlanejadoInv > 0 ? (totalInvestido / totalPlanejadoInv) * 100 : 0;
    const vezesAcimaPlano = totalPlanejadoInv > 0 ? totalInvestido / totalPlanejadoInv : 0;
    const labelInvestidos = totalPlanejadoInv > 0
      ? investidoOk
        ? vezesAcimaPlano > 1
          ? `${vezesAcimaPlano.toFixed(1).replace('.', ',')}x o plano`
          : '100% do aporte'
        : `${Math.round(pctInvestidoVsPlano)}% do aporte`
      : 'sem plano';
    const badgeDentro = totalPlanejadoDesp > 0 ? totalDespesas <= totalPlanejadoDesp : totalDespesas <= 0;

    return (
      <div className="bg-indigo-50 border border-indigo-100 rounded-2xl p-4">
        <div className="flex items-center justify-between mb-2">
          <p className="text-[13px] font-medium text-indigo-900">
            Restrição orçamentária (metas)
          </p>
          <span
            className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
              badgeDentro ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'
            }`}
          >
            {badgeDentro ? 'Dentro do plano' : 'Acima do plano'}
          </span>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <p className="text-[11px] text-indigo-600 uppercase">Receitas</p>
            <p className="text-[14px] font-semibold text-emerald-700">
              {formatCurrency(totalReceitas)}
            </p>
            <p className="text-[9px] text-indigo-600">sem plano</p>
          </div>
          <div className="border-x border-indigo-200">
            <p className="text-[11px] text-indigo-600 uppercase">Despesas</p>
            <p className="text-[14px] font-semibold text-red-600">
              {formatCurrency(totalDespesas)}
            </p>
            <p className="text-[9px] font-medium">
              {totalPlanejadoDesp > 0 ? (
                diffDesp >= 0 ? (
                  <span className="text-emerald-600">{formatCurrency(diffDesp)} abaixo</span>
                ) : (
                  <span className="text-red-600">{formatCurrency(-diffDesp)} acima</span>
                )
              ) : (
                <span className="text-indigo-500">sem plano</span>
              )}
            </p>
          </div>
          <div>
            <p className="text-[11px] text-indigo-600 uppercase">Investidos</p>
            <p className="text-[14px] font-semibold text-blue-600">
              {formatCurrency(totalInvestido)}
            </p>
            <p className="text-[9px] font-medium">
              {totalPlanejadoInv > 0 ? (
                investidoOk ? (
                  <span className="text-emerald-600">{labelInvestidos}</span>
                ) : (
                  <span className="text-amber-600">{labelInvestidos}</span>
                )
              ) : (
                <span className="text-indigo-500">{labelInvestidos}</span>
              )}
            </p>
          </div>
        </div>
      </div>
    );
  }

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
