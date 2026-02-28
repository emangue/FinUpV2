'use client';

/**
 * Construir Plano — wizard de 4 etapas para edição do plano financeiro.
 * Fase 0: shell pronto. Qualquer edição (renda, metas, sazonais, aporte) passa por aqui.
 *
 * Regra: não criar fluxos paralelos de edição.
 */

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { PlanoWizard } from '@/features/plano/components/PlanoWizard';
import {
  initialPlanoWizardState,
  type PlanoWizardState,
} from '@/features/plano/types/plano-wizard-state';

export default function ConstruirPlanoPage() {
  const router = useRouter();
  const [state, setState] = React.useState<PlanoWizardState>(initialPlanoWizardState);

  const handleFinish = () => {
    // Fase 5: persistir e redirecionar. Por ora, volta ao plano.
    router.push('/mobile/budget');
  };

  return (
    <PlanoWizard
      state={state}
      onStateChange={setState}
      onFinish={handleFinish}
    />
  );
}
