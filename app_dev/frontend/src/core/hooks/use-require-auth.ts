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

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/core/utils/api-client';

export function useRequireAuth(): boolean {
  const router = useRouter();
  const [isAuth, setIsAuth] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Verificar autenticação
    const checkAuth = () => {
      if (!isAuthenticated()) {
        console.warn('🚨 [AUTH] Usuário não autenticado - Redirecionando para login');
        router.push('/auth/login');
        return false;
      }
      
      setIsAuth(true);
      setIsChecking(false);
      return true;
    };

    checkAuth();
  }, [router]);

  // Durante verificação, retorna false
  return isAuth;
}

/**
 * Hook alternativo que retorna loading state
 * Útil para mostrar spinner durante verificação
 */
export function useAuth() {
  const router = useRouter();
  const [isAuth, setIsAuth] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = () => {
      if (!isAuthenticated()) {
        console.warn('🚨 [AUTH] Usuário não autenticado - Redirecionando para login');
        router.push('/auth/login');
        setIsAuth(false);
      } else {
        setIsAuth(true);
      }
      
      setIsLoading(false);
    };

    checkAuth();
  }, [router]);

  return { isAuth, isLoading };
}
