'use client'

import { Menu } from 'lucide-react'
import { SidebarTrigger } from '@/components/ui/sidebar'
import { useAuth } from '@/hooks/use-auth'

export function MobileHeader() {
  const { user } = useAuth()
  
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="flex items-center justify-between h-16 px-4">
        {/* Hamburger Menu */}
        <SidebarTrigger className="h-10 w-10 flex items-center justify-center hover:bg-gray-100 rounded-lg transition-colors">
          <Menu className="h-6 w-6 text-gray-700" />
        </SidebarTrigger>

        {/* Título e usuário */}
        <div className="flex-1 ml-4">
          <h1 className="text-lg font-semibold text-gray-900">
            Dashboard Financeiro
          </h1>
          {user && (
            <p className="text-xs text-gray-500">
              Olá, {user.name || user.email}
            </p>
          )}
        </div>

        {/* Espaço para ações futuras (notificações, etc) */}
        <div className="w-10" />
      </div>
    </header>
  )
}
