'use client';

/**
 * F.01: Redireciona para /mobile/onboarding/welcome se onboarding incompleto.
 * Respeita "Pular" (localStorage) e onboarding_completo da API.
 */

import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

const ONBOARDING_PULADO_KEY = 'onboarding_pulado';
const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export function OnboardingGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!pathname?.startsWith('/mobile')) {
      setChecking(false);
      return;
    }
    if (pathname.startsWith('/mobile/onboarding')) {
      setChecking(false);
      return;
    }
    if (!isAuthenticated || loading) {
      setChecking(false);
      return;
    }

    const pulado = localStorage.getItem(ONBOARDING_PULADO_KEY) === 'true';
    if (pulado) {
      setChecking(false);
      return;
    }

    fetch(`${apiUrl}/api/v1/onboarding/progress`, { credentials: 'include' })
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data?.onboarding_completo) {
          setChecking(false);
          return;
        }
        router.replace('/mobile/onboarding/welcome');
      })
      .catch(() => setChecking(false))
      .finally(() => setChecking(false));
  }, [pathname, isAuthenticated, loading, router]);

  if (checking) {
    return (
      <div className="min-h-dvh flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Carregando...</div>
      </div>
    );
  }

  return <>{children}</>;
}
