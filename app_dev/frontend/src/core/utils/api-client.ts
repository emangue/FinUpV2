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
  // Buscar token do localStorage (salvo no login)
  const token = localStorage.getItem('authToken')
  
  // Detectar se body é FormData (para uploads)
  const isFormData = options.body instanceof FormData
  
  // Mesclar headers existentes com Authorization
  // NÃO adicionar Content-Type se for FormData (browser adiciona automaticamente com boundary)
  const headers: HeadersInit = {
    ...(!isFormData && { 'Content-Type': 'application/json' }),
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  }

  // Fazer request com token (follow redirects com redirect: 'follow')
  const response = await fetch(url, {
    ...options,
    headers,
    redirect: 'follow',  // Segue redirects 307 automaticamente
  })
  
  // 🔐 REDIRECT AUTOMÁTICO - Se 401 Unauthorized, redirecionar para login
  if (response.status === 401) {
    // Limpar token inválido
    clearAuth()
    
    // Redirecionar para login (se estiver no browser)
    if (typeof window !== 'undefined') {
      window.location.href = '/auth/login'
    }
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

/**
 * Verifica se usuário está autenticado (tem token válido)
 * 
 * @returns true se token existe no localStorage
 */
export function isAuthenticated(): boolean {
  const token = localStorage.getItem('authToken')
  return !!token
}

/**
 * Remove token do localStorage (logout)
 */
export function clearAuth(): void {
  localStorage.removeItem('authToken')
}

/**
 * Salva token no localStorage (login)
 * 
 * @param token - Token JWT retornado do backend
 */
export function setAuthToken(token: string): void {
  localStorage.setItem('authToken', token)
}
