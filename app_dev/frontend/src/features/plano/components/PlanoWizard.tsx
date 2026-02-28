'use client';

/**
 * PlanoWizard — frame do construtor de plano em 4 etapas.
 * Fase 0: shell com navegação entre steps. Conteúdo real será preenchido na Fase 5.
 *
 * Etapas: 1.Renda | 2.Gastos | 3.Sazonais | 4.Aporte
 */

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { MobileHeader } from '@/components/mobile/mobile-header';
import { Button } from '@/components/ui/button';
import { mobileTypography } from '@/config/mobile-typography';
import type { PlanoWizardState } from '../types/plano-wizard-state';

const STEPS = [
  { id: 1, label: 'Renda', short: '1' },
  { id: 2, label: 'Gastos', short: '2' },
  { id: 3, label: 'Sazonais', short: '3' },
  { id: 4, label: 'Aporte', short: '4' },
] as const;

interface PlanoWizardProps {
  state: PlanoWizardState;
  onStateChange: (state: PlanoWizardState) => void;
  onFinish?: () => void;
}

export function PlanoWizard({ state, onStateChange, onFinish }: PlanoWizardProps) {
  const [step, setStep] = React.useState(1);
  const router = useRouter();

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    } else {
      router.back();
    }
  };

  const handleNext = () => {
    if (step < 4) {
      setStep(step + 1);
    } else if (onFinish) {
      onFinish();
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

      {/* Step content (placeholder) */}
      <div className="flex-1 overflow-y-auto p-5">
        <div className="rounded-2xl bg-white p-6 border border-gray-200 shadow-sm">
          <h2 className={mobileTypography.sectionTitle.tailwind + ' mb-2'}>
            Etapa {step}: {currentStep.label}
          </h2>
          <p className={mobileTypography.frequency.tailwind}>
            Conteúdo será preenchido na Fase 5. Por ora, este é o frame do wizard.
          </p>
          <div className="mt-4 p-4 bg-gray-50 rounded-xl text-sm text-gray-600">
            <p>Estado atual (preview):</p>
            <pre className="mt-2 text-xs overflow-x-auto">
              {JSON.stringify(
                {
                  renda_mensal: state.renda_mensal,
                  gastos_count: state.gastos_por_grupo.length,
                  sazonais_count: state.sazonais.length,
                  aporte: state.aporte,
                },
                null,
                2
              )}
            </pre>
          </div>
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
