"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react"
import { API_CONFIG } from "@/core/config/api.config"

export interface User {
  id: number
  email: string
  nome: string
  role: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  login: (email: string, password: string) => Promise<User>
  logout: () => void
  loadUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (typeof window === "undefined") return
    loadUser()
  }, [])

  const login = async (email: string, password: string) => {
    const apiUrl = API_CONFIG.BACKEND_URL
    const response = await fetch(`${apiUrl}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
      credentials: "include",
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || "Erro ao fazer login")
    }

    const data = await response.json()
    const userData = data.user
    setUser(userData)
    return userData
  }

  const logout = async () => {
    const apiUrl = API_CONFIG.BACKEND_URL
    try {
      await fetch(`${apiUrl}/api/v1/auth/logout`, {
        method: "POST",
        credentials: "include",
      })
    } finally {
      setUser(null)
    }
  }

  const loadUser = async () => {
    const apiUrl = API_CONFIG.BACKEND_URL
    try {
      const response = await fetch(`${apiUrl}/api/v1/auth/me`, {
        credentials: "include",
      })
      if (!response.ok) throw new Error("Token inválido")
      const userData = await response.json()
      setUser(userData)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    logout,
    loadUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (ctx === undefined) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
