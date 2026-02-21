'use client'

import { Settings, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
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
          aria-label="Voltar"
        >
          <ArrowLeft className="h-6 w-6" />
        </button>

        {/* Título centralizado */}
        <h1 className="flex-1 text-center text-lg font-semibold">
          Transações
        </h1>

        {/* Configurações (mobile não usa sidebar) */}
        <Link
          href="/settings"
          className="h-10 w-10 flex items-center justify-center hover:bg-primary-foreground/10 rounded-lg transition-colors"
          aria-label="Configurações"
        >
          <Settings className="h-6 w-6" />
        </Link>
      </div>
    </header>
  )
}
