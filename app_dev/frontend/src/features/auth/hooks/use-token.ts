/**
 * Hook para gerenciamento de tokens JWT
 * Persistência em localStorage
 * 
 * ⚠️ PADRONIZAÇÃO: Usa 'authToken' para consistência com api-client.ts
 */

const TOKEN_KEY = 'authToken'

export function saveToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token)
  } catch (error) {
    console.error('Erro ao salvar token:', error)
  }
}

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch (error) {
    console.error('Erro ao recuperar token:', error)
    return null
  }
}

export function removeToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch (error) {
    console.error('Erro ao remover token:', error)
  }
}

export function isTokenValid(token: string | null): boolean {
  if (!token) return false

  try {
    // Decodificar payload do JWT (base64)
    const payload = JSON.parse(atob(token.split('.')[1]))
    
    // Verificar expiração
    const exp = payload.exp
    if (!exp) return false

    // exp é timestamp em segundos, Date.now() é em milissegundos
    return Date.now() < exp * 1000
  } catch (error) {
    console.error('Erro ao validar token:', error)
    return false
  }
}

export function getTokenPayload(token: string): any {
  try {
    return JSON.parse(atob(token.split('.')[1]))
  } catch (error) {
    console.error('Erro ao decodificar token:', error)
    return null
  }
}

export function getUserIdFromToken(token: string | null): number | null {
  if (!token) return null

  try {
    const payload = getTokenPayload(token)
    return payload?.user_id || null
  } catch (error) {
    console.error('Erro ao extrair user_id:', error)
    return null
  }
}
