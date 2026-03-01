'use client';

/**
 * Perfil Financeiro — redireciona para /mobile/plano
 * O Plano é o hub único (restrição, cashflow, projeção, editar plano).
 */
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function PerfilFinanceiroPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/mobile/plano');
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="animate-spin h-8 w-8 border-2 border-indigo-600 border-t-transparent rounded-full" />
    </div>
  );
}
