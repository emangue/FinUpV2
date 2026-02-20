'use client'

/**
 * Contexto de Autenticação
 * Usa cookie httpOnly (backend) - não armazena token em localStorage
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

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

  useEffect(() => {
    if (typeof window === 'undefined') return
    loadUser()
  }, [])

  const login = async (email: string, password: string) => {
    const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
    const response = await fetch(`${apiUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      credentials: 'include',
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Erro ao fazer login')
    }

    const data = await response.json()
    setToken(data.access_token)
    setUser(data.user)
  }

  const logout = async () => {
    const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
    try {
      await fetch(`${apiUrl}/api/v1/auth/logout`, { method: 'POST', credentials: 'include' })
    } finally {
      setToken(null)
      setUser(null)
    }
  }

  const loadUser = async () => {
    const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
    try {
      const response = await fetch(`${apiUrl}/api/v1/auth/me`, { credentials: 'include' })
      if (!response.ok) throw new Error('Token inválido')
      const userData = await response.json()
      setUser(userData)
      setToken('cookie') // Placeholder - token está em httpOnly cookie
    } catch {
      setUser(null)
      setToken(null)
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
