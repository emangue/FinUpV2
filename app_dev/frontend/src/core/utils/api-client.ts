/**
 * Cliente HTTP com autenticação via cookie httpOnly.
 * Autenticação é gerenciada exclusivamente pelo cookie `auth_token`
 * setado pelo backend — não há leitura/escrita em localStorage.
 * @module api-client
 */

export async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const isFormData = options.body instanceof FormData
  const headers: HeadersInit = {
    ...(!isFormData && { 'Content-Type': 'application/json' }),
    ...options.headers,
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include', // cookie httpOnly enviado automaticamente
    redirect: 'follow',
  })

  if (response.status === 401 && typeof window !== 'undefined') {
    window.location.href = '/auth/login'
  }

  return response
}

/**
 * Faz requisição HTTP e retorna JSON parseado automaticamente
 * Lança erro se response não for OK (status >= 400)
 * 
 * @param url - URL completa do endpoint
 * @param options - Opções do fetch
 * @returns Promise com dados parseados (tipo genérico T)
 * 
 * @throws {Error} Se response.ok === false
 * 
 * @example
 * ```typescript
 * interface Resumo {
 *   total_investido: string
 *   rendimento_total: string
 * }
 * 
 * const resumo = await fetchJsonWithAuth<Resumo>(
 *   'http://localhost:8000/api/v1/investimentos/resumo'
 * )
 * console.log(resumo.total_investido)
 * ```
 */
export async function fetchJsonWithAuth<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetchWithAuth(url, options)
  
  // Validar se response é OK
  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(
      `HTTP ${response.status}: ${response.statusText}\n${errorText}`
    )
  }
  
  // Parsear JSON
  return response.json()
}

/** @deprecated Removido — autenticação via cookie httpOnly não é detectável via JS.
 * Use AuthContext para verificar estado de autenticação. */
export function isAuthenticated(): boolean {
  // Mantido apenas para compatibilidade de tipos — sempre retorna false
  // Migrar chamadores para AuthContext.isAuthenticated
  return false
}

/** @deprecated Removido — cookie httpOnly é limpo pelo backend no logout.
 * Chame POST /api/v1/auth/logout em vez disso. */
export function clearAuth(): void {
  // no-op intencional
}

/** @deprecated Removido — backend seta cookie httpOnly automaticamente no login.
 * Não armazenar token em localStorage. */
export function setAuthToken(_token: string): void {
  // no-op intencional
}
