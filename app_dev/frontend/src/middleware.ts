import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { API_ENDPOINTS } from '@/core/config/api.config';

// Rotas que NÃO requerem autenticação
const publicPaths = ['/login', '/register'];

// Rotas que requerem autenticação
const protectedPaths = ['/dashboard', '/transactions', '/upload', '/settings'];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Verificar se é uma rota protegida
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path));
  const isPublicPath = publicPaths.some(path => pathname.startsWith(path));

  // Se não é rota protegida, permitir acesso
  if (!isProtectedPath) {
    return NextResponse.next();
  }

  // ⚠️ Rota protegida: verificar autenticação via backend
  try {
    // Pegar cookie access_token do request
    const accessToken = request.cookies.get('access_token');
    
    if (!accessToken) {
      // Sem cookie, redirecionar para login
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('redirect', pathname);
      return NextResponse.redirect(loginUrl);
    }

    // Validar token chamando /auth/me
    const response = await fetch(API_ENDPOINTS.AUTH.ME, {
      method: 'GET',
      headers: {
        'Cookie': `access_token=${accessToken.value}`,
      },
      credentials: 'include',
    });

    if (!response.ok) {
      // Token inválido/expirado, redirecionar para login
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('redirect', pathname);
      return NextResponse.redirect(loginUrl);
    }

    // Token válido, permitir acesso
    return NextResponse.next();
    
  } catch (error) {
    // Erro na validação, redirecionar para login por segurança
    console.error('Middleware auth error:', error);
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
