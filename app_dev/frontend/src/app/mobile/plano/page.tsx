'use client';

/**
 * Hub do Plano Financeiro — /mobile/plano
 * Agrega: resumo, orçamento por grupo, nudge anos perdidos, CTA Editar plano
 */
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Target, Pencil } from 'lucide-react';
import { MobileHeader } from '@/components/mobile/mobile-header';
import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker';
import { PlanoResumoCard } from '@/features/plano/components/PlanoResumoCard';
import { OrcamentoCategorias } from '@/features/plano/components/OrcamentoCategorias';
import { AnosPerdidasCard } from '@/features/plano/components/AnosPerdidasCard';
import { TabelaReciboAnual } from '@/features/plano/components/TabelaReciboAnual';
import { ProjecaoChart } from '@/features/plano/components/ProjecaoChart';
import { EmptyState } from '@/components/empty-state';
import { useRequireAuth } from '@/core/hooks/use-require-auth';
import { getResumoPlano, getOrcamento } from '@/features/plano/api';

export default function PlanoHubPage() {
  const router = useRouter();
  const isAuth = useRequireAuth();
  const [selectedMonth, setSelectedMonth] = useState<Date>(new Date());
  const [isEmpty, setIsEmpty] = useState<boolean | null>(null);
  const [resumoPlano, setResumoPlano] = useState<{ renda: number | null; total_budget: number; disponivel_real: number | null } | null>(null);

  const year = selectedMonth.getFullYear();
  const month = selectedMonth.getMonth() + 1;

  useEffect(() => {
    Promise.all([getResumoPlano(year, month), getOrcamento(year, month)])
      .then(([resumo, orcamento]) => {
        const semRenda = resumo?.renda == null;
        const semMetas = (resumo?.total_budget ?? 0) === 0 && orcamento.length === 0;
        setIsEmpty(semRenda && semMetas);
        setResumoPlano(resumo ?? null);
      })
      .catch(() => setIsEmpty(false));
  }, [year, month]);

  if (!isAuth) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MobileHeader title="Plano" leftAction="back" onBack={() => router.back()} />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4" />
            <p className="text-gray-600">Verificando autenticação...</p>
          </div>
        </div>
      </div>
    );
  }

  if (isEmpty === null) {
    return (
      <div className="min-h-screen bg-gray-50 pb-24">
        <MobileHeader title="Plano" leftAction="back" onBack={() => router.back()} />
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin h-10 w-10 border-2 border-indigo-600 border-t-transparent rounded-full" />
        </div>
      </div>
    );
  }

  if (isEmpty === true) {
    return (
      <div className="min-h-screen bg-gray-50 pb-24">
        <MobileHeader title="Plano" leftAction="back" onBack={() => router.back()} />
        <div className="p-5">
          <EmptyState
            icon="📋"
            title="Seu plano começa com seus gastos reais"
            description="Suba seu extrato ou crie metas manualmente para acompanhar seu orçamento."
            ctaLabel="Construir plano"
            ctaHref="/mobile/construir-plano"
            ctaSecondaryLabel="Subir extrato primeiro"
            ctaSecondaryHref="/mobile/upload"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Fixo no topo (igual dashboard) */}
      <div className="sticky top-0 z-20 bg-white border-b border-gray-200 shrink-0">
        <MobileHeader
          title="Plano"
          leftAction="back"
          onBack={() => router.back()}
        />
        <div className="px-5 pb-3">
          <p className="text-[13px] text-gray-500 mb-1">Orçamento em:</p>
          <MonthScrollPicker
            selectedMonth={selectedMonth}
            onMonthChange={setSelectedMonth}
          />
        </div>
      </div>

      {/* Conteúdo rolável */}
      <div className="flex-1 overflow-y-auto pb-24">
        <div className="p-5 space-y-4">
          <Link
            href="/mobile/construir-plano"
            className="flex items-center justify-between gap-3 bg-white rounded-2xl p-4 shadow-sm border border-gray-100 hover:bg-gray-50"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                <Pencil className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <p className="font-semibold text-black">Editar plano</p>
                <p className="text-[13px] text-gray-500">
                  Renda, metas, sazonais e aporte
                </p>
              </div>
            </div>
            <span className="text-gray-400">→</span>
          </Link>

          <PlanoResumoCard year={year} month={month} resumoExterno={resumoPlano} />
          <AnosPerdidasCard ano={year} mes={month} />

          <TabelaReciboAnual ano={year} />
          <ProjecaoChart ano={year} />

          <OrcamentoCategorias ano={year} mes={month} />

          <Link
            href="/mobile/budget/manage"
            className="flex items-center justify-between gap-3 bg-white rounded-2xl p-4 shadow-sm border border-gray-100 hover:bg-gray-50"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                <Target className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <p className="font-semibold text-black">Gerenciar metas por grupo</p>
                <p className="text-[13px] text-gray-500">
                  Defina quanto planeja gastar em cada categoria
                </p>
              </div>
            </div>
            <span className="text-gray-400">→</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
