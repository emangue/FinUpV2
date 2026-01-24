/**
 * Cliente HTTP com autenticação JWT automática
 * 
 * Adiciona header Authorization: Bearer <token> em todas as requests
 * Busca token do localStorage automaticamente
 * 
 * @module api-client
 * @see PLANO_ISOLAMENTO_DADOS.md - FASE 1
 */

/**
 * Faz requisição HTTP com autenticação JWT automática
 * 
 * @param url - URL completa do endpoint
 * @param options - Opções do fetch (method, body, etc)
 * @returns Promise com Response
 * 
 * @example
 * ```typescript
 * const response = await fetchWithAuth('http://localhost:8000/api/v1/investimentos/resumo')
 * const data = await response.json()
 * ```
 */
export async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  // Buscar token do localStorage (salvo no login) - apenas no cliente
  const token = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null
  
  // 🐛 DEBUG TEMPORÁRIO - Remover após validar
  console.log('[api-client] fetchWithAuth chamado:', {
    url,
    tokenExists: !!token,
    tokenPreview: token ? `${token.substring(0, 20)}...` : 'NENHUM TOKEN',
  })
  
  // Mesclar headers existentes com Authorization
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  }

  // 🐛 DEBUG TEMPORÁRIO
  console.log('[api-client] Headers enviados:', headers)

  // Fazer request com token
  return fetch(url, {
    ...options,
    headers,
  })
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

/**
 * Verifica se usuário está autenticado (tem token válido)
 * 
 * @returns true se token existe no localStorage
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false
  const token = localStorage.getItem('authToken')
  return !!token
}

/**
 * Remove token do localStorage (logout)
 */
export function clearAuth(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem('authToken')
}

/**
 * Salva token no localStorage (login)
 * 
 * @param token - Token JWT retornado do backend
 */
export function setAuthToken(token: string): void {
  if (typeof window === 'undefined') return
  localStorage.setItem('authToken', token)
}
