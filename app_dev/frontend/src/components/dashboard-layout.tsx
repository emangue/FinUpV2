'use client'

/**
 * DashboardLayout - Layout minimalista para páginas desktop
 * Usado por settings, upload, transactions, etc.
 * Sem sidebar - link para mobile.
 */

import Link from 'next/link'

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-10 bg-white border-b px-4 py-3">
        <Link href="/mobile/dashboard" className="text-sm font-medium text-primary hover:underline">
          ← Voltar ao app
        </Link>
      </header>
      <main className="p-4">{children}</main>
    </div>
  )
}
