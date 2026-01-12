'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { authAPI } from '@/lib/api-client';

interface User {
  id: number;
  email: string;
  nome: string;
  role: string;
  ativo: number;
}

/**
 * Hook de autenticação
 * 
 * Valida autenticação via cookies httpOnly chamando /auth/me
 * 
 * @param redirectIfNotAuth - Se true, redireciona para /login se não autenticado
 */
export function useAuth(redirectIfNotAuth = true) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Chamar /auth/me - cookies httpOnly são enviados automaticamente
        const userData = await authAPI.me();
        setUser(userData);
        setLoading(false);
      } catch (error: any) {
        console.error('Auth check failed:', error);
        setUser(null);
        setLoading(false);
        
        // Se não autenticado e deve redirecionar
        if (redirectIfNotAuth && pathname !== '/login') {
          const redirectUrl = `/login?redirect=${encodeURIComponent(pathname)}`;
          router.replace(redirectUrl);
        }
      }
    };

    checkAuth();
  }, [router, pathname, redirectIfNotAuth]);

  return { 
    user, 
    loading, 
    isAuthenticated: !!user 
  };
}
