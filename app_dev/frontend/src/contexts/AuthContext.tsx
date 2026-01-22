'use client'

/**
 * Contexto de Autenticação
 * Gerencia estado global de autenticação do usuário
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { setAuthToken, clearAuth, fetchJsonWithAuth } from '@/core/utils/api-client'

export interface User {
  id: number
  email: string
  nome: string
  role: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // Carregar token do localStorage ao montar
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken')
    if (storedToken) {
      setToken(storedToken)
      loadUser(storedToken)
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      const response = await fetch(`${apiUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Erro ao fazer login')
      }

      const data = await response.json()
      const { access_token, user: userData } = data

      // 🐛 DEBUG TEMPORÁRIO - Remover após validar
      console.log('[AuthContext] Login bem-sucedido:', {
        tokenPreview: `${access_token.substring(0, 20)}...`,
        userId: userData.id,
        userEmail: userData.email,
      })

      // Salvar token no localStorage E no cookie (middleware espera 'auth_token')
      setAuthToken(access_token)
      document.cookie = `auth_token=${access_token}; path=/; max-age=3600; SameSite=Lax`
      
      setToken(access_token)
      setUser(userData)

      // 🐛 DEBUG TEMPORÁRIO - Verificar se foi salvo
      console.log('[AuthContext] Login completo:', {
        localStorage: localStorage.getItem('authToken') === access_token,
        cookieSet: document.cookie.includes('auth_token='),
        willRedirect: true
      })
    } catch (error) {
      console.error('Erro no login:', error)
      throw error
    }
  }

  const logout = () => {
    clearAuth()  // Remove 'authToken' do localStorage
    document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
    setToken(null)
    setUser(null)
  }

  const loadUser = async (authToken?: string) => {
    const tokenToUse = authToken || token

    if (!tokenToUse) {
      setLoading(false)
      return
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      const response = await fetch(`${apiUrl}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${tokenToUse}`,
        },
      })

      if (!response.ok) {
        throw new Error('Token inválido')
      }

      const userData = await response.json()
      setUser(userData)
    } catch (error) {
      console.error('Erro ao carregar usuário:', error)
      logout() // Token inválido, fazer logout
    } finally {
      setLoading(false)
    }
  }

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user,
    loading,
    login,
    logout,
    loadUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
