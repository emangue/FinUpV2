'use client';

/**
 * F.06: Banner quando usuário está em modo demo — CTA "Usar meus dados →"
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Sparkles } from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export function DemoModeBanner() {
  const router = useRouter();
  const [data, setData] = useState<{ tem_demo?: boolean } | null>(null);

  useEffect(() => {
    // P1: sessionStorage (não localStorage) — limpa ao trocar de conta/encerrar sessão
    if (typeof window !== 'undefined' && sessionStorage.getItem('sem_demo') === 'true') return;

    fetch(`${apiUrl}/api/v1/onboarding/progress`, { credentials: 'include' })
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d && !d.tem_demo) {
          // Cachear ausência de modo demo nesta sessão
          sessionStorage.setItem('sem_demo', 'true');
        }
        setData(d);
      });
  }, []);

  if (!data?.tem_demo) return null;

  const handleUsarMeusDados = async () => {
    try {
      await fetch(`${apiUrl}/api/v1/onboarding/modo-demo`, {
        method: 'DELETE',
        credentials: 'include',
      });
      router.push('/mobile/upload');
    } catch {
      router.push('/mobile/upload');
    }
  };

  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 mb-4 flex items-center justify-between gap-3">
      <div className="flex items-center gap-2">
        <Sparkles className="w-5 h-5 text-amber-600" />
        <span className="text-sm font-medium">Modo Exploração</span>
      </div>
      <Button size="sm" onClick={handleUsarMeusDados}>
        Usar meus dados →
      </Button>
    </div>
  );
}
