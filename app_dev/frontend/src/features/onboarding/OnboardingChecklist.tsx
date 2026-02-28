'use client';

/**
 * F.05: Checklist de progresso no Início — some quando onboarding_completo
 */

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

const ITEMS = [
  { key: 'conta_criada', label: 'Criou sua conta', href: null },
  { key: 'primeiro_upload', label: 'Suba seu primeiro extrato', href: '/mobile/upload' },
  { key: 'plano_criado', label: 'Crie seu Plano Financeiro', href: '/mobile/budget' },
  { key: 'investimento_adicionado', label: 'Adicione um investimento', href: '/mobile/carteira' },
] as const;

interface Progress {
  conta_criada: boolean;
  primeiro_upload: boolean;
  plano_criado: boolean;
  investimento_adicionado: boolean;
  onboarding_completo: boolean;
}

export function OnboardingChecklist() {
  const [data, setData] = useState<Progress | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch(`${apiUrl}/api/v1/onboarding/progress`, { credentials: 'include' })
      .then((r) => (r.ok ? r.json() : null))
      .then(setData)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading || !data) return null;
  if (data.onboarding_completo) return null;

  const done = [data.conta_criada, data.primeiro_upload, data.plano_criado, data.investimento_adicionado].filter(
    Boolean
  ).length;

  return (
    <div className="rounded-xl border border-primary/20 bg-primary/5 p-4 mb-4">
      <p className="text-sm font-medium mb-3">
        Seus primeiros passos · {done}/4 concluídos
      </p>
      {ITEMS.map((item) => (
        <div key={item.key} className="flex items-center gap-3 py-2" role="listitem">
          <span className="shrink-0">
            {data[item.key] ? '✅' : '⬜'}
          </span>
          <span
            className={cn(
              'text-sm flex-1',
              data[item.key] && 'text-muted-foreground line-through'
            )}
          >
            {item.label}
          </span>
          {!data[item.key] && item.href && (
            <Link href={item.href}>
              <Button size="sm" variant="outline">
                → Fazer
              </Button>
            </Link>
          )}
        </div>
      ))}
    </div>
  );
}
