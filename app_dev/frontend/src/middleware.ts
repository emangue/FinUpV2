/**
 * Mobile Redirect Middleware
 * 
 * Detecta dispositivos mobile (width < 768px) e redireciona
 * automaticamente para as rotas /mobile/*
 * 
 * Rotas mapeadas:
 * - / → /mobile/dashboard
 * - /dashboard → /mobile/dashboard
 * - /transactions → /mobile/transactions
 * - /budget → /mobile/budget
 * - /investimentos → /mobile/investimentos (futuro)
 * - /upload → /mobile/upload
 * - /profile → /mobile/profile
 */

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Rotas que devem ser redirecionadas para mobile
const MOBILE_ROUTES = {
  '/': '/mobile/dashboard',
  '/dashboard': '/mobile/dashboard',
  '/transactions': '/mobile/transactions',
  '/budget': '/mobile/budget',
  '/upload': '/mobile/upload',
  '/profile': '/mobile/profile',
}

// Rotas que NÃO devem ser redirecionadas
const EXCLUDE_PATHS = [
  '/api',
  '/_next',
  '/static',
  '/favicon.ico',
  '/login',
  '/mobile', // Já está em mobile
]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Não redirecionar rotas excluídas
  if (EXCLUDE_PATHS.some(path => pathname.startsWith(path))) {
    return NextResponse.next()
  }
  
  // Detectar se é mobile via User-Agent
  const userAgent = request.headers.get('user-agent') || ''
  const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent)
  
  // Detectar se usuário prefere mobile (cookie)
  const prefersMobile = request.cookies.get('prefer-mobile')?.value === 'true'
  const prefersDesktop = request.cookies.get('prefer-desktop')?.value === 'true'
  
  // Se usuário preferir desktop, não redirecionar
  if (prefersDesktop) {
    return NextResponse.next()
  }
  
  // Redirecionar para mobile se:
  // 1. É dispositivo mobile OU
  // 2. Usuário prefere mobile
  const shouldRedirectToMobile = isMobileDevice || prefersMobile
  
  if (shouldRedirectToMobile) {
    // Verificar se há mapeamento para essa rota
    const mobileRoute = MOBILE_ROUTES[pathname as keyof typeof MOBILE_ROUTES]
    
    if (mobileRoute) {
      const url = request.nextUrl.clone()
      url.pathname = mobileRoute
      
      // Preservar query params
      return NextResponse.redirect(url)
    }
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
