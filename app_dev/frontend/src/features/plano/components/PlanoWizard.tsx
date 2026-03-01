'use client';

/**
 * PlanoWizard — frame do construtor de plano em 4 etapas.
 * Etapas: 1.Renda | 2.Gastos | 3.Sazonais | 4.Recibo do Ano
 * Fases 8-11: Etapa 2 com grupos+media, Etapa 3 sazonais, Etapa 4 projeção longa.
 */

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { ChevronLeft, ChevronRight, Plus, Trash2 } from 'lucide-react';
import { MobileHeader } from '@/components/mobile/mobile-header';
import { Button } from '@/components/ui/button';
import { mobileTypography } from '@/config/mobile-typography';
import {
  getPerfil,
  putPerfil,
  postRenda,
  getGruposMedia3Meses,
  putOrcamentoBulk,
  getExpectativas,
  postExpectativa,
  deleteExpectativa,
  getProjecaoLonga,
} from '../api';
import { TabelaReciboAnual } from './TabelaReciboAnual';
import { ProjecaoChart } from './ProjecaoChart';
import type { PlanoWizardState } from '../types/plano-wizard-state';

const STEPS = [
  { id: 1, label: 'Renda', short: '1' },
  { id: 2, label: 'Gastos', short: '2' },
  { id: 3, label: 'Sazonais', short: '3' },
  { id: 4, label: 'Recibo do Ano', short: '4' },
] as const;

interface PlanoWizardProps {
  state: PlanoWizardState;
  onStateChange: React.Dispatch<React.SetStateAction<PlanoWizardState>>;
  onFinish?: () => void;
}

const RECORRENCIAS = [
  { value: 'unico', label: 'Único' },
  { value: 'bimestral', label: 'Bimestral' },
  { value: 'trimestral', label: 'Trimestral' },
  { value: 'semestral', label: 'Semestral' },
  { value: 'anual', label: 'Anual' },
] as const;

export function PlanoWizard({ state, onStateChange, onFinish }: PlanoWizardProps) {
  const [step, setStep] = React.useState(1);
  const [aporteLoaded, setAporteLoaded] = React.useState(false);
  const [rendaLoaded, setRendaLoaded] = React.useState(false);
  const [grupos, setGrupos] = React.useState<{ grupo: string; valor_planejado: number; valor_medio_3_meses: number }[]>([]);
  const [sazonais, setSazonais] = React.useState<{ id: number; descricao: string | null; valor: number; mes_referencia: string }[]>([]);
  const [extraRendas, setExtraRendas] = React.useState<{ id: number; descricao: string | null; valor: number; mes_referencia: string }[]>([]);
  const [projecaoLonga, setProjecaoLonga] = React.useState<{ patrimonio_final_real: number; meses: number } | null>(null);
  const [novoExtraRenda, setNovoExtraRenda] = React.useState<{
    descricao: string;
    valor: number;
    mes: number;
    recorrencia: 'unico' | 'bimestral' | 'trimestral' | 'semestral' | 'anual';
  }>({ descricao: '', valor: 0, mes: 1, recorrencia: 'anual' });
  const [novoSazonal, setNovoSazonal] = React.useState<{
    descricao: string;
    valor: number;
    mes: number;
    recorrencia: 'unico' | 'bimestral' | 'trimestral' | 'semestral' | 'anual';
  }>({ descricao: '', valor: 0, mes: 1, recorrencia: 'anual' });
  const router = useRouter();
  const ano = new Date().getFullYear();
  const mes = new Date().getMonth() + 1;

  React.useEffect(() => {
    if (step !== 1 || rendaLoaded) return;
    setRendaLoaded(true);
    getPerfil()
      .then((p) => {
        if (p.renda_mensal_liquida != null && p.renda_mensal_liquida > 0) {
          onStateChange((s) => ({ ...s, renda_mensal: p.renda_mensal_liquida! }));
        }
      })
      .catch(() => {});
  }, [step, rendaLoaded]);

  React.useEffect(() => {
    if (step !== 1) return;
    getExpectativas()
      .then((list) => setExtraRendas(list.filter((e) => e.tipo_expectativa === 'renda_plano')))
      .catch(() => setExtraRendas([]));
  }, [step]);

  React.useEffect(() => {
    if (step !== 2) return;
    getGruposMedia3Meses(ano, mes)
      .then(setGrupos)
      .catch(() => setGrupos([]));
  }, [step, ano, mes]);

  React.useEffect(() => {
    if (step !== 3) return;
    getExpectativas()
      .then((list) => setSazonais(list.filter((e) => e.tipo_expectativa === 'sazonal_plano')))
      .catch(() => setSazonais([]));
  }, [step]);

  React.useEffect(() => {
    if (step !== 4 || aporteLoaded) return;
    setAporteLoaded(true);
    getPerfil()
      .then((p) => {
        if (p.aporte_planejado != null && p.aporte_planejado > 0) {
          onStateChange((s) => ({ ...s, aporte: p.aporte_planejado! }));
        }
      })
      .catch(() => {});
    getProjecaoLonga()
      .then((r) => setProjecaoLonga({ patrimonio_final_real: r.patrimonio_final_real, meses: r.meses }))
      .catch(() => setProjecaoLonga(null));
  }, [step, aporteLoaded]);

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    } else {
      router.back();
    }
  };

  const handleNext = async () => {
    if (step === 1 && state.renda_mensal > 0) {
      try {
        await postRenda(state.renda_mensal);
      } catch {
        /* não bloqueia */
      }
    }
    if (step === 2 && grupos.length > 0) {
      try {
        const mesRef = `${ano}-${String(mes).padStart(2, '0')}`;
        await putOrcamentoBulk(
          mesRef,
          grupos.map((g) => ({ grupo: g.grupo, valor_planejado: g.valor_planejado }))
        );
      } catch {
        /* não bloqueia */
      }
    }
    if (step < 4) {
      setStep(step + 1);
    } else {
      if (state.aporte > 0) {
        try {
          await putPerfil({ aporte_planejado: state.aporte });
        } catch {
          /* não bloqueia */
        }
      }
      if (onFinish) onFinish();
    }
  };

  const handleAddSazonal = async () => {
    if (!novoSazonal.descricao || novoSazonal.valor <= 0) return;
    try {
      const mesRef = `${ano}-${String(novoSazonal.mes).padStart(2, '0')}`;
      await postExpectativa({
        descricao: novoSazonal.descricao,
        valor: novoSazonal.valor,
        mes_referencia: mesRef,
        tipo_lancamento: 'debito',
        tipo_expectativa: 'sazonal_plano',
        recorrencia: novoSazonal.recorrencia,
      });
      setNovoSazonal({ descricao: '', valor: 0, mes: 1, recorrencia: 'anual' });
      const list = await getExpectativas();
      setSazonais(list.filter((e) => e.tipo_expectativa === 'sazonal_plano'));
    } catch {
      /* ignore */
    }
  };

  const handleRemoveSazonal = async (id: number) => {
    try {
      await deleteExpectativa(id);
      setSazonais((prev) => prev.filter((e) => e.id !== id));
    } catch {
      /* ignore */
    }
  };

  const handleAddExtraRenda = async () => {
    if (!novoExtraRenda.descricao || novoExtraRenda.valor <= 0) return;
    try {
      const mesRef = `${ano}-${String(novoExtraRenda.mes).padStart(2, '0')}`;
      await postExpectativa({
        descricao: novoExtraRenda.descricao,
        valor: novoExtraRenda.valor,
        mes_referencia: mesRef,
        tipo_lancamento: 'credito',
        tipo_expectativa: 'renda_plano',
        recorrencia: novoExtraRenda.recorrencia,
      });
      setNovoExtraRenda({ descricao: '', valor: 0, mes: 1, recorrencia: 'anual' });
      const list = await getExpectativas();
      setExtraRendas(list.filter((e) => e.tipo_expectativa === 'renda_plano'));
    } catch {
      /* ignore */
    }
  };

  const handleRemoveExtraRenda = async (id: number) => {
    try {
      await deleteExpectativa(id);
      setExtraRendas((prev) => prev.filter((e) => e.id !== id));
    } catch {
      /* ignore */
    }
  };

  const updateGrupoMeta = (grupo: string, valor: number) => {
    setGrupos((prev) =>
      prev.map((g) => (g.grupo === grupo ? { ...g, valor_planejado: valor } : g))
    );
  };

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 0 }).format(v);

  const usarMediaComoMeta = () => {
    setGrupos((prev) =>
      prev.map((g) => ({ ...g, valor_planejado: g.valor_medio_3_meses }))
    );
  };

  const isStepValid =
    step === 1 ? (state.renda_mensal ?? 0) > 0 :
    step === 2 ? true :
    step === 3 ? true :
    step === 4 ? true : true;

  const currentStep = STEPS.find((s) => s.id === step)!;
  const isLastStep = step === 4;

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <MobileHeader
        title={`Construir plano — ${currentStep.label}`}
        leftAction="back"
        onBack={handleBack}
      />

      {/* Steps indicator */}
      <div className="flex items-center justify-center gap-2 py-4 px-4 bg-white border-b border-gray-200">
        {STEPS.map((s) => (
          <React.Fragment key={s.id}>
            <div
              className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-semibold ${
                s.id === step
                  ? 'bg-primary text-white'
                  : s.id < step
                    ? 'bg-primary/20 text-primary'
                    : 'bg-gray-200 text-gray-500'
              }`}
              aria-current={s.id === step ? 'step' : undefined}
            >
              {s.short}
            </div>
            {s.id < 4 && (
              <div className="w-4 h-0.5 bg-gray-200" aria-hidden />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Step content — pb para não ficar atrás do footer fixo */}
      <div className="flex-1 overflow-y-auto p-5 pb-28">
        <div className="rounded-2xl bg-white p-6 border border-gray-200 shadow-sm">
          <h2 className={mobileTypography.sectionTitle.tailwind + ' mb-2'}>
            Etapa {step}: {currentStep.label}
          </h2>
          {step === 1 ? (
            <div className="space-y-6">
              <div>
                <p className={mobileTypography.frequency.tailwind}>
                  Qual sua renda mensal líquida?
                </p>
                <div className="mt-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Renda (R$)</label>
                  <input
                    type="number"
                    min={0}
                    step={100}
                    value={state.renda_mensal || ''}
                    onChange={(e) => {
                      const v = parseFloat(e.target.value) || 0;
                      onStateChange({ ...state, renda_mensal: v });
                    }}
                    placeholder="0"
                    className="w-full rounded-xl border border-gray-200 px-4 py-3 text-lg font-semibold"
                  />
                </div>
              </div>
              <div>
                <p className={mobileTypography.frequency.tailwind}>
                  Receitas extraordinárias (13º, bônus, etc.)
                </p>
                <div className="space-y-2 mt-2">
                  {extraRendas.map((e) => (
                    <div key={e.id} className="flex items-center justify-between py-2 px-3 bg-green-50 rounded-xl">
                      <div>
                        <p className="font-medium">{e.descricao || '(sem descrição)'}</p>
                        <p className="text-sm text-gray-600">{formatCurrency(e.valor)} · {e.mes_referencia}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveExtraRenda(e.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                        aria-label="Excluir"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
                <div className="border border-gray-200 rounded-xl p-4 space-y-2 mt-2">
                  <input
                    type="text"
                    placeholder="Descrição (ex: 13º salário)"
                    value={novoExtraRenda.descricao}
                    onChange={(e) => setNovoExtraRenda((n) => ({ ...n, descricao: e.target.value }))}
                    className="w-full rounded-lg border border-gray-200 px-3 py-2"
                  />
                  <div className="flex gap-2 flex-wrap">
                    <input
                      type="number"
                      min={0}
                      step={50}
                      placeholder="Valor"
                      value={novoExtraRenda.valor || ''}
                      onChange={(e) => setNovoExtraRenda((n) => ({ ...n, valor: parseFloat(e.target.value) || 0 }))}
                      className="flex-1 min-w-[80px] rounded-lg border border-gray-200 px-3 py-2"
                    />
                    <select
                      value={novoExtraRenda.mes}
                      onChange={(e) => setNovoExtraRenda((n) => ({ ...n, mes: Number(e.target.value) }))}
                      className="rounded-lg border border-gray-200 px-3 py-2"
                    >
                      {[1,2,3,4,5,6,7,8,9,10,11,12].map((m) => (
                        <option key={m} value={m}>{['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][m-1]}</option>
                      ))}
                    </select>
                    <select
                      value={novoExtraRenda.recorrencia}
                      onChange={(e) => setNovoExtraRenda((n) => ({ ...n, recorrencia: e.target.value as typeof novoExtraRenda.recorrencia }))}
                      className="rounded-lg border border-gray-200 px-3 py-2"
                    >
                      {RECORRENCIAS.map((r) => (
                        <option key={r.value} value={r.value}>{r.label}</option>
                      ))}
                    </select>
                  </div>
                  <Button type="button" variant="outline" size="sm" onClick={handleAddExtraRenda} className="w-full">
                    <Plus className="w-4 h-4 mr-1" />
                    Adicionar
                  </Button>
                </div>
              </div>
            </div>
          ) : step === 2 ? (
            <div className="space-y-4">
              <p className={mobileTypography.frequency.tailwind}>
                Ajuste suas metas de gasto por categoria. Média 3 meses como referência.
              </p>
              {grupos.length > 0 && (
                <Button type="button" variant="outline" size="sm" onClick={usarMediaComoMeta} className="w-full">
                  Usar média como meta
                </Button>
              )}
              {grupos.length === 0 ? (
                <p className="text-sm text-gray-500">
                  Nenhum grupo com meta neste mês. Use &quot;Gerenciar metas por grupo&quot; no Plano primeiro.
                </p>
              ) : (
                <div className="space-y-3">
                  {grupos.map((g) => (
                    <div key={g.grupo} className="flex items-center justify-between gap-2 py-2 border-b border-gray-100 last:border-0">
                      <div>
                        <p className="font-medium text-gray-900">{g.grupo}</p>
                        <p className="text-xs text-gray-500">Média 3 meses: {formatCurrency(g.valor_medio_3_meses)}</p>
                      </div>
                      <input
                        type="number"
                        min={0}
                        step={50}
                        value={g.valor_planejado}
                        onChange={(e) => updateGrupoMeta(g.grupo, parseFloat(e.target.value) || 0)}
                        className="w-24 rounded-lg border border-gray-200 px-2 py-1.5 text-right"
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : step === 3 ? (
            <div className="space-y-4">
              <p className={mobileTypography.frequency.tailwind}>
                Gastos sazonais (IPVA, IPTU, 13º, etc.)
              </p>
              <div className="space-y-2">
                {sazonais.map((s) => (
                  <div key={s.id} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-xl">
                    <div>
                      <p className="font-medium">{s.descricao || '(sem descrição)'}</p>
                      <p className="text-sm text-gray-600">{formatCurrency(s.valor)} · {s.mes_referencia}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveSazonal(s.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                      aria-label="Excluir"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
              <div className="border border-gray-200 rounded-xl p-4 space-y-2">
                <input
                  type="text"
                  placeholder="Descrição (ex: IPVA)"
                  value={novoSazonal.descricao}
                  onChange={(e) => setNovoSazonal((n) => ({ ...n, descricao: e.target.value }))}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2"
                />
                <div className="flex gap-2">
                  <input
                    type="number"
                    min={0}
                    step={50}
                    placeholder="Valor"
                    value={novoSazonal.valor || ''}
                    onChange={(e) => setNovoSazonal((n) => ({ ...n, valor: parseFloat(e.target.value) || 0 }))}
                    className="flex-1 rounded-lg border border-gray-200 px-3 py-2"
                  />
                  <select
                    value={novoSazonal.mes}
                    onChange={(e) => setNovoSazonal((n) => ({ ...n, mes: Number(e.target.value) }))}
                    className="rounded-lg border border-gray-200 px-3 py-2"
                  >
                    {[1,2,3,4,5,6,7,8,9,10,11,12].map((m) => (
                      <option key={m} value={m}>{['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][m-1]}</option>
                    ))}
                  </select>
                  <select
                    value={novoSazonal.recorrencia}
                    onChange={(e) => setNovoSazonal((n) => ({ ...n, recorrencia: e.target.value as typeof novoSazonal.recorrencia }))}
                    className="rounded-lg border border-gray-200 px-3 py-2"
                  >
                    {RECORRENCIAS.map((r) => (
                      <option key={r.value} value={r.value}>{r.label}</option>
                    ))}
                  </select>
                </div>
                <Button type="button" variant="outline" size="sm" onClick={handleAddSazonal} className="w-full">
                  <Plus className="w-4 h-4 mr-1" />
                  Adicionar
                </Button>
              </div>
            </div>
          ) : step === 4 ? (
            <div className="space-y-4">
              <p className={mobileTypography.frequency.tailwind}>
                Recibo do ano e projeção até aposentadoria.
              </p>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Aporte mensal (R$)</label>
                <input
                  type="number"
                  min={0}
                  step={100}
                  value={state.aporte || ''}
                  onChange={(e) => {
                    const v = parseFloat(e.target.value) || 0;
                    onStateChange({ ...state, aporte: v });
                  }}
                  placeholder="0"
                  className="w-full rounded-xl border border-gray-200 px-4 py-3 text-lg font-semibold mb-4"
                />
              </div>
              <TabelaReciboAnual ano={ano} />
              <ProjecaoChart ano={ano} />
              {projecaoLonga && (
                <div className="rounded-xl bg-indigo-50 border border-indigo-100 p-4">
                  <p className="text-sm font-medium text-indigo-900">
                    Projeção até aposentadoria: {formatCurrency(projecaoLonga.patrimonio_final_real)} ({projecaoLonga.meses} meses)
                  </p>
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>

      {/* Footer: Prev / Next — fixo acima da bottom-nav (h-20) */}
      <div className="fixed bottom-20 left-0 right-0 z-40 p-5 bg-white border-t border-gray-200 flex gap-3">
        <Button
          variant="outline"
          className="flex-1"
          onClick={handleBack}
        >
          <ChevronLeft className="w-5 h-5 mr-1" />
          {step === 1 ? 'Voltar' : 'Anterior'}
        </Button>
        <Button
          className="flex-1"
          onClick={handleNext}
          disabled={step === 1 && !isStepValid}
        >
          {isLastStep ? 'Concluir' : 'Próximo'}
          <ChevronRight className="w-5 h-5 ml-1" />
        </Button>
      </div>
    </div>
  );
}
