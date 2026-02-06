import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Metas - Finance App',
  description: 'Gerenciamento de metas financeiras',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className="bg-gray-50">{children}</body>
    </html>
  )
}
