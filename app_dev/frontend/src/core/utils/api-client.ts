/**
 * Cliente HTTP com autenticação
 * Usa cookie httpOnly (credentials: 'include') - token não fica em localStorage
 * @module api-client
 */

export async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const isFormData = options.body instanceof FormData
  const token = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null
  const headers: HeadersInit = {
    ...(!isFormData && { 'Content-Type': 'application/json' }),
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',
    redirect: 'follow',
  })

  if (response.status === 401 && typeof window !== 'undefined') {
    localStorage.removeItem('authToken')
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

/** @deprecated Use useAuth() from AuthContext. Cookie httpOnly não é legível via JS. */
export function isAuthenticated(): boolean {
  return !!localStorage.getItem('authToken')
}

export function clearAuth(): void {
  localStorage.removeItem('authToken')
}

/** @deprecated Backend seta cookie httpOnly. Mantido para compatibilidade. */
export function setAuthToken(token: string): void {
  localStorage.setItem('authToken', token)
}
