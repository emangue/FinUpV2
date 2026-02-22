'use client'

import { Settings } from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '@/hooks/use-auth'

export function MobileHeader() {
  const { user } = useAuth()

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="flex items-center justify-between h-16 px-4">
        {/* Título e usuário */}
        <div className="flex-1">
          <h1 className="text-lg font-semibold text-gray-900">
            Dashboard Financeiro
          </h1>
          {user && (
            <p className="text-xs text-gray-500">
              Olá, {user.nome || user.email}
            </p>
          )}
        </div>

        {/* Configurações (mobile não usa sidebar) */}
        <Link
          href="/settings"
          className="h-10 w-10 flex items-center justify-center hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Configurações"
        >
          <Settings className="h-6 w-6 text-gray-700" />
        </Link>
      </div>
    </header>
  )
}
