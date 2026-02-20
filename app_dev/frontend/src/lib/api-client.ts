/**
 * Cliente API com interceptor de autenticação
 * Adiciona token JWT automaticamente e trata erros 401
 */

// Função helper para pegar token do localStorage
function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('token')
}

// Função helper para limpar autenticação
function clearAuth() {
  if (typeof window === 'undefined') return
  localStorage.removeItem('token')
  window.location.href = '/login'
}

/**
 * Fetch com interceptor de autenticação
 * Adiciona Authorization header automaticamente se token existir
 * Redireciona para /login em caso de 401 Unauthorized
 */
export async function apiFetch(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response> {
  // Preparar headers
  const headers = new Headers(init?.headers)
  
  // Adicionar token JWT se existir
  const token = getToken()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  
  // Fazer requisição
  const response = await fetch(input, {
    ...init,
    headers,
  })
  
  // Interceptar 401 Unauthorized
  if (response.status === 401) {
    console.warn('[API] 401 Unauthorized - Redirecionando para login')
    clearAuth()
    // Não retornar nada, pois vamos redirecionar
    return new Response(null, { status: 401 })
  }
  
  return response
}

/**
 * Helper para fazer requisições JSON
 */
export async function apiRequest<T = any>(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<T> {
  const response = await apiFetch(input, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Erro desconhecido' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }
  
  return response.json()
}

/**
 * Helpers específicos por método HTTP
 */
export const api = {
  get: <T = any>(url: string, init?: RequestInit) =>
    apiRequest<T>(url, { ...init, method: 'GET' }),
  
  post: <T = any>(url: string, data?: any, init?: RequestInit) =>
    apiRequest<T>(url, {
      ...init,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),
  
  put: <T = any>(url: string, data?: any, init?: RequestInit) =>
    apiRequest<T>(url, {
      ...init,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),
  
  patch: <T = any>(url: string, data?: any, init?: RequestInit) =>
    apiRequest<T>(url, {
      ...init,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }),
  
  delete: <T = any>(url: string, init?: RequestInit) =>
    apiRequest<T>(url, { ...init, method: 'DELETE' }),
}
