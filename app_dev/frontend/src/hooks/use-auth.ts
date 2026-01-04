'use client';

import { useRouter, usePathname } from 'next/navigation';

interface User {
  id: number;
  email: string;
  name: string;
  role: string;
}

export function useAuth(redirectIfNotAuth = true) {
  const router = useRouter();
  const pathname = usePathname();
  
  // ⚠️ BYPASS COMPLETO: Retornar usuário imediatamente sem checks
  // TODO: Reativar verificação de autenticação após correção
  const user: User = {
    id: 1,
    email: 'admin@financas.com',
    name: 'Administrator',
    role: 'admin'
  };

  return { 
    user, 
    loading: false, 
    isAuthenticated: true 
  };
  
  /* CÓDIGO ORIGINAL (REATIVAR DEPOIS):
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = () => {
      const authenticated = isAuthenticated();
      
      if (!authenticated) {
        setUser(null);
        setLoading(false);
        
        if (redirectIfNotAuth && pathname !== '/login') {
          router.replace('/login');
        }
        return;
      }

      const currentUser = getCurrentUser();
      setUser(currentUser);
      setLoading(false);
    };

    checkAuth();
  }, [router, pathname, redirectIfNotAuth]);

  return { user, loading, isAuthenticated: !!user };
  */
}
