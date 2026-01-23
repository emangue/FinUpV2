'use client'

import { Menu, ArrowLeft } from 'lucide-react'
import { SidebarTrigger } from '@/components/ui/sidebar'
import { useRouter } from 'next/navigation'

export function TransactionsMobileHeader() {
  const router = useRouter()
  
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-primary text-primary-foreground shadow-sm">
      <div className="flex items-center h-16 px-4">
        {/* Botão voltar */}
        <button
          onClick={() => router.back()}
          className="h-10 w-10 flex items-center justify-center hover:bg-primary-foreground/10 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-6 w-6" />
        </button>

        {/* Título centralizado */}
        <h1 className="flex-1 text-center text-lg font-semibold">
          Transações
        </h1>

        {/* Hamburger Menu */}
        <SidebarTrigger className="h-10 w-10 flex items-center justify-center hover:bg-primary-foreground/10 rounded-lg transition-colors">
          <Menu className="h-6 w-6" />
        </SidebarTrigger>
      </div>
    </header>
  )
}
