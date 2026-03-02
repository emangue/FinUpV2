'use client';

/**
 * PlanoWizard — frame do construtor de plano em 4 etapas.
 * Etapas: 1.Renda | 2.Gastos | 3.Sazonais | 4.Aporte
 * Fase 3: Etapa 4 com aporte real + persist via putPerfil.
 */

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { MobileHeader } from '@/components/mobile/mobile-header';
import { Button } from '@/components/ui/button';
import { mobileTypography } from '@/config/mobile-typography';
import { getPerfil, putPerfil, postRenda } from '../api';
import type { PlanoWizardState } from '../types/plano-wizard-state';

const STEPS = [
  { id: 1, label: 'Renda', short: '1' },
  { id: 2, label: 'Gastos', short: '2' },
  { id: 3, label: 'Sazonais', short: '3' },
  { id: 4, label: 'Aporte', short: '4' },
] as const;

interface PlanoWizardProps {
  state: PlanoWizardState;
  onStateChange: React.Dispatch<React.SetStateAction<PlanoWizardState>>;
  onFinish?: () => void;
}

export function PlanoWizard({ state, onStateChange, onFinish }: PlanoWizardProps) {
  const [step, setStep] = React.useState(1);
  const [aporteLoaded, setAporteLoaded] = React.useState(false);
  const [rendaLoaded, setRendaLoaded] = React.useState(false);
  const router = useRouter();

  // Carregar renda do perfil quando chegar na etapa 1
  React.useEffect(() => {
    if (step !== 1 || rendaLoaded) return
    setRendaLoaded(true)
    getPerfil()
      .then((p) => {
        if (p.renda_mensal_liquida != null && p.renda_mensal_liquida > 0) {
          onStateChange((s) => ({ ...s, renda_mensal: p.renda_mensal_liquida! }))
        }
      })
      .catch(() => {})
  }, [step, rendaLoaded])

  // Carregar aporte do perfil quando chegar na etapa 4
  React.useEffect(() => {
    if (step !== 4 || aporteLoaded) return
    setAporteLoaded(true)
    getPerfil()
      .then((p) => {
        if (p.aporte_planejado != null && p.aporte_planejado > 0) {
          onStateChange((s) => ({ ...s, aporte: p.aporte_planejado! }))
        }
      })
      .catch(() => {})
  }, [step, aporteLoaded])

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
        // não bloqueia
      }
    }
    if (step < 4) {
      setStep(step + 1);
    } else {
      if (state.aporte > 0) {
        try {
          await putPerfil({ aporte_planejado: state.aporte });
        } catch {
          // não bloqueia
        }
      }
      if (onFinish) onFinish();
    }
  };

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

      {/* Step content */}
      <div className="flex-1 overflow-y-auto p-5">
        <div className="rounded-2xl bg-white p-6 border border-gray-200 shadow-sm">
          <h2 className={mobileTypography.sectionTitle.tailwind + ' mb-2'}>
            Etapa {step}: {currentStep.label}
          </h2>
          {step === 1 ? (
            <div className="space-y-4">
              <p className={mobileTypography.frequency.tailwind}>
                Qual sua renda mensal líquida?
              </p>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Renda (R$)</label>
                <input
                  type="number"
                  min={0}
                  step={100}
                  value={state.renda_mensal || ''}
                  onChange={(e) => {
                    const v = parseFloat(e.target.value) || 0
                    onStateChange({ ...state, renda_mensal: v })
                  }}
                  placeholder="0"
                  className="w-full rounded-xl border border-gray-200 px-4 py-3 text-lg font-semibold"
                />
              </div>
            </div>
          ) : step === 3 ? (
            <div className="space-y-4">
              <p className={mobileTypography.frequency.tailwind}>
                Gastos sazonais (IPVA, IPTU, 13º, etc.) serão adicionados na próxima versão.
              </p>
              <p className="text-sm text-gray-500">
                Por ora, use a tela de metas para ajustar seus gastos por categoria.
              </p>
            </div>
          ) : step === 4 ? (
            <div className="space-y-4">
              <p className={mobileTypography.frequency.tailwind}>
                Quanto você planeja guardar por mês para investimentos?
              </p>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Aporte mensal (R$)</label>
                <input
                  type="number"
                  min={0}
                  step={100}
                  value={state.aporte || ''}
                  onChange={(e) => {
                    const v = parseFloat(e.target.value) || 0
                    onStateChange({ ...state, aporte: v })
                  }}
                  placeholder="0"
                  className="w-full rounded-xl border border-gray-200 px-4 py-3 text-lg font-semibold"
                />
              </div>
            </div>
          ) : step === 2 ? (
            <div className="space-y-4">
              <p className={mobileTypography.frequency.tailwind}>
                Defina suas metas de gasto por categoria.
              </p>
              <p className="text-sm text-gray-500">
                Use a tela &quot;Gerenciar metas por grupo&quot; no Plano para ajustar cada categoria. Avance para continuar.
              </p>
            </div>
          ) : null}
        </div>
      </div>

      {/* Footer: Prev / Next */}
      <div className="p-5 bg-white border-t border-gray-200 flex gap-3">
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
        >
          {isLastStep ? 'Concluir' : 'Próximo'}
          <ChevronRight className="w-5 h-5 ml-1" />
        </Button>
      </div>
    </div>
  );
}
