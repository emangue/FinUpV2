/**
 * Layout Mobile - Transações
 * Usa o mesmo layout que /mobile/* (BottomNavigation)
 */

import { BottomNavigation } from '@/components/mobile/bottom-navigation'

export default function TransactionsMobileLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-white pb-20">
      {children}
      <BottomNavigation />
    </div>
  )
}
