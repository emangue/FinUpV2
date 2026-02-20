/**
 * Mobile Redirect Middleware
 *
 * Visão 100% mobile: sempre redireciona rotas desktop para /mobile/*
 * Desktop removido do deploy - ver _arquivo_desktop/
 */

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const MOBILE_ROUTES: Record<string, string> = {
  '/': '/mobile/dashboard',
  '/dashboard': '/mobile/dashboard',
  '/transactions': '/mobile/transactions',
  '/budget': '/mobile/budget',
  '/investimentos': '/mobile/investimentos',
  '/upload': '/mobile/upload',
  '/profile': '/mobile/profile',
}

const EXCLUDE_PATHS = ['/api', '/_next', '/static', '/favicon.ico', '/login', '/auth', '/mobile']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  if (EXCLUDE_PATHS.some((path) => pathname.startsWith(path))) {
    return NextResponse.next()
  }

  const mobileRoute = MOBILE_ROUTES[pathname] ?? MOBILE_ROUTES[pathname.replace(/\/$/, '')]
  if (mobileRoute) {
    const url = request.nextUrl.clone()
    url.pathname = mobileRoute
    return NextResponse.redirect(url)
  }

  return NextResponse.next()
}

// Configurar quais rotas o middleware deve processar
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * 1. /api routes
     * 2. /_next (Next.js internals)
     * 3. /_static (inside /public)
     * 4. all root files inside /public (e.g. /favicon.ico)
     */
    '/((?!api|_next|_static|_vercel|[\\w-]+\\.\\w+).*)',
  ],
}
