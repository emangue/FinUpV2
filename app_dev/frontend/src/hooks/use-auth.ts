'use client';

/**
 * Re-export do AuthContext para compatibilidade
 * Este hook agora usa o AuthContext oficial em vez do bypass
 */

import { useAuth as useAuthContext } from '@/contexts/AuthContext';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect } from 'react';

export function useAuth(redirectIfNotAuth = true) {
  const router = useRouter();
  const pathname = usePathname();
  const authContext = useAuthContext();

  // Redirect para login se não autenticado (apenas se solicitado)
  useEffect(() => {
    if (redirectIfNotAuth && !authContext.loading && !authContext.isAuthenticated && pathname !== '/login') {
      router.replace('/login');
    }
  }, [authContext.isAuthenticated, authContext.loading, redirectIfNotAuth, pathname, router]);

  return {
    user: authContext.user,
    loading: authContext.loading,
    isAuthenticated: authContext.isAuthenticated,
    login: authContext.login,
    logout: authContext.logout,
  };
}
