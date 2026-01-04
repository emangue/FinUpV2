import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Rotas que NÃO requerem autenticação
const publicPaths = ['/login', '/register'];

// Rotas que requerem autenticação
const protectedPaths = ['/dashboard', '/transactions', '/upload', '/settings'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // ⚠️ BYPASS TEMPORÁRIO: Autenticação desabilitada para desenvolvimento
  // TODO: Reativar verificação de autenticação após correção dos problemas
  
  // Verificar se é uma rota protegida
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path));
  const isPublicPath = publicPaths.some(path => pathname.startsWith(path));

  // TEMPORÁRIO: Sempre permitir acesso (bypass de autenticação)
  return NextResponse.next();

  /* CÓDIGO ORIGINAL (REATIVAR DEPOIS):
  if (isProtectedPath) {
    // No middleware do Next.js não temos acesso ao localStorage
    // A verificação real será feita no cliente
    return NextResponse.next();
  }

  // Permitir acesso a rotas públicas e assets
  return NextResponse.next();
  */
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
