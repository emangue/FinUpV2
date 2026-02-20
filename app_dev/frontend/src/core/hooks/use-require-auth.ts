/**
 * Hook para proteger rotas que requerem autenticação
 * 
 * Redireciona automaticamente para /auth/login se usuário não estiver autenticado
 * 
 * @returns true se autenticado, false se redirecionando
 * 
 * @example
 * ```typescript
 * export default function ProtectedPage() {
 *   const isAuth = useRequireAuth()
 *   
 *   if (!isAuth) {
 *     return <div>Redirecionando...</div>
 *   }
 *   
 *   return <div>Conteúdo protegido</div>
 * }
 * ```
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export function useRequireAuth(): boolean {
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();

  useEffect(() => {
    if (loading) return;
    if (!isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, loading, router]);

  return isAuthenticated && !loading;
}

/** Hook alternativo com loading state */
export function useRequireAuthWithLoading() {
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();

  useEffect(() => {
    if (loading) return;
    if (!isAuthenticated) router.push('/auth/login');
  }, [isAuthenticated, loading, router]);

  return { isAuth: isAuthenticated, isLoading: loading };
}
