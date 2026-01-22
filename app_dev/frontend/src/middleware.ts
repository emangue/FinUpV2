import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Rotas que NÃO requerem autenticação
const publicPaths = ['/login', '/register'];

// Rotas que requerem autenticação
const protectedPaths = ['/dashboard', '/transactions', '/upload', '/settings'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Verificar se é uma rota protegida
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path));
  const isPublicPath = publicPaths.some(path => pathname.startsWith(path));

  // Se for rota protegida, verificar autenticação
  if (isProtectedPath) {
    // Verificar token no cookie
    const token = request.cookies.get('auth_token')?.value;
    
    if (!token) {
      // Sem token → redirecionar para login
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('redirect', pathname);
      return NextResponse.redirect(loginUrl);
    }
    
    // Token existe → permitir acesso
    return NextResponse.next();
  }

  // Permitir acesso a rotas públicas e assets
  return NextResponse.next();
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
